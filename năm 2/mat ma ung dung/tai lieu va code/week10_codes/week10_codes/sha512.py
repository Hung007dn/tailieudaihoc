import struct

# SHA-512 constants: 80 64-bit words.
K = [
    0x428a2f98d728ae22, 0x7137449123ef65cd,
    0xb5c0fbcfec4d3b2f, 0xe9b5dba58189dbbc,
    0x3956c25bf348b538, 0x59f111f1b605d019,
    0x923f82a4af194f9b, 0xab1c5ed5da6d8118,
    0xd807aa98a3030242, 0x12835b0145706fbe,
    0x243185be4ee4b28c, 0x550c7dc3d5ffb4e2,
    0x72be5d74f27b896f, 0x80deb1fe3b1696b1,
    0x9bdc06a725c71235, 0xc19bf174cf692694,
    0xe49b69c19ef14ad2, 0xefbe4786384f25e3,
    0x0fc19dc68b8cd5b5, 0x240ca1cc77ac9c65,
    0x2de92c6f592b0275, 0x4a7484aa6ea6e483,
    0x5cb0a9dcbd41fbd4, 0x76f988da831153b5,
    0x983e5152ee66dfab, 0xa831c66d2db43210,
    0xb00327c898fb213f, 0xbf597fc7beef0ee4,
    0xc6e00bf33da88fc2, 0xd5a79147930aa725,
    0x06ca6351e003826f, 0x142929670a0e6e70,
    0x27b70a8546d22ffc, 0x2e1b21385c26c926,
    0x4d2c6dfc5ac42aed, 0x53380d139d95b3df,
    0x650a73548baf63de, 0x766a0abb3c77b2a8,
    0x81c2c92e47edaee6, 0x92722c851482353b,
    0xa2bfe8a14cf10364, 0xa81a664bbc423001,
    0xc24b8b70d0f89791, 0xc76c51a30654be30,
    0xd192e819d6ef5218, 0xd69906245565a910,
    0xf40e35855771202a, 0x106aa07032bbd1b8,
    0x19a4c116b8d2d0c8, 0x1e376c085141ab53,
    0x2748774cdf8eeb99, 0x34b0bcb5e19b48a8,
    0x391c0cb3c5c95a63, 0x4ed8aa4ae3418acb,
    0x5b9cca4f7763e373, 0x682e6ff3d6b2b8a3,
    0x748f82ee5defb2fc, 0x78a5636f43172f60,
    0x84c87814a1f0ab72, 0x8cc702081a6439ec,
    0x90befffa23631e28, 0xa4506cebde82bde9,
    0xbef9a3f7b2c67915, 0xc67178f2e372532b,
    0xca273eceea26619c, 0xd186b8c721c0c207,
    0xeada7dd6cde0eb1e, 0xf57d4f7fee6ed178,
    0x06f067aa72176fba, 0x0a637dc5a2c898a6,
    0x113f9804bef90dae, 0x1b710b35131c471b,
    0x28db77f523047d84, 0x32caab7b40c72493,
    0x3c9ebe0a15c9bebc, 0x431d67c49c100d4c,
    0x4cc5d4becb3e42b6, 0x597f299cfc657e2a,
    0x5fcb6fab3ad6faec, 0x6c44198c4a475817
]

def pause(step_desc=""):
    input(f"\n--- {step_desc} \n\nPress Enter to continue...")

def right_rotate(n, d):
    """Right rotate a 64-bit integer n by d bits."""
    return ((n >> d) | (n << (64 - d))) & 0xffffffffffffffff

def sha512(message):
    # --- Preprocessing Step ---
    print("=== Preprocessing Step ===")
    print("Converting message to bytearray using UTF-8 encoding.")
    message_bytes = bytearray(message, 'utf-8')
    orig_len = len(message_bytes) * 8  # original length in bits
    print(f"Original message: {message}")
    print(f"Original message bytes: {' '.join(f'{b:02x}' for b in message_bytes)}")
    print(f"Original message length: {orig_len} bits")
    pause("Finish initial conversion and length computation:")

    # Append the bit '1' to the message (0x80 = 10000000 in binary)
    message_bytes.append(0x80)
    print("After appending 0x80 (binary 10000000):")
    print(' '.join(f'{b:02x}' for b in message_bytes))
    pause("Finish appending 0x80:")

    # Pad with zeros until message length in bits ≡ 896 (mod 1024)
    # (because 896 + 128 = 1024 bits per block)
    while (len(message_bytes) * 8 + 128) % 1024 != 0:
        message_bytes.append(0)
    print("After padding with zeros so that (message bits + 128) is a multiple of 1024:")
    print(' '.join(f'{b:02x}' for b in message_bytes))
    pause("Finish zero padding:")

    # Append the original message length as a 128-bit big-endian integer.
    # We split orig_len (an integer) into two 64-bit values.
    high = orig_len >> 64
    low = orig_len & 0xffffffffffffffff
    message_bytes += struct.pack('>QQ', high, low)
    print("After appending the 128-bit big-endian original message length:")
    print(' '.join(f'{b:02x}' for b in message_bytes))
    pause("Finish appending original length:")

    print(f"\nTotal padded message length: {len(message_bytes)*8} bits")

    # Initial hash values (first 64 bits of the fractional parts of the square roots of the first 8 primes)
    H = [
        0x6a09e667f3bcc908, 0xbb67ae8584caa73b,
        0x3c6ef372fe94f82b, 0xa54ff53a5f1d36f1,
        0x510e527fade682d1, 0x9b05688c2b3e6c1f,
        0x1f83d9abfb41bd6b, 0x5be0cd19137e2179
    ]
    print("\n=== Initial Hash Values ===")
    for idx, h_val in enumerate(H):
        print(f"H[{idx}] = {h_val:016x}")
    pause("Finish displaying initial hash values:")

    # Process each 1024-bit (128-byte) block
    for block_num in range(0, len(message_bytes), 128):
        print(f"\n###############################")
        print(f"Processing Block: {block_num // 128}")
        print(f"Block (in hex): {' '.join(f'{b:02x}' for b in message_bytes[block_num:block_num+128])}")
        print("###############################")

        # Prepare the message schedule 'w'
        chunk = message_bytes[block_num:block_num+128]
        # Unpack 16 64-bit words
        w = list(struct.unpack('>16Q', chunk)) + [0]*64

        print("\n=== Message Schedule: Initial 16 Words ===")
        for i in range(16):
            print(f"W[{i:02}] = {w[i]:016x}")
        pause("Finish initial 16 words of the block:")

        # Extend the message schedule to 80 words
        print("\n=== Extending Message Schedule to 80 Words ===")
        for j in range(16, 80):
            # For SHA-512, sigma0 and sigma1 are defined as:
            # sigma0(x) = ROTR(x,1) XOR ROTR(x,8) XOR (x >> 7)
            # sigma1(x) = ROTR(x,19) XOR ROTR(x,61) XOR (x >> 6)
            rot1   = right_rotate(w[j-15], 1)
            rot8   = right_rotate(w[j-15], 8)
            shift7 = w[j-15] >> 7
            s0 = rot1 ^ rot8 ^ shift7

            rot19  = right_rotate(w[j-2], 19)
            rot61  = right_rotate(w[j-2], 61)
            shift6 = w[j-2] >> 6
            s1 = rot19 ^ rot61 ^ shift6

            # Display the full formula and computed intermediate results
            print(f"\nW[{j:02}] computation:")
            print(f"   s0 = (right_rotate(W[{j-15}], 1) = {rot1:016x}) XOR (right_rotate(W[{j-15}], 8) = {rot8:016x}) XOR (W[{j-15}] >> 7 = {shift7:016x}) = {s0:016x}")
            print(f"   s1 = (right_rotate(W[{j-2}], 19) = {rot19:016x}) XOR (right_rotate(W[{j-2}], 61) = {rot61:016x}) XOR (W[{j-2}] >> 6 = {shift6:016x}) = {s1:016x}")
            w[j] = (w[j-16] + s0 + w[j-7] + s1) & 0xffffffffffffffff
            print(f"   W[{j:02}] = (W[{j-16}] + s0 + W[{j-7}] + s1) mod 2^64 = ({w[j-16]:016x} + {s0:016x} + {w[j-7]:016x} + {s1:016x}) mod 2^64 = {w[j]:016x}")
            pause(f"Finish computing W[{j:02}]:")
        
        print("\n=== Full Extended Message Schedule ===")
        for idx in range(16, 80):
            print(f"W[{idx:02}] = {w[idx]:016x}")
        pause("Finish full extension of message schedule:")

        # Initialize working variables with current hash value
        a, b, c, d, e, f, g, h_var = H  # use h_var to avoid conflict with 'h' function
        print("\n=== Initial Working Variables ===")
        print(f"a = {a:016x}")
        print(f"b = {b:016x}")
        print(f"c = {c:016x}")
        print(f"d = {d:016x}")
        print(f"e = {e:016x}")
        print(f"f = {f:016x}")
        print(f"g = {g:016x}")
        print(f"h = {h_var:016x}")
        pause("Finish initializing working variables:")

        # Main compression loop over 80 rounds
        print("\n=== Begin Compression Rounds ===")
        for j in range(80):
            # For SHA-512 the round functions are:
            # S1 = ROTR(e,14) XOR ROTR(e,18) XOR ROTR(e,41)
            # ch = (e AND f) XOR ((NOT e) AND g)
            # temp1 = (h + S1 + ch + K[j] + w[j]) mod 2^64
            # S0 = ROTR(a,28) XOR ROTR(a,34) XOR ROTR(a,39)
            # maj = (a AND b) XOR (a AND c) XOR (b AND c)
            # temp2 = (S0 + maj) mod 2^64
            S1 = right_rotate(e, 14) ^ right_rotate(e, 18) ^ right_rotate(e, 41)
            ch = (e & f) ^ ((~e) & g)
            temp1 = (h_var + S1 + ch + K[j] + w[j]) & 0xffffffffffffffff

            S0 = right_rotate(a, 28) ^ right_rotate(a, 34) ^ right_rotate(a, 39)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (S0 + maj) & 0xffffffffffffffff

            # Display formulas and computed intermediate values
            print(f"\n-- Round {j:02} --")
            print("Computed values:")
            print(f"   S1 = ROTR(e,14) XOR ROTR(e,18) XOR ROTR(e,41)")
            print(f"      = ({right_rotate(e,14):016x} XOR {right_rotate(e,18):016x} XOR {right_rotate(e,41):016x}) = {S1:016x}")
            print(f"   ch = (e AND f) XOR ((NOT e) AND g)")
            print(f"      = ({e:016x} AND {f:016x}) XOR ((~{e:016x}) AND {g:016x}) = {ch:016x}")
            print(f"   temp1 = h + S1 + ch + K[{j}] + W[{j}] mod 2^64")
            print(f"         = ({h_var:016x} + {S1:016x} + {ch:016x} + {K[j]:016x} + {w[j]:016x}) mod 2^64 = {temp1:016x}")

            print(f"   S0 = ROTR(a,28) XOR ROTR(a,34) XOR ROTR(a,39)")
            print(f"      = ({right_rotate(a,28):016x} XOR {right_rotate(a,34):016x} XOR {right_rotate(a,39):016x}) = {S0:016x}")
            print(f"   maj = (a AND b) XOR (a AND c) XOR (b AND c)")
            print(f"      = ({a:016x} AND {b:016x}) XOR ({a:016x} AND {c:016x}) XOR ({b:016x} AND {c:016x}) = {maj:016x}")
            print(f"   temp2 = S0 + maj mod 2^64")
            print(f"         = ({S0:016x} + {maj:016x}) mod 2^64 = {temp2:016x}")

            # Update the working variables for the next round
            new_h = g
            new_g = f
            new_f = e
            new_e = (d + temp1) & 0xffffffffffffffff
            new_d = c
            new_c = b
            new_b = a
            new_a = (temp1 + temp2) & 0xffffffffffffffff

            print("\nUpdated working variables:")
            print(f"   a = temp1 + temp2 = {temp1:016x} + {temp2:016x} = {new_a:016x}")
            print(f"   b = previous a = {a:016x}")
            print(f"   c = previous b = {b:016x}")
            print(f"   d = previous c = {c:016x}")
            print(f"   e = d + temp1 = {d:016x} + {temp1:016x} = {new_e:016x}")
            print(f"   f = previous e = {e:016x}")
            print(f"   g = previous f = {f:016x}")
            print(f"   h = previous g = {g:016x}")

            a, b, c, d, e, f, g, h_var = new_a, new_b, new_c, new_d, new_e, new_f, new_g, new_h

            pause(f"Finish round {j:02}:")

        # Update the hash values with the results from this block
        H = [(old + new_val) & 0xffffffffffffffff for old, new_val in zip(H, [a, b, c, d, e, f, g, h_var])]
        print("\n=== Updated Hash Values after processing block ===")
        for idx, h_val in enumerate(H):
            print(f"H[{idx}] = {h_val:016x}")
        pause("Finish updating hash values for the block:")

    # Produce the final digest by concatenating the hash values
    final_digest = ''.join(f'{h_val:016x}' for h_val in H)
    return final_digest

# === Main Program ===
if __name__ == '__main__':
    msg = input("Enter message: ")
    digest = sha512(msg)
    print("\n=== Final SHA-512 Digest ===")
    print(digest)
import struct

# SHA-512 constants: 80 64-bit words.
K = [
    0x428a2f98d728ae22, 0x7137449123ef65cd,
    0xb5c0fbcfec4d3b2f, 0xe9b5dba58189dbbc,
    0x3956c25bf348b538, 0x59f111f1b605d019,
    0x923f82a4af194f9b, 0xab1c5ed5da6d8118,
    0xd807aa98a3030242, 0x12835b0145706fbe,
    0x243185be4ee4b28c, 0x550c7dc3d5ffb4e2,
    0x72be5d74f27b896f, 0x80deb1fe3b1696b1,
    0x9bdc06a725c71235, 0xc19bf174cf692694,
    0xe49b69c19ef14ad2, 0xefbe4786384f25e3,
    0x0fc19dc68b8cd5b5, 0x240ca1cc77ac9c65,
    0x2de92c6f592b0275, 0x4a7484aa6ea6e483,
    0x5cb0a9dcbd41fbd4, 0x76f988da831153b5,
    0x983e5152ee66dfab, 0xa831c66d2db43210,
    0xb00327c898fb213f, 0xbf597fc7beef0ee4,
    0xc6e00bf33da88fc2, 0xd5a79147930aa725,
    0x06ca6351e003826f, 0x142929670a0e6e70,
    0x27b70a8546d22ffc, 0x2e1b21385c26c926,
    0x4d2c6dfc5ac42aed, 0x53380d139d95b3df,
    0x650a73548baf63de, 0x766a0abb3c77b2a8,
    0x81c2c92e47edaee6, 0x92722c851482353b,
    0xa2bfe8a14cf10364, 0xa81a664bbc423001,
    0xc24b8b70d0f89791, 0xc76c51a30654be30,
    0xd192e819d6ef5218, 0xd69906245565a910,
    0xf40e35855771202a, 0x106aa07032bbd1b8,
    0x19a4c116b8d2d0c8, 0x1e376c085141ab53,
    0x2748774cdf8eeb99, 0x34b0bcb5e19b48a8,
    0x391c0cb3c5c95a63, 0x4ed8aa4ae3418acb,
    0x5b9cca4f7763e373, 0x682e6ff3d6b2b8a3,
    0x748f82ee5defb2fc, 0x78a5636f43172f60,
    0x84c87814a1f0ab72, 0x8cc702081a6439ec,
    0x90befffa23631e28, 0xa4506cebde82bde9,
    0xbef9a3f7b2c67915, 0xc67178f2e372532b,
    0xca273eceea26619c, 0xd186b8c721c0c207,
    0xeada7dd6cde0eb1e, 0xf57d4f7fee6ed178,
    0x06f067aa72176fba, 0x0a637dc5a2c898a6,
    0x113f9804bef90dae, 0x1b710b35131c471b,
    0x28db77f523047d84, 0x32caab7b40c72493,
    0x3c9ebe0a15c9bebc, 0x431d67c49c100d4c,
    0x4cc5d4becb3e42b6, 0x597f299cfc657e2a,
    0x5fcb6fab3ad6faec, 0x6c44198c4a475817
]

def pause(step_desc=""):
    input(f"\n--- {step_desc} \n\nPress Enter to continue...")

def right_rotate(n, d):
    """Right rotate a 64-bit integer n by d bits."""
    return ((n >> d) | (n << (64 - d))) & 0xffffffffffffffff

def sha512(message):
    # --- Preprocessing Step ---
    print("=== Preprocessing Step ===")
    print("Converting message to bytearray using UTF-8 encoding.")
    message_bytes = bytearray(message, 'utf-8')
    orig_len = len(message_bytes) * 8  # original length in bits
    print(f"Original message: {message}")
    print(f"Original message bytes: {' '.join(f'{b:02x}' for b in message_bytes)}")
    print(f"Original message length: {orig_len} bits")
    pause("Finish initial conversion and length computation:")

    # Append the bit '1' to the message (0x80 = 10000000 in binary)
    message_bytes.append(0x80)
    print("After appending 0x80 (binary 10000000):")
    print(' '.join(f'{b:02x}' for b in message_bytes))
    pause("Finish appending 0x80:")

    # Pad with zeros until message length in bits ≡ 896 (mod 1024)
    # (because 896 + 128 = 1024 bits per block)
    while (len(message_bytes) * 8 + 128) % 1024 != 0:
        message_bytes.append(0)
    print("After padding with zeros so that (message bits + 128) is a multiple of 1024:")
    print(' '.join(f'{b:02x}' for b in message_bytes))
    pause("Finish zero padding:")

    # Append the original message length as a 128-bit big-endian integer.
    # We split orig_len (an integer) into two 64-bit values.
    high = orig_len >> 64
    low = orig_len & 0xffffffffffffffff
    message_bytes += struct.pack('>QQ', high, low)
    print("After appending the 128-bit big-endian original message length:")
    print(' '.join(f'{b:02x}' for b in message_bytes))
    pause("Finish appending original length:")

    print(f"\nTotal padded message length: {len(message_bytes)*8} bits")

    # Initial hash values (first 64 bits of the fractional parts of the square roots of the first 8 primes)
    H = [
        0x6a09e667f3bcc908, 0xbb67ae8584caa73b,
        0x3c6ef372fe94f82b, 0xa54ff53a5f1d36f1,
        0x510e527fade682d1, 0x9b05688c2b3e6c1f,
        0x1f83d9abfb41bd6b, 0x5be0cd19137e2179
    ]
    print("\n=== Initial Hash Values ===")
    for idx, h_val in enumerate(H):
        print(f"H[{idx}] = {h_val:016x}")
    pause("Finish displaying initial hash values:")

    # Process each 1024-bit (128-byte) block
    for block_num in range(0, len(message_bytes), 128):
        print(f"\n###############################")
        print(f"Processing Block: {block_num // 128}")
        print(f"Block (in hex): {' '.join(f'{b:02x}' for b in message_bytes[block_num:block_num+128])}")
        print("###############################")

        # Prepare the message schedule 'w'
        chunk = message_bytes[block_num:block_num+128]
        # Unpack 16 64-bit words
        w = list(struct.unpack('>16Q', chunk)) + [0]*64

        print("\n=== Message Schedule: Initial 16 Words ===")
        for i in range(16):
            print(f"W[{i:02}] = {w[i]:016x}")
        pause("Finish initial 16 words of the block:")

        # Extend the message schedule to 80 words
        print("\n=== Extending Message Schedule to 80 Words ===")
        for j in range(16, 80):
            # For SHA-512, sigma0 and sigma1 are defined as:
            # sigma0(x) = ROTR(x,1) XOR ROTR(x,8) XOR (x >> 7)
            # sigma1(x) = ROTR(x,19) XOR ROTR(x,61) XOR (x >> 6)
            rot1   = right_rotate(w[j-15], 1)
            rot8   = right_rotate(w[j-15], 8)
            shift7 = w[j-15] >> 7
            s0 = rot1 ^ rot8 ^ shift7

            rot19  = right_rotate(w[j-2], 19)
            rot61  = right_rotate(w[j-2], 61)
            shift6 = w[j-2] >> 6
            s1 = rot19 ^ rot61 ^ shift6

            # Display the full formula and computed intermediate results
            print(f"\nW[{j:02}] computation:")
            print(f"   s0 = (right_rotate(W[{j-15}], 1) = {rot1:016x}) XOR (right_rotate(W[{j-15}], 8) = {rot8:016x}) XOR (W[{j-15}] >> 7 = {shift7:016x}) = {s0:016x}")
            print(f"   s1 = (right_rotate(W[{j-2}], 19) = {rot19:016x}) XOR (right_rotate(W[{j-2}], 61) = {rot61:016x}) XOR (W[{j-2}] >> 6 = {shift6:016x}) = {s1:016x}")
            w[j] = (w[j-16] + s0 + w[j-7] + s1) & 0xffffffffffffffff
            print(f"   W[{j:02}] = (W[{j-16}] + s0 + W[{j-7}] + s1) mod 2^64 = ({w[j-16]:016x} + {s0:016x} + {w[j-7]:016x} + {s1:016x}) mod 2^64 = {w[j]:016x}")
            pause(f"Finish computing W[{j:02}]:")
        
        print("\n=== Full Extended Message Schedule ===")
        for idx in range(16, 80):
            print(f"W[{idx:02}] = {w[idx]:016x}")
        pause("Finish full extension of message schedule:")

        # Initialize working variables with current hash value
        a, b, c, d, e, f, g, h_var = H  # use h_var to avoid conflict with 'h' function
        print("\n=== Initial Working Variables ===")
        print(f"a = {a:016x}")
        print(f"b = {b:016x}")
        print(f"c = {c:016x}")
        print(f"d = {d:016x}")
        print(f"e = {e:016x}")
        print(f"f = {f:016x}")
        print(f"g = {g:016x}")
        print(f"h = {h_var:016x}")
        pause("Finish initializing working variables:")

        # Main compression loop over 80 rounds
        print("\n=== Begin Compression Rounds ===")
        for j in range(80):
            # For SHA-512 the round functions are:
            # S1 = ROTR(e,14) XOR ROTR(e,18) XOR ROTR(e,41)
            # ch = (e AND f) XOR ((NOT e) AND g)
            # temp1 = (h + S1 + ch + K[j] + w[j]) mod 2^64
            # S0 = ROTR(a,28) XOR ROTR(a,34) XOR ROTR(a,39)
            # maj = (a AND b) XOR (a AND c) XOR (b AND c)
            # temp2 = (S0 + maj) mod 2^64
            S1 = right_rotate(e, 14) ^ right_rotate(e, 18) ^ right_rotate(e, 41)
            ch = (e & f) ^ ((~e) & g)
            temp1 = (h_var + S1 + ch + K[j] + w[j]) & 0xffffffffffffffff

            S0 = right_rotate(a, 28) ^ right_rotate(a, 34) ^ right_rotate(a, 39)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (S0 + maj) & 0xffffffffffffffff

            # Display formulas and computed intermediate values
            print(f"\n-- Round {j:02} --")
            print("Computed values:")
            print(f"   S1 = ROTR(e,14) XOR ROTR(e,18) XOR ROTR(e,41)")
            print(f"      = ({right_rotate(e,14):016x} XOR {right_rotate(e,18):016x} XOR {right_rotate(e,41):016x}) = {S1:016x}")
            print(f"   ch = (e AND f) XOR ((NOT e) AND g)")
            print(f"      = ({e:016x} AND {f:016x}) XOR ((~{e:016x}) AND {g:016x}) = {ch:016x}")
            print(f"   temp1 = h + S1 + ch + K[{j}] + W[{j}] mod 2^64")
            print(f"         = ({h_var:016x} + {S1:016x} + {ch:016x} + {K[j]:016x} + {w[j]:016x}) mod 2^64 = {temp1:016x}")

            print(f"   S0 = ROTR(a,28) XOR ROTR(a,34) XOR ROTR(a,39)")
            print(f"      = ({right_rotate(a,28):016x} XOR {right_rotate(a,34):016x} XOR {right_rotate(a,39):016x}) = {S0:016x}")
            print(f"   maj = (a AND b) XOR (a AND c) XOR (b AND c)")
            print(f"      = ({a:016x} AND {b:016x}) XOR ({a:016x} AND {c:016x}) XOR ({b:016x} AND {c:016x}) = {maj:016x}")
            print(f"   temp2 = S0 + maj mod 2^64")
            print(f"         = ({S0:016x} + {maj:016x}) mod 2^64 = {temp2:016x}")

            # Update the working variables for the next round
            new_h = g
            new_g = f
            new_f = e
            new_e = (d + temp1) & 0xffffffffffffffff
            new_d = c
            new_c = b
            new_b = a
            new_a = (temp1 + temp2) & 0xffffffffffffffff

            print("\nUpdated working variables:")
            print(f"   a = temp1 + temp2 = {temp1:016x} + {temp2:016x} = {new_a:016x}")
            print(f"   b = previous a = {a:016x}")
            print(f"   c = previous b = {b:016x}")
            print(f"   d = previous c = {c:016x}")
            print(f"   e = d + temp1 = {d:016x} + {temp1:016x} = {new_e:016x}")
            print(f"   f = previous e = {e:016x}")
            print(f"   g = previous f = {f:016x}")
            print(f"   h = previous g = {g:016x}")

            a, b, c, d, e, f, g, h_var = new_a, new_b, new_c, new_d, new_e, new_f, new_g, new_h

            pause(f"Finish round {j:02}:")

        # Update the hash values with the results from this block
        H = [(old + new_val) & 0xffffffffffffffff for old, new_val in zip(H, [a, b, c, d, e, f, g, h_var])]
        print("\n=== Updated Hash Values after processing block ===")
        for idx, h_val in enumerate(H):
            print(f"H[{idx}] = {h_val:016x}")
        pause("Finish updating hash values for the block:")

    # Produce the final digest by concatenating the hash values
    final_digest = ''.join(f'{h_val:016x}' for h_val in H)
    return final_digest

# === Main Program ===
if __name__ == '__main__':
    msg = input("Enter message: ")
    digest = sha512(msg)
    print("\n=== Final SHA-512 Digest ===")
    print(digest)
import struct

# SHA-512 constants: 80 64-bit words.
K = [
    0x428a2f98d728ae22, 0x7137449123ef65cd,
    0xb5c0fbcfec4d3b2f, 0xe9b5dba58189dbbc,
    0x3956c25bf348b538, 0x59f111f1b605d019,
    0x923f82a4af194f9b, 0xab1c5ed5da6d8118,
    0xd807aa98a3030242, 0x12835b0145706fbe,
    0x243185be4ee4b28c, 0x550c7dc3d5ffb4e2,
    0x72be5d74f27b896f, 0x80deb1fe3b1696b1,
    0x9bdc06a725c71235, 0xc19bf174cf692694,
    0xe49b69c19ef14ad2, 0xefbe4786384f25e3,
    0x0fc19dc68b8cd5b5, 0x240ca1cc77ac9c65,
    0x2de92c6f592b0275, 0x4a7484aa6ea6e483,
    0x5cb0a9dcbd41fbd4, 0x76f988da831153b5,
    0x983e5152ee66dfab, 0xa831c66d2db43210,
    0xb00327c898fb213f, 0xbf597fc7beef0ee4,
    0xc6e00bf33da88fc2, 0xd5a79147930aa725,
    0x06ca6351e003826f, 0x142929670a0e6e70,
    0x27b70a8546d22ffc, 0x2e1b21385c26c926,
    0x4d2c6dfc5ac42aed, 0x53380d139d95b3df,
    0x650a73548baf63de, 0x766a0abb3c77b2a8,
    0x81c2c92e47edaee6, 0x92722c851482353b,
    0xa2bfe8a14cf10364, 0xa81a664bbc423001,
    0xc24b8b70d0f89791, 0xc76c51a30654be30,
    0xd192e819d6ef5218, 0xd69906245565a910,
    0xf40e35855771202a, 0x106aa07032bbd1b8,
    0x19a4c116b8d2d0c8, 0x1e376c085141ab53,
    0x2748774cdf8eeb99, 0x34b0bcb5e19b48a8,
    0x391c0cb3c5c95a63, 0x4ed8aa4ae3418acb,
    0x5b9cca4f7763e373, 0x682e6ff3d6b2b8a3,
    0x748f82ee5defb2fc, 0x78a5636f43172f60,
    0x84c87814a1f0ab72, 0x8cc702081a6439ec,
    0x90befffa23631e28, 0xa4506cebde82bde9,
    0xbef9a3f7b2c67915, 0xc67178f2e372532b,
    0xca273eceea26619c, 0xd186b8c721c0c207,
    0xeada7dd6cde0eb1e, 0xf57d4f7fee6ed178,
    0x06f067aa72176fba, 0x0a637dc5a2c898a6,
    0x113f9804bef90dae, 0x1b710b35131c471b,
    0x28db77f523047d84, 0x32caab7b40c72493,
    0x3c9ebe0a15c9bebc, 0x431d67c49c100d4c,
    0x4cc5d4becb3e42b6, 0x597f299cfc657e2a,
    0x5fcb6fab3ad6faec, 0x6c44198c4a475817
]

def pause(step_desc=""):
    input(f"\n--- {step_desc} \n\nPress Enter to continue...")

def right_rotate(n, d):
    """Right rotate a 64-bit integer n by d bits."""
    return ((n >> d) | (n << (64 - d))) & 0xffffffffffffffff

def sha512(message):
    # --- Preprocessing Step ---
    print("=== Preprocessing Step ===")
    print("Converting message to bytearray using UTF-8 encoding.")
    message_bytes = bytearray(message, 'utf-8')
    orig_len = len(message_bytes) * 8  # original length in bits
    print(f"Original message: {message}")
    print(f"Original message bytes: {' '.join(f'{b:02x}' for b in message_bytes)}")
    print(f"Original message length: {orig_len} bits")
    pause("Finish initial conversion and length computation:")

    # Append the bit '1' to the message (0x80 = 10000000 in binary)
    message_bytes.append(0x80)
    print("After appending 0x80 (binary 10000000):")
    print(' '.join(f'{b:02x}' for b in message_bytes))
    pause("Finish appending 0x80:")

    # Pad with zeros until message length in bits ≡ 896 (mod 1024)
    # (because 896 + 128 = 1024 bits per block)
    while (len(message_bytes) * 8 + 128) % 1024 != 0:
        message_bytes.append(0)
    print("After padding with zeros so that (message bits + 128) is a multiple of 1024:")
    print(' '.join(f'{b:02x}' for b in message_bytes))
    pause("Finish zero padding:")

    # Append the original message length as a 128-bit big-endian integer.
    # We split orig_len (an integer) into two 64-bit values.
    high = orig_len >> 64
    low = orig_len & 0xffffffffffffffff
    message_bytes += struct.pack('>QQ', high, low)
    print("After appending the 128-bit big-endian original message length:")
    print(' '.join(f'{b:02x}' for b in message_bytes))
    pause("Finish appending original length:")

    print(f"\nTotal padded message length: {len(message_bytes)*8} bits")

    # Initial hash values (first 64 bits of the fractional parts of the square roots of the first 8 primes)
    H = [
        0x6a09e667f3bcc908, 0xbb67ae8584caa73b,
        0x3c6ef372fe94f82b, 0xa54ff53a5f1d36f1,
        0x510e527fade682d1, 0x9b05688c2b3e6c1f,
        0x1f83d9abfb41bd6b, 0x5be0cd19137e2179
    ]
    print("\n=== Initial Hash Values ===")
    for idx, h_val in enumerate(H):
        print(f"H[{idx}] = {h_val:016x}")
    pause("Finish displaying initial hash values:")

    # Process each 1024-bit (128-byte) block
    for block_num in range(0, len(message_bytes), 128):
        print(f"\n###############################")
        print(f"Processing Block: {block_num // 128}")
        print(f"Block (in hex): {' '.join(f'{b:02x}' for b in message_bytes[block_num:block_num+128])}")
        print("###############################")

        # Prepare the message schedule 'w'
        chunk = message_bytes[block_num:block_num+128]
        # Unpack 16 64-bit words
        w = list(struct.unpack('>16Q', chunk)) + [0]*64

        print("\n=== Message Schedule: Initial 16 Words ===")
        for i in range(16):
            print(f"W[{i:02}] = {w[i]:016x}")
        pause("Finish initial 16 words of the block:")

        # Extend the message schedule to 80 words
        print("\n=== Extending Message Schedule to 80 Words ===")
        for j in range(16, 80):
            # For SHA-512, sigma0 and sigma1 are defined as:
            # sigma0(x) = ROTR(x,1) XOR ROTR(x,8) XOR (x >> 7)
            # sigma1(x) = ROTR(x,19) XOR ROTR(x,61) XOR (x >> 6)
            rot1   = right_rotate(w[j-15], 1)
            rot8   = right_rotate(w[j-15], 8)
            shift7 = w[j-15] >> 7
            s0 = rot1 ^ rot8 ^ shift7

            rot19  = right_rotate(w[j-2], 19)
            rot61  = right_rotate(w[j-2], 61)
            shift6 = w[j-2] >> 6
            s1 = rot19 ^ rot61 ^ shift6

            # Display the full formula and computed intermediate results
            print(f"\nW[{j:02}] computation:")
            print(f"   s0 = (right_rotate(W[{j-15}], 1) = {rot1:016x}) XOR (right_rotate(W[{j-15}], 8) = {rot8:016x}) XOR (W[{j-15}] >> 7 = {shift7:016x}) = {s0:016x}")
            print(f"   s1 = (right_rotate(W[{j-2}], 19) = {rot19:016x}) XOR (right_rotate(W[{j-2}], 61) = {rot61:016x}) XOR (W[{j-2}] >> 6 = {shift6:016x}) = {s1:016x}")
            w[j] = (w[j-16] + s0 + w[j-7] + s1) & 0xffffffffffffffff
            print(f"   W[{j:02}] = (W[{j-16}] + s0 + W[{j-7}] + s1) mod 2^64 = ({w[j-16]:016x} + {s0:016x} + {w[j-7]:016x} + {s1:016x}) mod 2^64 = {w[j]:016x}")
            pause(f"Finish computing W[{j:02}]:")
        
        print("\n=== Full Extended Message Schedule ===")
        for idx in range(16, 80):
            print(f"W[{idx:02}] = {w[idx]:016x}")
        pause("Finish full extension of message schedule:")

        # Initialize working variables with current hash value
        a, b, c, d, e, f, g, h_var = H  # use h_var to avoid conflict with 'h' function
        print("\n=== Initial Working Variables ===")
        print(f"a = {a:016x}")
        print(f"b = {b:016x}")
        print(f"c = {c:016x}")
        print(f"d = {d:016x}")
        print(f"e = {e:016x}")
        print(f"f = {f:016x}")
        print(f"g = {g:016x}")
        print(f"h = {h_var:016x}")
        pause("Finish initializing working variables:")

        # Main compression loop over 80 rounds
        print("\n=== Begin Compression Rounds ===")
        for j in range(80):
            # For SHA-512 the round functions are:
            # S1 = ROTR(e,14) XOR ROTR(e,18) XOR ROTR(e,41)
            # ch = (e AND f) XOR ((NOT e) AND g)
            # temp1 = (h + S1 + ch + K[j] + w[j]) mod 2^64
            # S0 = ROTR(a,28) XOR ROTR(a,34) XOR ROTR(a,39)
            # maj = (a AND b) XOR (a AND c) XOR (b AND c)
            # temp2 = (S0 + maj) mod 2^64
            S1 = right_rotate(e, 14) ^ right_rotate(e, 18) ^ right_rotate(e, 41)
            ch = (e & f) ^ ((~e) & g)
            temp1 = (h_var + S1 + ch + K[j] + w[j]) & 0xffffffffffffffff

            S0 = right_rotate(a, 28) ^ right_rotate(a, 34) ^ right_rotate(a, 39)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (S0 + maj) & 0xffffffffffffffff

            # Display formulas and computed intermediate values
            print(f"\n-- Round {j:02} --")
            print("Computed values:")
            print(f"   S1 = ROTR(e,14) XOR ROTR(e,18) XOR ROTR(e,41)")
            print(f"      = ({right_rotate(e,14):016x} XOR {right_rotate(e,18):016x} XOR {right_rotate(e,41):016x}) = {S1:016x}")
            print(f"   ch = (e AND f) XOR ((NOT e) AND g)")
            print(f"      = ({e:016x} AND {f:016x}) XOR ((~{e:016x}) AND {g:016x}) = {ch:016x}")
            print(f"   temp1 = h + S1 + ch + K[{j}] + W[{j}] mod 2^64")
            print(f"         = ({h_var:016x} + {S1:016x} + {ch:016x} + {K[j]:016x} + {w[j]:016x}) mod 2^64 = {temp1:016x}")

            print(f"   S0 = ROTR(a,28) XOR ROTR(a,34) XOR ROTR(a,39)")
            print(f"      = ({right_rotate(a,28):016x} XOR {right_rotate(a,34):016x} XOR {right_rotate(a,39):016x}) = {S0:016x}")
            print(f"   maj = (a AND b) XOR (a AND c) XOR (b AND c)")
            print(f"      = ({a:016x} AND {b:016x}) XOR ({a:016x} AND {c:016x}) XOR ({b:016x} AND {c:016x}) = {maj:016x}")
            print(f"   temp2 = S0 + maj mod 2^64")
            print(f"         = ({S0:016x} + {maj:016x}) mod 2^64 = {temp2:016x}")

            # Update the working variables for the next round
            new_h = g
            new_g = f
            new_f = e
            new_e = (d + temp1) & 0xffffffffffffffff
            new_d = c
            new_c = b
            new_b = a
            new_a = (temp1 + temp2) & 0xffffffffffffffff

            print("\nUpdated working variables:")
            print(f"   a = temp1 + temp2 = {temp1:016x} + {temp2:016x} = {new_a:016x}")
            print(f"   b = previous a = {a:016x}")
            print(f"   c = previous b = {b:016x}")
            print(f"   d = previous c = {c:016x}")
            print(f"   e = d + temp1 = {d:016x} + {temp1:016x} = {new_e:016x}")
            print(f"   f = previous e = {e:016x}")
            print(f"   g = previous f = {f:016x}")
            print(f"   h = previous g = {g:016x}")

            a, b, c, d, e, f, g, h_var = new_a, new_b, new_c, new_d, new_e, new_f, new_g, new_h

            pause(f"Finish round {j:02}:")

        # Update the hash values with the results from this block
        H = [(old + new_val) & 0xffffffffffffffff for old, new_val in zip(H, [a, b, c, d, e, f, g, h_var])]
        print("\n=== Updated Hash Values after processing block ===")
        for idx, h_val in enumerate(H):
            print(f"H[{idx}] = {h_val:016x}")
        pause("Finish updating hash values for the block:")

    # Produce the final digest by concatenating the hash values
    final_digest = ''.join(f'{h_val:016x}' for h_val in H)
    return final_digest

# === Main Program ===
if __name__ == '__main__':
    msg = input("Enter message: ")
    digest = sha512(msg)
    print("\n=== Final SHA-512 Digest ===")
    print(digest)
