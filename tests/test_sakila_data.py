"""
Test suite for Sakila database data validation.
Verifies data integrity, record counts, and data quality.
"""

import pytest
from data.sakila_test_data import (
    SAKILA_EXPECTED_COUNTS, 
    SAKILA_CATEGORIES, 
    SAKILA_RATINGS,
    SAKILA_LANGUAGES
)


@pytest.mark.sakila
@pytest.mark.data
class TestSakilaRecordCounts:
    """Tests to verify Sakila has expected data volumes."""
    
    def test_actor_count(self, sakila_db):
        """TC-SAK-015: Verify actor table has ~200 records."""
        result = sakila_db.execute_query("SELECT COUNT(*) as count FROM actor")
        
        assert result[0]['count'] == SAKILA_EXPECTED_COUNTS['actor']
    
    def test_film_count(self, sakila_db):
        """TC-SAK-016: Verify film table has 1000 records."""
        result = sakila_db.execute_query("SELECT COUNT(*) as count FROM film")
        
        assert result[0]['count'] == SAKILA_EXPECTED_COUNTS['film']
    
    def test_customer_count(self, sakila_db):
        """TC-SAK-017: Verify customer table has ~599 records."""
        result = sakila_db.execute_query("SELECT COUNT(*) as count FROM customer")
        
        assert result[0]['count'] == SAKILA_EXPECTED_COUNTS['customer']
    
    def test_rental_count(self, sakila_db):
        """TC-SAK-018: Verify rental table has ~16000 records."""
        result = sakila_db.execute_query("SELECT COUNT(*) as count FROM rental")
        count = result[0]['count']
        
        # Allow some variance
        assert count >= 16000, f"Expected ~16000 rentals, got {count}"
    
    def test_payment_count(self, sakila_db):
        """TC-SAK-019: Verify payment table has ~16000 records."""
        result = sakila_db.execute_query("SELECT COUNT(*) as count FROM payment")
        count = result[0]['count']
        
        assert count >= 16000, f"Expected ~16000 payments, got {count}"
    
    def test_category_count(self, sakila_db):
        """TC-SAK-020: Verify category table has 16 records."""
        result = sakila_db.execute_query("SELECT COUNT(*) as count FROM category")
        
        assert result[0]['count'] == 16
    
    def test_language_count(self, sakila_db):
        """TC-SAK-021: Verify language table has 6 records."""
        result = sakila_db.execute_query("SELECT COUNT(*) as count FROM language")
        
        assert result[0]['count'] == 6
    
    def test_store_count(self, sakila_db):
        """TC-SAK-022: Verify store table has 2 records."""
        result = sakila_db.execute_query("SELECT COUNT(*) as count FROM store")
        
        assert result[0]['count'] == 2
    
    def test_staff_count(self, sakila_db):
        """TC-SAK-023: Verify staff table has 2 records."""
        result = sakila_db.execute_query("SELECT COUNT(*) as count FROM staff")
        
        assert result[0]['count'] == 2


@pytest.mark.sakila
@pytest.mark.data
class TestSakilaDataValues:
    """Tests to verify Sakila data values are correct."""
    
    def test_all_categories_exist(self, sakila_db):
        """TC-SAK-024: Verify all 16 categories exist."""
        result = sakila_db.execute_query("SELECT name FROM category")
        categories = [row['name'] for row in result]
        
        for cat in SAKILA_CATEGORIES:
            assert cat in categories, f"Category '{cat}' should exist"
    
    def test_all_ratings_used(self, sakila_db):
        """TC-SAK-025: Verify all film ratings are used."""
        result = sakila_db.execute_query("SELECT DISTINCT rating FROM film")
        ratings = [row['rating'] for row in result]
        
        for rating in SAKILA_RATINGS:
            assert rating in ratings, f"Rating '{rating}' should be used"
    
    def test_all_languages_exist(self, sakila_db):
        """TC-SAK-026: Verify all languages exist."""
        result = sakila_db.execute_query("SELECT name FROM language")
        languages = [row['name'] for row in result]
        
        for lang in SAKILA_LANGUAGES:
            assert lang in languages, f"Language '{lang}' should exist"
    
    def test_film_rental_rates_valid(self, sakila_db):
        """TC-SAK-027: Verify film rental rates are positive."""
        result = sakila_db.execute_query(
            "SELECT COUNT(*) as count FROM film WHERE rental_rate <= 0"
        )
        
        assert result[0]['count'] == 0, "All rental rates should be positive"
    
    def test_film_replacement_costs_valid(self, sakila_db):
        """TC-SAK-028: Verify replacement costs are positive."""
        result = sakila_db.execute_query(
            "SELECT COUNT(*) as count FROM film WHERE replacement_cost <= 0"
        )
        
        assert result[0]['count'] == 0, "All replacement costs should be positive"
    
    def test_customer_emails_not_null(self, sakila_db):
        """TC-SAK-029: Verify all customers have emails."""
        result = sakila_db.execute_query(
            "SELECT COUNT(*) as count FROM customer WHERE email IS NULL OR email = ''"
        )
        
        assert result[0]['count'] == 0, "All customers should have emails"
    
    def test_payment_amounts_positive(self, sakila_db):
        """TC-SAK-030: Verify all payment amounts are positive."""
        result = sakila_db.execute_query(
            "SELECT COUNT(*) as count FROM payment WHERE amount < 0"
        )
        
        assert result[0]['count'] == 0, "All payments should be non-negative"


@pytest.mark.sakila
@pytest.mark.data
class TestSakilaDataIntegrity:
    """Tests to verify Sakila referential integrity."""
    
    def test_all_films_have_language(self, sakila_db):
        """TC-SAK-031: Verify all films have a valid language."""
        result = sakila_db.execute_query("""
            SELECT COUNT(*) as count FROM film f
            LEFT JOIN language l ON f.language_id = l.language_id
            WHERE l.language_id IS NULL
        """)
        
        assert result[0]['count'] == 0, "All films should have valid language"
    
    def test_all_rentals_have_customer(self, sakila_db):
        """TC-SAK-032: Verify all rentals have a valid customer."""
        result = sakila_db.execute_query("""
            SELECT COUNT(*) as count FROM rental r
            LEFT JOIN customer c ON r.customer_id = c.customer_id
            WHERE c.customer_id IS NULL
        """)
        
        assert result[0]['count'] == 0, "All rentals should have valid customer"
    
    def test_all_payments_have_rental(self, sakila_db):
        """TC-SAK-033: Verify payments reference valid rentals."""
        result = sakila_db.execute_query("""
            SELECT COUNT(*) as count FROM payment p
            LEFT JOIN rental r ON p.rental_id = r.rental_id
            WHERE p.rental_id IS NOT NULL AND r.rental_id IS NULL
        """)
        
        assert result[0]['count'] == 0, "All payments should have valid rental"
    
    def test_all_inventory_has_film(self, sakila_db):
        """TC-SAK-034: Verify all inventory items have valid film."""
        result = sakila_db.execute_query("""
            SELECT COUNT(*) as count FROM inventory i
            LEFT JOIN film f ON i.film_id = f.film_id
            WHERE f.film_id IS NULL
        """)
        
        assert result[0]['count'] == 0, "All inventory should have valid film"
    
    def test_film_categories_valid(self, sakila_db):
        """TC-SAK-035: Verify all film-category relationships are valid."""
        result = sakila_db.execute_query("""
            SELECT COUNT(*) as count FROM film_category fc
            LEFT JOIN film f ON fc.film_id = f.film_id
            LEFT JOIN category c ON fc.category_id = c.category_id
            WHERE f.film_id IS NULL OR c.category_id IS NULL
        """)
        
        assert result[0]['count'] == 0, "All film-category relations should be valid"
    
    def test_film_actors_valid(self, sakila_db):
        """TC-SAK-036: Verify all film-actor relationships are valid."""
        result = sakila_db.execute_query("""
            SELECT COUNT(*) as count FROM film_actor fa
            LEFT JOIN film f ON fa.film_id = f.film_id
            LEFT JOIN actor a ON fa.actor_id = a.actor_id
            WHERE f.film_id IS NULL OR a.actor_id IS NULL
        """)
        
        assert result[0]['count'] == 0, "All film-actor relations should be valid"
