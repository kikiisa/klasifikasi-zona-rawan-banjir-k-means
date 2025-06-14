from flask import Flask,render_template,redirect,url_for,flash
from werkzeug.utils import secure_filename
import utils.index
import os
app = Flask(__name__)
app.secret_key = "secret key"
dataset_dir = 'dataset'
@app.route('/')
def index():
    return render_template('index.html',title='Home')

@app.route('/login')
def login():
    return render_template('auth/login.html',title='Login')

@app.route('/dashboard')
def dashboard():
    file_path = os.path.join(dataset_dir,'dataset.csv')
    if(os.path.isfile(file_path)):
        return render_template('dashboard/index.html',title='Dashboard',status_file=True)
       
    else:
        return render_template('dashboard/index.html',title='Dashboard',status_file=False)
       
    

@app.route('/upload-file')
def upload_file():
    pass
if __name__ == '__main__':
    app.run(debug=True)
    