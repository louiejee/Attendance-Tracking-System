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