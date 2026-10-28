import struct
# We use A[x,y]=A[x,y,0..63] instead of A[x,y,z] for z=0...63
# 1D array of 25 lanes
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
    0x0000000000000001, 0x0000000000008082,
    0x800000000000808A, 0x8000000080008000,
    0x000000000000808B, 0x0000000080000001,
    0x8000000080008081, 0x8000000000008009,
    0x000000000000008A, 0x0000000000000088,
    0x0000000080008009, 0x000000008000000A,
    0x000000008000808B, 0x800000000000008B,
    0x8000000000008089, 0x8000000000008003,
    0x8000000000008002, 0x8000000000000080,
    0x000000000000800A, 0x800000008000000A,
    0x8000000080008081, 0x8000000000008080,
    0x0000000080000001, 0x8000000080008008
]

MASK64 = 0xFFFFFFFFFFFFFFFF

def pause(desc=""):
    input(f"\n--- {desc} ---\nPress Enter to continue...")

def rotl(x, shift):
    """Left-rotate 64-bit word x by shift bits."""
    s = shift % 64
    return ((x << s) | (x >> (64 - s))) & MASK64

def pad10x1(m: bytes, rate: int, suffix: int = 0x06) -> bytearray:
    """
    FIPS202 pad10*1:
      1) append suffix byte (0x06)
      2) append 0x00 until (len(m)+len(pad))%rate == rate-1
      3) append final 0x80 byte
    """
    pad = bytearray([suffix])
    while (len(m) + len(pad)) % rate != rate - 1:
        pad.append(0x00)
    pad.append(0x80)
    return pad

def keccak_f(state):
    """Keccak-f[1600] permutation with formula prints."""
    for rnd in range(24):
        # θ step
        print(f"\n===== Round {rnd}: θ =====")
        print("θ: C[x] = A[x,0] ⊕ A[x,1] ⊕ A[x,2] ⊕ A[x,3] ⊕ A[x,4]")
        C = [(state[x][0] ^ state[x][1] ^ state[x][2] ^ state[x][3] ^ state[x][4]) & MASK64
             for x in range(5)]
        for x in range(5):
            print(f"  C[{x}] = {C[x]:016x}")

        print("θ: D[x] = C[x−1] ⊕ ROTL(C[x+1],1)")
        D = [ (C[(x-1)%5] ^ rotl(C[(x+1)%5],1)) & MASK64 for x in range(5) ]
        for x in range(5):
            print(f"  D[{x}] = {D[x]:016x}")

        print("θ: A[x,y] = A[x,y] ⊕ D[x]")
        for x in range(5):
            for y in range(5):
                before = state[x][y]
                state[x][y] = (before ^ D[x]) & MASK64
                print(f"  A[{x},{y}] = {before:016x} ⊕ {D[x]:016x} = {state[x][y]:016x}")
        pause("after θ")

        # ρ + π steps
        print(f"\n===== Round {rnd}: ρ + π =====")
        print("ρ: ROTL(A[x,y], r[x][y])")
        print("π: B[y,(2x+3y)%5] = ρ-result")
        B = [[0]*5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                rotv = rotl(state[x][y], r[x][y])
                nx, ny = y, (2*x + 3*y) % 5
                B[nx][ny] = rotv
                print(f"  B[{nx},{ny}] = ROTL(A[{x},{y}],{r[x][y]}) = {rotv:016x}")
        pause("after ρ+π")

        # χ step
        print(f"\n===== Round {rnd}: χ =====")
        print("χ: A'[x,y] = B[x,y] ⊕ ((¬B[x+1,y]) & B[x+2,y])")
        newA = [[0]*5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                nb = (~B[(x+1)%5][y] & MASK64)
                newA[x][y] = (B[x][y] ^ (nb & B[(x+2)%5][y])) & MASK64
                print(
                    f"  A'[{x},{y}] = {B[x][y]:016x} ⊕ "
                    f"((~{B[(x+1)%5][y]:016x}) & {B[(x+2)%5][y]:016x}) = {newA[x][y]:016x}"
                )
        state[:] = newA
        pause("after χ")

        # ι step
        print(f"\n===== Round {rnd}: ι =====")
        print("ι: A[0,0] = A[0,0] ⊕ RC[rnd]")
        before = state[0][0]
        state[0][0] = (before ^ RC[rnd]) & MASK64
        print(f"  A[0,0] = {before:016x} ⊕ {RC[rnd]:016x} = {state[0][0]:016x}")
        pause("after ι")

    return state

def sha3_512(message: str) -> str:
    """Compute SHA3-512 with full formula prints at each step."""
    rate = 576//8           # 72 bytes
    out_len = 512//8        # 64 bytes
    state = [[0]*5 for _ in range(5)]

    # Initial state
    print("=== Initial State ===")
    for x in range(5):
        for y in range(5):
            print(f"  A[{x},{y}] = {state[x][y]:016x}")
    pause("initialization")

    # Padding
    m = message.encode('utf-8')
    print("\n=== Padding ===")
    print(f"  Message bytes ({len(m)}): {' '.join(f'{b:02x}' for b in m)}")
    pad = pad10x1(m, rate, suffix=0x06)
    print(f"  pad10*1 = {' '.join(f'{b:02x}' for b in pad)}")
    padded = m + pad
    print(f"  Total length after padding: {len(padded)} (should ≡ 0 mod {rate})")
    pause("padding complete")

    # Absorb phase
    print("\n=== Absorb Phase ===")
    for blk in range(0, len(padded), rate):
        idx = blk // rate
        chunk = padded[blk:blk+rate]
        print(f"\n-- Block {idx} --")
        for i in range(rate//8):
            x,y = i%5, i//5
            lane = int.from_bytes(chunk[8*i:8*i+8],'little')
            before = state[x][y]
            state[x][y] = (before ^ lane) & MASK64
            print(f"  A[{x},{y}] = {before:016x} ⊕ {lane:016x} = {state[x][y]:016x}")
        pause(f"after XOR block {idx}")
        state = keccak_f(state)

    # Squeeze phase
    print("\n=== Squeeze Phase ===")
    out = bytearray()
    round_idx = 0
    while len(out) < out_len:
        print(f"\n-- Squeezing round {round_idx} --")
        buf = bytearray()
        for i in range(rate//8):
            x,y = i%5, i//5
            lb = state[x][y].to_bytes(8,'little')
            print(f"  A[{x},{y}] = {state[x][y]:016x} → {lb.hex()}")
            buf += lb
            if len(out)+len(buf) >= out_len:
                break
        need = out_len - len(out)
        out += buf[:need]
        print(f"  Collected {need} bytes, total {len(out)}/{out_len}")
        if len(out) < out_len:
            pause(f"before keccak_f for squeeze round {round_idx+1}")
            state = keccak_f(state)
            round_idx += 1
        else:
            pause("squeeze complete")

    digest = out.hex()
    print(f"\n=== Final SHA3-512 Digest ===\n{digest}")
    return digest

if __name__ == "__main__":
    msg = input("Enter message: ")
    sha3_512(msg)
