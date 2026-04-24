# Services Architecture Documentation

## Overview
Proyek ini telah di-refactor menggunakan service-oriented architecture untuk meningkatkan maintainability dan separation of concerns. Semua logika bisnis telah dipindahkan dari `index.py` menjadi service modules yang terpisah.

## Struktur Folder Services

```
services/
├── __init__.py           # Package initialization
├── utils.py              # Utility functions dan decorators
├── auth_service.py       # Authentication (login/logout)
├── user_service.py       # User management (CRUD)
├── data_service.py       # Data management (CRUD)
├── upload_service.py     # File upload handling
└── ml_service.py         # Machine Learning & Clustering
```

## Service Modules Details

### 1. **auth_service.py**
**Fungsi:** Menangani autentikasi pengguna

**Functions:**
- `login_view()` - Menampilkan halaman login
- `logout_view()` - Proses logout
- `login_post_view()` - Memproses form login

**Routes:**
- `GET /login` - Halaman login
- `POST /login` - Proses login
- `GET /logout` - Proses logout

---

### 2. **user_service.py**
**Fungsi:** Manajemen user (CRUD operations)

**Functions:**
- `list_users()` - Menampilkan daftar user
- `create_user_view()` - Form buat user
- `edit_user_view(id)` - Form edit user
- `store_user()` - Simpan user baru
- `update_user(id)` - Update user
- `delete_user(id)` - Hapus user

**Routes:**
- `GET /management-user` - Daftar user
- `GET /create/user` - Form buat user
- `GET /edit/user/<id>` - Form edit user
- `POST /create/user/store` - Simpan user baru
- `POST /update/user/<id>` - Update user
- `GET /delete-user/<id>` - Hapus user

**Decorators:** `@login_required`, `@admin_required`

---

### 3. **data_service.py**
**Fungsi:** Manajemen data banjir (CRUD operations)

**Functions:**
- `list_data()` - Daftar data
- `create_data_view()` - Form buat data
- `edit_data_view(id)` - Form edit data
- `insert_data()` - Simpan data baru
- `update_data(id)` - Update data
- `delete_data(id)` - Hapus data
- `reset_data()` - Reset semua data
- `data_exists(filename)` - Cek keberadaan file

**Routes:**
- `GET /management-data` - Daftar data
- `GET /management-data/create` - Form buat data
- `GET /management-data/edit/<id>` - Form edit data
- `POST /insert-data` - Simpan data baru
- `POST /management-data/update/<id>` - Update data
- `GET /management-data/delete/<id>` - Hapus data
- `GET /reset-data` - Reset data

**Decorators:** `@login_required`

---

### 4. **upload_service.py**
**Fungsi:** Menangani upload file

**Functions:**
- `upload_file()` - Proses upload file CSV
- `save_file_upload(file, filename)` - Simpan file ke folder upload

**Routes:**
- `POST /upload-file` - Upload file CSV

---

### 5. **ml_service.py** ⭐ **MACHINE LEARNING MODULE**
**Fungsi:** K-Means clustering dan data processing

### **Class: KMeansProcessor**
Kelas utama untuk menangani semua proses machine learning.

**Methods:**
- `__init__(n_clusters=3, random_state=42)` - Initialize processor
- `load_data(file_path)` - Load data dari CSV
- `preprocess_data(data)` - Preprocessing & scaling dengan MinMaxScaler
- `run_kmeans_steps(data_scaled_df)` - Manual K-Means dengan step logging
- `fit_kmeans(data_scaled_df)` - Fit K-Means sklearn
- `map_clusters(data, kmeans)` - Map cluster numbers ke risk levels
- `plot_centroid_and_clusters()` - Visualisasi hasil clustering
- `process(input_file)` - Pipeline lengkap processing

**Service Functions:**
- `management_cluster_view()` - Halaman manajemen clustering
- `sinkronasi_data()` - Sinkronisasi data dari database ke CSV
- `process_clustering()` - Proses clustering utama
- `get_results()` - Ambil hasil clustering sebagai df
- `get_filter_by_district(id)` - Filter desa berdasarkan kecamatan

**Routes:**
- `GET /cluster-data` - Halaman clustering
- `POST /sinkronasi` - Sinkronisasi data
- `POST /prosess` - Proses clustering
- `GET /api/results` - Hasil clustering (JSON)
- `GET /api/filter-by/<id>` - Filter desa

---

### 6. **utils.py**
**Fungsi:** Helper functions dan decorators

**Decorators:**
- `@login_required` - Cek user login
- `@admin_required` - Cek role admin

**Functions:**
- `allowed_file(filename, allowed_extensions)` - Validasi ekstensi file
- `ensure_directory(directory)` - Buat folder jika belum ada
- `get_kecamatan_data()` - Data static kecamatan

---

## Refactored index.py Structure

File `index.py` sekarang hanya berisi:
1. Import services
2. Flask app initialization
3. Route definitions yang simple (hanya delegate ke services)

**Struktur Routes di index.py:**

```python
# FRONTEND ROUTES
@app.route('/')
@app.route("/hasil-cluster")
@app.route("/peta-bencana")

# AUTHENTICATION ROUTES
@app.route("/login", methods=['GET', 'POST'])
@app.route('/logout')

# USER PROFILE ROUTES
@app.route("/setting")
@app.route('/contact')
@app.route('/dashboard')

# USER MANAGEMENT ROUTES
@app.route("/management-user")
@app.route("/create/user")
@app.route("/edit/user/<id>")
@app.route("/create/user/store")
@app.route("/update/user/<id>")
@app.route("/delete-user/<id>")

# DATA MANAGEMENT ROUTES
@app.route('/management-data')
@app.route('/management-data/create')
@app.route("/management-data/edit/<id>")
@app.route("/management-data/update/<id>")
@app.route("/management-data/delete/<id>")
@app.route('/insert-data')
@app.route("/reset-data")

# FILE UPLOAD ROUTES
@app.route('/upload-file')

# MACHINE LEARNING / CLUSTERING ROUTES
@app.route("/cluster-data")
@app.route("/sinkronasi")
@app.route('/prosess')
@app.route("/api/results")
@app.route("/api/filter-by/<id>")
```

---

## Keuntungan Refactoring

### 1. **Separation of Concerns**
   - Setiap service fokus pada satu tanggung jawab
   - Machine learning terpisah dari logika HTTP

### 2. **Testability**
   - Setiap service dapat ditest secara independen
   - Mock data lebih mudah dibuat

### 3. **Maintainability**
   - File lebih kecil dan mudah dipahami
   - Debugging lebih cepat
   - Perubahan di satu tempat

### 4. **Reusability**
   - Function di service dapat digunakan di route berbeda
   - Machine learning logic mudah diintegrasikan ke module lain

### 5. **Scalability**
   - Mudah menambah feature baru
   - Struktur siap untuk microservices

---

## Usage Examples

### Menggunakan Service dalam Route Baru

```python
from services import ml_service

@app.route('/custom-route')
def custom_route():
    result = ml_service.get_results()
    return render_template('custom.html', data=result)
```

### Menggunakan Machine Learning Service

```python
from services.ml_service import KMeansProcessor

processor = KMeansProcessor(n_clusters=3, random_state=42)
result = processor.process('storage/sinkronasi.csv')
print(result['result'])  # DataFrame hasil clustering
```

### Cek File Exists

```python
from services import data_service

if data_service.data_exists('result.csv'):
    print("Result file tersedia")
```

---

## Migration Guide

Jika ingin menambah fitur baru:

1. **Tentukan kategori fitur** (user, data, ml, upload, etc)
2. **Buat atau update service** yang sesuai
3. **Buat route di index.py** yang delegate ke service
4. **Gunakan decorators** `@login_required`, `@admin_required` jika perlu

---

## File Tree

```
k-means-banjir/
├── index.py              ← Refactored
├── services/             ← NEW
│   ├── __init__.py
│   ├── auth_service.py
│   ├── user_service.py
│   ├── data_service.py
│   ├── upload_service.py
│   ├── ml_service.py     ← Main ML module
│   └── utils.py
├── database/
├── static/
├── templates/
├── algoritma/
├── storage/
└── ... (other files)
```

---

## Notes

- Machine Learning logic sekarang terkonsentrasi di `ml_service.py` dengan class `KMeansProcessor`
- Semua decorator dan utility functions ada di `utils.py`
- Setiap service dapat diimport dan digunakan standalone
- Database connection masih menggunakan `database.ConnectionDb.run` seperti sebelumnya
