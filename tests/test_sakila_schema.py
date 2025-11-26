"""
Test suite for Sakila database schema validation.
Verifies tables, views, columns, and relationships exist correctly.
"""

import pytest
from data.sakila_test_data import SAKILA_TABLES, SAKILA_VIEWS


@pytest.mark.sakila
@pytest.mark.schema
class TestSakilaSchemaExists:
    """Tests to verify Sakila schema objects exist."""
    
    def test_sakila_database_accessible(self, sakila_db):
        """TC-SAK-001: Verify Sakila database is accessible."""
        result = sakila_db.execute_query("SELECT DATABASE()")
        
        assert result is not None
        assert result[0]['DATABASE()'] == 'sakila'
    
    @pytest.mark.parametrize("table_name", list(SAKILA_TABLES.keys()))
    def test_table_exists(self, sakila_db, table_name):
        """TC-SAK-002: Verify each Sakila table exists."""
        query = """
            SELECT COUNT(*) as count 
            FROM information_schema.tables 
            WHERE table_schema = 'sakila' AND table_name = %s
        """
        result = sakila_db.execute_query(query, (table_name,))
        
        assert result[0]['count'] == 1, f"Table '{table_name}' should exist"
    
    @pytest.mark.parametrize("view_name", SAKILA_VIEWS)
    def test_view_exists(self, sakila_db, view_name):
        """TC-SAK-003: Verify each Sakila view exists."""
        query = """
            SELECT COUNT(*) as count 
            FROM information_schema.views 
            WHERE table_schema = 'sakila' AND table_name = %s
        """
        result = sakila_db.execute_query(query, (view_name,))
        
        assert result[0]['count'] == 1, f"View '{view_name}' should exist"
    
    def test_total_table_count(self, sakila_db):
        """TC-SAK-004: Verify Sakila has 16 tables."""
        query = """
            SELECT COUNT(*) as count 
            FROM information_schema.tables 
            WHERE table_schema = 'sakila' AND table_type = 'BASE TABLE'
        """
        result = sakila_db.execute_query(query)
        
        assert result[0]['count'] == 16
    
    def test_total_view_count(self, sakila_db):
        """TC-SAK-005: Verify Sakila has 7 views."""
        query = """
            SELECT COUNT(*) as count 
            FROM information_schema.views 
            WHERE table_schema = 'sakila'
        """
        result = sakila_db.execute_query(query)
        
        assert result[0]['count'] == 7


@pytest.mark.sakila
@pytest.mark.schema
class TestSakilaTableColumns:
    """Tests to verify Sakila table columns."""
    
    def test_actor_table_columns(self, sakila_db):
        """TC-SAK-006: Verify actor table has correct columns."""
        expected = ['actor_id', 'first_name', 'last_name', 'last_update']
        
        query = """
            SELECT COLUMN_NAME 
            FROM information_schema.columns 
            WHERE table_schema = 'sakila' AND table_name = 'actor'
            ORDER BY ordinal_position
        """
        result = sakila_db.execute_query(query)
        columns = [row['COLUMN_NAME'] for row in result]
        
        for col in expected:
            assert col in columns, f"Column '{col}' should exist in actor table"
    
    def test_film_table_columns(self, sakila_db):
        """TC-SAK-007: Verify film table has correct columns."""
        expected = ['film_id', 'title', 'description', 'release_year', 
                   'language_id', 'rental_duration', 'rental_rate', 
                   'length', 'replacement_cost', 'rating']
        
        query = """
            SELECT COLUMN_NAME 
            FROM information_schema.columns 
            WHERE table_schema = 'sakila' AND table_name = 'film'
        """
        result = sakila_db.execute_query(query)
        columns = [row['COLUMN_NAME'] for row in result]
        
        for col in expected:
            assert col in columns, f"Column '{col}' should exist in film table"
    
    def test_customer_table_columns(self, sakila_db):
        """TC-SAK-008: Verify customer table has correct columns."""
        expected = ['customer_id', 'store_id', 'first_name', 'last_name', 
                   'email', 'address_id', 'active', 'create_date']
        
        query = """
            SELECT COLUMN_NAME 
            FROM information_schema.columns 
            WHERE table_schema = 'sakila' AND table_name = 'customer'
        """
        result = sakila_db.execute_query(query)
        columns = [row['COLUMN_NAME'] for row in result]
        
        for col in expected:
            assert col in columns, f"Column '{col}' should exist in customer table"
    
    def test_rental_table_columns(self, sakila_db):
        """TC-SAK-009: Verify rental table has correct columns."""
        expected = ['rental_id', 'rental_date', 'inventory_id', 
                   'customer_id', 'return_date', 'staff_id']
        
        query = """
            SELECT COLUMN_NAME 
            FROM information_schema.columns 
            WHERE table_schema = 'sakila' AND table_name = 'rental'
        """
        result = sakila_db.execute_query(query)
        columns = [row['COLUMN_NAME'] for row in result]
        
        for col in expected:
            assert col in columns, f"Column '{col}' should exist in rental table"
    
    def test_payment_table_columns(self, sakila_db):
        """TC-SAK-010: Verify payment table has correct columns."""
        expected = ['payment_id', 'customer_id', 'staff_id', 
                   'rental_id', 'amount', 'payment_date']
        
        query = """
            SELECT COLUMN_NAME 
            FROM information_schema.columns 
            WHERE table_schema = 'sakila' AND table_name = 'payment'
        """
        result = sakila_db.execute_query(query)
        columns = [row['COLUMN_NAME'] for row in result]
        
        for col in expected:
            assert col in columns, f"Column '{col}' should exist in payment table"


@pytest.mark.sakila
@pytest.mark.schema
class TestSakilaConstraints:
    """Tests to verify Sakila constraints and keys."""
    
    def test_film_primary_key(self, sakila_db):
        """TC-SAK-011: Verify film table has primary key."""
        query = """
            SELECT COLUMN_NAME 
            FROM information_schema.key_column_usage 
            WHERE table_schema = 'sakila' 
            AND table_name = 'film' 
            AND constraint_name = 'PRIMARY'
        """
        result = sakila_db.execute_query(query)
        
        assert len(result) == 1
        assert result[0]['COLUMN_NAME'] == 'film_id'
    
    def test_rental_foreign_keys(self, sakila_db):
        """TC-SAK-012: Verify rental table has foreign keys."""
        query = """
            SELECT COLUMN_NAME, REFERENCED_TABLE_NAME 
            FROM information_schema.key_column_usage 
            WHERE table_schema = 'sakila' 
            AND table_name = 'rental' 
            AND REFERENCED_TABLE_NAME IS NOT NULL
        """
        result = sakila_db.execute_query(query)
        
        referenced_tables = [row['REFERENCED_TABLE_NAME'] for row in result]
        
        assert 'customer' in referenced_tables
        assert 'inventory' in referenced_tables
        assert 'staff' in referenced_tables
    
    def test_film_actor_composite_key(self, sakila_db):
        """TC-SAK-013: Verify film_actor has composite primary key."""
        query = """
            SELECT COLUMN_NAME 
            FROM information_schema.key_column_usage 
            WHERE table_schema = 'sakila' 
            AND table_name = 'film_actor' 
            AND constraint_name = 'PRIMARY'
        """
        result = sakila_db.execute_query(query)
        columns = [row['COLUMN_NAME'] for row in result]
        
        assert 'actor_id' in columns
        assert 'film_id' in columns
    
    def test_film_rating_enum(self, sakila_db):
        """TC-SAK-014: Verify film rating uses ENUM constraint."""
        query = """
            SELECT COLUMN_TYPE 
            FROM information_schema.columns 
            WHERE table_schema = 'sakila' 
            AND table_name = 'film' 
            AND COLUMN_NAME = 'rating'
        """
        result = sakila_db.execute_query(query)
        
        assert 'enum' in result[0]['COLUMN_TYPE'].lower()
        assert 'G' in result[0]['COLUMN_TYPE']
        assert 'PG' in result[0]['COLUMN_TYPE']
        assert 'R' in result[0]['COLUMN_TYPE']
