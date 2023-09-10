from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson import ObjectId  # Import ObjectId from bson module
from werkzeug.utils import secure_filename
import os

client = MongoClient("mongodb://localhost:27017/")
db = client["user_db"]
collection = db["users"]

app = Flask(__name__, template_folder='templates')

# Define a directory to store uploaded images
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ...

# secret key
secret_key = "abc"
app.secret_key = secret_key

@app.route('/')
def index():
    users = collection.find()
    return render_template('viewUsers.html', users=users)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        flash("Data Inserted Successfully")
        status = None  # Declare status with an initial value
        if request.form.get('status') == 'on':
            status = 'active'
        else:
            status = 'inactive'
        user_data = {
            "name": request.form.get('name'),
            "email": request.form.get('email'),
            "contact": request.form.get('contact'),
            "status": status,
        }

          # Handle file upload
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                corrected_file_path = file_path.replace("\\", "/")
                file.save(corrected_file_path)
                print(f"Image saved to: {corrected_file_path}")  # Print to console
                user_data['profile_image'] = corrected_file_path

        collection.insert_one(user_data)
        return redirect(url_for('index'))
    
    return render_template('addUser.html')

@app.route('/update_status', methods=['POST'])
def update_status():
    flash("Status updated successfully")
    user_id = request.form.get('user_id')
    status = request.form.get('status')

    collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"status":status}})
    return redirect(url_for('index'))

@app.route('/edit/<user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = collection.find_one({"_id": ObjectId(user_id)})
    if request.method == 'POST':
        flash("Data Updated Successfully")
        status = None  # Declare status with an initial value
        if request.form.get('status') == 'on':
            status = 'active'
        else:
            status = 'inactive'

        user_data = {
            "name": request.form.get('name'),
            "email": request.form.get('email'),
            "contact": request.form.get('contact'),
            "status": status
        }

        # Handle file upload for editing
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                corrected_file_path = file_path.replace("\\", "/")
                file.save(corrected_file_path)
                print(f"Image saved to: {corrected_file_path}")  # Print to console
                user_data['profile_image'] = corrected_file_path

        collection.update_one({"_id": ObjectId(user_id)}, {"$set": user_data})
        return redirect(url_for('index'))
    return render_template("editUser.html", user=user)

@app.route('/delete/<user_id>')
def delete_user(user_id):
    flash("Data Deleted Successfully")
    collection.delete_one({"_id" : ObjectId(user_id)})
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)