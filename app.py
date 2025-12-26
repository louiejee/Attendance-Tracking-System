from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from dbhelper import * 
from datetime import datetime
import json
from io import BytesIO
import base64
from PIL import Image
import os
import qrcode 

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', '@#$@#$@#$')

# Initialize database
initialize_database()

os.makedirs('static/qrcode', exist_ok=True)
os.makedirs('static/image', exist_ok=True)
os.makedirs('static/qr_codes', exist_ok=True)  # Add this

# Add Student Form
@app.route("/add")
def add_user():
    return render_template("student.html", pagetitle="STUDENT")

# Add Student Action
@app.route("/add_student", methods=["POST"])
def add_student():
    idno = request.form['idno']
    lastname = request.form['lastname']
    firstname = request.form['firstname']
    course = request.form['course']
    level = request.form['level']
    
    # Check if student already exists
    if check_user_exists(idno):
        return render_template("student.html", pagetitle="STUDENT", 
                              error="Student ID already exists!")
    
    insert_user(idno, lastname, firstname, course, level)
    return redirect(url_for('userlist'))

# Admin Login
@app.route("/admin", methods=["GET"])
def admin():
    return render_template("login.html", pagetitle="FINAL PROJECT")

# User Validation
@app.route("/validateuser", methods=['POST'])
def validateuser():
    username = request.form['username']
    password = request.form['password']
    
    result = validate_user(username, password)
    
    if result:
        session['username'] = username
        session['logged_in'] = True
        return redirect(url_for('userlist'))
    else:
        return render_template("login.html", pagetitle="FINAL PROJECT", error="Invalid credentials")

# User List Page
@app.route("/userlist")
def userlist():
    if not session.get('logged_in'):
        return redirect(url_for('admin'))
    
    users = get_all_users_formatted()
    return render_template("userlist.html", ulist=users, pagetitle='STUDENTLIST')

# Get Student Info
@app.route("/get_student_info/<student_id>")
def get_student_info(student_id):
    student = get_student_by_id(student_id)
    if student:
        return jsonify({'success': True, 'student': student})
    else:
        return jsonify({'success': False})

# Attendance Page
@app.route("/attendance")
def attendance():
    if not session.get('logged_in'):
        return redirect(url_for('admin'))
    return render_template("view_attendance.html", pagetitle="ATTENDANCE CHECKER")

# Scan QR Code and Log Attendance
@app.route("/scan_qr", methods=["POST"])
def scan_qr():
    qr_data = request.get_json()
    student_info = qr_data.get('student_info', {})

    if student_info:
        time_logged = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if student exists in database
        student = get_student_by_id(student_info.get('id', student_info.get('idno', '')))
        
        if student:
            insert_attendance(
                student['idno'],
                student['lastname'],
                student['firstname'],
                student['course'],
                student['level'],
                time_logged
            )
            return jsonify({"success": True})
    
    return jsonify({"success": False, "error": "Student not found"})

# API Routes
@app.route("/api/students")
def api_students():
    students = get_all_users_formatted()
    return jsonify(students)

@app.route("/api/student/<idno>")
def api_student(idno):
    student = get_student_by_id(idno)
    if student:
        return jsonify(student)
    return jsonify(None), 404

@app.route("/api/attendance")
def api_attendance():
    attendance = get_all_attendance()
    return jsonify(attendance)

# Student Management Routes
@app.route("/delete_student/<idno>", methods=["DELETE"])
def delete_student_route(idno):
    if delete_user(idno):
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route("/update_student/<idno>", methods=["PUT"])
def update_student_route(idno):
    data = request.get_json()
    if update_user(idno, data['lastname'], data['firstname'], data['course'], data['level']):
        return jsonify({"success": True})
    return jsonify({"success": False})

# Image and QR Code Handling
@app.route('/save_image', methods=['POST'])
def save_image():
    data = request.get_json()
    image_data = data.get('image_data')
    idno = data.get('idno')

    if not image_data or not idno:
        return jsonify({"success": False, "error": "Missing data"})

    try:
        # Decode the base64 image
        image_data = image_data.split(',')[1]
        image = Image.open(BytesIO(base64.b64decode(image_data)))

        # Define the image filename
        image_filename = f"static/image/{idno}.jpg"

        # Save the image
        image.save(image_filename)
        return jsonify({"success": True, "image_url": image_filename})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/save_qr_code', methods=['POST'])
def save_qr_code():
    data = request.get_json()
    qr_code_url = data.get('qr_code_url')
    idno = data.get('idno')
    
    if not qr_code_url or not idno:
        return jsonify({'success': False, 'message': 'Missing data'})

    try:
        # Extract the image data from the base64 URL
        if ',' in qr_code_url:
            image_data = qr_code_url.split(',')[1]
        else:
            image_data = qr_code_url
            
        image_data = base64.b64decode(image_data)

        # Define the file path where the QR code image will be saved
        image_filename = f"static/qr_codes/{idno}_qrcode.png"
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(image_filename), exist_ok=True)

        # Save the image
        with open(image_filename, 'wb') as f:
            f.write(image_data)
        
        return jsonify({'success': True, 'image_path': image_filename})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('admin'))

# Home Page
@app.route("/")
def index():
    return render_template("attendance_checker.html", pagetitle="ATTENDANCE CHECKER")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
