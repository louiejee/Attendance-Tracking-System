# dbhelper.py - Temporary workaround
import os
from urllib.parse import urlparse
import psycopg2
import traceback

print("=== Loading dbhelper.py ===")

def get_db_connection():
    """Get database connection with fallback"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        
        if not database_url:
            print("WARNING: DATABASE_URL not set. Using dummy connection.")
            # Return a dummy connection object
            class DummyConnection:
                def cursor(self): return DummyCursor()
                def close(self): pass
                def commit(self): pass
            class DummyCursor:
                def execute(self, *args): pass
                def fetchall(self): return []
                def fetchone(self): return None
                def close(self): pass
                @property
                def description(self): return []
            return DummyConnection()
        
        print(f"Connecting to database...")
        result = urlparse(database_url)
        
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port,
            connect_timeout=10
        )
        
        print("✓ Database connection successful!")
        return conn
        
    except Exception as e:
        print(f"✗ Database connection failed: {str(e)}")
        # Fallback to dummy connection
        class DummyConnection:
            def cursor(self): return DummyCursor()
            def close(self): pass
            def commit(self): pass
        return DummyConnection()

def validate_user(username, password):
    """Validate user - hardcoded for now"""
    print(f"Validating: {username}/{password}")
    
    # Hardcoded admin for testing
    if username == "admin" and password == "admin123":
        return [{"username": "admin", "password": "admin123"}]
    
    return []

def initialize_database():
    """Initialize database - just print message"""
    print("Skipping database initialization (no DATABASE_URL)")
    return

# Other functions remain as stubs...
def get_all_users_formatted():
    return []

def insert_user(idno, lastname, firstname, course, level):
    """Insert new user into database"""
    print(f"Inserting user: {idno}, {lastname}, {firstname}, {course}, {level}")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if USE_POSTGRESQL:
            sql = "INSERT INTO users (idno, lastname, firstname, course, level) VALUES (%s, %s, %s, %s, %s)"
        else:
            sql = "INSERT INTO users (idno, lastname, firstname, course, level) VALUES (%s, %s, %s, %s, %s)"
        
        cursor.execute(sql, (idno, lastname, firstname, course, level))
        conn.commit()
        
        print(f"✓ User {idno} inserted successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error inserting user: {e}")
        print(traceback.format_exc())
        return False

def check_user_exists(idno):
    """Check if a user with given IDNO already exists"""
    print(f"Checking if user exists: {idno}")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if USE_POSTGRESQL:
            sql = "SELECT idno FROM users WHERE idno = %s"
        else:
            sql = "SELECT idno FROM users WHERE idno = %s"
        
        cursor.execute(sql, (idno,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        exists = result is not None
        print(f"User {idno} exists: {exists}")
        return exists
        
    except Exception as e:
        print(f"Error checking user existence: {e}")
        print(traceback.format_exc())
        return False  # Return False on error to allow trying


