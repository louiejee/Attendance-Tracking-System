# setup.py - One-time setup script
import os
from dbhelper import get_db_connection

def setup_database():
    """Setup database tables"""
    print("Setting up database...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Your table creation SQL here
    tables_sql = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            idno VARCHAR(50) NOT NULL UNIQUE,
            lastname VARCHAR(100) NOT NULL,
            firstname VARCHAR(100) NOT NULL,
            course VARCHAR(50) NOT NULL,
            level VARCHAR(10) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id SERIAL PRIMARY KEY,
            idno VARCHAR(50) NOT NULL,
            lastname VARCHAR(100) NOT NULL,
            firstname VARCHAR(100) NOT NULL,
            course VARCHAR(50) NOT NULL,
            level VARCHAR(10) NOT NULL,
            time_logged TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS admin_users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(100) NOT NULL
        )
        """,
        """
        INSERT INTO admin_users (username, password) 
        VALUES ('admin', 'admin123')
        ON CONFLICT (username) DO NOTHING
        """
    ]
    
    for sql in tables_sql:
        cursor.execute(sql)
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("Database setup complete!")

if __name__ == "__main__":
    setup_database()
