"""Data Management Service - CRUD operations for data"""
from flask import render_template, request, redirect, url_for, flash
import os
import database.ConnectionDb
from .utils import login_required, get_kecamatan_data
from .upload_service import save_file_upload

initDb = database.ConnectionDb.run
DATASET_DIR = 'storage'


@login_required
def list_data():
    """Display list of data"""
    data = initDb.fetchData()
    return render_template('management-data/index.html', title='Management Data', data=data)


@login_required
def create_data_view():
    """Display create data page"""
    kecamatan_data = get_kecamatan_data()
    return render_template('management-data/create.html', title='Create Data', kecamatan=kecamatan_data)


@login_required
def edit_data_view(id):
    """Display edit data page"""
    data = initDb.fetchDataUserById(id)
    kecamatan_data = get_kecamatan_data()
    return render_template('management-data/edit.html', title='Edit Data', data=data, kecamatan=kecamatan_data)


@login_required
def insert_data():
    """Insert new data to database"""
    if request.method == 'POST':
        lng = request.form.get('lng')
        lat = request.form.get('lat')
        nama_desa = request.form.get('nama_desa')
        curah_hujan = request.form.get('curah_hujan')
        kemiringan = request.form.get('kemiringan')
        banjir_histori = request.form.get('banjir_histori')
        kecamatan = request.form.get("kecamatan")
        
        file = request.files.get('upload')
        filename = None
        
        if file and file.filename != '':
            filename = save_file_upload(file, nama_desa)

        initDb.insertData(lng, lat, nama_desa, curah_hujan, kemiringan, banjir_histori, filename, kecamatan)
        flash('Data Berhasil Disimpan', 'success')
        return redirect(url_for('management_data'))


@login_required
def update_data(id):
    """Update data"""
    lng = request.form.get('lng')
    lat = request.form.get('lat')
    nama_desa = request.form.get('nama_desa')
    curah_hujan = request.form.get('curah_hujan')
    kemiringan = request.form.get('kemiringan')
    banjir_histori = request.form.get('banjir_histori')
    kecamatan = request.form.get("kecamatan")

    file = request.files.get('upload')
    
    if file and file.filename != '':
        filename = save_file_upload(file, nama_desa)
        initDb.updateData(id, lng, lat, nama_desa, curah_hujan, kemiringan, banjir_histori, filename, kecamatan)
    else:
        initDb.updateDataNoData(id, lng, lat, nama_desa, curah_hujan, kemiringan, banjir_histori, kecamatan)
        
    flash("Berhasil Updated Data", "success")
    return redirect(url_for('management_data'))


@login_required
def delete_data(id):
    """Delete data"""
    initDb.deleteData(id)
    flash("Berhasil Menghapus Data", "success")
    return redirect(url_for('management_data'))


@login_required
def reset_data():
    """Reset all data files"""
    filelist = [f for f in os.listdir(DATASET_DIR) if f.endswith(".csv")]
    for f in filelist:
        os.remove(os.path.join(DATASET_DIR, f))
    flash("Berhasil Reset Data", "success")
    return redirect(url_for('management_cluster'))


def data_exists(filename):
    """Check if data file exists"""
    return os.path.isfile(os.path.join(DATASET_DIR, filename))
