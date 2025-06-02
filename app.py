# === Flask Backend for Attendance + Certificate Upload (PostgreSQL + Supabase) ===

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from supabase import create_client, Client
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid

app = Flask(__name__)
CORS(app)

# === Config ===
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://your_user:your_password@your_host:5432/your_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# === Supabase Config ===
SUPABASE_URL = 'https://your-project.supabase.co'
SUPABASE_KEY = 'your-supabase-service-role-key'
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === Models ===

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # cleaner, executive, auditor
    assigned_branches = db.Column(db.Text)  # comma-separated list

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

class CertificateUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    file_type = db.Column(db.String(10))  # JCC, DCC, JSDN
    bank = db.Column(db.String(50))
    branch = db.Column(db.String(120))
    month = db.Column(db.String(20))
    file_url = db.Column(db.String(300))
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)

# === Endpoints ===

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email'], password=data['password']).first()
    if user:
        return jsonify({
            "id": user.id,
            "name": user.name,
            "role": user.role,
            "branches": user.assigned_branches.split(',') if user.assigned_branches else []
        })
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/attendance', methods=['POST'])
def record_attendance():
    data = request.json
    record = Attendance(
        user_id=data['user_id'],
        latitude=data['latitude'],
        longitude=data['longitude']
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({"message": "Attendance recorded"})

@app.route('/upload_certificate', methods=['POST'])
def upload_certificate():
    user_id = request.form['user_id']
    file_type = request.form['file_type']
    bank = request.form['bank']
    branch = request.form['branch']
    month = request.form['month']
    file = request.files['file']

    if file:
        filename = secure_filename(file.filename)
        unique_filename = str(uuid.uuid4()) + "_" + filename
        file_bytes = file.read()

        # Upload to Supabase
        path = f"certificates/{unique_filename}"
        response = supabase.storage.from_('your-bucket').upload(path, file_bytes, {'content-type': file.mimetype})

        if response.status_code >= 300:
            return jsonify({"error": "Failed to upload to Supabase"}), 500

        public_url = f"{SUPABASE_URL}/storage/v1/object/public/your-bucket/{path}"

        record = CertificateUpload(
            user_id=user_id,
            file_type=file_type,
            bank=bank,
            branch=branch,
            month=month,
            file_url=public_url
        )
        db.session.add(record)
        db.session.commit()
        return jsonify({"message": "File uploaded", "url": public_url})
    return jsonify({"error": "File missing"}), 400

@app.route('/certificates', methods=['GET'])
def get_certificates():
    month = request.args.get('month')
    file_type = request.args.get('type')
    query = CertificateUpload.query
    if month:
        query = query.filter_by(month=month)
    if file_type:
        query = query.filter_by(file_type=file_type)
    certs = query.all()
    return jsonify([{ 
        "branch": c.branch, 
        "file_type": c.file_type, 
        "url": c.file_url, 
        "upload_time": c.upload_time 
    } for c in certs])

@app.route('/summary', methods=['GET'])
def summary():
    cert_count = CertificateUpload.query.count()
    attendance_count = Attendance.query.count()
    return jsonify({
        "total_certificates": cert_count,
        "total_attendance_records": attendance_count
    })

# === Init DB ===
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
