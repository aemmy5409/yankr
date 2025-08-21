from flask import Flask, request, jsonify, send_file, session
import uuid
import os
import yt_dlp
import shutil
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import query


load_dotenv()
app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "my_secure_secret_key")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")
DATABASE = os.getenv("DATABASE", "users.db")
DEBUG_MODE = os.getenv("DEBUG", True)

query.set_db_path(DATABASE)

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

query.init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return jsonify({"error": "Authentication required. Kindly login or register!"}), 401
        return f(args, kwargs)
    return decorated_function

def build_format_string(resolution=None):
    if resolution:
        return f"bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]/best"
    return "bestvideo+bestaudio/best"


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return  jsonify({"error": "Email and Password are required!"}), 400
    
    hashed_password = generate_password_hash(password)

    if query.add_user(email, hashed_password):
        return jsonify({"message": "User successfully created"}), 201
    else:
        return jsonify({"error": "User creation failed: user already exists"}), 409

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return  jsonify({"error": "Email and Password are required!"}), 400
    
    stored_password = query.get_user_password(email)
    if stored_password and check_password_hash(stored_password, password):
        return jsonify({"message": "User login successful"}), 200
    
    return jsonify({"error": "Invalid credentials!"}), 401

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.pop("email", None)
    return jsonify({"message": "User logout successful"}), 200

@app.route("/download", methods=["POST"])
@login_required
def download():
    data = request.get_json()
    url = data.get("url")
    resolution = data.get("resolution")
    
    if not url:
        return jsonify({"error": "Missing YouTube URL!"}), 400
    
    session_id = str(uuid.uuid4())
    output_path = os.path.join(DOWNLOAD_DIR, session_id)

    ydl_opts = {
        "outtmpl": os.path.join(output_path, '%(title)s.%(ext)s'),
        "format": build_format_string(resolution),
        "merge_output_format": "mp4",
        "quiet": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        shutil.rmtree(output_path, ignore_errors=True)
        return jsonify({"error": str(e)}), 500
    
    files = os.listdir(output_path)
    if not files:
        shutil.rmtree(output_path, ignore_errors=True)
        return jsonify({"error": "Download failed or file(s) not found"}), 404
    
    if len(files) == 1 :
        file_path = os.path.join(output_path, files[0])
        return send_file(file_path, as_attachment=True)
    
    zip_path = f"{output_path}.zip"
    shutil.make_archive(output_path, 'zip', output_path)
    shutil.rmtree(output_path, ignore_errors=True)
    return send_file(zip_path, as_attachment=True, mimetype='application/zip')

@app.route('/')
def index():
    return jsonify({"message": "Yankr is active and running..."})


if __name__ == "__main__":
    app.run(debug=True)
