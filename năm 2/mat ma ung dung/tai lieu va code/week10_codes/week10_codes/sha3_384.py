import struct

# Rotation offsets r[x][y] for Keccak-f[1600]
r = [
    [0,   36,   3,  41,  18],
    [1,   44,  10,  45,   2],
    [62,   6,  43,  15,  61],
    [28,  55,  25,  21,  56],
    [27,  20,  39,   8,  14],
]

# Round constants for Keccak-f[1600]
RC = [
    0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
    0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
    0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
    0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
    0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
    0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008
]

MASK64 = 0xFFFFFFFFFFFFFFFF

def pause(desc=""):
    input(f"\n--- {desc} ---\nPress Enter to continue...")

def rotl(x, shift):
    """Rotate 64-bit word x LEFT by shift bits."""
    s = shift % 64
    return ((x << s) | (x >> (64 - s))) & MASK64

def pad10x1(m: bytes, rate: int, suffix: int = 0x06) -> bytearray:
    """
    FIPS202 pad10*1:
      1) append one byte = suffix
      2) append 0x00 until (len(m)+len(pad)) % rate == rate-1
      3) append one byte 0x80
    """
    pad = bytearray([suffix])
    while (len(m) + len(pad)) % rate != rate - 1:
        pad.append(0x00)
    pad.append(0x80)
    return pad

def keccak_f(state):
    """Verbose Keccak-f[1600] permutation on 5×5 lanes."""
    for rnd in range(24):
        # θ step
        print(f"\n===== Round {rnd}: θ =====")
        C = [(state[x][0] ^ state[x][1] ^ state[x][2] ^ state[x][3] ^ state[x][4]) & MASK64
             for x in range(5)]
        print("θ formula: C[x] = A[x,0] ⊕ A[x,1] ⊕ A[x,2] ⊕ A[x,3] ⊕ A[x,4]")
        for x in range(5):
            print(f"  C[{x}] = {C[x]:016x}")
        D = [ (C[(x-1)%5] ^ rotl(C[(x+1)%5],1)) & MASK64 for x in range(5) ]
        print("θ formula: D[x] = C[x-1] ⊕ ROTL(C[x+1],1)")
        for x in range(5):
            print(f"  D[{x}] = {D[x]:016x}")
        for x in range(5):
            for y in range(5):
                before = state[x][y]
                state[x][y] = (before ^ D[x]) & MASK64
                print(f"  A[{x},{y}] = {before:016x} ⊕ {D[x]:016x} = {state[x][y]:016x}")
        pause("after θ")

        # ρ + π steps
        print(f"\n===== Round {rnd}: ρ + π =====")
        B = [[0]*5 for _ in range(5)]
        print("ρ+π formula: B[y,(2x+3y)%5] = ROTL(A[x,y], r[x][y])")
        for x in range(5):
            for y in range(5):
                rotated = rotl(state[x][y], r[x][y])
                new_x, new_y = y, (2*x + 3*y) % 5
                B[new_x][new_y] = rotated
                print(f"  B[{new_x},{new_y}] = ROTL(A[{x},{y}],{r[x][y]}) = {rotated:016x}")
        pause("after ρ+π")

        # χ step
        print(f"\n===== Round {rnd}: χ =====")
        print("χ formula: A'[x,y] = B[x,y] ⊕ ((¬B[x+1,y]) & B[x+2,y])")
        A_prime = [[0]*5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                nb = (~B[(x+1)%5][y] & MASK64)
                A_prime[x][y] = (B[x][y] ^ (nb & B[(x+2)%5][y])) & MASK64
                print(
                    f"  A'[{x},{y}] = {B[x][y]:016x} ⊕ "
                    f"((~{B[(x+1)%5][y]:016x}) & {B[(x+2)%5][y]:016x}) = {A_prime[x][y]:016x}"
                )
        state[:] = A_prime
        pause("after χ")

        # ι step
        print(f"\n===== Round {rnd}: ι =====")
        before = state[0][0]
        state[0][0] = (before ^ RC[rnd]) & MASK64
        print(f"ι formula: A[0,0] = A[0,0] ⊕ RC[{rnd}]")
        print(f"  = {before:016x} ⊕ {RC[rnd]:016x} = {state[0][0]:016x}")
        pause("after ι")

    return state

def sha3_384(message: str) -> str:
    """Compute SHA3-384 with detailed step-by-step prints."""
    rate_bytes       = (1600 - 768) // 8    # 104 bytes
    output_len_bytes = 384 // 8            # 48 bytes
    state = [[0]*5 for _ in range(5)]

    # Initial state
    print("=== Initial State ===")
    for x in range(5):
        for y in range(5):
            print(f"  A[{x},{y}] = {state[x][y]:016x}")
    pause("initialization")

    # Padding
    msg = message.encode('utf-8')
    print("\n=== Padding ===")
    print(f"  Original bytes ({len(msg)}): {' '.join(f'{b:02x}' for b in msg)}")
    pad = pad10x1(msg, rate_bytes, suffix=0x06)
    padded = msg + pad
    print(f"  pad10*1 suffix+zeros+0x80 → {' '.join(f'{b:02x}' for b in pad)}")
    print(f"  Padded length: {len(padded)} bytes (multiple of {rate_bytes})")
    pause("padding complete")

    # Absorb phase
    print("\n=== Absorb Phase ===")
    for blk in range(0, len(padded), rate_bytes):
        blk_idx = blk // rate_bytes
        block = padded[blk:blk+rate_bytes]
        print(f"\n-- Block {blk_idx} ({len(block)} bytes) --")
        for i in range(rate_bytes // 8):
            x, y = i % 5, i // 5
            chunk = int.from_bytes(block[8*i:8*i+8], 'little')
            before = state[x][y]
            state[x][y] = (before ^ chunk) & MASK64
            print(f"  A[{x},{y}] = {before:016x} ⊕ {chunk:016x} = {state[x][y]:016x}")
        pause(f"after XOR block {blk_idx}")
        state = keccak_f(state)

    # Squeeze phase
    print("\n=== Squeeze Phase ===")
    output = bytearray()
    round_idx = 0
    while len(output) < output_len_bytes:
        print(f"\n-- Squeezing round {round_idx} --")
        temp = bytearray()
        for i in range(rate_bytes // 8):
            x, y = i % 5, i // 5
            lb = state[x][y].to_bytes(8, 'little')
            print(f"  A[{x},{y}] = {state[x][y]:016x} → {lb.hex()}")
            temp += lb
            if len(output) + len(temp) >= output_len_bytes:
                break
        need = output_len_bytes - len(output)
        output += temp[:need]
        print(f"  Collected {need} bytes, total {len(output)}/{output_len_bytes}")
        if len(output) < output_len_bytes:
            pause(f"before keccak_f for squeeze round {round_idx+1}")
            state = keccak_f(state)
            round_idx += 1
        else:
            pause("squeeze complete")

    digest = output.hex()
    print(f"\n=== Final SHA3-384 Digest ===\n{digest}")
    return digest

# Main
if __name__ == "__main__":
    msg = input("Enter message: ")
    sha3_384(msg)
