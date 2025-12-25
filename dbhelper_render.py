import os
from datetime import datetime

# Try PostgreSQL first (for Render), fall back to MySQL/SQLite
try:
    import psycopg2
    from urllib.parse import urlparse
    USE_POSTGRESQL = True
except ImportError:
    USE_POSTGRESQL = False
    try:
        import mysql.connector
    except ImportError:
        import sqlite3

def get_db_connection():
    """Get database connection based on environment"""
    if USE_POSTGRESQL:
        # For Render PostgreSQL
        database_url = os.environ.get('DATABASE_URL')
        
        if database_url:
            result = urlparse(database_url)
            conn = psycopg2.connect(
                database=result.path[1:],
                user=result.username,
                password=result.password,
                host=result.hostname,
                port=result.port
            )
            return conn
        else:
            # Fallback for local PostgreSQL
            return psycopg2.connect(
                host='localhost',
                database='attendance_db',
                user='postgres',
                password='password'
            )
    else:
        # Try MySQL (for local development)
        try:
            return mysql.connector.connect(
                host='localhost',
                user='flaskuser',
                password='password',
                database='users'
            )
        except:
            # Fallback to SQLite
            return sqlite3.connect("attendance.db")

def get_all_users():
    """Get all users from database"""
    sql = "SELECT * FROM users ORDER BY lastname, firstname"
    conn = get_db_connection()
    
    if USE_POSTGRESQL:
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    else:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        data = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return data

def get_all_attendance():
    """Get all attendance records"""
    sql = "SELECT * FROM attendance ORDER BY time_logged DESC"
    conn = get_db_connection()
    
    if USE_POSTGRESQL:
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    else:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        data = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return data

def validate_user(username, password):
    """Validate admin user"""
    if USE_POSTGRESQL:
        sql = "SELECT * FROM admin_users WHERE username = %s AND password = %s"
    else:
        sql = "SELECT * FROM users WHERE username = %s AND password = %s"
    
    conn = get_db_connection()
    
    if USE_POSTGRESQL:
        cursor = conn.cursor()
        cursor.execute(sql, (username, password))
        columns = [desc[0] for desc in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    else:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, (username, password))
        data = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return data

def insert_user(idno, lastname, firstname, course, level):
    """Insert new user"""
    if USE_POSTGRESQL:
        sql = "INSERT INTO users (idno, lastname, firstname, course, level) VALUES (%s, %s, %s, %s, %s)"
    else:
        sql = "INSERT INTO users (idno, lastname, firstname, course, level) VALUES (%s, %s, %s, %s, %s)"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (idno, lastname, firstname, course, level))
    conn.commit()
    cursor.close()
    conn.close()

def get_student_by_id(student_id):
    """Get student by ID"""
    if USE_POSTGRESQL:
        sql = "SELECT * FROM users WHERE idno = %s"
    else:
        sql = "SELECT * FROM users WHERE idno = %s"
    
    conn = get_db_connection()
    
    if USE_POSTGRESQL:
        cursor = conn.cursor()
        cursor.execute(sql, (student_id,))
        columns = [desc[0] for desc in cursor.description]
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return dict(zip(columns, result)) if result else None
    else:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, (student_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

def insert_attendance(idno, lastname, firstname, course, level, time_logged):
    """Insert attendance record"""
    if USE_POSTGRESQL:
        sql = """
        INSERT INTO attendance (idno, lastname, firstname, course, level, time_logged) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
    else:
        sql = """
        INSERT INTO attendance (idno, lastname, firstname, course, level, time_logged)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (idno, lastname, firstname, course, level, time_logged))
    conn.commit()
    cursor.close()
    conn.close()

def initialize_database():
    """Initialize database tables (PostgreSQL only)"""
    if not USE_POSTGRESQL:
        return
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            idno VARCHAR(50) NOT NULL UNIQUE,
            lastname VARCHAR(100) NOT NULL,
            firstname VARCHAR(100) NOT NULL,
            course VARCHAR(50) NOT NULL,
            level VARCHAR(10) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create attendance table
        cursor.execute("""
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
        """)
        
        # Create admin users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(100) NOT NULL
        )
        """)
        
        # Insert default admin if not exists
        cursor.execute("""
        INSERT INTO admin_users (username, password) 
        VALUES ('admin', 'admin123')
        ON CONFLICT (username) DO NOTHING
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database tables initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")

# Initialize database on import (for PostgreSQL)
if USE_POSTGRESQL:
    initialize_database()
