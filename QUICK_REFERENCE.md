# Quick Reference Guide - Services Architecture

## 📋 Cheat Sheet untuk Development

### Menggunakan Services dalam Route

#### Auth Service
```python
from services import auth_service

@app.route("/login")
def login():
    return auth_service.login_view()
```

#### User Service
```python
from services import user_service

@app.route("/management-user")
def users():
    return user_service.list_users()
```

#### Data Service
```python
from services import data_service

@app.route("/management-data")
def data():
    return data_service.list_data()
```

#### Machine Learning Service
```python
from services import ml_service

@app.route("/cluster-data")
def cluster():
    return ml_service.management_cluster_view()
```

#### Upload Service
```python
from services import upload_service

@app.route("/upload-file")
def upload():
    return upload_service.upload_file()
```

---

## 🔒 Menggunakan Decorators

### Login Required
```python
from services.utils import login_required

@app.route("/protected")
@login_required
def protected_route():
    return "Only logged in users"
```

### Admin Required
```python
from services.utils import admin_required

@app.route("/admin-only")
@admin_required
def admin_route():
    return "Only admins can access"
```

---

## 🤖 Machine Learning Usage

### Basic Usage
```python
from services.ml_service import KMeansProcessor

processor = KMeansProcessor(n_clusters=3, random_state=42)
result = processor.process('storage/sinkronasi.csv')

# Access results
print(result['result'])          # DataFrame hasil
print(result['centers'])         # DataFrame centroid
print(result['data_scaled'])     # Data scaled
print(result['log_iterasi'])     # Log iterasi processing
```

### Custom Processing
```python
from services.ml_service import KMeansProcessor
import pandas as pd

processor = KMeansProcessor(n_clusters=3)

# Step by step
data = processor.load_data('file.csv')
data_scaled = processor.preprocess_data(data)
kmeans = processor.fit_kmeans(data_scaled)
data, centers, label_map = processor.map_clusters(data, kmeans)

# Visualize
processor.plot_centroid_and_clusters(data_scaled, data, kmeans, label_map)
```

---

## 📂 File Mapping

| File | Routes | Functions |
|------|--------|-----------|
| `auth_service.py` | `/login`, `/logout` | login, logout |
| `user_service.py` | `/management-user`, `/create/user`, etc | CRUD users |
| `data_service.py` | `/management-data`, `/insert-data`, etc | CRUD data |
| `upload_service.py` | `/upload-file` | upload CSV |
| `ml_service.py` | `/cluster-data`, `/prosess`, `/api/results` | K-Means, processing |
| `utils.py` | - | decorators, helpers |

---

## 🎯 Common Tasks

### Add New Route
1. Pilih service yang sesuai (atau buat baru)
2. Buat function di service
3. Buat route di `index.py` yang delegate ke service
4. Add decorators jika perlu: `@login_required`, `@admin_required`

### Add New Service
1. Buat file `services/new_service.py`
2. Implement functions
3. Add import di `services/__init__.py`
4. Create routes di `index.py`
5. Update import jika perlu

### Modify ML Algorithm
1. Edit `services/ml_service.py`
2. Modify `KMeansProcessor` class
3. Change `process()` method atau tambah method baru
4. Test dengan calling `process()` atau specific methods

---

## 📊 Data Flow

```
Route Request
    ↓
index.py route handler
    ↓
Service function
    ↓
Business logic (database, ML, etc)
    ↓
Return (template/JSON/redirect)
```

---

## 🧪 Testing Services

```python
# Test auth
from services import auth_service
# Mock login form

# Test ML
from services.ml_service import KMeansProcessor
processor = KMeansProcessor()
result = processor.process('test.csv')

# Test data
from services import data_service
print(data_service.data_exists('result.csv'))
```

---

## ⚠️ Important Notes

- Services **harus** import dari proper modules
- Use `@login_required` untuk protected routes
- Use `@admin_required` untuk admin-only routes
- ML Service sudah robust dengan error handling
- Database operations masih via `database.ConnectionDb.run`
- File paths use `os.path.join()` untuk compatibility

---

## 🚀 Performance Tips

- Cache kecamatan data: Already done di `utils.get_kecamatan_data()`
- Use pagination untuk list routes
- Cache hasil clustering jika tidak berubah
- Use lazy loading untuk large CSV files

---

## 📞 Troubleshooting

**Import Error:**
```
# Ensure services folder is in project root
# Double check __init__.py exists in services/
from services import auth_service
```

**Route Not Found:**
```
# Check route is defined in index.py
# Check service function name matches
# Restart Flask server
```

**ML not working:**
```
# Ensure sinkronasi.csv exists
# Check file format matches expected schema
# Check disk space for result files
```

---

**Last Updated:** 2024
**Version:** 1.0
**Status:** Production Ready ✅
