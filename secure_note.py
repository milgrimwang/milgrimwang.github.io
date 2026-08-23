#!/usr/bin/env python
import os

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from jinja2 import Environment, FileSystemLoader

# Constants
PBKDF2_COUNT = 100000
SALT_LEN = 16
ENCRYPTION_KEY_LEN = 32
TEMPLATE_FILE = "secure.tpl.html"

# Env vars
NOTE_TITLE = os.environ["NOTE_TITLE"]
NOTE_FILE = os.environ["NOTE_FILE"]
NOTE_PASSWORD = os.environ["NOTE_PASSWORD"].encode()
NOTE_TEXT = os.environ["NOTE_TEXT"].encode()


def main(password, plain_text):
    salt = get_random_bytes(SALT_LEN)
    encryption_key = PBKDF2(password, salt, dkLen=ENCRYPTION_KEY_LEN, count=PBKDF2_COUNT, hmac_hash_module=SHA256)
    cipher = AES.new(encryption_key, AES.MODE_GCM)
    cipher_text, tag = cipher.encrypt_and_digest(plain_text)
    cipher_text += tag

    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template(TEMPLATE_FILE)
    with open(f"{NOTE_FILE}.html", "w") as index_file:
        index_file.write(template.render(
            title=NOTE_TITLE,
            salt=list(salt),
            iv=list(cipher.nonce),
            iterations=PBKDF2_COUNT,
            encrypted=list(cipher_text),
        ))


if __name__ == "__main__":
    main(NOTE_PASSWORD, NOTE_TEXT)
