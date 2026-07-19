import os, re
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidTag

NONCE_SIZE = 12 # Recommended size for GCM mode
TAG_SIZE = 16 # Recommended size for GCM mode
SALT_SIZE = 16 # Recommended size for PBKDF2
METHOD_SIZE = 1 # Size to store the key size used during encryption (1 byte is enough to store 16 or 32)
ITERATIONS = 300_000 # Recommended number of iterations for PBKDF2
VALID_KEY_SIZES = (16, 32) # Valid key sizes for AES (16 bytes for AES-128, 32 bytes for AES-256)
MIN_LENGTH = METHOD_SIZE + NONCE_SIZE + TAG_SIZE + SALT_SIZE # Minimum length of the encrypted message (method + nonce + tag + salt + ciphertext)

def aes_encrypt(message: str, password: str, key_size: int) -> bytes:
    # Pre: A string that contains the clear message, the password to derive the key and the key_size (16 - 128, 32 -256)
    # Post: The encrypted message, the key used during encryption, the nonce to ensure that two messages with the same key generate different ciphertexts, the authentication tag and the salt to derive the key
    if not message:
        raise ValueError("Message cannot be empty")
    if not password:
        raise ValueError("A password is required")
    if key_size not in (16, 32):
        raise ValueError("Key size incorrect")

    passwordComplexity(password)

    # Key is derived from the password
    key, salt = derive_key(password, key_size=key_size)
    # Nonce set as recommended (generated from a secure random number generation function)
    nonce = os.urandom(NONCE_SIZE)

    # Encrypt the message
    return encrypt_aes_aux(key, nonce, message, salt, key_size)

def aes_decrypt(data: bytes, password: str) -> str:
    # Pre: The encrypted message, the salt to obtain the key used during encryption, the nonce to ensure that two messages with the same key generate different ciphertexts, the authentication tag, the password and the key_size
    # Post: A string that contains the clear message
    if len(data) < MIN_LENGTH:
        raise ValueError("Ciphertext too short")
    if not data:
        raise ValueError("There is no text")
    if not password:
        raise ValueError("A password is required")

    # Extract the method, nonce, tag, salt and ciphertext from the data
    method = data[:METHOD_SIZE]
    offset = METHOD_SIZE
    
    # Extract the nonce, tag, salt and ciphertext from the data
    nonce = data[offset:offset + NONCE_SIZE]
    offset += NONCE_SIZE

    tag = data[offset:offset + TAG_SIZE]
    offset += TAG_SIZE

    salt = data[offset:offset + SALT_SIZE]
    offset += SALT_SIZE

    ciphertext = data[offset:]
    
    if not salt:
        raise ValueError("Salt is not defined")
    if not nonce:
        raise ValueError("Nonce is not defined")
    if not tag:
        raise ValueError("Tag is not defined")
    if not method:
        raise ValueError("Method is not defined")

    key_size = method[0]

    if key_size not in VALID_KEY_SIZES:
        raise ValueError("Invalid key size")
    
    key, _ = derive_key(password, salt, key_size)

    # Decrypt the message
    plaintext = decrypt_aes_aux(key, nonce, ciphertext, tag)
    return plaintext.decode()

def encrypt_aes_aux(key: bytes, nonce: bytes, message: str, salt: bytes, key_size: int) -> bytes:
    # Pre: The encryption key, the nonce, the clear message and the salt used to obtain the key
    # Post: The message encrypted, the key used, the nonce and the salt
    
    # Encrypted in GCM mode depending on the key size used
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(message.encode()) + encryptor.finalize()

    tag = encryptor.tag
    method = key_size.to_bytes(METHOD_SIZE, "big")

    return method+nonce+tag+salt+ciphertext

def decrypt_aes_aux(key: bytes, nonce: bytes, ciphertext: bytes, tag: bytes) -> bytes:
    # Pre: The key to decrypt, the nonce, the message encrypted and the tag 
    # Post: The clear message
    
    # Decrypted in GCM mode depending on the key size used
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag))
    decryptor = cipher.decryptor()

    try:
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext
    except InvalidTag:
        raise ValueError("Authentication failed")

def derive_key(password: str, salt: bytes = None, key_size: int = 16) -> tuple:
    # Pre: The password to derive the key, the salt (if empty we're creating the key, otherwise we're obtaining the one used) and the key_size
    # Post: The key (to be used to encrypt/decrypt) and the salt (to generate the key by combining it with the password)
    
    # Generate a random salt if it isn't set (generated from a secure random number generation function)
    if salt is None:
        salt = os.urandom(SALT_SIZE)

    # Defined parameters to obtain key
    kdf = PBKDF2HMAC(
        algorithm= hashes.SHA256(),
        length= key_size,
        salt= salt,
        iterations= ITERATIONS
    )
    
    # Key derived from the password
    key = kdf.derive(password.encode())
    return key, salt

def passwordComplexity(password: str):
    # Pre: The password that will be verified
    # Post: --

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter")

    if not re.search(r"[0-9]", password):
        raise ValueError("Password must contain at least one digit")

