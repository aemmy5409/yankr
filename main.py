from flask import Flask, request, jsonify, send_file
import uuid
import os
import yt_dlp
import shutil

app = Flask(__name__)


DOWNLOAD_DIR = "downloads"

def build_format_string(resolution=None):
    if resolution:
        return f"bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]/best"
    return "bestvideo+bestaudio/best"


@app.route("/download", methods=["POST"])
def download():
    url = request.form.get('url');
    resolution = request.form.get('resolution', None)
    
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
