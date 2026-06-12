import hashlib
import json
import time
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Table as RTTable

import qrcode


# ==========================================================
# HASH SHA-256 DATA LAGU
# ==========================================================

def calculate_songs_hash(songs):
    songs_data = []

    for s in songs:
        songs_data.append({
            'id': s['id'],
            'judul_lagu': s['judul_lagu'],
            'penyanyi': s['penyanyi'],
            'negara': s['negara'],
            'genre': s['genre'],
            'tahun': s['tahun']
        })

    songs_data.sort(key=lambda x: x['id'])

    serialized = json.dumps(
        songs_data,
        sort_keys=True,
        ensure_ascii=False
    )

    return hashlib.sha256(
        serialized.encode('utf-8')
    ).hexdigest()


# ==========================================================
# GENERATE PDF
# ==========================================================

def generate_pdf_buffer(songs, verify_url=None):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    story = []

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=20
    )

    story.append(
        Paragraph(
            "Koleksi Lagu Digital",
            title_style
        )
    )

    story.append(Spacer(1, 10))

    # ==========================================================
    # TABEL LAGU
    # ==========================================================

    data = [[
        "Judul Lagu",
        "Penyanyi",
        "Negara",
        "Genre",
        "Tahun"
    ]]

    for s in songs:
        data.append([
            s['judul_lagu'],
            s['penyanyi'],
            s['negara'],
            s['genre'],
            str(s['tahun'])
        ])

    table = Table(
        data,
        colWidths=[140, 120, 90, 80, 60]
    )

    table.setStyle(TableStyle([

        ('BACKGROUND', (0, 0), (-1, 0),
         colors.HexColor('#7c3aed')),

        ('TEXTCOLOR', (0, 0), (-1, 0),
         colors.whitesmoke),

        ('FONTNAME', (0, 0), (-1, 0),
         'Helvetica-Bold'),

        ('FONTSIZE', (0, 0), (-1, 0), 10),

        ('ALIGN', (0, 0), (-1, -1),
         'LEFT'),

        ('GRID', (0, 0), (-1, -1),
         0.5,
         colors.HexColor('#cbd5e1')),

        ('BACKGROUND', (0, 1), (-1, -1),
         colors.HexColor('#f8fafc')),

        ('TEXTCOLOR', (0, 1), (-1, -1),
         colors.HexColor('#334155'))

    ]))

    story.append(table)

    story.append(Spacer(1, 40))

    # ==========================================================
    # HASH SHA-256
    # ==========================================================

    sha256_hash = calculate_songs_hash(songs)

    story.append(
        Paragraph(
            "<b>SHA-256 Digital Signature</b>",
            styles['Heading3']
        )
    )

    story.append(
        Paragraph(
            sha256_hash,
            styles['Code']
        )
    )

    story.append(Spacer(1, 20))

    # ==========================================================
    # QR CODE VERIFIKASI
    # ==========================================================

    if not verify_url:
        verify_url = "http://127.0.0.1:5000/verify/token_example"

    qr_buffer = BytesIO()

    qr = qrcode.QRCode(
        version=5,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=25,
        border=8
    )

    qr.add_data(verify_url)
    qr.make(fit=True)

    qr_image = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    qr_image.save(
        qr_buffer,
        format='PNG'
    )

    qr_buffer.seek(0)

    qr_img = Image(
        qr_buffer,
        width=160,
        height=160
    )

    jabatan_style = ParagraphStyle(
        'Jabatan',
        fontName='Helvetica',
        fontSize=9,
        alignment=2,
        textColor=colors.HexColor('#64748b')
    )

    nama_style = ParagraphStyle(
        'Nama',
        fontName='Helvetica-Bold',
        fontSize=11,
        alignment=2,
        textColor=colors.HexColor('#1e293b')
    )

    ttd_content = [

        Paragraph(
            "Music Archive Manager",
            jabatan_style
        ),

        Spacer(1, 8),

        qr_img,

        Spacer(1, 8),

        Paragraph(
            "Digital Signature Authority",
            nama_style
        )
    ]

    ttd_table = RTTable(
        [[ttd_content]],
        colWidths=[180]
    )

    ttd_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))

    story.append(ttd_table)

    story.append(Spacer(1, 20))

    # ==========================================================
    # FOOTER
    # ==========================================================

    timestamp = time.strftime(
        "%Y-%m-%d %H:%M:%S",
        time.localtime()
    )

    footer_style = ParagraphStyle(
        'Footer',
        fontName='Helvetica-Oblique',
        fontSize=8,
        alignment=1,
        textColor=colors.HexColor('#94a3b8')
    )

    story.append(
        Paragraph(
            f"Dokumen Koleksi Lagu dibuat otomatis pada: {timestamp}",
            footer_style
        )
    )

    doc.build(story)

    buffer.seek(0)

    return buffer
