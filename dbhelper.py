from mysql.connector import connect

import sqlite3

def dbconnect():
    return connect(
        host='localhost',
        user='flaskuser',
        password='password',
        database='users'
    )

def getall_users():
    sql = f"SELECT * FROM `users`"
    db = dbconnect()
    cursor = db.cursor(dictionary=True)
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()  # Close the cursor
    db.close()  # Close the connection
    return data

def get_all_attendance():
    sql = f"SELECT * FROM `attendance`"  # Adjust table name as needed
    db = dbconnect()
    cursor = db.cursor(dictionary=True)
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()  # Close the cursor
    db.close()  # Close the connection
    return data

def validate_user(username, password):
    sql = f"SELECT * FROM `users` WHERE `username`='{username}' AND `password`='{password}'"
    db = dbconnect()
    cursor = db.cursor(dictionary=True)
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()  # Close the cursor
    db.close()  # Close the connection
    return data

def insert_user(idno, lastname, firstname, course, level):
    sql = "INSERT INTO `users` (`idno`, `lastname`, `firstname`, `course`, `level`) VALUES (%s, %s, %s, %s, %s)"
    db = dbconnect()
    cursor = db.cursor()
    cursor.execute(sql, (idno, lastname, firstname, course, level))
    db.commit()  # Commit the transaction
    cursor.close()  # Close the cursor
    db.close()  # Close the connection

def get_student_by_id(student_id):
    conn = sqlite3.connect("your_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE idno=?", (student_id,))
    student = cursor.fetchone()
    conn.close()
    return student

def insert_attendance(idno, lastname, firstname, course, level, time_logged):
    conn = sqlite3.connect("your_database.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO attendance (idno, lastname, firstname, course, level, time_logged)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (idno, lastname, firstname, course, level, time_logged))
    conn.commit()

    conn.close()

def get_all_users_formatted():
    """Get all users formatted for the userlist page"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT idno, lastname, firstname, course, level FROM users ORDER BY lastname")
        users = cursor.fetchall()
        
        # Format as list of dictionaries
        result = []
        for user in users:
            result.append({
                'idno': user[0],
                'lastname': user[1],
                'firstname': user[2],
                'course': user[3],
                'level': user[4]
            })
        return result
    finally:
        cursor.close()
        conn.close()

def delete_user(idno):
    """Delete user from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM users WHERE idno = %s", (idno,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()

def update_user(idno, lastname, firstname, course, level):
    """Update user in database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE users 
            SET lastname = %s, firstname = %s, course = %s, level = %s 
            WHERE idno = %s
        """, (lastname, firstname, course, level, idno))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()

def check_user_exists(idno):
    """Check if user already exists"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT idno FROM users WHERE idno = %s", (idno,))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()
