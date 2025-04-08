# import the necessary packages
from flask import Flask, render_template, redirect, url_for, request,session,Response,flash
#from werkzeug import secure_filename
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
# from supportFile import predict
import os
import cv2
import sqlite3
import predict
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import sqlite3
from datetime import datetime
import re

app = Flask(__name__)

app.secret_key = '1234'
app.config["CACHE_TYPE"] = "null"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

#@app.route('/', methods=['GET', 'POST'])
#def landing():
#	return render_template('home.html')

@app.route('/', methods=['GET', 'POST'])
def landing():
	return redirect(url_for('input'))

def is_valid_email(email):
    return re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)

def is_valid_contact(contact):
    return re.match(r"^[0-9]{10}$", contact)

def is_valid_password(password):
    return re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+{}\[\]:;<>,.?~\\-]).{8}$", password)

def is_valid_age(age):
    """Checks if an age is a valid integer and greater than 18."""
    try:
        age_int = int(age)
        return age_int > 18
    except ValueError:
        return False

@app.route('/input', methods=['GET', 'POST'])
def input():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        contact = request.form['contact']
        gender = request.form['gender']
        password = request.form['password']
        age = request.form['age'] #added age
        
        
        errors = {}

        if not name:
            errors['name'] = "Name is required."
        if not email:
            errors['email'] = "Email is required."
        elif not is_valid_email(email):
            errors['email'] = "Invalid email format."
        if not contact:
            errors['contact'] = "Contact number is required."
        elif not is_valid_contact(contact):
            errors['contact'] = "Invalid contact number format. Must be 10 digits."
        if not password:
            errors['password'] = "Password is required."
        if not gender:
            errors['gender'] = "Gender is required."
        if not is_valid_age(age):
            errors['age'] = "Age must be a number greater than 18."

        if errors:
            for error in errors.values():
                flash(error, 'error')
            return render_template('input.html', errors=errors, name=name, email=email, contact=contact, gender=gender, age=age) #added age

        try:
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            with sqlite3.connect('mydatabase.db') as con:
                cursor = con.cursor()
                cursor.execute("CREATE TABLE IF NOT EXISTS users (Date text, name TEXT, email TEXT, contact TEXT, gender TEXT, password TEXT, age INTEGER)")
                cursor.execute("INSERT INTO users (Date, name, email, contact, gender, password, age) VALUES (?, ?, ?, ?, ?, ?, ?)", (dt_string, name, email, contact, gender, password, int(age)))
                con.commit()
            flash("Registration successful!", 'success')
            return redirect(url_for('login'))

        except sqlite3.Error as e:
            flash(f"Database error: {e}", 'error')
            return render_template('input.html', name=name, email=email, contact=contact, gender=gender, age=age) #added age

    return render_template('input.html')
#Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            with sqlite3.connect('mydatabase.db') as con:
                cursor = con.cursor()
                cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
                user = cursor.fetchone()

                if user:
                    flash("Login successful!", 'success')
                    return redirect(url_for('home')) #replace with your home route
                else:
                    flash("Invalid email or password.", 'error')
                    return render_template('login.html')

        except sqlite3.Error as e:
            flash(f"Database error: {e}", 'error')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
	return render_template('home.html')

@app.route('/info', methods=['GET', 'POST'])
def info():
	return render_template('info.html')

@app.route('/image', methods=['GET', 'POST'])
def image():
    uploaded_image = None  # Initialize uploaded_image

    if request.method == 'POST':
        if request.form['sub'] == 'Upload':
            savepath = r'upload/'
            if not os.path.exists(savepath):
                os.makedirs(savepath)
            photo = request.files['photo']
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(savepath, filename))
            image = cv2.imread(os.path.join(savepath, filename))
            cv2.imwrite(os.path.join("static/images/", "test_image.jpg"), image)
            uploaded_image = "images/test_image.jpg"
            return render_template('image.html', uploaded_image=uploaded_image)

        elif request.form['sub'] == 'Test':
            APP_ROOT = os.path.dirname(os.path.abspath(__file__))
            target = os.path.join(APP_ROOT, 'static/images/')
            namefile_ = 'test_image.jpg'
            destination = "/".join([target, namefile_])
            # Assuming you have a predict.predict function
            fruit, result = predict.predict(destination)
            uploaded_image = "images/test_image.jpg"
            return render_template('image.html', result=result, fruit=fruit, uploaded_image=uploaded_image)
            return render_template('image.html', uploaded_image=uploaded_image)

    # This return statement ensures a response is sent for GET requests and if no POST conditions are met.
    return render_template('image.html', uploaded_image=uploaded_image)
 
# No caching at all for API endpoints.
@app.after_request
def add_header(response):
	# response.cache_control.no_store = True
	response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '-1'
	return response


if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True, threaded=True)
