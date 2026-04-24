"""File Upload Service - Handle file uploads"""
from flask import request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from .utils import allowed_file


UPLOAD_FOLDER = 'dataset'
ALLOWED_EXTENSIONS = {'csv'}


def upload_file():
    """Handle file upload"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Tidak ada file dalam form.', 'danger')
            return redirect(request.url)
        
        file = request.files['file']

        if file.filename == '':
            flash('Tidak ada file yang dipilih.', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower()
            new_filename = f"dataset.{ext}"
            filepath = os.path.join(UPLOAD_FOLDER, new_filename)
            file.save(filepath)
            flash('File berhasil diupload: ' + new_filename, 'success')
            return redirect(url_for('upload_file'))
        
        flash('File tidak diizinkan.', 'danger')
        return redirect(request.url)
    
    return redirect(url_for('dashboard'))


def save_file_upload(file, filename):
    """Save uploaded file to static/upload folder"""
    if file and file.filename != '':
        ext = os.path.splitext(file.filename)[1]
        filename_with_ext = filename + ext
        upload_folder = os.path.join('static', 'upload')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename_with_ext)
        file.save(file_path)
        return filename_with_ext
    return None
