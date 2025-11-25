"""
Database connector module.
Provides a wrapper class for MySQL database operations with context management.
"""

import mysql.connector
from mysql.connector import Error
from typing import Optional, List, Dict, Any, Tuple
from config.db_config import DBConfig


class DatabaseConnector:
    """
    MySQL Database connector with CRUD operations and utility methods.
    Supports context management for automatic resource cleanup.
    """
    
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        """Establish database connection."""
        try:
            self.connection = mysql.connector.connect(**DBConfig.get_connection_params())
            self.cursor = self.connection.cursor(dictionary=True)
            return True
        except Error as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close database connection and cursor."""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup."""
        self.disconnect()
    
    # === CRUD Operations ===
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> Optional[List[Dict]]:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL SELECT statement
            params: Optional tuple of parameters for parameterized queries
            
        Returns:
            List of dictionaries representing rows, or None on error
        """
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error executing query: {e}")
            return None
    
    def execute_non_query(self, query: str, params: Optional[Tuple] = None) -> int:
        """
        Execute INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL statement
            params: Optional tuple of parameters
            
        Returns:
            Number of affected rows, or -1 on error
        """
        try:
            self.cursor.execute(query, params or ())
            self.connection.commit()
            return self.cursor.rowcount
        except Error as e:
            print(f"Error executing non-query: {e}")
            self.connection.rollback()
            return -1
    
    def insert(self, table: str, data: Dict[str, Any]) -> Optional[int]:
        """
        Insert a single record into a table.
        
        Args:
            table: Table name
            data: Dictionary of column-value pairs
            
        Returns:
            Last inserted ID, or None on error
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        try:
            self.cursor.execute(query, tuple(data.values()))
            self.connection.commit()
            return self.cursor.lastrowid
        except Error as e:
            print(f"Error inserting record: {e}")
            self.connection.rollback()
            return None
    
    def insert_many(self, table: str, columns: List[str], data: List[Tuple]) -> int:
        """
        Insert multiple records into a table.
        
        Args:
            table: Table name
            columns: List of column names
            data: List of tuples with values
            
        Returns:
            Number of inserted rows, or -1 on error
        """
        cols = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))
        query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        
        try:
            self.cursor.executemany(query, data)
            self.connection.commit()
            return self.cursor.rowcount
        except Error as e:
            print(f"Error inserting multiple records: {e}")
            self.connection.rollback()
            return -1
    
    def update(self, table: str, data: Dict[str, Any], condition: str, 
               condition_params: Tuple) -> int:
        """
        Update records in a table.
        
        Args:
            table: Table name
            data: Dictionary of column-value pairs to update
            condition: WHERE clause (without 'WHERE' keyword)
            condition_params: Parameters for the WHERE clause
            
        Returns:
            Number of affected rows, or -1 on error
        """
        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        params = tuple(data.values()) + condition_params
        
        return self.execute_non_query(query, params)
    
    def delete(self, table: str, condition: str, condition_params: Tuple) -> int:
        """
        Delete records from a table.
        
        Args:
            table: Table name
            condition: WHERE clause (without 'WHERE' keyword)
            condition_params: Parameters for the WHERE clause
            
        Returns:
            Number of deleted rows, or -1 on error
        """
        query = f"DELETE FROM {table} WHERE {condition}"
        return self.execute_non_query(query, condition_params)
    
    def select(self, table: str, columns: str = "*", condition: str = None,
               condition_params: Tuple = None, order_by: str = None,
               limit: int = None) -> Optional[List[Dict]]:
        """
        Select records from a table with optional filtering.
        
        Args:
            table: Table name
            columns: Columns to select (default: *)
            condition: Optional WHERE clause
            condition_params: Parameters for WHERE clause
            order_by: Optional ORDER BY clause
            limit: Optional LIMIT value
            
        Returns:
            List of dictionaries representing rows
        """
        query = f"SELECT {columns} FROM {table}"
        
        if condition:
            query += f" WHERE {condition}"
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"
        
        return self.execute_query(query, condition_params)
    
    def count(self, table: str, condition: str = None, 
              condition_params: Tuple = None) -> int:
        """
        Count records in a table.
        
        Args:
            table: Table name
            condition: Optional WHERE clause
            condition_params: Parameters for WHERE clause
            
        Returns:
            Number of records, or -1 on error
        """
        query = f"SELECT COUNT(*) as count FROM {table}"
        if condition:
            query += f" WHERE {condition}"
        
        result = self.execute_query(query, condition_params)
        return result[0]['count'] if result else -1
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        query = """
            SELECT COUNT(*) as count 
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = %s
        """
        result = self.execute_query(query, (DBConfig.DATABASE, table_name))
        return result[0]['count'] > 0 if result else False
    
    def get_table_columns(self, table_name: str) -> Optional[List[Dict]]:
        """Get column information for a table."""
        query = """
            SELECT column_name, data_type, is_nullable, column_key, column_default
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """
        return self.execute_query(query, (DBConfig.DATABASE, table_name))
    
    def truncate_table(self, table_name: str) -> bool:
        """Truncate a table (remove all data)."""
        try:
            self.cursor.execute(f"TRUNCATE TABLE {table_name}")
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error truncating table: {e}")
            return False
    
    def execute_script(self, script: str) -> bool:
        """Execute multiple SQL statements."""
        try:
            for statement in script.split(';'):
                statement = statement.strip()
                if statement:
                    self.cursor.execute(statement)
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error executing script: {e}")
            self.connection.rollback()
            return False
