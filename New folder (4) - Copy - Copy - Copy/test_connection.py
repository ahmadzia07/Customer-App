#!/usr/bin/env python3
"""
Simple script to test PostgreSQL connection with your credentials
"""

import psycopg2
from dotenv import load_dotenv
import os

def test_connection():
    """Test connection with your .env file settings"""
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Get connection details from .env file
        host = os.getenv('DB_HOST', 'localhost')
        port = os.getenv('DB_PORT', '5432')
        database = os.getenv('DB_NAME', 'employee_db')
        user = os.getenv('DB_USER', 'postgres')
        password = os.getenv('DB_PASSWORD', '')
        
        print("Testing connection with your .env file settings:")
        print(f"Host: {host}")
        print(f"Port: {port}")
        print(f"Database: {database}")
        print(f"User: {user}")
        print(f"Password: {'*' * len(password) if password else '(empty)'}")
        print("-" * 50)
        
        # Try to connect
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print("SUCCESS! Connected to PostgreSQL")
        print(f"Version: {version[0]}")
        
        # Check if employees table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'employees'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("Employees table already exists!")
            
            # Count records
            cursor.execute("SELECT COUNT(*) FROM employees;")
            count = cursor.fetchone()[0]
            print(f"Number of employees: {count}")
        else:
            print("Employees table does not exist yet.")
            print("The Flask app will create it automatically when you run it.")
        
        cursor.close()
        conn.close()
        
        print("\nYour Flask app should work now!")
        print("Run: python app.py")
        
        return True
        
    except psycopg2.Error as e:
        print(f"Connection failed: {e}")
        print("\nPlease check your .env file and make sure:")
        print("1. PostgreSQL is running")
        print("2. The password in .env is correct")
        print("3. The database 'employee_db' exists in pgAdmin 4")
        return False

if __name__ == "__main__":
    test_connection()
