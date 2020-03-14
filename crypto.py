from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Signature import pss
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from log import logger
from api.exceptions import *

log = logger.get_logger()


def rsa_generate_key(nbits=2048) -> RsaKey:
    return RSA.generate(nbits)


def save_key(key: RsaKey, user_id: str):
    with open(f"keys/{user_id}.pem", "wb") as f:
        f.write(key.export_key("PEM"))


def load_key(user_id: str) -> RsaKey:
    with open(f"keys/{user_id}.pem", "r") as f:
        return RSA.import_key(f.read())


def get_public_key(key: RsaKey) -> str:
    return key.publickey().export_key("PEM").decode("utf-8")


def sign_message(message, key: RsaKey):
    return pss.new(key).sign(SHA256.new(message))


def verify_signature(message, sender_public_key):
    signature = message[:sender_public_key.size_in_bytes()]  # Assume encryption has been done with same key size
    original_message = message[sender_public_key.size_in_bytes():]
    h = SHA256.new(original_message)
    verifier = pss.new(sender_public_key)
    try:
        verifier.verify(h, signature)
    except (ValueError, TypeError):
        raise SignatureNotAuthentic


def encrypt_message(message, receiver_public_key, nbits=256) -> bytes:
    aes_key = get_random_bytes(nbits // 8)
    cipher_aes = AES.new(aes_key, AES.MODE_CBC)
    return encrypt_aes_key(cipher_aes.iv + aes_key, receiver_public_key) + cipher_aes.encrypt(
        pad(message, AES.block_size))


def encrypt_aes_key(aes_key, receiver_public_key) -> bytes:
    cipher_rsa = PKCS1_OAEP.new(receiver_public_key)
    return cipher_rsa.encrypt(aes_key)


def decrypt_message(message, key: RsaKey):
    enc_aes_key = message[:key.size_in_bytes()]  # Assume encryption has been done with same key size
    enc_message = message[key.size_in_bytes():]

    cipher_rsa = PKCS1_OAEP.new(key)
    aes_key_and_iv = cipher_rsa.decrypt(enc_aes_key)
    iv = aes_key_and_iv[:16]  # IV is always 16 bytes long when encrypting with AES
    aes_key = aes_key_and_iv[16:]

    cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv)
    return unpad(cipher_aes.decrypt(enc_message), AES.block_size)


"""
data = b'message secret'
rsa_generate_key()
signature = sign_message(data)
enc_message = encrypt_message(signature + data, rsa_get_public_key())
print(enc_message)
orig_message = decrypt_message(enc_message)
print(orig_message)
verify_signature(orig_message, rsa_get_public_key())
"""
