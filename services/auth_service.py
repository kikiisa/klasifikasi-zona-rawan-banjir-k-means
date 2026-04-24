"""Authentication Service - Handle login/logout"""
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
import database.ConnectionDb

initDb = database.ConnectionDb.run


def login_view():
    """Display login page"""
    if session.get('status'):
        return redirect(url_for('dashboard'))
    else:
        return render_template('auth/auth.html', title='Login')


def logout_view():
    """Handle user logout"""
    session.pop('status', None)
    session.pop('id', None)
    return redirect(url_for('login'))


def login_post_view():
    """Handle login form submission"""
    username = request.form.get("username")
    password = request.form.get("password")
    user = initDb.getUserByUsername(username)
    
    if user:    
        if user['status'] != 'active':
            flash("Akun anda di Nonaktifkan", 'danger')
            return redirect(url_for("login"))
        
        if check_password_hash(user['password'], password):
            session['id'] = user
            session['status'] = True
            return redirect(url_for("dashboard"))
        else:
            flash("Username atau Password Salah", 'danger')
            return redirect(url_for("login"))
    else:
        flash("Usernme atau Password Salah", 'danger')
        return redirect(url_for("login"))
