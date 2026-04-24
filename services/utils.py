"""Utility functions for services"""
import os
from functools import wraps
from flask import session, redirect, url_for, flash


def allowed_file(filename, allowed_extensions={'csv'}):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def login_required(f):
    """Decorator to check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('status'):
            flash('Silahkan Login Terlebih Dahulu !', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to check if user is admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('status'):
            flash('Silahkan Login Terlebih Dahulu !', 'warning')
            return redirect(url_for('login'))
        
        user = session.get('id')
        if user.get('role') != 'admin':
            flash('Maaf Akses Terbatas', 'danger')
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function


def ensure_directory(directory):
    """Ensure directory exists, create if not"""
    os.makedirs(directory, exist_ok=True)
    return directory


def get_kecamatan_data():
    """Get list of kecamatan (district) data"""
    return [
        {
            "id": "7107010",
            "regency_id": "7107",
            "name": "SANGKUB"
        },
        {
            "id": "7107020",
            "regency_id": "7107",
            "name": "BINTAUNA"
        },
        {
            "id": "7107030",
            "regency_id": "7107",
            "name": "BOLANG ITANG TIMUR"
        },
        {
            "id": "7107040",
            "regency_id": "7107",
            "name": "BOLANG ITANG BARAT"
        },
        {
            "id": "7107050",
            "regency_id": "7107",
            "name": "KAIDIPANG"
        },
        {
            "id": "7107060",
            "regency_id": "7107",
            "name": "PINOGALUMAN"
        }
    ]
