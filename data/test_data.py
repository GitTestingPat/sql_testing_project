"""
Test data module.
Provides test data constants and generators using Faker.
"""

from faker import Faker
from typing import Dict, List, Tuple, Any

fake = Faker()


# === SQL Scripts for Test Setup ===

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    age INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)
"""

CREATE_PRODUCTS_TABLE = """
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INT DEFAULT 0,
    category VARCHAR(50),
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_ORDERS_TABLE = """
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
)
"""

DROP_TABLES_SCRIPT = """
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users
"""


# === Static Test Data ===

VALID_USER = {
    'username': 'testuser',
    'email': 'testuser@example.com',
    'password_hash': 'hashed_password_123',
    'first_name': 'Test',
    'last_name': 'User',
    'age': 25,
    'is_active': True
}

VALID_PRODUCT = {
    'name': 'Test Product',
    'description': 'A test product for automated testing',
    'price': 29.99,
    'stock': 100,
    'category': 'Electronics',
    'is_available': True
}

INVALID_USER_DATA = [
    {'username': None, 'email': 'test@test.com', 'password_hash': 'hash'},  # Null username
    {'username': '', 'email': 'test@test.com', 'password_hash': 'hash'},     # Empty username
    {'username': 'a' * 100, 'email': 'test@test.com', 'password_hash': 'h'}, # Too long username
]

INVALID_PRODUCT_DATA = [
    {'name': 'Test', 'price': -10.00, 'stock': 5},   # Negative price
    {'name': 'Test', 'price': 10.00, 'stock': -5},   # Negative stock
    {'name': None, 'price': 10.00, 'stock': 5},      # Null name
]


# === Data Generators ===

class TestDataGenerator:
    """Generate random test data using Faker."""
    
    @staticmethod
    def generate_user() -> Dict[str, Any]:
        """Generate a random user record."""
        return {
            'username': fake.user_name()[:50],
            'email': fake.email(),
            'password_hash': fake.sha256(),
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'age': fake.random_int(min=18, max=80),
            'is_active': fake.boolean(chance_of_getting_true=80)
        }
    
    @staticmethod
    def generate_users(count: int) -> List[Dict[str, Any]]:
        """Generate multiple random user records."""
        return [TestDataGenerator.generate_user() for _ in range(count)]
    
    @staticmethod
    def generate_product() -> Dict[str, Any]:
        """Generate a random product record."""
        categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports', 'Food']
        return {
            'name': fake.catch_phrase()[:100],
            'description': fake.text(max_nb_chars=200),
            'price': round(fake.random.uniform(1.00, 999.99), 2),
            'stock': fake.random_int(min=0, max=500),
            'category': fake.random_element(categories),
            'is_available': fake.boolean(chance_of_getting_true=90)
        }
    
    @staticmethod
    def generate_products(count: int) -> List[Dict[str, Any]]:
        """Generate multiple random product records."""
        return [TestDataGenerator.generate_product() for _ in range(count)]
    
    @staticmethod
    def generate_order(user_id: int, product_id: int, product_price: float) -> Dict[str, Any]:
        """Generate a random order record."""
        quantity = fake.random_int(min=1, max=10)
        statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        return {
            'user_id': user_id,
            'product_id': product_id,
            'quantity': quantity,
            'total_price': round(product_price * quantity, 2),
            'status': fake.random_element(statuses)
        }
    
    @staticmethod
    def generate_bulk_users_tuple(count: int) -> Tuple[List[str], List[Tuple]]:
        """
        Generate bulk user data as tuples for insert_many().
        
        Returns:
            Tuple of (column_names, list_of_value_tuples)
        """
        columns = ['username', 'email', 'password_hash', 'first_name', 
                   'last_name', 'age', 'is_active']
        data = []
        
        for i in range(count):
            user = TestDataGenerator.generate_user()
            # Ensure unique username/email by adding index
            user['username'] = f"{user['username']}_{i}"
            user['email'] = f"{i}_{user['email']}"
            data.append(tuple(user[col] for col in columns))
        
        return columns, data
    
    @staticmethod
    def generate_bulk_products_tuple(count: int) -> Tuple[List[str], List[Tuple]]:
        """
        Generate bulk product data as tuples for insert_many().
        
        Returns:
            Tuple of (column_names, list_of_value_tuples)
        """
        columns = ['name', 'description', 'price', 'stock', 'category', 'is_available']
        data = []
        
        for i in range(count):
            product = TestDataGenerator.generate_product()
            product['name'] = f"{product['name']} #{i}"
            data.append(tuple(product[col] for col in columns))
        
        return columns, data
