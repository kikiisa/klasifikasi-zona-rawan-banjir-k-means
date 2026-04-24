
"""
Main Flask Application - K-Means Flood Clustering System
Routes are organized using service modules for better maintainability
"""
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_cors import CORS
import os
import pandas as pd
import database.ConnectionDb

# Import services
from services import auth_service, user_service, data_service, upload_service, ml_service
from services.utils import login_required

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = "jody"
CORS(app)

# Configuration
UPLOAD_FOLDER = 'dataset'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

initDb = database.ConnectionDb.run

# ==================== FRONTEND ROUTES ====================

@app.route('/')
def index():
    """Display home page"""
    data = initDb.fetchContact()
    result_path_final = os.path.join('storage', 'result.csv')
    converHTMLresultFinal = None
    status_final_result = os.path.isfile(result_path_final)
    
    if status_final_result:
        resultFinal = pd.read_csv(result_path_final).drop(columns=['id', 'geojson'], errors='ignore')
        converHTMLresultFinal = resultFinal.to_html(classes='table table-bordered', index=False)

    statusFile = os.path.isfile(os.path.join('storage', 'result.csv'))
    return render_template('front/index.html', data=data, final=converHTMLresultFinal, existFile=statusFile)


@app.route("/hasil-cluster", methods=['GET'])
def hasil_cluster():
    """Display clustering results"""
    data = initDb.fetchContact()
    return render_template('front/cluster.html', data=data)


@app.route("/peta-bencana", methods=["GET"])
def peta_bencana():
    """Display disaster map"""
    data = initDb.fetchContact()
    return render_template("front/peta-bencana.html", data=data)


# ==================== AUTHENTICATION ROUTES ====================

@app.route("/login", methods=['GET'])
def login():
    """Display login page"""
    return auth_service.login_view()


@app.route("/login", methods=['POST'])
def login_post():
    """Handle login form submission"""
    return auth_service.login_post_view()


@app.route('/logout', methods=['GET'])
def logout():
    """Handle user logout"""
    return auth_service.logout_view()


# ==================== USER PROFILE ROUTES ====================

@app.route("/setting", methods=["GET"])
@login_required
def settings():
    """Display user settings"""
    return render_template("profile/index.html", data=session.get("id"))


@app.route('/contact', methods=['GET'])
def contact():
    """Display contact page"""
    data = initDb.fetchContact()
    return render_template('contact/index.html', contact=data)


@app.route('/contact', methods=['POST'])
def update_contact():
    """Update contact information"""
    instagram = request.form.get('instagram')
    facebook = request.form.get('facebook')
    whatsapp = request.form.get('whatsapp')
    initDb.updateContact(1, instagram, facebook, whatsapp)
    flash('Contact updated successfully', 'success')
    return redirect(url_for('contact'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Display main dashboard"""
    statusFile = os.path.isfile(os.path.join('storage', 'result.csv'))
    return render_template('dashboard/index.html', title='Dashboard', existFile=statusFile)
# ==================== USER MANAGEMENT ROUTES ====================

@app.route("/management-user", methods=['GET'])
@login_required
def management_user():
    """Display user management page"""
    return user_service.list_users()


@app.route("/create/user", methods=["GET"])
def create_user():
    """Display create user form"""
    return user_service.create_user_view()


@app.route("/edit/user/<id>", methods=["GET"])
@login_required
def edit_user(id):
    """Display edit user form"""
    return user_service.edit_user_view(id)


@app.route("/create/user/store", methods=["POST"])
@login_required
def store_user():
    """Store new user"""
    return user_service.store_user()


@app.route("/update/user/<id>", methods=["POST"])
@login_required
def update_user(id):
    """Update user data"""
    return user_service.update_user(id)


@app.route("/delete-user/<id>", methods=["GET"])
@login_required
def delete_user(id):
    """Delete user"""
    return user_service.delete_user(id)

# ==================== DATA MANAGEMENT ROUTES ====================

@app.route('/management-data', methods=['GET'])
@login_required
def management_data():
    """Display data management page"""
    return data_service.list_data()


@app.route("/data-peta", methods=['GET'])
@login_required
def data_peta():
    """Display map data page"""
    statusFile = os.path.isfile(os.path.join('storage', 'result.csv'))
    return render_template('peta/index.html', title='Data Peta', existFile=statusFile)


@app.route('/management-data/create', methods=['GET'])
@login_required
def create():
    """Display create data form"""
    return data_service.create_data_view()


@app.route("/management-data/edit/<id>", methods=['GET'])
@login_required
def edit(id):
    """Display edit data form"""
    return data_service.edit_data_view(id)


@app.route("/management-data/update/<id>", methods=['POST'])
@login_required
def update(id):
    """Update data"""
    return data_service.update_data(id)


@app.route("/management-data/delete/<id>", methods=['GET'])
@login_required
def delete(id):
    """Delete data"""
    return data_service.delete_data(id)


@app.route('/insert-data', methods=['POST'])
@login_required
def insertData():
    """Insert new data"""
    return data_service.insert_data()


@app.route("/reset-data", methods=['GET'])
@login_required
def reset_data():
    """Reset all data"""
    return data_service.reset_data()
    

# ==================== FILE UPLOAD ROUTES ====================

@app.route('/upload-file', methods=['POST', 'GET'])
@login_required
def upload_file():
    """Handle file upload"""
    return upload_service.upload_file()


# ==================== MACHINE LEARNING / CLUSTERING ROUTES ====================

@app.route("/cluster-data", methods=["GET"])
@login_required
def management_cluster():
    """Display clustering management page"""
    return ml_service.management_cluster_view()


@app.route("/sinkronasi", methods=["POST"])
@login_required
def sinkronasi():
    """Synchronize data from database"""
    return ml_service.sinkronasi_data()


@app.route('/prosess', methods=['POST'])
@login_required
def prosess():
    """Process clustering"""
    return ml_service.process_clustering()


@app.route("/api/results", methods=["GET"])
def results():
    """Get clustering results as JSON"""
    result = ml_service.get_results()
    if result is None:
        return jsonify({"error": "Not Found"}), 404
    return result.to_json(orient="records")


@app.route("/api/filter-by/<id>", methods=['GET'])
@login_required
def filterbyidKecamatan(id):
    """Get villages filtered by district"""
    data = ml_service.get_filter_by_district(id)
    return jsonify(data)


# ==================== APPLICATION ENTRY POINT ====================

if __name__ == '__main__':
    """Run Flask application in debug mode"""
    app.run(debug=True)
