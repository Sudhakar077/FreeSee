from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify, abort
import os, sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024 * 1024

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DB = os.path.join(BASE_DIR, "freesee.db")
ALLOWED = {"mp4", "webm", "ogg", "mov", "m4v"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    con.execute("""CREATE TABLE IF NOT EXISTS videos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        category TEXT DEFAULT 'General',
        filename TEXT NOT NULL,
        views INTEGER DEFAULT 0
    )""")
    count = con.execute("SELECT COUNT(*) FROM videos").fetchone()[0]
    if count == 0:
        demo = [
            ("Welcome to FreeSee", "Your video streaming platform.", "Featured", "demo.mp4"),
            ("Trending Video", "Add your own videos from the upload page.", "Trending", "demo.mp4"),
        ]
        for row in demo:
            # Demo entries are intentionally not inserted because demo.mp4 does not exist.
            pass
    con.commit()
    con.close()

# Fix demo insertion cleanly if database is created for the first time.
def safe_init():
    con = db()
    con.execute("""CREATE TABLE IF NOT EXISTS videos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        category TEXT DEFAULT 'General',
        filename TEXT NOT NULL,
        views INTEGER DEFAULT 0
    )""")
    con.commit()
    con.close()

@app.route("/")
def home():
    con = db()
    videos = con.execute("SELECT * FROM videos ORDER BY id DESC").fetchall()
    con.close()
    return render_template("index.html", videos=videos)

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "General").strip()
        video = request.files.get("video")

        if not title or not video or not video.filename:
            return render_template("upload.html", error="Title and video are required.")

        ext = video.filename.rsplit(".", 1)[-1].lower() if "." in video.filename else ""
        if ext not in ALLOWED:
            return render_template("upload.html", error="Allowed formats: MP4, WebM, OGG, MOV, M4V.")

        filename = secure_filename(video.filename)
        stem, extension = os.path.splitext(filename)
        i = 1
        while os.path.exists(os.path.join(UPLOAD_FOLDER, filename)):
            filename = f"{stem}_{i}{extension}"
            i += 1

        video.save(os.path.join(UPLOAD_FOLDER, filename))
        con = db()
        con.execute(
            "INSERT INTO videos(title,description,category,filename) VALUES(?,?,?,?)",
            (title, description, category, filename)
        )
        con.commit()
        con.close()
        return redirect(url_for("home"))

    return render_template("upload.html")

@app.route("/video/<int:video_id>")
def watch(video_id):
    con = db()
    video = con.execute("SELECT * FROM videos WHERE id=?", (video_id,)).fetchone()
    if not video:
        con.close()
        abort(404)
    con.execute("UPDATE videos SET views=views+1 WHERE id=?", (video_id,))
    con.commit()
    con.close()
    return render_template("watch.html", video=video)

@app.route("/media/<path:filename>")
def media(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, conditional=True)

@app.route("/api/videos")
def api_videos():
    con = db()
    rows = [dict(r) for r in con.execute("SELECT * FROM videos ORDER BY id DESC").fetchall()]
    con.close()
    return jsonify(rows)

if __name__ == "__main__":
    safe_init()
    app.run(debug=True, host="127.0.0.1", port=5000)
