"""
Test suite for CRUD (Create, Read, Update, Delete) operations.
"""

import pytest
from data.test_data import TestDataGenerator


@pytest.mark.crud
@pytest.mark.smoke
class TestCreateOperations:
    """Tests for INSERT operations."""
    
    def test_insert_single_user(self, db, sample_user):
        """TC-CR-001: Verify single user insertion returns valid ID."""
        user_id = db.insert('users', sample_user)
        
        assert user_id is not None, "Insert should return a valid ID"
        assert user_id > 0, "User ID should be positive"
    
    def test_insert_user_data_persisted(self, db, sample_user):
        """TC-CR-002: Verify inserted user data is correctly persisted."""
        user_id = db.insert('users', sample_user)
        
        result = db.select('users', condition='id = %s', condition_params=(user_id,))
        
        assert len(result) == 1, "Should find exactly one user"
        assert result[0]['username'] == sample_user['username']
        assert result[0]['email'] == sample_user['email']
        assert result[0]['first_name'] == sample_user['first_name']
    
    def test_insert_single_product(self, db, sample_product):
        """TC-CR-003: Verify single product insertion."""
        product_id = db.insert('products', sample_product)
        
        assert product_id is not None
        result = db.select('products', condition='id = %s', condition_params=(product_id,))
        assert result[0]['name'] == sample_product['name']
        assert float(result[0]['price']) == sample_product['price']
    
    def test_insert_many_users(self, db, data_generator):
        """TC-CR-004: Verify bulk insertion of multiple users."""
        columns, data = data_generator.generate_bulk_users_tuple(50)
        
        rows_inserted = db.insert_many('users', columns, data)
        
        assert rows_inserted == 50, f"Expected 50 rows inserted, got {rows_inserted}"
        assert db.count('users') == 50
    
    def test_insert_many_products(self, db, data_generator):
        """TC-CR-005: Verify bulk insertion of multiple products."""
        columns, data = data_generator.generate_bulk_products_tuple(25)
        
        rows_inserted = db.insert_many('products', columns, data)
        
        assert rows_inserted == 25
        assert db.count('products') == 25
    
    def test_insert_duplicate_username_fails(self, db, sample_user):
        """TC-CR-006: Verify duplicate username insertion fails."""
        db.insert('users', sample_user)
        
        # Try to insert duplicate
        duplicate_user = sample_user.copy()
        duplicate_user['email'] = 'different@email.com'
        result = db.insert('users', duplicate_user)
        
        assert result is None, "Duplicate username insertion should fail"
    
    def test_insert_duplicate_email_fails(self, db, sample_user):
        """TC-CR-007: Verify duplicate email insertion fails."""
        db.insert('users', sample_user)
        
        duplicate_user = sample_user.copy()
        duplicate_user['username'] = 'different_username'
        result = db.insert('users', duplicate_user)
        
        assert result is None, "Duplicate email insertion should fail"


@pytest.mark.crud
@pytest.mark.smoke
class TestReadOperations:
    """Tests for SELECT operations."""
    
    def test_select_all_users(self, db, populated_users):
        """TC-RD-001: Verify selecting all users returns correct count."""
        result = db.select('users')
        
        assert len(result) == len(populated_users)
    
    def test_select_with_condition(self, db, sample_user):
        """TC-RD-002: Verify selecting with WHERE condition."""
        db.insert('users', sample_user)
        
        result = db.select('users', 
                          condition='username = %s', 
                          condition_params=(sample_user['username'],))
        
        assert len(result) == 1
        assert result[0]['email'] == sample_user['email']
    
    def test_select_specific_columns(self, db, sample_user):
        """TC-RD-003: Verify selecting specific columns."""
        db.insert('users', sample_user)
        
        result = db.select('users', columns='username, email')
        
        assert 'username' in result[0]
        assert 'email' in result[0]
        assert 'password_hash' not in result[0]
    
    def test_select_with_order_by(self, db, populated_users):
        """TC-RD-004: Verify selecting with ORDER BY."""
        result = db.select('users', order_by='id DESC')
        
        ids = [row['id'] for row in result]
        assert ids == sorted(ids, reverse=True), "Results should be ordered DESC"
    
    def test_select_with_limit(self, db, populated_users):
        """TC-RD-005: Verify selecting with LIMIT."""
        result = db.select('users', limit=5)
        
        assert len(result) == 5
    
    def test_count_records(self, db, populated_users):
        """TC-RD-006: Verify count operation."""
        count = db.count('users')
        
        assert count == len(populated_users)
    
    def test_count_with_condition(self, db, sample_user):
        """TC-RD-007: Verify count with condition."""
        sample_user['is_active'] = True
        db.insert('users', sample_user)
        
        inactive_user = TestDataGenerator.generate_user()
        inactive_user['is_active'] = False
        db.insert('users', inactive_user)
        
        active_count = db.count('users', 
                                condition='is_active = %s', 
                                condition_params=(True,))
        
        assert active_count == 1
    
    def test_execute_custom_query(self, db, populated_products):
        """TC-RD-008: Verify custom query execution."""
        query = "SELECT AVG(price) as avg_price FROM products"
        result = db.execute_query(query)
        
        assert result is not None
        assert 'avg_price' in result[0]
        assert float(result[0]['avg_price']) > 0


@pytest.mark.crud
@pytest.mark.smoke
class TestUpdateOperations:
    """Tests for UPDATE operations."""
    
    def test_update_single_field(self, db, inserted_user, sample_user):
        """TC-UP-001: Verify updating a single field."""
        new_email = 'updated@example.com'
        
        rows_affected = db.update('users', 
                                  {'email': new_email}, 
                                  'id = %s', 
                                  (inserted_user,))
        
        assert rows_affected == 1
        result = db.select('users', condition='id = %s', condition_params=(inserted_user,))
        assert result[0]['email'] == new_email
    
    def test_update_multiple_fields(self, db, inserted_user):
        """TC-UP-002: Verify updating multiple fields."""
        updates = {
            'first_name': 'UpdatedFirst',
            'last_name': 'UpdatedLast',
            'age': 30
        }
        
        rows_affected = db.update('users', updates, 'id = %s', (inserted_user,))
        
        assert rows_affected == 1
        result = db.select('users', condition='id = %s', condition_params=(inserted_user,))
        assert result[0]['first_name'] == 'UpdatedFirst'
        assert result[0]['last_name'] == 'UpdatedLast'
        assert result[0]['age'] == 30
    
    def test_update_nonexistent_record(self, db):
        """TC-UP-003: Verify updating non-existent record affects 0 rows."""
        rows_affected = db.update('users', 
                                  {'email': 'new@email.com'}, 
                                  'id = %s', 
                                  (99999,))
        
        assert rows_affected == 0
    
    def test_update_with_complex_condition(self, db, populated_users):
        """TC-UP-004: Verify update with complex WHERE condition."""
        # Update all active users older than 25
        db.execute_non_query(
            "UPDATE users SET first_name = 'Senior' WHERE is_active = TRUE AND age > 25"
        )
        
        result = db.select('users', 
                          condition='first_name = %s', 
                          condition_params=('Senior',))
        
        for user in result:
            assert user['is_active'] == 1
            assert user['age'] > 25
    
    def test_update_product_stock(self, db, inserted_product):
        """TC-UP-005: Verify product stock update."""
        new_stock = 50
        
        db.update('products', {'stock': new_stock}, 'id = %s', (inserted_product,))
        
        result = db.select('products', 
                          condition='id = %s', 
                          condition_params=(inserted_product,))
        assert result[0]['stock'] == new_stock


@pytest.mark.crud
@pytest.mark.smoke
class TestDeleteOperations:
    """Tests for DELETE operations."""
    
    def test_delete_single_record(self, db, inserted_user):
        """TC-DL-001: Verify deleting a single record."""
        rows_deleted = db.delete('users', 'id = %s', (inserted_user,))
        
        assert rows_deleted == 1
        assert db.count('users') == 0
    
    def test_delete_with_condition(self, db, populated_users):
        """TC-DL-002: Verify deleting with condition."""
        initial_count = db.count('users')
        
        # Delete inactive users
        db.delete('users', 'is_active = %s', (False,))
        
        remaining = db.count('users', 'is_active = %s', (True,))
        deleted = initial_count - db.count('users')
        
        assert deleted >= 0
        assert remaining == db.count('users')
    
    def test_delete_nonexistent_record(self, db):
        """TC-DL-003: Verify deleting non-existent record affects 0 rows."""
        rows_deleted = db.delete('users', 'id = %s', (99999,))
        
        assert rows_deleted == 0
    
    def test_delete_cascade_orders(self, db, inserted_user, inserted_product):
        """TC-DL-004: Verify cascade delete removes related orders."""
        # Create an order
        order = {
            'user_id': inserted_user,
            'product_id': inserted_product,
            'quantity': 2,
            'total_price': 59.98,
            'status': 'pending'
        }
        db.insert('orders', order)
        
        # Delete user - should cascade to orders
        db.delete('users', 'id = %s', (inserted_user,))
        
        order_count = db.count('orders', 'user_id = %s', (inserted_user,))
        assert order_count == 0, "Orders should be deleted with cascade"
    
    def test_truncate_table(self, db, populated_users):
        """TC-DL-005: Verify truncate removes all records."""
        assert db.count('users') > 0
        
        # Disable FK checks for truncate
        db.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        result = db.truncate_table('users')
        db.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        assert result is True
        assert db.count('users') == 0
