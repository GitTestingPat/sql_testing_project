"""
Pytest configuration and fixtures for database testing.
"""

import pytest
import sys
from pathlib import Path
import mysql.connector
from config.db_config import SakilaConfig

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_connector import DatabaseConnector
from data.test_data import (
    CREATE_USERS_TABLE,
    CREATE_PRODUCTS_TABLE,
    CREATE_ORDERS_TABLE,
    DROP_TABLES_SCRIPT,
    VALID_USER,
    VALID_PRODUCT,
    TestDataGenerator
)


# === Session-scoped Fixtures ===

@pytest.fixture(scope='session')
def db_connection():
    """
    Session-scoped database connection.
    Creates tables at the start and drops them at the end.
    """
    db = DatabaseConnector()
    db.connect()
    
    # Setup: Create tables
    db.execute_script(DROP_TABLES_SCRIPT)
    db.cursor.execute(CREATE_USERS_TABLE)
    db.cursor.execute(CREATE_PRODUCTS_TABLE)
    db.cursor.execute(CREATE_ORDERS_TABLE)
    db.connection.commit()
    
    yield db
    
    # Teardown: Drop tables and close connection
    db.execute_script(DROP_TABLES_SCRIPT)
    db.disconnect()


@pytest.fixture(scope='function')
def db(db_connection):
    """
    Function-scoped fixture that provides a clean database state.
    Truncates tables before each test.
    """
    # Disable foreign key checks for truncation
    db_connection.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    db_connection.truncate_table('orders')
    db_connection.truncate_table('products')
    db_connection.truncate_table('users')
    db_connection.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    db_connection.connection.commit()
    
    return db_connection


# === Data Fixtures ===

@pytest.fixture
def sample_user():
    """Provide a sample user dictionary."""
    return VALID_USER.copy()


@pytest.fixture
def sample_product():
    """Provide a sample product dictionary."""
    return VALID_PRODUCT.copy()


@pytest.fixture
def random_user():
    """Provide a randomly generated user."""
    return TestDataGenerator.generate_user()


@pytest.fixture
def random_product():
    """Provide a randomly generated product."""
    return TestDataGenerator.generate_product()


@pytest.fixture
def inserted_user(db, sample_user):
    """Insert a sample user and return the ID."""
    user_id = db.insert('users', sample_user)
    return user_id


@pytest.fixture
def inserted_product(db, sample_product):
    """Insert a sample product and return the ID."""
    product_id = db.insert('products', sample_product)
    return product_id


@pytest.fixture
def populated_users(db):
    """Insert multiple users and return their IDs."""
    columns, data = TestDataGenerator.generate_bulk_users_tuple(10)
    db.insert_many('users', columns, data)
    result = db.select('users', columns='id')
    return [row['id'] for row in result]


@pytest.fixture
def populated_products(db):
    """Insert multiple products and return their IDs."""
    columns, data = TestDataGenerator.generate_bulk_products_tuple(10)
    db.insert_many('products', columns, data)
    result = db.select('products', columns='id, price')
    return result


# === Utility Fixtures ===

@pytest.fixture
def data_generator():
    """Provide access to the TestDataGenerator class."""
    return TestDataGenerator


# === Pytest Hooks ===

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "crud: Tests for CRUD operations")
    config.addinivalue_line("markers", "integrity: Tests for data integrity")
    config.addinivalue_line("markers", "performance: Tests for performance")
    config.addinivalue_line("markers", "smoke: Quick smoke tests")
    config.addinivalue_line("markers", "regression: Full regression tests")


def pytest_html_report_title(report):
    """Set the title for HTML report."""
    report.title = "SQL Database Test Report"


@pytest.fixture(scope='session')
def sakila_connection():
    """Session-scoped connection to Sakila database."""
    from config.db_config import SakilaConfig

    db = DatabaseConnector()
    params = SakilaConfig.get_connection_params()
    db.connection = mysql.connector.connect(**params)
    db.cursor = db.connection.cursor(dictionary=True)

    # Asegurar uso de la base de datos sakila
    db.cursor.execute("USE sakila")

    yield db

    db.disconnect()


@pytest.fixture(scope='function')
def sakila_db(sakila_connection):
    """Function-scoped fixture for Sakila database."""
    return sakila_connection
