from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import hashlib
import barcode
import qrcode
from barcode.writer import ImageWriter
from reportlab.platypus import Image
import os
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.lib import colors
from reportlab.platypus import Spacer
import io
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================
# MODEL
# ==========================

class Buku(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(200))
    penulis = db.Column(db.String(200))
    penerbit = db.Column(db.String(200))

with app.app_context():
    db.create_all()

# ==========================
# SHA256 SIGNATURE
# ==========================

def generate_signature():
    semua_buku = Buku.query.all()

    data = ""

    for buku in semua_buku:
        data += buku.judul
        data += buku.penulis
        data += buku.penerbit

    return hashlib.sha256(data.encode()).hexdigest()

def generate_barcode(signature):

    os.makedirs("static/barcode", exist_ok=True)

    code128 = barcode.get(
        "code128",
        signature,
        writer=ImageWriter()
    )

    filename = f"static/barcode/{signature}"

    code128.save(filename)

    return filename + ".png"

def generate_qr(signature):

    os.makedirs("static/qr", exist_ok=True)

    filename = f"static/qr/{signature}.png"

    qr = qrcode.make(signature)

    qr.save(filename)

    return filename


# ==========================
# HOME
# ==========================

@app.route('/')
def index():
    buku = Buku.query.all()

    return render_template(
        'index.html',
        buku=buku,
        total=len(buku)
    )

# ==========================
# TAMBAH
# ==========================

@app.route('/tambah', methods=['GET','POST'])
def tambah():

    if request.method == 'POST':

        buku = Buku(
            judul=request.form['judul'],
            penulis=request.form['penulis'],
            penerbit=request.form['penerbit']
        )

        db.session.add(buku)
        db.session.commit()

        return redirect('/')

    return render_template('tambah.html')

# ==========================
# EDIT
# ==========================

@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):

    buku = Buku.query.get_or_404(id)

    if request.method == 'POST':

        buku.judul = request.form['judul']
        buku.penulis = request.form['penulis']
        buku.penerbit = request.form['penerbit']

        db.session.commit()

        return redirect('/')

    return render_template('edit.html', buku=buku)

# ==========================
# HAPUS
# ==========================

@app.route('/hapus/<int:id>')
def hapus(id):

    buku = Buku.query.get_or_404(id)

    db.session.delete(buku)
    db.session.commit()

    return redirect('/')

# ==========================
# EXPORT PDF
# ==========================

@app.route('/export')
def export_pdf():

    buffer = io.BytesIO()

    pdf = SimpleDocTemplate(buffer)

    data = [
        ['Judul', 'Penulis', 'Penerbit']
    ]

    buku = Buku.query.all()

    for b in buku:

        data.append([
            b.judul,
            b.penulis,
            b.penerbit
        ])

    signature = generate_signature()

    tabel = Table(data)

    tabel.setStyle([
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey)
    ])

    barcode_file = generate_barcode(signature)

    barcode_img = Image(
        barcode_file,
        width=350,
        height=80
    )

    qr_file = generate_qr(signature)

    qr_img = Image(
        qr_file,
        width=120,
        height=120
    )

    signature_table = Table([
        ["SHA-256 Signature"],
        [signature]
    ])

    signature_table.setStyle([
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey)
    ])

    elements = [
        tabel,
        Spacer(1, 20),
        signature_table,
        Spacer(1, 20),
        barcode_img,
        Spacer(1, 20),
        qr_img
    ]

    pdf.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name='data_buku_signed.pdf',
        mimetype='application/pdf'
    )


if __name__ == "__main__":
    app.run(debug=True)
