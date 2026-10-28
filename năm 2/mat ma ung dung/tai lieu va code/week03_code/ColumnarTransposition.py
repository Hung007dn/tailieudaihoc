import math

def transposition_encrypt(plaintext, key):
    """
    Encrypts the plaintext using a columnar transposition cipher.
    The plaintext is stripped of spaces, converted to uppercase, and padded with 'X' if needed.
    The key (alphabetic) determines the column order.
    Returns the ciphertext, the encryption matrix, and the column order.
    """
    # Remove spaces and convert to uppercase.
    
    plaintext = "".join(plaintext.split()).upper()
    num_cols = len(key)
    num_rows = math.ceil(len(plaintext) / num_cols)
    # Pad plaintext with 'X' to fill the matrix completely.
    padded = plaintext.ljust(num_cols * num_rows, 'X')
    
    # Fill the matrix row-wise.
    matrix = [list(padded[i * num_cols:(i + 1) * num_cols]) for i in range(num_rows)]
    
    # Determine the column order:
    # Sort indices by the corresponding letter in the key (using stable sort to preserve order for duplicates).
    key_order = sorted(range(len(key)), key=lambda i: (key[i].upper(), i))
    
    # Read columns in the sorted order to produce the ciphertext.
    ciphertext = ""
    for col in key_order:
        for row in matrix:
            ciphertext += row[col]
    
    return ciphertext, matrix, key_order

def transposition_decrypt(ciphertext, key):
    """
    Decrypts the ciphertext using a columnar transposition cipher.
    Returns the recovered plaintext, the decryption matrix, and the column order.
    """
    ciphertext = ciphertext.upper()
    num_cols = len(key)
    num_rows = len(ciphertext) // num_cols
    
    # Determine the same column order as used in encryption.
    key_order = sorted(range(len(key)), key=lambda i: (key[i].upper(), i))
    
    # Create an empty matrix.
    matrix = [[''] * num_cols for _ in range(num_rows)]
    
    # Fill the matrix column-by-column in the order given by key_order.
    pos = 0
    for col in key_order:
        for row in range(num_rows):
            matrix[row][col] = ciphertext[pos]
            pos += 1
    
    # Read the matrix row-wise to recover the plaintext.
    plaintext = ""
    for row in matrix:
        plaintext += "".join(row)
    
    return plaintext, matrix, key_order

def print_matrix(matrix):
    """
    Prints the given matrix row by row.
    """
    for row in matrix:
        print(" ".join(row))

def main():
    print("Columnar Transposition Cipher")
    plaintext = input("Enter the plaintext: ")
    key = input("Enter the transposition cipher key (alphabetic): ").strip()
    
    # Encrypt
    ciphertext, enc_matrix, key_order = transposition_encrypt(plaintext, key)
    print("\nEncryption Matrix:")
    print_matrix(enc_matrix)
    print("\nKey Order (column indices in sorted order):", key_order)
    print("\nCiphertext:")
    print(ciphertext)
    
    input("\nPress Enter to continue to decryption...")
    
    # Decrypt
    recovered_plaintext, dec_matrix, dec_key_order = transposition_decrypt(ciphertext, key)
    print("\nDecryption Matrix:")
    print_matrix(dec_matrix)
    print("\nRecovered Plaintext (with padding):")
    print(recovered_plaintext)

if __name__ == "__main__":
    main()
