from flask import *
from models import *
from crypto_utils import *

import qrcode
import os
import datetime

from reportlab.pdfgen import canvas

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = \
"sqlite:///database.db"

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def index():

    data = Message.query.all()

    return render_template(
        "index.html",
        data=data
    )

@app.route("/add",methods=["GET","POST"])
def add():

    if request.method=="POST":

        text=request.form["text"]

        algo=request.form["algo"]

        key=request.form.get("key","")

        if algo=="AES":
            encrypted=aes_encrypt(text)

        elif algo=="Caesar":
            encrypted=caesar_encrypt(text)

        else:
            encrypted=vigenere_encrypt(
                text,
                key
            )

        signature=sha_signature(encrypted)

        qr=qrcode.make(encrypted)

        qr_name=f"static/qr/{signature}.png"

        qr.save(qr_name)

        msg=Message(
            plain_text=text,
            encrypted_text=encrypted,
            algorithm=algo,
            signature=signature,
            qr_path=qr_name,
            created_at=datetime.datetime.now()
        )

        db.session.add(msg)

        db.session.commit()

        return redirect("/")

    return render_template("add.html")

@app.route("/delete/<int:id>")
def delete(id):

    msg=Message.query.get(id)

    db.session.delete(msg)

    db.session.commit()

    return redirect("/")

@app.route("/pdf/<int:id>")
def pdf(id):

    msg=Message.query.get(id)

    filename=f"static/pdf/{id}.pdf"

    c=canvas.Canvas(filename)

    c.drawString(100,800,"CryptoVault Report")

    c.drawString(
        100,
        760,
        msg.plain_text
    )

    c.drawString(
        100,
        720,
        msg.encrypted_text
    )

    c.drawString(
        100,
        680,
        msg.signature
    )

    c.save()

    return send_file(
        filename,
        as_attachment=True
    )

if __name__=="__main__":
    app.run(debug=True)