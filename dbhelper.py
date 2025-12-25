from mysql.connector import connect

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