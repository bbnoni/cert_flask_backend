from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
#from supabase import create_client, Client
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid
from supabase_client import supabase
from datetime import datetime







app = Flask(__name__)
CORS(app)

# === Config ===#
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://certification_db_user:MATgBqLZPkxcgsXKF29Eesc5czYrJDAg@dpg-d0uqlih5pdvs73a9g7tg-a.oregon-postgres.render.com/certification_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# === Supabase Config ===
# SUPABASE_URL = 'https://fhnxhnhbpjkedbuptzd.supabase.co'
# SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZobnhobmJocGprZWRidWZwdHpkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODg3MjkyNiwiZXhwIjoyMDY0NDQ4OTI2fQ.RIKA8_QcegoSAN46Rt_2L565uwxM3CIF7RHKDmXBDF4'
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === Models ===
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # cleaner, executive, auditor
    assigned_branches = db.Column(db.Text)

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
        branches = user.assigned_branches.split(',') if user.assigned_branches else []
        branch_pairs = [
            f"{branches[i].strip()},{branches[i+1].strip()}"
            for i in range(0, len(branches) - 1, 2)
        ]
        return jsonify({
            "id": user.id,
            "name": user.name,
            "role": user.role,
            "branches": branch_pairs
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
    try:
        print("📥 Upload route triggered")

        # ✅ DNS resolution test here (right at the start)
        import socket
        try:
            ip = socket.gethostbyname("gottknpkjqqlmghyilcf.supabase.co")
            print(f"🌐 DNS resolved: gottknpkjqqlmghyilcf.supabase.co -> {ip}")
        except Exception as dns_err:
            print(f"❌ DNS resolution failed: {dns_err}")
            return jsonify({"error": "DNS resolution failed"}), 500
        
        user_id = request.form['user_id']
        file_type = request.form['file_type']
        bank = request.form['bank']
        branch = request.form['branch']
        month = request.form['month']
        file = request.files['file']

        print(f"📦 user_id={user_id}, file_type={file_type}, bank={bank}, branch={branch}, month={month}")

        if file:
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_bytes = file.read()

            path = f"certificates/{unique_filename}"
            print(f"📁 Original file: {filename} -> {unique_filename}")
            print(f"🚀 Uploading to Supabase path: {path}")

            # Try uploading
            response = supabase.storage.from_('certificates').upload(
                path, file_bytes, {'content-type': file.mimetype}
            )

            if hasattr(response, 'status_code') and response.status_code >= 300:
                print(f"❌ Upload error: {response}")
                return jsonify({"error": "Failed to upload to Supabase"}), 500

            #public_url = f"{SUPABASE_URL}/storage/v1/object/public/certificates/{path}"
            #public_url = supabase.storage.from_("certificates").get_public_url(path)
            SUPABASE_PUBLIC_URL = "https://gottknpkjqqlmghyilcf.supabase.co/storage/v1/object/public"
            public_url = f"{SUPABASE_PUBLIC_URL}/{path}"
            #public_url = supabase.storage.from_("certificates").get_public_url(path)





            # Save to DB
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
            print("✅ Upload and DB record successful.")
            return jsonify({"message": "File uploaded", "url": public_url})

        return jsonify({"error": "File missing"}), 400

    except Exception as e:
        print(f"🔥 Exception during upload: {e}")
        return jsonify({"error": str(e)}), 500



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



@app.route('/audit_files', methods=['GET'])
def audit_files():
    # Get current month or passed ?month=June
    month = request.args.get('month') or datetime.utcnow().strftime('%B')

    uploads = CertificateUpload.query.filter_by(month=month).all()
    result = [
        {
            'bank': upload.bank,
            'branch': upload.branch,
            'file_type': upload.file_type,
            'file_url': upload.file_url,
            'uploaded_at': upload.upload_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for upload in uploads
    ]
    return jsonify(result)

@app.route('/audit_summary', methods=['GET'])
def audit_summary():
    from sqlalchemy import func

    month = request.args.get('month') or datetime.utcnow().strftime('%B')

    # Step 1: Fetch executive users only
    executive_users = User.query.filter_by(role='executive').all()
    user_ids = [u.id for u in executive_users]

    # Step 2: Fetch their certificate uploads
    uploads = (
        db.session.query(
            User.id,
            User.name,
            CertificateUpload.bank,
            CertificateUpload.branch,
            CertificateUpload.file_type,
            func.count(CertificateUpload.id)
        )
        .join(User, User.id == CertificateUpload.user_id)
        .filter(CertificateUpload.month == month)
        .filter(User.id.in_(user_ids))
        .group_by(User.id, User.name, CertificateUpload.bank, CertificateUpload.branch, CertificateUpload.file_type)
        .all()
    )

    # Step 3: Organize uploads by user and branch
    user_branch_uploads = {}
    for user_id, name, bank, branch, file_type, count in uploads:
        key = (user_id, f"{bank.strip()},{branch.strip()}")
        if key not in user_branch_uploads:
            user_branch_uploads[key] = {"JCC": 0, "DCC": 0, "JSDN": 0}
        user_branch_uploads[key][file_type] = count

    # Step 4: Assemble summary per executive
    summary = {}
    for user in executive_users:
        key = user.id
        assigned_branches = user.assigned_branches.split(',') if user.assigned_branches else []
        branch_pairs = [
            f"{assigned_branches[i].strip()},{assigned_branches[i+1].strip()}"
            for i in range(0, len(assigned_branches) - 1, 2)
        ]

        summary_entry = {
            "user_id": user.id,
            "user": user.name,
            "month": month,
            "JCC": 0,
            "DCC": 0,
            "JSDN": 0,
            "has_missing": False
        }

        for pair in branch_pairs:
            b_upload = user_branch_uploads.get((user.id, pair), {"JCC": 0, "DCC": 0, "JSDN": 0})
            summary_entry["JCC"] += b_upload["JCC"]
            summary_entry["DCC"] += b_upload["DCC"]
            summary_entry["JSDN"] += b_upload["JSDN"]

            if b_upload["JCC"] == 0 or b_upload["DCC"] == 0 or b_upload["JSDN"] == 0:
                summary_entry["has_missing"] = True

        summary[key] = summary_entry

    return jsonify(list(summary.values()))



@app.route('/user_branch_summary', methods=['GET'])
def user_branch_summary():
    from sqlalchemy import func

    user_id = request.args.get('user_id')
    month = request.args.get('month')

    print(f"📥 Received user_branch_summary request: user_id={user_id}, month={month}")

    if not user_id or not month:
        return jsonify({"error": "Missing user_id or month"}), 400

    # Get user by ID
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify([])

    print(f"✅ Found user: {user.name}, branches: {user.assigned_branches}")

    # Parse branch pairs
    branches = user.assigned_branches.split(',') if user.assigned_branches else []
    branch_pairs = [
        (branches[i].strip(), branches[i + 1].strip())
        for i in range(0, len(branches) - 1, 2)
    ]

    # Fetch uploads by user and month
    uploads = CertificateUpload.query.filter_by(user_id=user.id, month=month).all()

    # Organize uploads into summary
    summary_map = {}
    for u in uploads:
        key = f"{u.bank},{u.branch}"
        if key not in summary_map:
            summary_map[key] = {
                "bank": u.bank,
                "branch": u.branch,
                "JCC": 0,
                "DCC": 0,
                "JSDN": 0,
                "JCC_url": None,
                "DCC_url": None,
                "JSDN_url": None,
            }

        summary_map[key][u.file_type] = 1
        summary_map[key][f"{u.file_type}_url"] = u.file_url

    # Fill in unsubmitted branches with zeros
    for bank, branch in branch_pairs:
        key = f"{bank},{branch}"
        if key not in summary_map:
            summary_map[key] = {
                "bank": bank,
                "branch": branch,
                "JCC": 0,
                "DCC": 0,
                "JSDN": 0,
                "JCC_url": None,
                "DCC_url": None,
                "JSDN_url": None,
            }

    return jsonify(list(summary_map.values()))







import socket

@app.route('/dns_check')
def dns_check():
    try:
        ip = socket.gethostbyname('gottknpkjqqlmghyilcf.supabase.co')
        return f"DNS resolved to {ip}"
    except Exception as e:
        return f"DNS resolution failed: {str(e)}"




@app.route('/test_upload')
def test_upload():
    try:
        content = b"Hello Supabase"
        path = "certificates/test_upload.txt"
        res = supabase.storage.from_("certificates").upload(path, content, {"content-type": "text/plain"})

        if hasattr(res, "status_code") and res.status_code >= 300:
            return jsonify({"error": "Upload failed", "response": str(res)})

        url = supabase.storage.from_("certificates").get_public_url(path)
        return jsonify({"message": "Test upload successful", "url": url})

    except Exception as e:
        return jsonify({"error": str(e)})



# === Init DB ===
with app.app_context():
    db.create_all()

# ✅ Add this health check route just before the app.run block
@app.route('/')
def index():
    return jsonify({"message": "Service is running."})    


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
