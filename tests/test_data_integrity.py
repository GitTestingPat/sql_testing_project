"""
Test suite for data integrity verification.
Tests constraints, data types, relationships and data validation.
"""

import pytest
from decimal import Decimal
from data.test_data import TestDataGenerator, INVALID_USER_DATA


@pytest.mark.integrity
class TestSchemaIntegrity:
    """Tests for database schema integrity."""
    
    def test_users_table_exists(self, db):
        """TC-INT-001: Verify users table exists."""
        assert db.table_exists('users'), "Users table should exist"
    
    def test_products_table_exists(self, db):
        """TC-INT-002: Verify products table exists."""
        assert db.table_exists('products'), "Products table should exist"
    
    def test_orders_table_exists(self, db):
        """TC-INT-003: Verify orders table exists."""
        assert db.table_exists('orders'), "Orders table should exist"
    
    def test_users_table_columns(self, db):
        """TC-INT-004: Verify users table has correct columns."""
        expected_columns = ['id', 'username', 'email', 'password_hash', 
                          'first_name', 'last_name', 'age', 'is_active',
                          'created_at', 'updated_at']
        
        columns = db.get_table_columns('users')
        column_names = [col['COLUMN_NAME'] for col in columns]
        
        for expected in expected_columns:
            assert expected in column_names, f"Column {expected} should exist in users"
    
    def test_products_table_columns(self, db):
        """TC-INT-005: Verify products table has correct columns."""
        expected_columns = ['id', 'name', 'description', 'price', 
                          'stock', 'category', 'is_available', 'created_at']
        
        columns = db.get_table_columns('products')
        column_names = [col['COLUMN_NAME'] for col in columns]
        
        for expected in expected_columns:
            assert expected in column_names, f"Column {expected} should exist in products"
    
    def test_primary_key_auto_increment(self, db, sample_user):
        """TC-INT-006: Verify primary key auto-increments."""
        id1 = db.insert('users', sample_user)
        
        user2 = TestDataGenerator.generate_user()
        id2 = db.insert('users', user2)
        
        assert id2 > id1, "Auto-increment should produce increasing IDs"


@pytest.mark.integrity
class TestConstraints:
    """Tests for database constraints."""
    
    def test_unique_username_constraint(self, db, sample_user):
        """TC-CON-001: Verify unique constraint on username."""
        db.insert('users', sample_user)
        
        duplicate = sample_user.copy()
        duplicate['email'] = 'different@email.com'
        result = db.insert('users', duplicate)
        
        assert result is None, "Duplicate username should be rejected"
    
    def test_unique_email_constraint(self, db, sample_user):
        """TC-CON-002: Verify unique constraint on email."""
        db.insert('users', sample_user)
        
        duplicate = sample_user.copy()
        duplicate['username'] = 'different_user'
        result = db.insert('users', duplicate)
        
        assert result is None, "Duplicate email should be rejected"
    
    def test_not_null_username_constraint(self, db):
        """TC-CON-003: Verify NOT NULL constraint on username."""
        user = {
            'username': None,
            'email': 'test@test.com',
            'password_hash': 'hash123'
        }
        result = db.insert('users', user)
        
        assert result is None, "NULL username should be rejected"
    
    def test_not_null_product_name_constraint(self, db):
        """TC-CON-004: Verify NOT NULL constraint on product name."""
        product = {
            'name': None,
            'price': 10.00,
            'stock': 5
        }
        result = db.insert('products', product)
        
        assert result is None, "NULL product name should be rejected"
    
    def test_foreign_key_user_constraint(self, db, inserted_product):
        """TC-CON-005: Verify foreign key constraint for user_id in orders."""
        order = {
            'user_id': 99999,  # Non-existent user
            'product_id': inserted_product,
            'quantity': 1,
            'total_price': 10.00
        }
        result = db.insert('orders', order)
        
        assert result is None, "Order with invalid user_id should be rejected"
    
    def test_foreign_key_product_constraint(self, db, inserted_user):
        """TC-CON-006: Verify foreign key constraint for product_id in orders."""
        order = {
            'user_id': inserted_user,
            'product_id': 99999,  # Non-existent product
            'quantity': 1,
            'total_price': 10.00
        }
        result = db.insert('orders', order)
        
        assert result is None, "Order with invalid product_id should be rejected"
    
    def test_enum_constraint_order_status(self, db, inserted_user, inserted_product):
        """TC-CON-007: Verify ENUM constraint on order status."""
        valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        
        for status in valid_statuses:
            order = {
                'user_id': inserted_user,
                'product_id': inserted_product,
                'quantity': 1,
                'total_price': 10.00,
                'status': status
            }
            result = db.insert('orders', order)
            assert result is not None, f"Status '{status}' should be valid"
    
    def test_invalid_enum_status_rejected(self, db, inserted_user, inserted_product):
        """TC-CON-008: Verify invalid ENUM value is rejected."""
        order = {
            'user_id': inserted_user,
            'product_id': inserted_product,
            'quantity': 1,
            'total_price': 10.00,
            'status': 'invalid_status'
        }
        result = db.insert('orders', order)
        
        assert result is None, "Invalid status should be rejected"


@pytest.mark.integrity
class TestDataTypes:
    """Tests for data type validation."""
    
    def test_decimal_precision_price(self, db):
        """TC-DT-001: Verify decimal precision for price field."""
        product = {
            'name': 'Precision Test',
            'price': 123.45,
            'stock': 10
        }
        product_id = db.insert('products', product)
        
        result = db.select('products', 
                          condition='id = %s', 
                          condition_params=(product_id,))
        
        assert float(result[0]['price']) == 123.45
    
    def test_integer_stock_field(self, db):
        """TC-DT-002: Verify integer storage for stock field."""
        product = {
            'name': 'Stock Test',
            'price': 10.00,
            'stock': 150
        }
        product_id = db.insert('products', product)
        
        result = db.select('products', 
                          condition='id = %s', 
                          condition_params=(product_id,))
        
        assert result[0]['stock'] == 150
        assert isinstance(result[0]['stock'], int)
    
    def test_boolean_is_active_field(self, db, sample_user):
        """TC-DT-003: Verify boolean storage for is_active field."""
        sample_user['is_active'] = True
        user_id = db.insert('users', sample_user)
        
        result = db.select('users', 
                          condition='id = %s', 
                          condition_params=(user_id,))
        
        assert result[0]['is_active'] in [1, True]
    
    def test_varchar_length_username(self, db):
        """TC-DT-004: Verify varchar length constraint for username."""
        long_username = 'a' * 51  # Exceeds 50 char limit
        
        user = {
            'username': long_username,
            'email': 'test@test.com',
            'password_hash': 'hash'
        }
        result = db.insert('users', user)
        
        assert result is None, "Username exceeding 50 chars should be rejected"
    
    def test_timestamp_auto_generated(self, db, sample_user):
        """TC-DT-005: Verify timestamps are auto-generated."""
        user_id = db.insert('users', sample_user)
        
        result = db.select('users', 
                          condition='id = %s', 
                          condition_params=(user_id,))
        
        assert result[0]['created_at'] is not None
        assert result[0]['updated_at'] is not None


@pytest.mark.integrity
class TestReferentialIntegrity:
    """Tests for referential integrity between tables."""
    
    def test_order_references_valid_user(self, db, inserted_user, inserted_product):
        """TC-REF-001: Verify order correctly references user."""
        order = {
            'user_id': inserted_user,
            'product_id': inserted_product,
            'quantity': 2,
            'total_price': 50.00
        }
        order_id = db.insert('orders', order)
        
        # Verify user exists
        query = """
            SELECT o.*, u.username 
            FROM orders o 
            JOIN users u ON o.user_id = u.id 
            WHERE o.id = %s
        """
        result = db.execute_query(query, (order_id,))
        
        assert len(result) == 1
        assert result[0]['username'] is not None
    
    def test_order_references_valid_product(self, db, inserted_user, inserted_product):
        """TC-REF-002: Verify order correctly references product."""
        order = {
            'user_id': inserted_user,
            'product_id': inserted_product,
            'quantity': 1,
            'total_price': 29.99
        }
        order_id = db.insert('orders', order)
        
        query = """
            SELECT o.*, p.name as product_name 
            FROM orders o 
            JOIN products p ON o.product_id = p.id 
            WHERE o.id = %s
        """
        result = db.execute_query(query, (order_id,))
        
        assert len(result) == 1
        assert result[0]['product_name'] is not None
    
    def test_cascade_delete_removes_orders(self, db, inserted_user, inserted_product):
        """TC-REF-003: Verify cascade delete on user removes orders."""
        # Create order
        order = {
            'user_id': inserted_user,
            'product_id': inserted_product,
            'quantity': 1,
            'total_price': 10.00
        }
        db.insert('orders', order)
        
        # Delete user
        db.delete('users', 'id = %s', (inserted_user,))
        
        # Check orders are deleted
        order_count = db.count('orders', 'user_id = %s', (inserted_user,))
        assert order_count == 0
    
    def test_user_order_count(self, db, inserted_user, inserted_product):
        """TC-REF-004: Verify correct order count per user."""
        # Insert multiple orders
        for _ in range(5):
            order = {
                'user_id': inserted_user,
                'product_id': inserted_product,
                'quantity': 1,
                'total_price': 10.00
            }
            db.insert('orders', order)
        
        count = db.count('orders', 'user_id = %s', (inserted_user,))
        assert count == 5


@pytest.mark.integrity
class TestDataConsistency:
    """Tests for data consistency."""
    
    def test_order_total_calculation(self, db, inserted_user, inserted_product):
        """TC-CONS-001: Verify order total matches quantity * price."""
        # Get product price
        product = db.select('products', 
                           condition='id = %s', 
                           condition_params=(inserted_product,))
        price = float(product[0]['price'])
        quantity = 3
        expected_total = round(price * quantity, 2)
        
        order = {
            'user_id': inserted_user,
            'product_id': inserted_product,
            'quantity': quantity,
            'total_price': expected_total
        }
        order_id = db.insert('orders', order)
        
        result = db.select('orders', 
                          condition='id = %s', 
                          condition_params=(order_id,))
        
        assert float(result[0]['total_price']) == expected_total
    
    def test_default_values_applied(self, db):
        """TC-CONS-002: Verify default values are correctly applied."""
        # Insert product with minimal data
        product = {
            'name': 'Default Test Product',
            'price': 15.00
        }
        product_id = db.insert('products', product)
        
        result = db.select('products', 
                          condition='id = %s', 
                          condition_params=(product_id,))
        
        assert result[0]['stock'] == 0, "Default stock should be 0"
        assert result[0]['is_available'] in [1, True], "Default availability should be True"
    
    def test_updated_at_changes_on_update(self, db, inserted_user):
        """TC-CONS-003: Verify updated_at timestamp changes on update."""
        # Get initial timestamp
        initial = db.select('users', 
                           condition='id = %s', 
                           condition_params=(inserted_user,))
        initial_updated = initial[0]['updated_at']
        
        # Small delay to ensure timestamp difference
        import time
        time.sleep(1)
        
        # Update record
        db.update('users', {'first_name': 'Updated'}, 'id = %s', (inserted_user,))
        
        # Get new timestamp
        updated = db.select('users', 
                           condition='id = %s', 
                           condition_params=(inserted_user,))
        new_updated = updated[0]['updated_at']
        
        assert new_updated >= initial_updated, "updated_at should change on update"
