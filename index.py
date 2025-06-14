from flask import Flask,render_template,request,redirect,url_for,flash
from werkzeug.utils import secure_filename
import os
import pandas as pd
import time
app = Flask(__name__)

app.secret_key = "jody"
dataset_dir = 'dataset'
UPLOAD_FOLDER = 'dataset'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        df = pd.read_csv(file_path)
        convertHTML = df.to_html(classes='',index=False)
        return render_template('dashboard/index.html',title='Dashboard',status_file=True,data=convertHTML)
    else:
        return render_template('dashboard/index.html',title='Dashboard',status_file=False)
       


@app.route('/upload-file',methods=['POST','GET'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Tidak ada file dalam form.')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash('Tidak ada file yang dipilih.')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)  # Hindari nama aneh
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower()
            # Rename otomatis dengan timestamp
            new_filename = f"dataset.{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            file.save(filepath)
            flash('File berhasil diupload: ' + new_filename)
            return redirect(url_for('upload_file'))
        flash('File tidak diizinkan.')
        return redirect(request.url)
    
    
    return redirect(url_for('dashboard'))
if __name__ == '__main__':
    app.run(debug=True)
    