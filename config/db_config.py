"""
Database configuration module.
Loads environment variables and provides database connection settings.
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
    def get_connection_params(cls) -> dict:
        """Return connection parameters as a dictionary."""
        return {
            'host': cls.HOST,
            'port': cls.PORT,
            'user': cls.USER,
            'password': cls.PASSWORD,
            'database': cls.DATABASE
        }
    
    @classmethod
    def get_connection_string(cls) -> str:
        """Return connection string for logging purposes (password masked)."""
        return f"mysql://{cls.USER}:****@{cls.HOST}:{cls.PORT}/{cls.DATABASE}"
