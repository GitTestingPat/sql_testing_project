"""
Test suite for Sakila database performance testing.
Measures query execution times and identifies potential bottlenecks.
"""

import pytest
import time


@pytest.mark.sakila
@pytest.mark.performance
class TestSakilaQueryPerformance:
    """Tests for Sakila query performance."""
    
    def test_simple_select_performance(self, sakila_db):
        """TC-SAK-058: Measure simple SELECT performance."""
        start = time.time()
        
        result = sakila_db.execute_query("SELECT * FROM film")
        
        execution_time = time.time() - start
        
        assert len(result) == 1000
        assert execution_time < 1.0, f"Query took {execution_time:.2f}s"
        print(f"\nSELECT * FROM film (1000 rows): {execution_time:.4f}s")
    
    def test_filtered_select_performance(self, sakila_db):
        """TC-SAK-059: Measure filtered SELECT performance."""
        start = time.time()
        
        result = sakila_db.execute_query(
            "SELECT * FROM film WHERE rating = %s", ('PG-13',)
        )
        
        execution_time = time.time() - start
        
        assert execution_time < 0.5, f"Query took {execution_time:.2f}s"
        print(f"\nFiltered SELECT: {execution_time:.4f}s ({len(result)} rows)")
    
    def test_join_performance(self, sakila_db):
        """TC-SAK-060: Measure JOIN query performance."""
        start = time.time()
        
        result = sakila_db.execute_query("""
            SELECT f.title, c.name as category
            FROM film f
            JOIN film_category fc ON f.film_id = fc.film_id
            JOIN category c ON fc.category_id = c.category_id
        """)
        
        execution_time = time.time() - start
        
        assert execution_time < 1.0, f"Query took {execution_time:.2f}s"
        print(f"\n2-table JOIN: {execution_time:.4f}s ({len(result)} rows)")
    
    def test_complex_join_performance(self, sakila_db):
        """TC-SAK-061: Measure complex multi-table JOIN performance."""
        start = time.time()
        
        result = sakila_db.execute_query("""
            SELECT r.rental_id, c.first_name, c.last_name, 
                   f.title, s.first_name as staff_name
            FROM rental r
            JOIN customer c ON r.customer_id = c.customer_id
            JOIN inventory i ON r.inventory_id = i.inventory_id
            JOIN film f ON i.film_id = f.film_id
            JOIN staff s ON r.staff_id = s.staff_id
        """)
        
        execution_time = time.time() - start
        
        assert execution_time < 3.0, f"Query took {execution_time:.2f}s"
        print(f"\n5-table JOIN: {execution_time:.4f}s ({len(result)} rows)")
    
    def test_aggregation_performance(self, sakila_db):
        """TC-SAK-062: Measure aggregation query performance."""
        start = time.time()
        
        result = sakila_db.execute_query("""
            SELECT c.name as category, 
                   COUNT(f.film_id) as film_count,
                   AVG(f.rental_rate) as avg_rate
            FROM category c
            JOIN film_category fc ON c.category_id = fc.category_id
            JOIN film f ON fc.film_id = f.film_id
            GROUP BY c.category_id, c.name
            ORDER BY film_count DESC
        """)
        
        execution_time = time.time() - start
        
        assert len(result) == 16
        assert execution_time < 1.0, f"Query took {execution_time:.2f}s"
        print(f"\nAggregation with GROUP BY: {execution_time:.4f}s")
    
    def test_subquery_performance(self, sakila_db):
        """TC-SAK-063: Measure subquery performance."""
        start = time.time()
        
        result = sakila_db.execute_query("""
            SELECT title, rental_rate
            FROM film
            WHERE rental_rate > (SELECT AVG(rental_rate) FROM film)
        """)
        
        execution_time = time.time() - start
        
        assert execution_time < 1.0, f"Query took {execution_time:.2f}s"
        print(f"\nSubquery: {execution_time:.4f}s ({len(result)} rows)")
    
    def test_full_text_search_simulation(self, sakila_db):
        """TC-SAK-064: Measure LIKE pattern search performance."""
        start = time.time()
        
        result = sakila_db.execute_query(
            "SELECT * FROM film WHERE description LIKE %s", ('%Drama%',)
        )
        
        execution_time = time.time() - start
        
        assert execution_time < 1.0, f"Query took {execution_time:.2f}s"
        print(f"\nLIKE search: {execution_time:.4f}s ({len(result)} rows)")
    
    def test_order_by_performance(self, sakila_db):
        """TC-SAK-065: Measure ORDER BY performance on large table."""
        start = time.time()
        
        result = sakila_db.execute_query("""
            SELECT * FROM rental 
            ORDER BY rental_date DESC
        """)
        
        execution_time = time.time() - start
        
        assert execution_time < 2.0, f"Query took {execution_time:.2f}s"
        print(f"\nORDER BY on rental: {execution_time:.4f}s ({len(result)} rows)")
    
    def test_count_performance(self, sakila_db):
        """TC-SAK-066: Measure COUNT performance."""
        start = time.time()
        
        result = sakila_db.execute_query("SELECT COUNT(*) as total FROM payment")
        
        execution_time = time.time() - start
        
        assert execution_time < 0.5, f"Query took {execution_time:.2f}s"
        print(f"\nCOUNT on payment: {execution_time:.4f}s")
    
    def test_distinct_performance(self, sakila_db):
        """TC-SAK-067: Measure DISTINCT performance."""
        start = time.time()
        
        result = sakila_db.execute_query("""
            SELECT DISTINCT customer_id FROM rental
        """)
        
        execution_time = time.time() - start
        
        assert execution_time < 1.0, f"Query took {execution_time:.2f}s"
        print(f"\nDISTINCT: {execution_time:.4f}s ({len(result)} unique customers)")


@pytest.mark.sakila
@pytest.mark.performance
class TestSakilaViewPerformance:
    """Tests for Sakila view performance."""
    
    def test_customer_list_view(self, sakila_db):
        """TC-SAK-068: Measure customer_list view performance."""
        start = time.time()
        
        result = sakila_db.execute_query("SELECT * FROM customer_list")
        
        execution_time = time.time() - start
        
        assert execution_time < 2.0, f"Query took {execution_time:.2f}s"
        print(f"\ncustomer_list view: {execution_time:.4f}s ({len(result)} rows)")
    
    def test_film_list_view(self, sakila_db):
        """TC-SAK-069: Measure film_list view performance."""
        start = time.time()
        
        result = sakila_db.execute_query("SELECT * FROM film_list")
        
        execution_time = time.time() - start
        
        assert execution_time < 2.0, f"Query took {execution_time:.2f}s"
        print(f"\nfilm_list view: {execution_time:.4f}s ({len(result)} rows)")
    
    def test_sales_by_category_view(self, sakila_db):
        """TC-SAK-070: Measure sales_by_film_category view performance."""
        start = time.time()
        
        result = sakila_db.execute_query("SELECT * FROM sales_by_film_category")
        
        execution_time = time.time() - start
        
        assert execution_time < 2.0, f"Query took {execution_time:.2f}s"
        print(f"\nsales_by_film_category view: {execution_time:.4f}s ({len(result)} rows)")
