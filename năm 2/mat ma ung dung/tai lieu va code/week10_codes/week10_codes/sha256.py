import struct

# SHA-256 constants
K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
    0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
    0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
]

def pause(step_desc=""):
    input(f"--- {step_desc} \n \n Press Enter to continue...")

def right_rotate(n, d):
    """Right rotate a 32-bit integer n by d bits."""
    return ((n >> d) | (n << (32 - d))) & 0xffffffff

def sha256(message):
    # --- Preprocessing Step ---
    print("=== Preprocessing Step ===")
    print("Converting message to bytearray using UTF-8 encoding.")
    message_bytes = bytearray(message, 'utf-8')
    orig_len = len(message_bytes) * 8  # original length in bits
    print(f"Original message: {message}")
    print(f"Original message bytes: {' '.join(f'{b:02x}' for b in message_bytes)}")
    print(f"Original message length: {orig_len} bits")
    pause("Finish initial conversion and length computation:")

    # Append the bit '1' to the message (0x80 == 10000000 in binary)
    message_bytes.append(0x80)
    print("Appending 0x80 (binary 10000000):")
    print(' '.join(f'{b:02x}' for b in message_bytes))
    pause("Finish appending 0x80:")

    # Pad with zeros until message length in bits ≡ 448 (mod 512)
    while (len(message_bytes) * 8 + 64) % 512 != 0:
        message_bytes.append(0)
    print("Padding with zeros so that (message bits + 64) is a multiple of 512:")
    print(' '.join(f'{b:02x}' for b in message_bytes))
    pause("Finish zero padding:")

    # Append the original message length as a 64-bit big-endian integer
    message_bytes += struct.pack('>Q', orig_len)
    print("Appending the 64-bit big-endian original message length:")
    print(' '.join(f'{b:02x}' for b in message_bytes))
    pause("Finish appending original length:")

    print(f"\nTotal padded message length: {len(message_bytes)*8} bits")

    # Initial hash values (first 32 bits of the fractional parts of the square roots of the first 8 primes)
    H = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    ]

    print("\n=== Initial Hash Values ===")
    for idx, h_val in enumerate(H):
        print(f"H[{idx}] = {h_val:08x}")
    pause("Finish displaying initial hash values:")

    # Process each 512-bit (64-byte) block
    for block_num in range(0, len(message_bytes), 64):
        print(f"\n###############################")
        print(f"Processing Block: {block_num // 64}")
        print(f"Block (in hex): {' '.join(f'{b:02x}' for b in message_bytes[block_num:block_num+64])}")
        print("###############################")

        # Prepare the message schedule 'w'
        chunk = message_bytes[block_num:block_num+64]
        w = list(struct.unpack('>16L', chunk)) + [0]*48

        print("\n=== Message Schedule: Initial 16 Words ===")
        for i in range(16):
            print(f"W[{i:02}] = {w[i]:08x}")
        pause("Finish initial 16 words of the block:")

        # Extend the message schedule to 64 words
        print("\n=== Extending Message Schedule to 64 Words ===")
        for j in range(16, 64):
            # s0 = (w[j-15] right rotated by 7) XOR (w[j-15] right rotated by 18) XOR (w[j-15] >> 3)
            rot7   = right_rotate(w[j-15], 7)
            rot18  = right_rotate(w[j-15], 18)
            shift3 = w[j-15] >> 3
            s0 = rot7 ^ rot18 ^ shift3

            # s1 = (w[j-2] right rotated by 17) XOR (w[j-2] right rotated by 19) XOR (w[j-2] >> 10)
            rot17  = right_rotate(w[j-2], 17)
            rot19  = right_rotate(w[j-2], 19)
            shift10 = w[j-2] >> 10
            s1 = rot17 ^ rot19 ^ shift10

            # Display the full formula and computed intermediate results
            print(f"\nW[{j:02}] computation:")
            print(f"   s0 = (right_rotate(W[{j-15}],7) = {rot7:08x}) XOR (right_rotate(W[{j-15}],18) = {rot18:08x}) XOR (W[{j-15}]>>3 = {shift3:08x}) = {s0:08x}")
            print(f"   s1 = (right_rotate(W[{j-2}],17) = {rot17:08x}) XOR (right_rotate(W[{j-2}],19) = {rot19:08x}) XOR (W[{j-2}]>>10 = {shift10:08x}) = {s1:08x}")
            w[j] = (w[j-16] + s0 + w[j-7] + s1) & 0xffffffff
            print(f"   W[{j:02}] = (W[{j-16}] + s0 + W[{j-7}] + s1) mod 2^32 = ({w[j-16]:08x} + {s0:08x} + {w[j-7]:08x} + {s1:08x}) mod 2^32 = {w[j]:08x}")
            pause(f"Finish computing W[{j:02}]:")
        
        print("\n=== Full Extended Message Schedule ===")
        for idx in range(16, 64):
            print(f"W[{idx:02}] = {w[idx]:08x}")
        pause("Finish full extension of message schedule:")

        # Initialize working variables with current hash value
        a, b, c, d, e, f, g, h_var = H  # use h_var since h is used later as a temporary
        print("\n=== Initial Working Variables ===")
        print(f"a = {a:08x}")
        print(f"b = {b:08x}")
        print(f"c = {c:08x}")
        print(f"d = {d:08x}")
        print(f"e = {e:08x}")
        print(f"f = {f:08x}")
        print(f"g = {g:08x}")
        print(f"h = {h_var:08x}")
        pause("Finish initializing working variables:")

        # Main compression loop over 64 rounds
        print("\n=== Begin Compression Rounds ===")
        for j in range(64):
            # Compute the formulas for this round
            S1 = right_rotate(e, 6) ^ right_rotate(e, 11) ^ right_rotate(e, 25)
            ch = (e & f) ^ ((~e) & g)
            temp1 = (h_var + S1 + ch + K[j] + w[j]) & 0xffffffff

            S0 = right_rotate(a, 2) ^ right_rotate(a, 13) ^ right_rotate(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (S0 + maj) & 0xffffffff

            # Display the formulas and computed intermediate values
            print(f"\n-- Round {j:02} --")
            print("Computed values:")
            print(f"   S1 = right_rotate(e,6) XOR right_rotate(e,11) XOR right_rotate(e,25)")
            print(f"      = ({right_rotate(e,6):08x} XOR {right_rotate(e,11):08x} XOR {right_rotate(e,25):08x}) = {S1:08x}")
            print(f"   ch = (e AND f) XOR ((NOT e) AND g)")
            print(f"      = ({e:08x} AND {f:08x}) XOR ((~{e:08x}) AND {g:08x}) = {ch:08x}")
            print(f"   temp1 = (h + S1 + ch + K[{j}] + W[{j}]) mod 2^32")
            print(f"         = ({h_var:08x} + {S1:08x} + {ch:08x} + {K[j]:08x} + {w[j]:08x}) mod 2^32 = {temp1:08x}")

            print(f"   S0 = right_rotate(a,2) XOR right_rotate(a,13) XOR right_rotate(a,22)")
            print(f"      = ({right_rotate(a,2):08x} XOR {right_rotate(a,13):08x} XOR {right_rotate(a,22):08x}) = {S0:08x}")
            print(f"   maj = (a AND b) XOR (a AND c) XOR (b AND c)")
            print(f"      = ({a:08x} AND {b:08x}) XOR ({a:08x} AND {c:08x}) XOR ({b:08x} AND {c:08x}) = {maj:08x}")
            print(f"   temp2 = (S0 + maj) mod 2^32")
            print(f"         = ({S0:08x} + {maj:08x}) mod 2^32 = {temp2:08x}")

            # Update the working variables
            new_h = g
            new_g = f
            new_f = e
            new_e = (d + temp1) & 0xffffffff
            new_d = c
            new_c = b
            new_b = a
            new_a = (temp1 + temp2) & 0xffffffff

            print("\nUpdated working variables:")
            print(f"   a = temp1 + temp2 = {temp1:08x} + {temp2:08x} = {new_a:08x}")
            print(f"   b = previous a = {a:08x}")
            print(f"   c = previous b = {b:08x}")
            print(f"   d = previous c = {c:08x}")
            print(f"   e = d + temp1 = {d:08x} + {temp1:08x} = {new_e:08x}")
            print(f"   f = previous e = {e:08x}")
            print(f"   g = previous f = {f:08x}")
            print(f"   h = previous g = {g:08x}")
            
            # Assign new values for next round
            a, b, c, d, e, f, g, h_var = new_a, new_b, new_c, new_d, new_e, new_f, new_g, new_h

            pause(f"Finish round {j:02}:")

        # Update the hash values with results from this block
        H = [(old + new) & 0xffffffff for old, new in zip(H, [a, b, c, d, e, f, g, h_var])]
        print("\n=== Updated Hash Values after processing block ===")
        for idx, h_val in enumerate(H):
            print(f"H[{idx}] = {h_val:08x}")
        pause("Finish updating hash values for the block:")

    # Produce the final digest by concatenating the hash values
    final_digest = ''.join(f'{h_val:08x}' for h_val in H)
    return final_digest

# === Main Program ===
if __name__ == '__main__':
    msg = input("Enter message: ")
    digest = sha256(msg)
    print("\n=== Final SHA-256 Digest ===")
    print(digest)
