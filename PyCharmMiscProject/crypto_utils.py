import hashlib
import base64

from cryptography.fernet import Fernet

# AES KEY
key = Fernet.generate_key()

cipher = Fernet(key)

def aes_encrypt(text):

    return cipher.encrypt(
        text.encode()
    ).decode()

def aes_decrypt(text):

    return cipher.decrypt(
        text.encode()
    ).decode()

def caesar_encrypt(text, shift=3):

    result = ""

    for char in text:

        if char.isalpha():

            start = ord('A') if char.isupper() else ord('a')

            result += chr(
                (ord(char)-start+shift)%26 + start
            )

        else:
            result += char

    return result

def vigenere_encrypt(text,key):

    result=""

    key=key.upper()

    j=0

    for char in text:

        if char.isalpha():

            shift=ord(key[j%len(key)])-65

            start=65 if char.isupper() else 97

            result+=chr(
                (ord(char)-start+shift)%26+start
            )

            j+=1

        else:
            result+=char

    return result

def sha_signature(data):

    return hashlib.sha256(
        data.encode()
    ).hexdigest()