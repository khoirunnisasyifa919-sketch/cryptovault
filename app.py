from flask import Flask, render_template, request, redirect, url_for, flash, send_file, abort
import os
import sqlite3
import uuid
import base64
import time
import secrets
from io import BytesIO
import qrcode

from export_pdf import calculate_songs_hash, generate_pdf_buffer

app = Flask(**name**)
app.secret_key = os.environ.get(
'SECRET_KEY',
'music-collection-secret-key'
)

download_tokens = {}

if os.environ.get('VERCEL'):
    DATABASE = '/tmp/songs.db'
else:
    DATABASE = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'songs.db'
    )

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db_dir = os.path.dirname(DATABASE)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs(
            id TEXT PRIMARY KEY,
            judul_lagu TEXT NOT NULL,
            penyanyi TEXT NOT NULL,
            negara TEXT NOT NULL,
            genre TEXT NOT NULL,
            tahun INTEGER NOT NULL
        )
    ''')
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM songs")
    if cursor.fetchone()[0] == 0:
        sample_songs = [
            (
                str(uuid.uuid4()),
                "Perfect",
                "Ed Sheeran",
                "Inggris",
                "Pop",
                2017
            ),
            (
                str(uuid.uuid4()),
                "Shape of You",
                "Ed Sheeran",
                "Inggris",
                "Pop",
                2017
            ),
            (
                str(uuid.uuid4()),
                "Hati-Hati di Jalan",
                "Tulus",
                "Indonesia",
                "Pop",
                2022
            )
        ]
        cursor.executemany(
            '
            INSERT INTO songs
            (id, judul_lagu, penyanyi, negara, genre, tahun)
            VALUES (?, ?, ?, ?, ?, ?)
            ',
            sample_songs
        )
        conn.commit()
    conn.close()

init_db()

def generate_download_token():
    """Generate token unik untuk download"""
    return secrets.token_urlsafe(32)

@app.route('/')
def index():
    conn = get_db()
    songs = conn.execute('SELECT * FROM songs').fetchall()
    conn.close()
    return render_template('index.html',songs=songs)

@app.route('/add', methods=['GET', 'POST'])
def add_song():
    if request.method == 'POST':
        judul_lagu = request.form.get('judul_lagu','').strip()
        penyanyi = request.form.get('penyanyi','').strip()
        negara = request.form.get('negara','').strip()
        genre = request.form.get('genre','').strip()
        tahun = request.form.get('tahun','').strip()

         if not judul_lagu or not penyanyi or not negara or not genre or not tahun:
             flash('Semua field harus diisi!', 'danger')
             return redirect(url_for('add_song'))
        
        songs_id = str(uuid.uuid4())
        
        try:
            conn = get_db()
            conn.execute('INSERT INTO songs (id, judul_lagu, penyanyi, negara, genre, tahun) VALUES (?, ?, ?, ?, ?, ?)',(judul_lagu, penyanyi, negara, genre, tahun))
            conn.commit()
            conn.close()
            flash('Lagu berhasil ditambahkan!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Gagal menambahkan lagu {str(e)}', 'danger')
            return redirect(url_for('add_song'))
    
    return render_template('add.html')


@app.route('/edit/<song_id>', methods=['GET', 'POST'])
def edit_song(song_id):
    conn = get_db()
    song = conn.execute('SELECT * FROM songs WHERE id=?',(song_id,)).fetchone()
    conn.close()
    
    if not song:
        flash('Lagu tidak ditemukan!', 'danger')
        return redirect(url_for('index'))

    
    if request.method == 'POST':
        judul_lagu = request.form.get('judul_lagu','').strip()
        penyanyi = request.form.get('penyanyi','').strip()
        negara = request.form.get('negara','').strip()
        genre = request.form.get('genre','').strip()
        tahun = request.form.get('tahun','').strip()

        if not judul_lagu or not penyanyi or not negara or not genre or not tahun:
            flash('Semua field harus diisi!', 'danger')
            return redirect(url_for('edit_song', song_id=song_id'))
        try:
            conn.execute('
            UPDATE songs
            SET
            judul_lagu=?,
            penyanyi=?,
            negara=?,
            genre=?,
            tahun=?
            WHERE id=?',
            (judul_lagu, penyanyi, negara, genre,tahun, song_id))
            conn.commit()
            conn.close()
            flash("Data lagu berhasil diperbarui", "success")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Gagal memperbarui lagu: {str(e)}', 'danger')
            return redirect(url_for('edit_song', song_id=song_id))
    
    return render_template('edit.html', song=song)
  

@app.route('/delete/<song_id>', methods=['POST'])
def delete_song(song_id):
    try:
        conn = get_db()
        conn.execute('DELETE FROM songs WHERE id=?', (song_id,))
        conn.commit()
        conn.close()
        flash("Lagu berhasil dihapus", "success")
    except Exception as e:
        flash(f'Gagal menghapus lagu: {str(e)}', 'danger')
    
    return redirect(url_for('index'))


@app.route('/export')
def preview_export():
    try:
        conn = get_db()
        songs = conn.execute('SELECT * FROM songs').fetchall()
        conn.close()
        if not songs:
            flash('Tidak ada data lagu untuk diexport!', 'danger')
            return redirect(url_for('index'))

        songs_list = [dict(x) for x in songs]
        doc_hash = calculate_songs_hash(songs_list)

        token = generate_download_token()

        download_tokens[token] = {
            'songs': songs_list,
            'hash': doc_hash,
            'timestamp': time.time()
        }

        base_url = request.host_url.rstrip('/')
        qr_url = f"{base_url}/verify/{token}"

        qr = qrcode.QRCode(
            version=5,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4
        )
        
        qr.add_data(qr_url)
        qr.make(fit=True)
        qr_img = qr.make_image()
        qr_buffer = BytesIO()
        qr_img.save(
            qr_buffer,
            format='PNG'
        )
        
        qr_base64 = base64.b64encode(
            qr_buffer.getvalue()
        ).decode()
        
        return render_template(
            'preview.html',
            songs=songs_list,
            qr_base64=qr_base64,
            qr_url=qr_url,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )

@app.route('/verify/<token>')
def verify_document(token):

    data = download_tokens.get(token)
    
    if not data:
        return render_template(
            'verify_error.html'
        ), 404
    
    songs = data['songs']
    
    saved_hash = data['hash']
    
    current_hash = calculate_songs_hash(
        songs
    )
    
    is_valid = (
        saved_hash == current_hash
    )
    
    return render_template(
        'verify.html',
        songs=songs,
        doc_hash=saved_hash,
        is_valid=is_valid,
        timestamp=time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(data['timestamp'])
        )
    )


@app.route('/download/<token>')
def download_from_token(token):

    data = download_tokens.get(token)
    
    if not data:
        abort(404)
    
    pdf_buffer = generate_pdf_buffer(
        data['songs']
    )
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='koleksi_lagu_signed.pdf'
    )


@app.route('/export/download')
def download_pdf():
    try:
        conn = get_db()
        songs = conn.execute(
            "SELECT * FROM songs"
        ).fetchall()
        
        conn.close()
        
        songs_list = [dict(x) for x in songs]
        
        base_url = request.host_url.rstrip('/')
        
        pdf_buffer = generate_pdf_buffer(
            songs_list,
            verify_url=f"{base_url}/verify/example"
        )
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='koleksi_lagu_signed.pdf'
        )


if __name__ == '__main__':
    app.run(
    debug=True,
    port=5000
    )
