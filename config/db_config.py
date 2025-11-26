"""
Database configuration module.
Loads environment variables and provides database connection settings.
Supports multiple databases: test_database and sakila.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class DBConfig:
    """Database configuration class with settings loaded from environment variables."""
    
    HOST = os.getenv('DB_HOST', 'localhost')
    PORT = int(os.getenv('DB_PORT', 3306))
    USER = os.getenv('DB_USER', 'root')
    PASSWORD = os.getenv('DB_PASSWORD', '')
    DATABASE = os.getenv('DB_NAME', 'test_database')
    
    @classmethod
    def get_connection_params(cls, database: str = None) -> dict:
        """
        Return connection parameters as a dictionary.
        
        Args:
            database: Optional database name. If None, uses default from env.
        """
        return {
            'host': cls.HOST,
            'port': cls.PORT,
            'user': cls.USER,
            'password': cls.PASSWORD,
            'database': database or cls.DATABASE
        }
    
    @classmethod
    def get_connection_string(cls, database: str = None) -> str:
        """Return connection string for logging purposes (password masked)."""
        db = database or cls.DATABASE
        return f"mysql://{cls.USER}:****@{cls.HOST}:{cls.PORT}/{db}"


class SakilaConfig:
    """Configuration specific to Sakila database."""
    
    DATABASE = 'sakila'
    
    # Sakila table names
    TABLES = [
        'actor', 'address', 'category', 'city', 'country',
        'customer', 'film', 'film_actor', 'film_category', 'film_text',
        'inventory', 'language', 'payment', 'rental', 'staff', 'store'
    ]
    
    # Sakila views
    VIEWS = [
        'actor_info', 'customer_list', 'film_list', 
        'nicer_but_slower_film_list', 'sales_by_film_category',
        'sales_by_store', 'staff_list'
    ]
    
    @classmethod
    def get_connection_params(cls) -> dict:
        """Return connection parameters for Sakila database."""
        return DBConfig.get_connection_params(cls.DATABASE)
