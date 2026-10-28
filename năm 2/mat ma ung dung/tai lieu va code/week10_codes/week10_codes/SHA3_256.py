import struct

# Rotation offsets r[x][y] for Keccak‐f[1600]
r = [
    [0,   36,   3,  41,  18],
    [1,   44,  10,  45,   2],
    [62,   6,  43,  15,  61],
    [28,  55,  25,  21,  56],
    [27,  20,  39,   8,  14],
]

# Round constants for Keccak‐f[1600]
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

def pause(desc=""):
    input(f"\n--- {desc} \nPress Enter to continue...")

def rotl(x, shift):
    """Rotate 64-bit word x LEFT by shift bits."""
    shift %= 64 # Ensure shift is within 0-63
    return ((x << shift) | (x >> (64 - shift))) & 0xFFFFFFFFFFFFFFFF

def keccak_f(state):
    """Perform the Keccak-f[1600] permutation on the 5×5 state with verbose output."""
    mask = 0xFFFFFFFFFFFFFFFF
    for rnd in range(24):
        print(f"\n===== Round {rnd} =====")

        # θ step
        C = [state[x][0] ^ state[x][1] ^ state[x][2] ^ state[x][3] ^ state[x][4] for x in range(5)]
        print("θ: C[x] = XOR of column x across all 5 lanes")
        for x in range(5):
            print(f"  C[{x}] = {C[x]:016x}")
        # Corrected: Use rotl (left rotate)
        D = [(C[(x-1)%5] ^ rotl(C[(x+1)%5], 1)) for x in range(5)]
        print("θ: D[x] = C[x-1] XOR ROTL(C[x+1],1)")
        for x in range(5):
            print(f"  D[{x}] = {D[x]:016x}")
        state_before_theta_xor = [[state[x][y] for y in range(5)] for x in range(5)] # Keep copy for printing
        for x in range(5):
            for y in range(5):
                state[x][y] ^= D[x]
                print(f"  state[{x}][{y}] ^= D[{x}] → {state_before_theta_xor[x][y]:016x} XOR {D[x]:016x} = {state[x][y]:016x}")
        pause("After θ")

        # ρ and π steps
        B = [[0]*5 for _ in range(5)]
        print("\nρ and π: rotate then permute")
        for x in range(5):
            for y in range(5):
                new_x, new_y = y, (2*x + 3*y) % 5
                # Corrected: Use rotl (left rotate)
                rotated = rotl(state[x][y], r[x][y])
                B[new_x][new_y] = rotated
                print(f"  B[{new_x}][{new_y}] = ROTL(state[{x}][{y}],{r[x][y]}) = {rotated:016x}")
        pause("After ρ and π")

        # χ step (state is updated using B)
        print("\nχ: non-linear mixing per row")
        state_before_chi = [[state[x][y] for y in range(5)] for x in range(5)] # Use B for calculation
        for x in range(5):
            for y in range(5):
                # Corrected: Apply 64-bit mask to the result of bitwise NOT
                state[x][y] = B[x][y] ^ (((~B[(x+1)%5][y]) & mask) & B[(x+2)%5][y])
                print(
                    f"  state[{x}][{y}] = B[{x}][{y}] XOR ((~B[{(x+1)%5}][{y}]) & B[{(x+2)%5}][{y}])\n"
                    f"               = {B[x][y]:016x} XOR ((~{B[(x+1)%5][y]:016x}) & {B[(x+2)%5][y]:016x}) = {state[x][y]:016x}"
                )
        pause("After χ")

        # ι step
        print("\nι: add round constant to state[0][0]")
        state_before_iota = state[0][0]
        state[0][0] ^= RC[rnd]
        print(f"  state[0][0] ^= RC[{rnd}] ({RC[rnd]:016x}) → {state_before_iota:016x} XOR {RC[rnd]:016x} = {state[0][0]:016x}")
        pause("After ι")

    return state

def sha3_256(message: str) -> str:
    """Compute SHA3-256 with step-by-step formulas and prints."""
    rate_bytes       = 136
    output_len_bytes = 32
    state = [[0]*5 for _ in range(5)]

    # 1) Show initial state
    print("=== Initial State ===")
    for x in range(5):
        for y in range(5):
            print(f"  A[{x},{y}] = {state[x][y]:016x}")
    pause("Initial state")

    # 2) Padding
    msg_bytes = message.encode("utf-8")
    print("\n=== Padding ===")
    print(f"  Original message bytes ({len(msg_bytes)}):")
    print("    " + " ".join(f"{b:02x}" for b in msg_bytes))

    padded = bytearray(msg_bytes)
    padded += b'\x06'
    print("\n  After appending domain separator 0x06:")
    print("    " + " ".join(f"{b:02x}" for b in padded))

    zeros_to_add = (rate_bytes - 1 - len(padded) % rate_bytes) % rate_bytes
    padded += b'\x00' * zeros_to_add
    print(f"\n  After padding with {zeros_to_add} zero byte(s):")
    print("    " + " ".join(f"{b:02x}" for b in padded))

    padded += b'\x80'
    print("\n  After appending final 0x80 bit:")
    print("    " + " ".join(f"{b:02x}" for b in padded))

    print(f"\n  Total padded length: {len(padded)} bytes (should be multiple of {rate_bytes})")
    pause("End of padding")

    # 3) Absorb phase
    print("\n=== Absorb Phase ===")
    for blk_idx in range(0, len(padded), rate_bytes):
        block = padded[blk_idx:blk_idx+rate_bytes]
        print(f"\n-- Block {blk_idx // rate_bytes} ({len(block)} bytes) --")
        print("   Block data:")
        print("     " + " ".join(f"{b:02x}" for b in block))

        # XOR into state
        for i in range(rate_bytes // 8):
            x, y = i % 5, i // 5
            lane = int.from_bytes(block[8*i:8*i+8], 'little')
            before = state[x][y]
            state[x][y] ^= lane
            print(f"   A[{x},{y}] = {before:016x} ⊕ {lane:016x} = {state[x][y]:016x}")

        pause(f"After XOR of block {blk_idx // rate_bytes}")
        state = keccak_f(state)

    # 4) Squeeze phase
    print("\n=== Squeeze Phase ===")
    output_bytes = bytearray()
    squeeze_round = 0
    while len(output_bytes) < output_len_bytes:
        print(f"\n-- Extracting round {squeeze_round} --")
        chunk_bytes = bytearray()
        for i in range(rate_bytes // 8):
            x, y = i % 5, i // 5
            lane_bytes = state[x][y].to_bytes(8, 'little')
            print(f"   A[{x},{y}] = {state[x][y]:016x} → {lane_bytes.hex()}")
            chunk_bytes += lane_bytes
            if len(output_bytes) + len(chunk_bytes) >= output_len_bytes:
                break

        need = output_len_bytes - len(output_bytes)
        output_bytes += chunk_bytes[:need]
        print(f"   Collected {need} byte(s), total {len(output_bytes)}/{output_len_bytes}")
        if len(output_bytes) < output_len_bytes:
            pause(f"Before keccak_f for squeeze round {squeeze_round+1}")
            state = keccak_f(state)
            squeeze_round += 1
        else:
            pause("Finished squeezing")

    digest = output_bytes.hex()
    print(f"\n=== Final SHA3-256 Digest ===\n{digest}")
    return digest

# === Main Program ===
if __name__ == "__main__":
    msg = input("Enter message: ")
    sha3_256(msg)