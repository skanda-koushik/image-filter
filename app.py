import sys
import os
import glob
import re
import numpy as np
import tensorflow as tf

from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

config = ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.5
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)
# Keras
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Flask utils
from flask import Flask, redirect, url_for, request, render_template,session,flash,redirect, url_for, session,flash
from werkzeug.utils import secure_filename
#from gevent.pywsgi import WSGIServer
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

import os
from datetime import datetime

import shutil
import os
import shutil
import ctypes
import platform

def unhide_folder(folder_path):
    if platform.system() == 'Windows':
        # Windows-specific code to unhide folder
        if not os.path.exists(folder_path):
            print(f"The folder '{folder_path}' does not exist.")
            return

        attrs = ctypes.windll.kernel32.GetFileAttributesW(folder_path)
        if attrs & 2:  # FILE_ATTRIBUTE_HIDDEN = 0x2
            new_attrs = attrs & ~2
            result = ctypes.windll.kernel32.SetFileAttributesW(folder_path, new_attrs)
            
            if result:
                print(f"The folder '{folder_path}' is now unhidden.")
            else:
                print(f"Failed to unhide the folder '{folder_path}'.")
        else:
            print(f"The folder '{folder_path}' is not hidden.")
    else:
        # Unix-like system code to unhide folder
        if not os.path.exists(folder_path):
            print(f"The folder '{folder_path}' does not exist.")
            return

        dir_name = os.path.dirname(folder_path)
        base_name = os.path.basename(folder_path)

        if base_name.startswith('.'):
            new_name = base_name[1:]
            new_folder_path = os.path.join(dir_name, new_name)
            shutil.move(folder_path, new_folder_path)
            print(f"The folder '{folder_path}' is now unhidden as '{new_folder_path}'.")
        else:
            print(f"The folder '{folder_path}' is not hidden.")
            
def create_folder_with_date():
    try:
        # Get the current date
        today = datetime.today()
        # Format the date as YYYY-MM-DD
        folder_name = today.strftime("%Y-%m-%d")
        # Create the folder
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' created successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return(folder_name)
def hide_folder(folder_path):
    try:
        # Check if the folder exists
        if not os.path.exists(folder_path):
            raise FileNotFoundError("Folder not found.")
        
        # Hide the folder by setting the 'hidden' attribute
        os.system(f'attrib +h "{folder_path}"')
        print(f"{folder_path} has been hidden.")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Define a flask app
app = Flask(__name__)
app.secret_key = '1a2b3c4d5e'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'accoumts'

# Intialize MySQL
mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def login():
# Output message if something goes wrong...
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
                # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            #session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return render_template('index.html',title="Plant")#redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            flash("Incorrect username/password!", "danger")
    return render_template('login.html',title="Login")



@app.route('/register', methods=['GET', 'POST'])
def register():
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
                # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('SELECT * FROM accounts WHERE username = %s', (username))
        cursor.execute( "SELECT * FROM accounts WHERE username LIKE %s", [username] )
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            flash("Account already exists!", "danger")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Invalid email address!", "danger")
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash("Username must contain only characters and numbers!", "danger")
        elif not username or not password or not email:
            flash("Incorrect username/password!", "danger")
        else:
        # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (%s, %s, %s)', (username,email, password))
            mysql.connection.commit()
            flash("You have successfully registered!", "success")
            return render_template('login.html',title="Login")

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash("Please fill out the form!", "danger")
    # Show registration form with message (if any)
    return render_template('login.html',title="Register")
# Model saved with Keras model.save()
MODEL_PATH ='imfilter.h5'

# Load your trained model
model = load_model(MODEL_PATH)




def model_predict(img_path, model):
    print(img_path)
    img = image.load_img(img_path, target_size=(224, 224))

    # Preprocessing the image
    x = image.img_to_array(img)
    # x = np.true_divide(x, 255)
    ## Scaling
    x=x/255
    x = np.expand_dims(x, axis=0)
   

    # Be careful how your trained model deals with the input
    # otherwise, it won't make correct prediction!
   # x = preprocess_input(x)

    preds = model.predict(x)
    preds=np.argmax(preds, axis=1)
    if preds==0:
        preds=0
        
    elif preds==1:
        preds=1
        
    elif preds==2:
        preds=2
        
    elif preds==3:
        preds=3
    return (preds)


@app.route('/home', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')

@app.route('/home1', methods=['GET'])
def index1():
    # Main page
    return render_template('index1.html')

def move_file(source_path, destination_path):
    try:
        # Move the file to the destination folder
        shutil.move(source_path, destination_path)
        print(f"File moved successfully from '{source_path}' to '{destination_path}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

            
@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.form['file']
        print(f)
        import os
        from os import listdir
        folder_dir = f
        fr=create_folder_with_date()
        for images in os.listdir(folder_dir):
            if (images.endswith(".png") or images.endswith(".jpg") or images.endswith(".jpeg")):
                preds=model_predict(f+'/'+images, model)
                print(preds)
                if(preds!=2):
                    source_file_path = f+'/'+images
                    destination_folder_path = fr
                    move_file(source_file_path, destination_folder_path)
            hide_folder(fr)
            result="Files Hidden"
                
    return result

@app.route('/predict1', methods=['GET', 'POST'])
def upload1():
    result=""
    if request.method == 'POST':
        today=request.form['file']
        print(today)
        #today = datetime.today()
        folder_name = today
        print(folder_name[0])
        unhide_folder(folder_name)
        result="Unhided"
                
    return render_template("index1.html",result=result)

if __name__ == '__main__':
    app.run(port=5001,debug=False,host='0.0.0.0')
