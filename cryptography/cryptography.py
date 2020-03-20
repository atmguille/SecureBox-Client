from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Signature import pkcs1_15
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from cryptography.exceptions import *

IV_LEN = 16


def rsa_generate_key(nbits: int = 2048) -> RsaKey:
    """
    Generates a Rsa Key of nbits
    :param nbits: number of bits of the key (2048 by default)
    :return: RsaKey
    """
    return RSA.generate(nbits)


def sign_message(message: bytes, key: RsaKey) -> bytes:
    """
    Signs a message with the specified key
    :param message: message to by signed
    :param key: key to use in signing
    :return: signed message
    """
    return pkcs1_15.new(key).sign(SHA256.new(message))


def verify_signature(message: bytes, sender_public_key: RsaKey) -> bytes:
    """
    Verifies if the message has a valid signature, raising SignatureNotAuthentic if not
    :param message: message to be verified
    :param sender_public_key: public key of the pretended sender
    :return: original message without signature if it is valid
    :raise: SignatureNotAuthentic if signature is not valid
    """
    signature = message[:sender_public_key.size_in_bytes()]  # Assume encryption has been done with same key size
    original_message = message[sender_public_key.size_in_bytes():]
    h = SHA256.new(original_message)
    verifier = pkcs1_15.new(sender_public_key)
    try:
        verifier.verify(h, signature)
        return original_message
    except ValueError:
        raise SignatureNotAuthentic


def encrypt_message(message: bytes, receiver_public_key: RsaKey, nbits: int = 256) -> bytes:
    """
    Encrypts a message using the hybrid scheme
    :param message: message to be encrypted
    :param receiver_public_key: destination public key
    :param nbits: number of bits of the symmetric key
    :return: IV + encrypted symmetric key + encrypted message
    """
    aes_key = get_random_bytes(nbits // 8)
    cipher_aes = AES.new(aes_key, AES.MODE_CBC)
    return cipher_aes.iv + _encrypt_aes_key(aes_key, receiver_public_key) + cipher_aes.encrypt(
        pad(message, AES.block_size))  # Padding have to be added in case the size does not fit in exact blocks


def _encrypt_aes_key(aes_key: bytes, receiver_public_key: RsaKey) -> bytes:
    """
    Encrypts symmetric key with the specified RsaKey
    :param aes_key: symmetric key to be encrypted
    :param receiver_public_key: RsaKey to encrypt the symmetric key
    :return: encrypted symmetric key
    """
    cipher_rsa = PKCS1_OAEP.new(receiver_public_key)
    return cipher_rsa.encrypt(aes_key)


def decrypt_message(message: bytes, key: RsaKey) -> bytes:
    """
    Decrypts message, using the specified key to decrypt symmetric key firs
    :param message: message with the following structure: IV + encrypted symmetric key + encrypted message
    :param key: RsaKey to decrypt symmetric key
    :return: decrypted message
    """
    iv = message[:IV_LEN]
    enc_aes_key = message[IV_LEN:IV_LEN + key.size_in_bytes()]  # Assume encryption has been done with same key size
    enc_message = message[IV_LEN + key.size_in_bytes():]

    cipher_rsa = PKCS1_OAEP.new(key)
    aes_key = cipher_rsa.decrypt(enc_aes_key)

    cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv)
    return unpad(cipher_aes.decrypt(enc_message), AES.block_size)  # Padding have to be removed
