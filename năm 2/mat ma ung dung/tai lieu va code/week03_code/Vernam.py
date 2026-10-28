import os
import binascii
from collections import Counter

def vernam_encrypt(plaintext, key):
    """
    Encrypts the plaintext using the Vernam cipher (one-time pad) by XORing each byte.
    The key must be at least as long as the plaintext.
    Returns the ciphertext as a hexadecimal string.
    """
    if len(key) < len(plaintext):
        raise ValueError("Key must be at least as long as plaintext.")
    plaintext_bytes = plaintext.encode('utf-8')
    ciphertext = bytearray()
    for p, k in zip(plaintext_bytes, key):
        ciphertext.append(p ^ k)  # XOR bytes
    return binascii.hexlify(ciphertext).decode('utf-8')

def vernam_decrypt(ciphertext_hex, key):
    """
    Decrypts the ciphertext (given as a hexadecimal string) using the Vernam cipher.
    Returns the plaintext string.
    """
    ciphertext = binascii.unhexlify(ciphertext_hex)
    plaintext = bytearray()
    for c, k in zip(ciphertext, key):
        plaintext.append(c ^ k)
    return plaintext.decode('utf-8')

def generate_random_key(length):
    """
    Generates a random key (bytes) of the given length.
    """
    return os.urandom(length)

def main():
    plaintext = input("Enter the plaintext: ")
    print(f"plaintext length (bytes): {len(plaintext)}")
    
    # Generate a random key of the same length as the plaintext.
    key = generate_random_key(len(plaintext))
    
    # Print the key (as a hexadecimal string)
    key_hex = binascii.hexlify(key).decode('utf-8')
    print("\nKey (hex):")
    print(key_hex)
    print(f"key length (bytes): {len(key)}")
    
    ciphertext = vernam_encrypt(plaintext, key)
    print("\nCiphertext (hex):")
    print(ciphertext)
    
    # --- New Block: Print Byte Frequency of Ciphertext ---
    # Convert ciphertext (hex) back to bytes and count frequencies.
    ciphertext_bytes = binascii.unhexlify(ciphertext)
    byte_freq = Counter(ciphertext_bytes)
    print("\nByte Frequency in Ciphertext:")
    for byte, count in sorted(byte_freq.items()):
        # Print byte in 2-digit hex format.
        print(f"{byte:02x}: {count}")
    
    input("\nPress Enter to continue to decryption...")
    
    decrypted_text = vernam_decrypt(ciphertext, key)
    print("\nDecrypted text:")
    print(decrypted_text)

if __name__ == "__main__":
    main()
