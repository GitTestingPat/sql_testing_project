"""
Test suite for Sakila database query validation.
Tests complex queries, aggregations, joins, and business logic.
"""

import pytest
from data.sakila_test_data import SAKILA_TEST_QUERIES


@pytest.mark.sakila
@pytest.mark.queries
class TestSakilaBasicQueries:
    """Tests for basic SELECT queries on Sakila."""
    
    def test_select_all_actors(self, sakila_db):
        """TC-SAK-037: Verify selecting all actors."""
        result = sakila_db.execute_query("SELECT * FROM actor LIMIT 10")
        
        assert len(result) == 10
        assert 'actor_id' in result[0]
        assert 'first_name' in result[0]
        assert 'last_name' in result[0]
    
    def test_select_films_by_rating(self, sakila_db):
        """TC-SAK-038: Verify selecting films by rating."""
        result = sakila_db.execute_query(
            "SELECT * FROM film WHERE rating = %s", ('PG-13',)
        )
        
        assert len(result) > 0
        for film in result:
            assert film['rating'] == 'PG-13'
    
    def test_select_active_customers(self, sakila_db):
        """TC-SAK-039: Verify selecting active customers."""
        result = sakila_db.execute_query(
            "SELECT * FROM customer WHERE active = 1"
        )
        
        assert len(result) > 0
        for customer in result:
            assert customer['active'] == 1
    
    def test_select_films_with_order(self, sakila_db):
        """TC-SAK-040: Verify selecting films with ORDER BY."""
        result = sakila_db.execute_query(
            "SELECT title, rental_rate FROM film ORDER BY rental_rate DESC LIMIT 10"
        )
        
        rates = [float(row['rental_rate']) for row in result]
        assert rates == sorted(rates, reverse=True)
    
    def test_select_with_like(self, sakila_db):
        """TC-SAK-041: Verify LIKE pattern matching."""
        result = sakila_db.execute_query(
            "SELECT * FROM film WHERE title LIKE %s", ('A%',)
        )
        
        assert len(result) > 0
        for film in result:
            assert film['title'].startswith('A')


@pytest.mark.sakila
@pytest.mark.queries
class TestSakilaJoinQueries:
    """Tests for JOIN queries on Sakila."""
    
    def test_film_with_language(self, sakila_db):
        """TC-SAK-042: Verify film-language join."""
        result = sakila_db.execute_query("""
            SELECT f.title, l.name as language
            FROM film f
            JOIN language l ON f.language_id = l.language_id
            LIMIT 10
        """)
        
        assert len(result) == 10
        for row in result:
            assert row['language'] is not None
    
    def test_customer_with_address(self, sakila_db):
        """TC-SAK-043: Verify customer-address join."""
        result = sakila_db.execute_query("""
            SELECT c.first_name, c.last_name, a.address, ci.city
            FROM customer c
            JOIN address a ON c.address_id = a.address_id
            JOIN city ci ON a.city_id = ci.city_id
            LIMIT 10
        """)
        
        assert len(result) == 10
        for row in result:
            assert row['city'] is not None
    
    def test_rental_full_details(self, sakila_db):
        """TC-SAK-044: Verify multi-table join for rental details."""
        result = sakila_db.execute_query("""
            SELECT r.rental_id, c.first_name, c.last_name, 
                   f.title, r.rental_date
            FROM rental r
            JOIN customer c ON r.customer_id = c.customer_id
            JOIN inventory i ON r.inventory_id = i.inventory_id
            JOIN film f ON i.film_id = f.film_id
            LIMIT 10
        """)
        
        assert len(result) == 10
        for row in result:
            assert row['title'] is not None
            assert row['first_name'] is not None
    
    def test_film_with_actors(self, sakila_db):
        """TC-SAK-045: Verify film-actor join."""
        result = sakila_db.execute_query("""
            SELECT f.title, a.first_name, a.last_name
            FROM film f
            JOIN film_actor fa ON f.film_id = fa.film_id
            JOIN actor a ON fa.actor_id = a.actor_id
            WHERE f.film_id = 1
        """)
        
        assert len(result) > 0
    
    def test_film_with_categories(self, sakila_db):
        """TC-SAK-046: Verify film-category join."""
        result = sakila_db.execute_query("""
            SELECT f.title, c.name as category
            FROM film f
            JOIN film_category fc ON f.film_id = fc.film_id
            JOIN category c ON fc.category_id = c.category_id
            LIMIT 20
        """)
        
        assert len(result) == 20


@pytest.mark.sakila
@pytest.mark.queries
class TestSakilaAggregationQueries:
    """Tests for aggregation queries on Sakila."""
    
    def test_count_films_by_rating(self, sakila_db):
        """TC-SAK-047: Verify COUNT with GROUP BY."""
        result = sakila_db.execute_query(SAKILA_TEST_QUERIES['films_by_rating'])
        
        assert len(result) == 5  # G, PG, PG-13, R, NC-17
        total = sum(row['film_count'] for row in result)
        assert total == 1000
    
    def test_top_rented_films(self, sakila_db):
        """TC-SAK-048: Verify top rented films query."""
        result = sakila_db.execute_query(SAKILA_TEST_QUERIES['top_rented_films'])
        
        assert len(result) == 10
        counts = [row['rental_count'] for row in result]
        assert counts == sorted(counts, reverse=True)
    
    def test_revenue_by_category(self, sakila_db):
        """TC-SAK-049: Verify revenue aggregation by category."""
        result = sakila_db.execute_query(SAKILA_TEST_QUERIES['revenue_by_category'])
        
        assert len(result) == 16  # 16 categories
        for row in result:
            assert float(row['total_revenue']) > 0
    
    def test_customer_rental_history(self, sakila_db):
        """TC-SAK-050: Verify customer rental count aggregation."""
        result = sakila_db.execute_query(SAKILA_TEST_QUERIES['customer_rental_history'])
        
        assert len(result) == 10
        for row in result:
            assert row['total_rentals'] > 0
    
    def test_actor_film_count(self, sakila_db):
        """TC-SAK-051: Verify actor film count aggregation."""
        result = sakila_db.execute_query(SAKILA_TEST_QUERIES['actor_film_count'])
        
        assert len(result) == 10
        counts = [row['film_count'] for row in result]
        assert counts == sorted(counts, reverse=True)
    
    def test_average_rental_rate(self, sakila_db):
        """TC-SAK-052: Verify AVG aggregation."""
        result = sakila_db.execute_query(
            "SELECT AVG(rental_rate) as avg_rate FROM film"
        )
        
        avg = float(result[0]['avg_rate'])
        assert 0 < avg < 10
    
    def test_total_revenue(self, sakila_db):
        """TC-SAK-053: Verify SUM aggregation on payments."""
        result = sakila_db.execute_query(
            "SELECT SUM(amount) as total FROM payment"
        )
        
        total = float(result[0]['total'])
        assert total > 0
    
    def test_min_max_film_length(self, sakila_db):
        """TC-SAK-054: Verify MIN/MAX aggregation."""
        result = sakila_db.execute_query("""
            SELECT MIN(length) as shortest, MAX(length) as longest FROM film
        """)
        
        assert result[0]['shortest'] < result[0]['longest']


@pytest.mark.sakila
@pytest.mark.queries
class TestSakilaSubqueries:
    """Tests for subqueries on Sakila."""
    
    def test_films_above_average_rental(self, sakila_db):
        """TC-SAK-055: Verify subquery for above average rental rate."""
        result = sakila_db.execute_query("""
            SELECT title, rental_rate 
            FROM film 
            WHERE rental_rate > (SELECT AVG(rental_rate) FROM film)
            LIMIT 10
        """)
        
        avg_result = sakila_db.execute_query("SELECT AVG(rental_rate) as avg FROM film")
        avg_rate = float(avg_result[0]['avg'])
        
        for film in result:
            assert float(film['rental_rate']) > avg_rate
    
    def test_customers_with_most_rentals(self, sakila_db):
        """TC-SAK-056: Verify subquery for top customers."""
        result = sakila_db.execute_query("""
            SELECT c.first_name, c.last_name,
                (SELECT COUNT(*) FROM rental r WHERE r.customer_id = c.customer_id) as rentals
            FROM customer c
            ORDER BY rentals DESC
            LIMIT 5
        """)
        
        assert len(result) == 5
        rentals = [row['rentals'] for row in result]
        assert rentals == sorted(rentals, reverse=True)
    
    def test_films_not_rented(self, sakila_db):
        """TC-SAK-057: Verify NOT IN subquery."""
        result = sakila_db.execute_query("""
            SELECT COUNT(*) as count FROM film 
            WHERE film_id NOT IN (
                SELECT DISTINCT film_id FROM inventory
            )
        """)
        
        # Some films may not be in inventory
        assert result[0]['count'] >= 0
