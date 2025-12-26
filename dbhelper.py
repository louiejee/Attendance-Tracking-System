# dbhelper.py - Fixed version
import os
from urllib.parse import urlparse
import psycopg2
import traceback

print("=== Loading dbhelper.py ===")  # Debug

def get_db_connection():
    """Get database connection for Render PostgreSQL"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        
        if not database_url:
            print("ERROR: DATABASE_URL environment variable is not set!")
            raise Exception("DATABASE_URL not found in environment variables")
        
        print(f"Connecting to database...")  # Don't print full URL for security
        
        # Parse the database URL
        result = urlparse(database_url)
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            database=result.path[1:],      # Remove leading '/'
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port,
            connect_timeout=10  # 10 second timeout
        )
        
        print("✓ Database connection successful!")
        return conn
        
    except Exception as e:
        print(f"✗ Database connection failed: {str(e)}")
        print(traceback.format_exc())
        raise

def validate_user(username, password):
    """Validate admin user"""
    print(f"Attempting to validate user: {username}")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check admin_users table
        sql = "SELECT * FROM admin_users WHERE username = %s AND password = %s"
        cursor.execute(sql, (username, password))
        
        # Get column names
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        result = [dict(zip(columns, row)) for row in rows]
        
        cursor.close()
        conn.close()
        
        print(f"Validation result: {len(result)} records found")
        return result
        
    except Exception as e:
        print(f"Error in validate_user: {e}")
        print(traceback.format_exc())
        return []

def initialize_database():
    """Initialize database tables"""
    print("=== Initializing database ===")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Create users table
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
        print("✓ Created users table")
        
        # 2. Create attendance table
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
        print("✓ Created attendance table")
        
        # 3. Create admin_users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(100) NOT NULL
        )
        """)
        print("✓ Created admin_users table")
        
        # 4. Insert default admin if not exists
        cursor.execute("""
        INSERT INTO admin_users (username, password) 
        VALUES ('admin', 'admin123')
        ON CONFLICT (username) DO NOTHING
        """)
        print("✓ Added default admin user")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("=== Database initialization complete ===")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        print(traceback.format_exc())

# Stub functions (implement as needed)
def get_all_users_formatted():
    return []

def insert_user(idno, lastname, firstname, course, level):
    pass

def get_student_by_id(student_id):
    return None

def insert_attendance(idno, lastname, firstname, course, level, time_logged):
    pass

def delete_user(idno):
    return True

def update_user(idno, lastname, firstname, course, level):
    return True

def check_user_exists(idno):
    return False

def get_all_attendance():
    return []
