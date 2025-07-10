
from flask import Flask,render_template,request,redirect,url_for,flash,session,jsonify,make_response
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import pandas as pd
import db
import database.ConnectionDb
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
import csv
import db.index
import datetime

app = Flask(__name__)

initDb = database.ConnectionDb.run
app.secret_key = "jody"
CORS(app)
dataset_dir = 'storage'
UPLOAD_FOLDER = 'dataset'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    
    if(session.get('status')):
        return redirect(url_for('dashboard'))
    else:
        return render_template('auth/auth.html',title='Login')


@app.route('/logout',methods=['GET'])
def logout():
    session.pop('status',None)
    session.pop('id',None)
    return redirect(url_for('index'))

@app.route('/login',methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    user = db.index.login(username,password)
    if user:
        session['id'] = user[0]
        session['status'] = True
        return redirect(url_for('dashboard'))
    else:
        flash('Username atau Password Salah')
        return redirect(url_for('index'))
@app.route('/dashboard')
def dashboard():
    statusFile = False
    checkFile = os.path.isfile(os.path.join(dataset_dir,'result.csv'))
    if(checkFile):
        statusFile = True
    else:
        statusFile = False
    return render_template('dashboard/index.html',title='Dashboard',existFile=statusFile)

# route management data
@app.route('/management-data',methods=['GET'])
def management_data():
    if(not session.get('status')):
        flash('Silahkan Login Terlebih Dahulu !')
        return redirect(url_for('login'))
    data = initDb.fetchData()

    return render_template('management-data/index.html',title='Management Data',data=data)

@app.route("/data-peta",methods=['GET'])
def data_peta():
    if(not session.get('status')):
        flash('Silahkan Login Terlebih Dahulu !')
        return redirect(url_for('login'))
    statusFile = False
    checkFile = os.path.isfile(os.path.join(dataset_dir,'result.csv'))
    if(checkFile):
        statusFile = True
    else:
        statusFile = False
 
    return render_template('peta/index.html',title='Data Peta',existFile=statusFile)

@app.route("/reset-data",methods=['GET'])
def reset_data():
    if(not session.get('status')):
        flash('Silahkan Login Terlebih Dahulu !')
        return redirect(url_for('login'))
    
    filelist = [ f for f in os.listdir(dataset_dir) if f.endswith(".csv") ]
    for f in filelist:
        os.remove(os.path.join(dataset_dir, f))
    flash("Berhasil Reset Data","success")
    return redirect(url_for('management_cluster'))
@app.route('/management-data/create',methods=['GET'])
def create():
    if(not session.get('status')):
        flash('Silahkan Login Terlebih Dahulu !')
        return redirect(url_for('login'))
    
    return render_template('management-data/create.html',title='Create Data')

@app.route("/management-data/edit/<id>",methods=['GET'])
def edit(id):
    if(not session.get('status')):
        flash('Silahkan Login Terlebih Dahulu !')
        return redirect(url_for('login'))
    data = initDb.fetchDataById(id)
    return render_template('management-data/edit.html',title='Edit Data',data=data)
@app.route("/management-data/update/<id>",methods=['POST'])
def update(id):
    if(not session.get('status')):
        flash('Silahkan Login Terlebih Dahulu !')
        return redirect(url_for('login'))
    lng = request.form.get('lng')
    lat = request.form.get('lat')
    nama_desa = request.form.get('nama_desa')
    curah_hujan = request.form.get('curah_hujan')
    kemiringan = request.form.get('kemiringan')
    banjir_histori = request.form.get('banjir_histori')

    
    initDb.updateData(id,lng,lat,nama_desa,curah_hujan,kemiringan,banjir_histori)
    flash("Berhasil Updated Data","success")
    return redirect(url_for('management_data'))

@app.route("/management-data/delete/<id>",methods=['GET'])
def delete(id):
    if(not session.get('status')):
        flash('Silahkan Login Terlebih Dahulu !')
        return redirect(url_for('login'))
    initDb.deleteData(id)
    
    flash("Berhasil Menghapus Data","success")
    return redirect(url_for('management_data'))


# end route management data
@app.route('/insert-data',methods=['POST'])
def insertData():
    if(request.method == 'POST'):
        lng = request.form.get('lng')
        lat = request.form.get('lat')
        nama_desa = request.form.get('nama_desa')
        curah_hujan = request.form.get('curah_hujan')
        kemiringan = request.form.get('kemiringan')
        banjir_histori = request.form.get('banjir_histori')

        initDb.insertData(lng,lat,nama_desa,curah_hujan,kemiringan,banjir_histori)
        flash('Data Berhasil Disimpan','success')
        return redirect(url_for('management_data'))
    


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


@app.route("/cluster-data",methods=["GET"])
def management_cluster():
    if(not session.get('status')):
        flash('Silahkan Login Terlebih Dahulu !')
        return redirect(url_for('login'))
    
    result_path = os.path.join('storage', 'sinkronasi.csv')
    result_path_processing = os.path.join('storage', 'prosessing.csv')
    result_path_final = os.path.join('storage', 'result.csv')
    
    # Inisialisasi nilai default
    converHTMLresultSinkronasi = None
    converHTMLresultFinal = None
    convertHTMLresultProcessing = None
    
    status_sinkronasi = os.path.isfile(result_path)
    processingData = os.path.isfile(result_path_processing)
    status_final_result = os.path.isfile(result_path_final)
    
    if status_sinkronasi:
        resultSinkronasi = pd.read_csv(result_path).drop(columns=['id','claster'])
        converHTMLresultSinkronasi = resultSinkronasi.to_html(classes='table table-bordered', index=False)  
    
    if processingData:
        resultProcessing = pd.read_csv(result_path_processing)
        convertHTMLresultProcessing = resultProcessing.to_html(classes='table table-bordered', index=False)
        
      
    if status_final_result:
        resultFinal = pd.read_csv(result_path_final).drop(columns=['id'])
        converHTMLresultFinal = resultFinal.to_html(classes='table table-bordered', index=False)
    return render_template(
        'klaster/index.html',
        title='Dashboard',
        resultSinkronasi=converHTMLresultSinkronasi,
        resultFinalData=converHTMLresultFinal,
        resultStepProsessing=convertHTMLresultProcessing
        
    )




@app.route("/api/results", methods=["GET"])
def results():  
    file_path = os.path.join("storage", "result.csv")
    if not os.path.isfile(file_path):
        return jsonify({"error": "Not Found"}), 404

    data = pd.read_csv(file_path)
    return  data.to_json(orient="records")


@app.route("/sinkronasi", methods=["POST"])
def sinkronasi():
    datas = initDb.fetchData()

    if not datas:
       flash("Data Tidak Ditemukan","danger")
       return redirect(url_for('management_cluster'))

    # Pastikan direktori 'storage/' ada
    os.makedirs("storage", exist_ok=True)

    # Tentukan path file tujuan
    file_path = os.path.join("storage", "sinkronasi.csv")

    # Simpan ke file
    with open(file_path, mode="w", newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=datas[0].keys())
        writer.writeheader()
        writer.writerows(datas)
    flash(f"Berhasil Menyinkronkan Data, Lakukan Prosessing Data","success")
    return redirect(url_for('management_cluster'))
@app.route('/prosess',methods=['POST'])
def prosess():
    if request.method == 'POST':
        file_path = os.path.join(dataset_dir,'sinkronasi.csv')
        if(not os.path.isfile(file_path)):
            flash('File CSV Tidak Ditemukan, Silahkan Sinkronasi Kembali',"danger")
            return redirect(url_for('management_cluster'))
        
        # === 3. Preprocessing ===
        data= pd.read_csv(file_path)
        fitur = ['curah_hujan',
         'kemiringan','banjir_histori']
        
        # === 3. Preprocessing ===
        scaler = MinMaxScaler()
        data_scaled = scaler.fit_transform(data[fitur])
        
        # Konversi ke DataFrame
        
        data_scaled_df = pd.DataFrame(data_scaled, columns=fitur)
        data_scaled_df.to_csv("storage/prosessing.csv")
        
        print(data_scaled_df)
        # === 4. Jalankan K-Means ===
        k = 3
        kmeans = KMeans(n_clusters=k, random_state=42)
        data['claster'] = kmeans.fit_predict(data_scaled)

        # === 5. Pemetaan label klaster ke zonasi ===
        mapping = {0: 'Tidak Rawan', 1: 'Rawan', 2: 'Sangat Rawan'}

        # Urutkan berdasarkan elevasi rata-rata per klaster (agar labelnya masuk akal)
        centers = pd.DataFrame(kmeans.cluster_centers_, columns=fitur)
        order = centers['curah_hujan'].argsort().values
        label_map = {old: mapping[new] for new, old in enumerate(order)}
        data['claster'] = data['claster'].map(label_map)
        
        # === 6. Simpan hasilnya ke CSV ===
        data.to_csv("storage/result.csv", index=False)
        flash('Proses Berhasil','success')
        return redirect(url_for('management_cluster'))
if __name__ == '__main__':
    app.run(debug=True)
    