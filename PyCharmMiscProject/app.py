from flask import Flask, render_template, request, send_file
import hashlib
import qrcode
import os

from cryptography.fernet import Fernet

application = Flask(__name__)

QR_FOLDER = "static/qrcode"

os.makedirs(QR_FOLDER, exist_ok=True)

# AES Key
key = Fernet.generate_key()
cipher = Fernet(key)


# =====================
# Caesar Cipher
# =====================

def caesar_encrypt(text, shift=3):
    result = ""

    for char in text:
        result += chr(ord(char) + shift)

    return result


# =====================
# Vigenere Cipher
# =====================

def vigenere_encrypt(text, key="KRIPTO"):
    result = ""

    key_index = 0

    for char in text:

        if char.isalpha():

            shift = ord(key[key_index %
                            len(key)].upper()) - 65

            if char.isupper():
                result += chr(
                    (ord(char)-65+shift)%26+65
                )

            else:
                result += chr(
                    (ord(char)-97+shift)%26+97
                )

            key_index += 1

        else:
            result += char

    return result


# =====================
# Home
# =====================

@application.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':

        nama = request.form['nama']

        caesar = caesar_encrypt(nama)

        vigenere = vigenere_encrypt(nama)

        sha256_hash = hashlib.sha256(
            nama.encode()
        ).hexdigest()

        aes_encrypt = cipher.encrypt(
            nama.encode()
        ).decode()

        # QR Code

        qr = qrcode.make(
            f"Nama:{nama}\nSHA256:{sha256_hash}"
        )

        qr_path = os.path.join(
            QR_FOLDER,
            "qr.png"
        )

        qr.save(qr_path)

        return render_template(
            "result.html",
            nama=nama,
            caesar=caesar,
            vigenere=vigenere,
            sha256=sha256_hash,
            aes=aes_encrypt,
            qr_path=qr_path
        )

    return render_template("index.html")


if __name__ == '__main__':
    application.run(
        host='0.0.0.0',
        port=5000
    )