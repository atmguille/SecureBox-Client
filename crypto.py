from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Signature import pkcs1_15
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from api.exceptions import *

IV_LEN = 16

def rsa_generate_key(nbits=2048) -> RsaKey:
    return RSA.generate(nbits)

def rsa_generate_key(nbits=2048) -> RsaKey:
    return RSA.generate(nbits)

def sign_message(message, key: RsaKey):
    return pkcs1_15.new(key).sign(SHA256.new(message))

def sign_message(message, key: RsaKey):
    return pkcs1_15.new(key).sign(SHA256.new(message))


def verify_signature(message, sender_public_key):
    signature = message[:sender_public_key.size_in_bytes()]  # Assume encryption has been done with same key size
    original_message = message[sender_public_key.size_in_bytes():]
    h = SHA256.new(original_message)
    verifier = pkcs1_15.new(sender_public_key)
    try:
        verifier.verify(h, signature)
        return original_message
    except (ValueError, TypeError):
        raise SignatureNotAuthentic


def encrypt_message(message, receiver_public_key, nbits=256) -> bytes:
    aes_key = get_random_bytes(nbits // 8)
    cipher_aes = AES.new(aes_key, AES.MODE_CBC)
    return cipher_aes.iv + _encrypt_aes_key(aes_key, receiver_public_key) + cipher_aes.encrypt(
        pad(message, AES.block_size))


def _encrypt_aes_key(aes_key, receiver_public_key) -> bytes:
    cipher_rsa = PKCS1_OAEP.new(receiver_public_key)
    return cipher_rsa.encrypt(aes_key)


def decrypt_message(message, key: RsaKey):
    iv = message[:IV_LEN]
    enc_aes_key = message[IV_LEN:IV_LEN + key.size_in_bytes()]  # Assume encryption has been done with same key size
    enc_message = message[IV_LEN + key.size_in_bytes():]

    cipher_rsa = PKCS1_OAEP.new(key)
    aes_key = cipher_rsa.decrypt(enc_aes_key)

    cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv)
    return unpad(cipher_aes.decrypt(enc_message), AES.block_size)