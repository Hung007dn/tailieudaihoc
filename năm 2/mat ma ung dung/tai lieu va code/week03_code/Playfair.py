import string
from collections import Counter

def create_key_square(keyword):
    """
    Given a keyword, constructs a 5x5 key square for the Playfair cipher.
    The letters I and J are merged (J is replaced by I).
    """
    # Remove non-letters, convert to uppercase, and replace J with I.
    keyword = "".join([char.upper() for char in keyword if char.isalpha()]).replace("J", "I")
    
    # Create an ordered list of characters from the keyword, preserving order.
    seen = set()
    key_letters = []
    for char in keyword:
        if char not in seen:
            seen.add(char)
            key_letters.append(char)
    
    # Append the rest of the alphabet (without J).
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # Note: J is omitted.
    for char in alphabet:
        if char not in seen:
            key_letters.append(char)
    
    # Build the 5x5 matrix.
    key_square = [key_letters[i*5:(i+1)*5] for i in range(5)]
    return key_square

def print_key_square(key_square):
    """
    Prints the 5x5 key square.
    """
    print("Playfair Key Square:")
    for row in key_square:
        print(" ".join(row))
        
def get_position(key_square):
    """
    Returns a dictionary mapping each letter to its (row, col) position.
    Letters I and J share the same position.
    """
    pos = {}
    for row_idx, row in enumerate(key_square):
        for col_idx, letter in enumerate(row):
            pos[letter] = (row_idx, col_idx)
    return pos

def preprocess_text(text, for_encryption=True):
    """
    Preprocesses the text:
      - Removes non-alphabetic characters.
      - Converts to uppercase.
      - Replaces J with I.
    If for_encryption is True, also splits into digraphs and inserts 'X' as needed.
    """
    text = "".join([char.upper() for char in text if char.isalpha()]).replace("J", "I")
    if not for_encryption:
        return text
    
    # Split into digraphs, inserting 'X' between identical letters.
    digraphs = []
    i = 0
    while i < len(text):
        letter1 = text[i]
        if i+1 < len(text):
            letter2 = text[i+1]
            if letter1 == letter2:
                # If both letters are same, insert X after the first letter.
                digraphs.append(letter1 + "X")
                i += 1
            else:
                digraphs.append(letter1 + letter2)
                i += 2
        else:
            # If only one letter remains, pad with X.
            digraphs.append(letter1 + "X")
            i += 1
    return digraphs

def playfair_encrypt(plaintext, key_square):
    """
    Encrypts plaintext using the Playfair cipher and the provided key square.
    """
    pos = get_position(key_square)
    digraphs = preprocess_text(plaintext, for_encryption=True)
    ciphertext = ""
    
    for pair in digraphs:
        a, b = pair[0], pair[1]
        row1, col1 = pos[a]
        row2, col2 = pos[b]
        if row1 == row2:
            # Same row: shift columns to right (wrap-around)
            ciphertext += key_square[row1][(col1+1)%5]
            ciphertext += key_square[row2][(col2+1)%5]
        elif col1 == col2:
            # Same column: shift rows down (wrap-around)
            ciphertext += key_square[(row1+1)%5][col1]
            ciphertext += key_square[(row2+1)%5][col2]
        else:
            # Rectangle: swap columns.
            ciphertext += key_square[row1][col2]
            ciphertext += key_square[row2][col1]
    
    return ciphertext

def playfair_decrypt(ciphertext, key_square):
    """
    Decrypts ciphertext using the Playfair cipher and the provided key square.
    """
    pos = get_position(key_square)
    # Process ciphertext in pairs.
    digraphs = [ciphertext[i:i+2] for i in range(0, len(ciphertext), 2)]
    plaintext = ""
    
    for pair in digraphs:
        a, b = pair[0], pair[1]
        row1, col1 = pos[a]
        row2, col2 = pos[b]
        if row1 == row2:
            # Same row: shift columns to left (wrap-around)
            plaintext += key_square[row1][(col1-1)%5]
            plaintext += key_square[row2][(col2-1)%5]
        elif col1 == col2:
            # Same column: shift rows up (wrap-around)
            plaintext += key_square[(row1-1)%5][col1]
            plaintext += key_square[(row2-1)%5][col2]
        else:
            # Rectangle: swap columns.
            plaintext += key_square[row1][col2]
            plaintext += key_square[row2][col1]
    
    return plaintext

def count_cipher_frequencies(text):
    """
    Counts the frequencies of alphabetic characters in the given text (ignoring case).
    Returns a list of tuples sorted by descending frequency.
    """
    letters = ''.join(filter(str.isalpha, text.upper()))
    counts = Counter(letters)
    return counts.most_common()

def main():
    print("Playfair Cipher")
    key = input("Enter the keyword: ").strip()
    key_square = create_key_square(key)
    print_key_square(key_square)
    
    plaintext = input("\nEnter the plaintext: ")
    encrypted_text = playfair_encrypt(plaintext, key_square)
    print("\nEncrypted Text:")
    print(encrypted_text)
    
    # Count and display ciphertext letter frequencies.
    freqs = count_cipher_frequencies(encrypted_text)
    print("\nCiphertext Letter Frequencies (most common first):")
    for letter, count in freqs:
        print(f"{letter}: {count}")
    
    input("\nPress Enter to continue to decryption...")
    
    decrypted_text = playfair_decrypt(encrypted_text, key_square)
    print("\nDecrypted Text:")
    print(decrypted_text)

if __name__ == "__main__":
    main()
