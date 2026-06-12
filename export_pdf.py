import json
import hashlib
import qrcode
import os

from io import BytesIO
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

DATA_FILE="songs.json"

def generate_signed_pdf():

    with open(DATA_FILE,"r") as f:
        songs=json.load(f)

    data_string=json.dumps(
        songs,
        sort_keys=True
    )

    verify_url = (
    f"pemrograman-kriptografi-production-digitalmusic-syifa.up.railway.app/verify/{sha_signature}"
    )
    
    qr = qrcode.make(verify_url)
    
    qr_buffer=BytesIO()
    qr.save(qr_buffer)
    qr_buffer.seek(0)

    pdf_path="koleksi_lagu_signed.pdf"

    doc=SimpleDocTemplate(pdf_path)

    styles=getSampleStyleSheet()

    elements=[]

    elements.append(
        Paragraph(
            "Data Koleksi Lagu",
            styles["Title"]
        )
    )

    elements.append(Spacer(1,20))

    table_data=[
        [
            "Judul Lagu",
            "Penyanyi",
            "Negara",
            "Genre",
            "Tahun"
        ]
    ]

    for s in songs:

        table_data.append([
            s["judul"],
            s["penyanyi"],
            s["negara"],
            s["genre"],
            s["tahun"]
        ])

    table=Table(table_data)

    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#5546ff")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),1,colors.grey),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold")
    ]))

    elements.append(table)

    elements.append(Spacer(1,25))

    elements.append(
        Paragraph(
            f"<b>SHA-256:</b><br/>{sha_signature}",
            styles["BodyText"]
        )
    )

    elements.append(Spacer(1,20))

    qr_img=Image(qr_buffer, width=150, height=150)

    elements.append(qr_img)

    elements.append(Spacer(1,10))

    elements.append(
        Paragraph(
            "CEO Alunan Amerta",
            styles["BodyText"]
        )
    )

    elements.append(
        Paragraph(
            "Syifa Khoirunnisa",
            styles["Heading3"]
        )
    )

    elements.append(
        Paragraph(
            datetime.now().strftime(
                "%d-%m-%Y %H:%M:%S"
            ),
            styles["Italic"]
        )
    )

    doc.build(elements)

    return pdf_path
