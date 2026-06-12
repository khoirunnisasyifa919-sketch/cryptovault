from flask import Flask, render_template, request, redirect, url_for, send_file
import json
import os
from export_pdf import generate_signed_pdf

app = Flask(__name__)

DATA_FILE = "songs.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

def load_songs():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_songs(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/")
def index():
    songs = load_songs()
    return render_template("index.html", songs=songs)

@app.route("/add", methods=["GET","POST"])
def add_song():
    if request.method == "POST":

        songs = load_songs()

        songs.append({
            "judul": request.form["judul"],
            "penyanyi": request.form["penyanyi"],
            "negara": request.form["negara"],
            "genre": request.form["genre"],
            "tahun": request.form["tahun"]
        })

        save_songs(songs)

        return redirect("/")

    return render_template("add.html")

@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit_song(id):

    songs = load_songs()

    if request.method == "POST":

        songs[id] = {
            "judul": request.form["judul"],
            "penyanyi": request.form["penyanyi"],
            "negara": request.form["negara"],
            "genre": request.form["genre"],
            "tahun": request.form["tahun"]
        }

        save_songs(songs)

        return redirect("/")

    return render_template(
        "edit.html",
        song=songs[id],
        id=id
    )

@app.route("/delete/<int:id>")
def delete_song(id):

    songs = load_songs()

    songs.pop(id)

    save_songs(songs)

    return redirect("/")

@app.route("/preview")
def preview():

    songs = load_songs()

    return render_template(
        "preview.html",
        songs=songs
    )

@app.route("/export")
def export_pdf_route():

    pdf_path = generate_signed_pdf()

    return send_file(
        pdf_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="koleksi_lagu_signed.pdf"
    )
@app.route("/verify/<signature>")
def verify(signature):

    songs = load_songs()

    import hashlib
    import json

    current_hash = hashlib.sha256(
        json.dumps(
            songs,
            sort_keys=True
        ).encode()
    ).hexdigest()

    if signature == current_hash:
        return render_template(
            "verify.html",
            hash=signature
        )

    return render_template(
        "verify_error.html",
        hash=signature
    )

if __name__ == "__main__":
    app.run(debug=True)
