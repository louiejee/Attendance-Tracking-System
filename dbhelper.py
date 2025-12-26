# dbhelper.py - Complete version
import os
import json
from urllib.parse import urlparse
import psycopg2
import traceback

print("=== Loading dbhelper.py ===")

def get_db_connection():
    """Get database connection for Render PostgreSQL"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        
        if not database_url:
            print("WARNING: DATABASE_URL not set.")
            return None
        
        print("Connecting to database...")
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
        return None

def get_all_attendance():
    """Get all attendance records, most recent first - FIXED FOR POSTGRESQL"""
    try:
        conn = get_db_connection()
        if not conn:
            print("No database connection")
            # Fallback to file
            return get_attendance_from_file()
            
        cursor = conn.cursor()
        
        # ✅ POSTGRESQL syntax (not SQLite)
        cursor.execute("""
            SELECT idno, lastname, firstname, course, level, time_logged 
            FROM attendance 
            ORDER BY time_logged DESC
        """)
        
        records = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        attendance_list = []
        for record in records:
            attendance_list.append({
                'idno': record[0],
                'lastname': record[1],
                'firstname': record[2],
                'course': record[3],
                'level': record[4],
                'time_logged': str(record[5])  # Convert timestamp to string
            })
        
        print(f"Found {len(attendance_list)} attendance records")
        return attendance_list
        
    except Exception as e:
        print(f"Error in get_all_attendance: {e}")
        traceback.print_exc()
        return []

def get_attendance_from_file():
    """Fallback: Get attendance from JSON file"""
    try:
        attendance_file = "attendance_data.json"
        
        if os.path.exists(attendance_file):
            with open(attendance_file, 'r') as f:
                attendance = json.load(f)
            print(f"Loaded {len(attendance)} records from file")
            return attendance
        else:
            print("No attendance file found")
            return []
            
    except Exception as e:
        print(f"Error reading attendance file: {e}")
        return []

def check_user_exists(idno):
    """Check if a user with given IDNO already exists"""
    print(f"Checking if user exists: {idno}")
    
    try:
        conn = get_db_connection()
        if conn is None:
            return False
            
        cursor = conn.cursor()
        cursor.execute("SELECT idno FROM users WHERE idno = %s", (idno,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        exists = result is not None
        print(f"User {idno} exists: {exists}")
        return exists
        
    except Exception as e:
        print(f"Error checking user existence: {e}")
        return False

def insert_user(idno, lastname, firstname, course, level):
    """Insert new user into database"""
    print(f"Inserting user: {idno}, {lastname}, {firstname}, {course}, {level}")
    
    try:
        conn = get_db_connection()
        if conn is None:
            print("No database connection")
            return False
            
        cursor = conn.cursor()
        sql = "INSERT INTO users (idno, lastname, firstname, course, level) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (idno, lastname, firstname, course, level))
        conn.commit()
        
        print(f"✓ User {idno} inserted successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error inserting user: {e}")
        return False

def validate_user(username, password):
    """Validate admin user"""
    print(f"Validating user: {username}")
    
    try:
        conn = get_db_connection()
        if conn is None:
            # Fallback for testing
            if username == "admin" and password == "admin123":
                return [{"username": "admin"}]
            return []
            
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin_users WHERE username = %s AND password = %s", 
                      (username, password))
        
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        result = [dict(zip(columns, row)) for row in rows]
        
        cursor.close()
        conn.close()
        
        print(f"Validation result: {len(result)} records found")
        return result
        
    except Exception as e:
        print(f"Error in validate_user: {e}")
        return []

def get_all_users_formatted():
    """Get all users for display"""
    print("Getting all users...")
    
    try:
        conn = get_db_connection()
        if conn is None:
            return []
            
        cursor = conn.cursor()
        cursor.execute("SELECT idno, lastname, firstname, course, level FROM users ORDER BY lastname")
        users = cursor.fetchall()
        
        result = []
        for user in users:
            result.append({
                'idno': user[0],
                'lastname': user[1],
                'firstname': user[2],
                'course': user[3],
                'level': user[4]
            })
        
        cursor.close()
        conn.close()
        
        print(f"Found {len(result)} users")
        return result
        
    except Exception as e:
        print(f"Error getting users: {e}")
        return []

def initialize_database():
    """Initialize database tables"""
    print("=== Initializing database ===")
    
    try:
        conn = get_db_connection()
        if conn is None:
            print("No database connection for initialization")
            return
            
        cursor = conn.cursor()
        
        # Create tables
        tables = [
            """CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                idno VARCHAR(50) NOT NULL UNIQUE,
                lastname VARCHAR(100) NOT NULL,
                firstname VARCHAR(100) NOT NULL,
                course VARCHAR(50) NOT NULL,
                level VARCHAR(10) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS attendance (
                id SERIAL PRIMARY KEY,
                idno VARCHAR(50) NOT NULL,
                lastname VARCHAR(100) NOT NULL,
                firstname VARCHAR(100) NOT NULL,
                course VARCHAR(50) NOT NULL,
                level VARCHAR(10) NOT NULL,
                time_logged TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS admin_users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(100) NOT NULL
            )"""
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)
        
        # Add default admin
        cursor.execute("""
            INSERT INTO admin_users (username, password) 
            VALUES ('admin', 'admin123')
            ON CONFLICT (username) DO NOTHING
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✓ Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")

def get_student_by_id(student_id):
    """Get student by ID"""
    try:
        conn = get_db_connection()
        if not conn:
            return None
            
        cursor = conn.cursor()
        cursor.execute("SELECT idno, lastname, firstname, course, level FROM users WHERE idno = %s", (student_id,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result:
            return {
                'idno': result[0],
                'lastname': result[1],
                'firstname': result[2],
                'course': result[3],
                'level': result[4]
            }
        return None
        
    except Exception as e:
        print(f"Error getting student: {e}")
        return None

def insert_attendance(idno, lastname, firstname, course, level, time_logged):
    """Insert attendance record into database"""
    print(f"Inserting attendance: {idno} at {time_logged}")
    
    try:
        conn = get_db_connection()
        if not conn:
            print("No database connection for attendance")
            # Fallback to file storage
            return insert_attendance_to_file(idno, lastname, firstname, course, level, time_logged)
            
        cursor = conn.cursor()
        
        sql = """
        INSERT INTO attendance (idno, lastname, firstname, course, level, time_logged) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(sql, (idno, lastname, firstname, course, level, time_logged))
        conn.commit()
        
        print(f"✓ Attendance recorded for {idno}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error inserting attendance: {e}")
        # Try file storage as fallback
        return insert_attendance_to_file(idno, lastname, firstname, course, level, time_logged)

def insert_attendance_to_file(idno, lastname, firstname, course, level, time_logged):
    """Fallback: Save attendance to JSON file"""
    try:
        attendance_file = "attendance_data.json"
        
        # Load existing attendance
        if os.path.exists(attendance_file):
            with open(attendance_file, 'r') as f:
                attendance = json.load(f)
        else:
            attendance = []
        
        # Add new record
        attendance.append({
            'idno': idno,
            'lastname': lastname,
            'firstname': firstname,
            'course': course,
            'level': level,
            'time_logged': time_logged
        })
        
        # Save back to file
        with open(attendance_file, 'w') as f:
            json.dump(attendance, f, indent=2)
        
        print(f"✓ Attendance saved to file for {idno}")
        return True
        
    except Exception as e:
        print(f"✗ File save also failed: {e}")
        return False

def delete_user(idno):
    """Delete user from database"""
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE idno = %s", (idno,))
        conn.commit()
        
        success = cursor.rowcount > 0
        cursor.close()
        conn.close()
        
        print(f"Delete user {idno}: {'success' if success else 'not found'}")
        return success
        
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False

def update_user(idno, lastname, firstname, course, level):
    """Update user information"""
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET lastname = %s, firstname = %s, course = %s, level = %s 
            WHERE idno = %s
        """, (lastname, firstname, course, level, idno))
        conn.commit()
        
        success = cursor.rowcount > 0
        cursor.close()
        conn.close()
        
        print(f"Update user {idno}: {'success' if success else 'not found'}")
        return success
        
    except Exception as e:
        print(f"Error updating user: {e}")
        return False
