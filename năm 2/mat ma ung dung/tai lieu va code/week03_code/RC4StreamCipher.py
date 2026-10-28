import os
import binascii

def generate_rc4_key(length=16):
    """
    Generates a random key (bytes) for RC4.
    By default, 16 bytes (128 bits) are returned.
    """
    return os.urandom(length)

def rc4_crypt(key: bytes, data: bytes) -> bytes:
    """
    Encrypts or decrypts data using the RC4 stream cipher with the given key.
    (Encryption and decryption are identical for RC4.)
    """
    # RC4 Key Scheduling Algorithm (KSA)
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    
    # RC4 Pseudo-Random Generation Algorithm (PRGA)
    result = bytearray()
    i = 0
    j = 0
    for byte in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        keystream_byte = S[(S[i] + S[j]) % 256]
        result.append(byte ^ keystream_byte)
    
    return bytes(result)

def main():
    print("=== RC4 DEMO ===")
    
    # Generate a random key (16 bytes by default)
    key = generate_rc4_key()
    print("Generated RC4 key (hex):", binascii.hexlify(key).decode())

    # Input plaintext (UTF-8)
    plaintext = input("Enter plaintext to encrypt: ")
    plaintext_bytes = plaintext.encode('utf-8')

    # Encrypt
    ciphertext = rc4_crypt(key, plaintext_bytes)
    print("\nCiphertext (hex):", ciphertext.hex())

    # Decrypt (same function)
    decrypted_bytes = rc4_crypt(key, ciphertext)
    decrypted_text = decrypted_bytes.decode('utf-8', errors='replace')
    print("\nDecrypted text:", decrypted_text)

if __name__ == "__main__":
    main()
