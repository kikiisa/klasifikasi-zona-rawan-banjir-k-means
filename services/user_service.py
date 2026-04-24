"""User Management Service - CRUD operations for users"""
from flask import render_template, request, redirect, url_for, flash
import database.ConnectionDb
from .utils import admin_required, login_required

initDb = database.ConnectionDb.run


@login_required
@admin_required
def list_users():
    """Display list of users"""
    data = initDb.fetchDataUser()
    return render_template("management-user/index.html", data=data)


def create_user_view():
    """Display create user page"""
    return render_template("management-user/create.html")


@login_required
@admin_required
def edit_user_view(id):
    """Display edit user page"""
    data = initDb.editUser(id)
    return render_template("management-user/edit.html", data=data)


@login_required
@admin_required
def store_user():
    """Store new user to database"""
    username = request.form.get('username')
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    password = request.form.get('password')
    status = request.form.get('status')
    role = request.form.get('role')
    
    initDb.insertUser(username, full_name, email, password, status, role)
    flash("Berhasil Menambahkan User", "success")
    return redirect(url_for("management_user"))


@login_required
@admin_required
def update_user(id):
    """Update user data"""
    username = request.form.get('username')
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    password = request.form.get('password')
    status = request.form.get('status')
    role = request.form.get('role')
    
    initDb.updateUser(id, username, full_name, email, password, status, role)
    flash("Berhasil Update User", "success")
    return redirect(url_for('management_user'))


@login_required
@admin_required
def delete_user(id):
    """Delete user from database"""
    initDb.deleteUser(id)
    flash("Berhasil Menghapus User", "success")
    return redirect(url_for('management_user'))
