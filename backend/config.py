"""
MySQL Database Configuration
Generated: 2026-01-05 10:55:40 UTC
"""

import mysql.connector
from mysql.connector import Error

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Lokesh@24',
    'database': 'vehicle_challan_system'
}

def get_db_connection():
    """
    Establish and return a MySQL database connection
    
    Returns:
        mysql.connector.MySQLConnection: Database connection object
        
    Raises:
        Error: If connection fails
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Successfully connected to MySQL Server version {db_info}")
            return connection
    except Error as err:
        if err.errno == 2003:
            print("Error: Unable to connect to MySQL Server. Make sure the server is running.")
        elif err.errno == 1045:
            print("Error: Invalid username or password.")
        elif err.errno == 1049:
            print("Error: Database does not exist.")
        else:
            print(f"Error: {err}")
        raise

def close_db_connection(connection):
    """
    Close the MySQL database connection
    
    Args:
        connection: MySQL database connection object
    """
    if connection and connection.is_connected():
        connection.close()
        print("MySQL connection is closed")

if __name__ == "__main__":
    # Test database connection
    try:
        conn = get_db_connection()
        close_db_connection(conn)
    except Error as e:
        print(f"Connection test failed: {e}")
