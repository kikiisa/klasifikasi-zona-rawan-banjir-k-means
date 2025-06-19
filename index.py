from flask import Flask,render_template,request,redirect,url_for,flash,session,jsonify
from werkzeug.utils import secure_filename
import os
import pandas as pd
import db 
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans

import db.index
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

@app.route('/login',methods=['GET'])
def login():
    if(session.get('status')):
        return redirect(url_for('dashboard'))
    else:
        return render_template('auth/login.html',title='Login')

@app.route('/logout',methods=['GET'])
def logout():
    session.pop('status',None)
    session.pop('id',None)
    return redirect(url_for('login'))

@app.route('/login',methods=['POST'])
def login_post():
    
    username = request.form.get('username')
    password = request.form.get('password')
    user = db.index.login(username,password)
    session['id'] = user[0]
    session['status'] = True
    if user:
        return redirect(url_for('dashboard'))
    else:
        flash('Username atau Password Salah')
        return redirect(url_for('login'))
@app.route('/dashboard')
def dashboard():
    if(not session.get('status')):
        flash('Silahkan Login Terlebih Dahulu !')
        return redirect(url_for('login'))
    file_path = os.path.join(dataset_dir, 'dataset.csv')
    result_path = os.path.join('output', 'result.csv')

    # Inisialisasi nilai default
    convertHTML = None
    converHTMLresult = None

    status_file = os.path.isfile(file_path)
    status_result = os.path.isfile(result_path)

    if status_file:
        df = pd.read_csv(file_path)
        convertHTML = df.to_html(classes='table table-bordered', index=False)

    if status_result:
        result = pd.read_csv(result_path)
        converHTMLresult = result.to_html(classes='table table-bordered', index=False)

    return render_template(
        'dashboard/index.html',
        title='Dashboard',
        status_file=status_file,
        status_result=status_result,
        data=convertHTML,
        result=converHTMLresult
    )

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


@app.route("/api/results", methods=["GET"])
def results():  
    data = pd.read_csv('output/result.csv')
    return  data.to_json(orient="records")
    # data.to_json(orient="records")

@app.route('/prosess',methods=['POST'])
def prosess():
    if request.method == 'POST':
        file_path = os.path.join(dataset_dir,'dataset.csv')
        if(not os.path.isfile(file_path)):
            flash('File CSV Tidak Ditemukan')
            return redirect(url_for('dashboard'))
        
        # === 3. Preprocessing ===
        data= pd.read_csv(file_path)
        fitur = ['curah_hujan_mm',
         'kemiringan_persen','banjir_historis']
        
        # === 3. Preprocessing ===
        
        scaler = MinMaxScaler()
        data_scaled = scaler.fit_transform(data[fitur])
        
        # === 4. Jalankan K-Means ===
        k = 3
        kmeans = KMeans(n_clusters=k, random_state=42)
        data['klaster'] = kmeans.fit_predict(data_scaled)

        # === 5. Pemetaan label klaster ke zonasi ===
        mapping = {0: 'Rendah', 1: 'Sedang', 2: 'Tinggi'}

        # Urutkan berdasarkan elevasi rata-rata per klaster (agar labelnya masuk akal)
        centers = pd.DataFrame(kmeans.cluster_centers_, columns=fitur)
        order = centers['curah_hujan_mm'].argsort().values
        label_map = {old: mapping[new] for new, old in enumerate(order)}
        data['klaster_banjir'] = data['klaster'].map(label_map)
        # === 6. Simpan hasilnya ke CSV ===
        data.to_csv("output/result.csv", index=False)
        flash('Proses Berhasil')
        return redirect(url_for('dashboard'))
if __name__ == '__main__':
    app.run(debug=True)
    