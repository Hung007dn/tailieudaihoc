def rail_fence_encrypt(plaintext, rails):
    """
    Encrypts the plaintext (including spaces) using the Rail Fence Cipher with the given number of rails.
    Returns the ciphertext as a string of the same length as plaintext.
    Also prints the zigzag pattern in a column-aligned table.
    """
    if rails <= 1:
        return plaintext

    n = len(plaintext)
    # Create a matrix (rails x n), filling unoccupied spots with None (not a space).
    fence_matrix = [[None for _ in range(n)] for _ in range(rails)]

    # Zigzag placement of characters
    row = 0
    direction = 1  # +1 means moving "down", -1 means moving "up"
    for col, char in enumerate(plaintext):
        fence_matrix[row][col] = char
        row += direction
        if row == 0 or row == rails - 1:
            direction *= -1

    # --- Print the zigzag table (align columns) ---
    print("Rail Fence Structure (as a table):")
    # Use a fixed width (e.g. 3) to align columns
    for r in range(rails):
        row_str = []
        for c in range(n):
            val = fence_matrix[r][c]
            if val is None:
                row_str.append("   ")   # empty cell
            else:
                row_str.append(f"{val:^3}")  # center the actual character
        print("".join(row_str))
    print()

    # Gather ciphertext by reading row by row, ignoring None
    ciphertext_chars = []
    for r in range(rails):
        for c in range(n):
            if fence_matrix[r][c] is not None:
                ciphertext_chars.append(fence_matrix[r][c])

    return "".join(ciphertext_chars)

def rail_fence_decrypt(ciphertext, rails):
    """
    Decrypts the ciphertext produced by the above Rail Fence Cipher (including spaces) with the given number of rails.
    Returns the recovered plaintext, which should match the original plaintext exactly.
    """
    if rails <= 1:
        return ciphertext

    n = len(ciphertext)
    # First, create a matrix of None
    fence_matrix = [[None for _ in range(n)] for _ in range(rails)]

    # Mark zigzag positions with a placeholder (e.g. '*') so we know where to place characters
    row = 0
    direction = 1
    for col in range(n):
        fence_matrix[row][col] = '*'  # mark an occupied cell
        row += direction
        if row == 0 or row == rails - 1:
            direction *= -1

    # Fill the marked positions with ciphertext in order
    idx = 0
    for r in range(rails):
        for c in range(n):
            if fence_matrix[r][c] == '*' and idx < n:
                fence_matrix[r][c] = ciphertext[idx]
                idx += 1

    # Reconstruct plaintext by traversing the zigzag again
    result = []
    row = 0
    direction = 1
    for col in range(n):
        # We know fence_matrix[row][col] is a character
        result.append(fence_matrix[row][col])
        row += direction
        if row == 0 or row == rails - 1:
            direction *= -1

    return "".join(result)

def main():
    print("Rail Fence Cipher (Corrected for spaces)")
    plaintext = input("Enter the plaintext (spaces included): ")
    try:
        rails = int(input("Enter the number of rails: "))
    except ValueError:
        print("Please enter a valid integer for the number of rails.")
        return
    
    # Encrypt
    ciphertext = rail_fence_encrypt(plaintext, rails)
    print("Encrypted Text:")
    print(ciphertext)
    
    input("\nPress Enter to continue to decryption...")
    
    # Decrypt
    decrypted_text = rail_fence_decrypt(ciphertext, rails)
    print("\nDecrypted Text:")
    print(decrypted_text)

if __name__ == "__main__":
    main()
