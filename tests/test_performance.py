"""
Test suite for database performance testing.
Measures query execution times, bulk operations, and concurrent access.
"""

import pytest
import time
from data.test_data import TestDataGenerator


@pytest.mark.performance
class TestQueryPerformance:
    """Tests for query execution performance."""
    
    @pytest.fixture
    def large_dataset(self, db):
        """Populate database with large dataset for performance testing."""
        # Insert 1000 users
        columns, data = TestDataGenerator.generate_bulk_users_tuple(1000)
        db.insert_many('users', columns, data)
        
        # Insert 500 products
        columns, data = TestDataGenerator.generate_bulk_products_tuple(500)
        db.insert_many('products', columns, data)
        
        return {'users': 1000, 'products': 500}
    
    def test_select_all_performance(self, db, large_dataset):
        """TC-PERF-001: Measure SELECT * performance on large table."""
        start_time = time.time()
        
        result = db.select('users')
        
        execution_time = time.time() - start_time
        
        assert len(result) == large_dataset['users']
        assert execution_time < 2.0, f"Query took {execution_time:.2f}s, expected < 2s"
        print(f"\nSELECT * on {large_dataset['users']} users: {execution_time:.4f}s")
    
    def test_select_with_condition_performance(self, db, large_dataset):
        """TC-PERF-002: Measure SELECT with WHERE clause performance."""
        start_time = time.time()
        
        result = db.select('users', 
                          condition='is_active = %s', 
                          condition_params=(True,))
        
        execution_time = time.time() - start_time
        
        assert execution_time < 1.0, f"Query took {execution_time:.2f}s, expected < 1s"
        print(f"\nSELECT with condition: {execution_time:.4f}s, found {len(result)} records")
    
    def test_select_with_order_performance(self, db, large_dataset):
        """TC-PERF-003: Measure SELECT with ORDER BY performance."""
        start_time = time.time()
        
        result = db.select('users', order_by='created_at DESC', limit=100)
        
        execution_time = time.time() - start_time
        
        assert len(result) == 100
        assert execution_time < 1.0, f"Query took {execution_time:.2f}s, expected < 1s"
        print(f"\nSELECT with ORDER BY and LIMIT: {execution_time:.4f}s")
    
    def test_count_performance(self, db, large_dataset):
        """TC-PERF-004: Measure COUNT query performance."""
        start_time = time.time()
        
        count = db.count('users')
        
        execution_time = time.time() - start_time
        
        assert count == large_dataset['users']
        assert execution_time < 0.5, f"COUNT took {execution_time:.2f}s, expected < 0.5s"
        print(f"\nCOUNT query: {execution_time:.4f}s")
    
    def test_join_performance(self, db, large_dataset):
        """TC-PERF-005: Measure JOIN query performance."""
        # First create some orders
        users = db.select('users', columns='id', limit=100)
        products = db.select('products', columns='id, price', limit=50)
        
        # Create 200 orders
        for i in range(200):
            user = users[i % len(users)]
            product = products[i % len(products)]
            order = {
                'user_id': user['id'],
                'product_id': product['id'],
                'quantity': 1,
                'total_price': float(product['price'])
            }
            db.insert('orders', order)
        
        start_time = time.time()
        
        query = """
            SELECT o.id, u.username, p.name, o.total_price
            FROM orders o
            JOIN users u ON o.user_id = u.id
            JOIN products p ON o.product_id = p.id
        """
        result = db.execute_query(query)
        
        execution_time = time.time() - start_time
        
        assert len(result) == 200
        assert execution_time < 2.0, f"JOIN took {execution_time:.2f}s, expected < 2s"
        print(f"\nJOIN query on 200 orders: {execution_time:.4f}s")


@pytest.mark.performance
class TestBulkOperationPerformance:
    """Tests for bulk operation performance."""
    
    def test_bulk_insert_100_records(self, db):
        """TC-PERF-006: Measure bulk insert of 100 records."""
        columns, data = TestDataGenerator.generate_bulk_users_tuple(100)
        
        start_time = time.time()
        rows = db.insert_many('users', columns, data)
        execution_time = time.time() - start_time
        
        assert rows == 100
        assert execution_time < 1.0, f"Insert took {execution_time:.2f}s, expected < 1s"
        print(f"\nBulk insert 100 records: {execution_time:.4f}s")
    
    def test_bulk_insert_1000_records(self, db):
        """TC-PERF-007: Measure bulk insert of 1000 records."""
        columns, data = TestDataGenerator.generate_bulk_users_tuple(1000)
        
        start_time = time.time()
        rows = db.insert_many('users', columns, data)
        execution_time = time.time() - start_time
        
        assert rows == 1000
        assert execution_time < 5.0, f"Insert took {execution_time:.2f}s, expected < 5s"
        print(f"\nBulk insert 1000 records: {execution_time:.4f}s")
    
    def test_bulk_update_performance(self, db):
        """TC-PERF-008: Measure bulk update performance."""
        # First insert data
        columns, data = TestDataGenerator.generate_bulk_users_tuple(500)
        db.insert_many('users', columns, data)
        
        start_time = time.time()
        
        # Update all active users
        db.execute_non_query(
            "UPDATE users SET first_name = 'BulkUpdated' WHERE is_active = TRUE"
        )
        
        execution_time = time.time() - start_time
        
        assert execution_time < 2.0, f"Update took {execution_time:.2f}s, expected < 2s"
        print(f"\nBulk update: {execution_time:.4f}s")
    
    def test_bulk_delete_performance(self, db):
        """TC-PERF-009: Measure bulk delete performance."""
        # First insert data
        columns, data = TestDataGenerator.generate_bulk_users_tuple(500)
        db.insert_many('users', columns, data)
        
        start_time = time.time()
        
        # Delete inactive users
        deleted = db.delete('users', 'is_active = %s', (False,))
        
        execution_time = time.time() - start_time
        
        assert execution_time < 1.0, f"Delete took {execution_time:.2f}s, expected < 1s"
        print(f"\nBulk delete {deleted} records: {execution_time:.4f}s")


@pytest.mark.performance
class TestStressTests:
    """Stress tests for database operations."""
    
    def test_repeated_single_inserts(self, db):
        """TC-PERF-010: Measure repeated single insert performance."""
        start_time = time.time()
        
        for i in range(100):
            user = TestDataGenerator.generate_user()
            user['username'] = f"stress_test_user_{i}"
            user['email'] = f"stress_{i}@test.com"
            db.insert('users', user)
        
        execution_time = time.time() - start_time
        
        assert db.count('users') == 100
        assert execution_time < 10.0, f"100 inserts took {execution_time:.2f}s"
        print(f"\n100 individual inserts: {execution_time:.4f}s ({execution_time/100*1000:.2f}ms per insert)")
    
    def test_mixed_operations(self, db):
        """TC-PERF-011: Measure mixed CRUD operations performance."""
        start_time = time.time()
        
        # Insert 50 users
        for i in range(50):
            user = TestDataGenerator.generate_user()
            user['username'] = f"mixed_user_{i}"
            user['email'] = f"mixed_{i}@test.com"
            db.insert('users', user)
        
        # Read all
        db.select('users')
        
        # Update 25
        db.execute_non_query(
            "UPDATE users SET first_name = 'MixedTest' WHERE id <= 25"
        )
        
        # Delete 10
        db.execute_non_query("DELETE FROM users WHERE id <= 10")
        
        # Count remaining
        count = db.count('users')
        
        execution_time = time.time() - start_time
        
        assert count == 40
        assert execution_time < 5.0, f"Mixed ops took {execution_time:.2f}s"
        print(f"\nMixed CRUD operations: {execution_time:.4f}s")
    
    def test_complex_query_performance(self, db):
        """TC-PERF-012: Measure complex aggregation query performance."""
        # Setup data
        columns, user_data = TestDataGenerator.generate_bulk_users_tuple(200)
        db.insert_many('users', columns, user_data)
        
        columns, product_data = TestDataGenerator.generate_bulk_products_tuple(100)
        db.insert_many('products', columns, product_data)
        
        # Create orders
        users = db.select('users', columns='id', limit=100)
        products = db.select('products', columns='id, price', limit=50)
        
        for i in range(300):
            order = {
                'user_id': users[i % len(users)]['id'],
                'product_id': products[i % len(products)]['id'],
                'quantity': (i % 5) + 1,
                'total_price': float(products[i % len(products)]['price']) * ((i % 5) + 1)
            }
            db.insert('orders', order)
        
        start_time = time.time()
        
        # Complex aggregation query
        query = """
            SELECT 
                u.username,
                COUNT(o.id) as order_count,
                SUM(o.total_price) as total_spent,
                AVG(o.quantity) as avg_quantity
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            GROUP BY u.id, u.username
            HAVING COUNT(o.id) > 0
            ORDER BY total_spent DESC
            LIMIT 10
        """
        result = db.execute_query(query)
        
        execution_time = time.time() - start_time
        
        assert len(result) <= 10
        assert execution_time < 3.0, f"Complex query took {execution_time:.2f}s"
        print(f"\nComplex aggregation query: {execution_time:.4f}s")


@pytest.mark.performance
class TestConnectionPerformance:
    """Tests for connection handling performance."""
    
    def test_connection_establishment(self, db_connection):
        """TC-PERF-013: Measure connection establishment time."""
        from database.db_connector import DatabaseConnector
        
        times = []
        for _ in range(10):
            connector = DatabaseConnector()
            
            start_time = time.time()
            connector.connect()
            connection_time = time.time() - start_time
            times.append(connection_time)
            connector.disconnect()
        
        avg_time = sum(times) / len(times)
        
        assert avg_time < 1.0, f"Avg connection time {avg_time:.2f}s, expected < 1s"
        print(f"\nAvg connection time: {avg_time*1000:.2f}ms")
    
    def test_context_manager_overhead(self, db_connection):
        """TC-PERF-014: Measure context manager overhead."""
        from database.db_connector import DatabaseConnector
        
        start_time = time.time()
        
        for _ in range(10):
            with DatabaseConnector() as db:
                db.select('users', limit=1)
        
        execution_time = time.time() - start_time
        avg_time = execution_time / 10
        
        assert avg_time < 1.0, f"Avg time per operation {avg_time:.2f}s"
        print(f"\nAvg context manager cycle: {avg_time*1000:.2f}ms")
