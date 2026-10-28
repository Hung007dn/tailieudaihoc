import numpy as np
from PIL import Image
import os

class HenonMap:
    def __init__(self, x0=0.1, y0=0.1, a=1.4, b=0.3):
        self.x = x0
        self.y = y0
        self.a = a
        self.b = b
        self.initial_x = x0
        self.initial_y = y0
    
    def reset(self):
        self.x = self.initial_x
        self.y = self.initial_y
    
    def next(self):
        x_next = 1 - self.a * self.x**2 + self.y
        y_next = self.b * self.x
        self.x, self.y = x_next, y_next
        return self.x, self.y
    
    def generate_sbox(self, size=256):
        self.reset()
        seq = []
        for _ in range(size * 2):
            seq.append(abs(self.next()[0]))
        
        normalized = [int(s * 255) % 256 for s in seq]
        sbox = []
        seen = set()
        for val in normalized:
            if val not in seen and len(sbox) < size:
                sbox.append(val)
                seen.add(val)
        
        for i in range(256):
            if i not in seen and len(sbox) < size:
                sbox.append(i)
                seen.add(i)
        return sbox
    
    def generate_dynamic_sbox(self, block_index):
        self.reset()
        self.x = (self.x + block_index * 0.001) % 1
        self.y = (self.y + block_index * 0.001) % 1
        return self.generate_sbox()

class LogisticMap:
    def __init__(self, x0=0.5, r=3.99):
        self.x = x0
        self.r = r
        self.initial_x = x0
    
    def reset(self):
        self.x = self.initial_x
    
    def next(self):
        self.x = self.r * self.x * (1 - self.x)
        return self.x
    
    def generate_permutation(self, n):
        self.reset()
        seq = [self.next() for _ in range(n)]
        indexed = list(enumerate(seq))
        indexed.sort(key=lambda x: x[1])
        return [i for i, _ in indexed]
    
    def generate_keystream(self, n):
        self.reset()
        seq = [self.next() for _ in range(n)]
        return bytes([int(s * 255) % 256 for s in seq])
    
    def generate_shift_pattern(self, block_index):
        self.reset()
        self.x = (self.x + block_index * 0.0001) % 1
        shifts = []
        for _ in range(4):
            self.next()
            shift = int(self.x * 4) % 4
            shifts.append(shift)
        return shifts

class ChaoticAES_Full:
    def __init__(self, master_key, henon_seeds=(0.1, 0.1), logistic_seed=0.5):
        self.master_key = master_key
        self.henon = HenonMap(henon_seeds[0], henon_seeds[1])
        self.logistic = LogisticMap(logistic_seed)
    
    def _sub_bytes(self, data, sbox):
        return bytes([sbox[b] for b in data])
    
    def _shift_rows_dynamic(self, data, shift_pattern):
        state = list(data)
        shift1 = shift_pattern[0] % 4
        new_state = state[:]
        for i in range(4):
            new_state[4 + i] = state[4 + (i - shift1) % 4]
        shift2 = shift_pattern[1] % 4
        for i in range(4):
            new_state[8 + i] = state[8 + (i - shift2) % 4]
        shift3 = shift_pattern[2] % 4
        for i in range(4):
            new_state[12 + i] = state[12 + (i - shift3) % 4]
        return bytes(new_state)
    
    def _inv_shift_rows_dynamic(self, data, shift_pattern):
        state = list(data)
        shift1 = shift_pattern[0] % 4
        new_state = state[:]
        for i in range(4):
            new_state[4 + (i - shift1) % 4] = state[4 + i]
        shift2 = shift_pattern[1] % 4
        for i in range(4):
            new_state[8 + (i - shift2) % 4] = state[8 + i]
        shift3 = shift_pattern[2] % 4
        for i in range(4):
            new_state[12 + (i - shift3) % 4] = state[12 + i]
        return bytes(new_state)
    
    def _mix_columns(self, data):
        def mul(a, b):
            res = 0
            for _ in range(8):
                if b & 1:
                    res ^= a
                a <<= 1
                if a & 0x100:
                    a ^= 0x11B
                b >>= 1
            return res & 0xFF
        
        state = list(data)
        for col in range(4):
            s0, s1, s2, s3 = state[col*4], state[col*4+1], state[col*4+2], state[col*4+3]
            state[col*4] = mul(s0, 2) ^ mul(s1, 3) ^ s2 ^ s3
            state[col*4+1] = s0 ^ mul(s1, 2) ^ mul(s2, 3) ^ s3
            state[col*4+2] = s0 ^ s1 ^ mul(s2, 2) ^ mul(s3, 3)
            state[col*4+3] = mul(s0, 3) ^ s1 ^ s2 ^ mul(s3, 2)
        return bytes(state)
    
    def _inv_mix_columns(self, data):
        def mul(a, b):
            res = 0
            for _ in range(8):
                if b & 1:
                    res ^= a
                a <<= 1
                if a & 0x100:
                    a ^= 0x11B
                b >>= 1
            return res & 0xFF
        
        state = list(data)
        for col in range(4):
            s0, s1, s2, s3 = state[col*4], state[col*4+1], state[col*4+2], state[col*4+3]
            state[col*4] = mul(s0, 14) ^ mul(s1, 11) ^ mul(s2, 13) ^ mul(s3, 9)
            state[col*4+1] = mul(s0, 9) ^ mul(s1, 14) ^ mul(s2, 11) ^ mul(s3, 13)
            state[col*4+2] = mul(s0, 13) ^ mul(s1, 9) ^ mul(s2, 14) ^ mul(s3, 11)
            state[col*4+3] = mul(s0, 11) ^ mul(s1, 13) ^ mul(s2, 9) ^ mul(s3, 14)
        return bytes(state)
    
    def _add_round_key(self, data, round_key):
        return bytes(a ^ b for a, b in zip(data, round_key))
    
    def _key_expansion(self, sbox):
        round_keys = [self.master_key]
        for r in range(10):
            prev = round_keys[-1]
            new_key = bytearray(16)
            for i in range(16):
                new_key[i] = prev[i] ^ sbox[(prev[(i+1) % 16] + r) % 256]
            round_keys.append(bytes(new_key))
        return round_keys
    
    def encrypt_block(self, block, block_index):
        sbox = self.henon.generate_dynamic_sbox(block_index)
        shift_pattern = self.logistic.generate_shift_pattern(block_index)
        round_keys = self._key_expansion(sbox)
        
        state = self._add_round_key(block, round_keys[0])
        for r in range(1, 10):
            state = self._sub_bytes(state, sbox)
            state = self._shift_rows_dynamic(state, shift_pattern)
            state = self._mix_columns(state)
            state = self._add_round_key(state, round_keys[r])
        
        state = self._sub_bytes(state, sbox)
        state = self._shift_rows_dynamic(state, shift_pattern)
        state = self._add_round_key(state, round_keys[10])
        return state
    
    def decrypt_block(self, block, block_index):
        sbox = self.henon.generate_dynamic_sbox(block_index)
        inv_sbox = [0] * 256
        for i, val in enumerate(sbox):
            inv_sbox[val] = i
        
        shift_pattern = self.logistic.generate_shift_pattern(block_index)
        round_keys = self._key_expansion(sbox)
        
        state = self._add_round_key(block, round_keys[10])
        state = self._inv_shift_rows_dynamic(state, shift_pattern)
        state = self._sub_bytes(state, inv_sbox)
        
        for r in range(9, 0, -1):
            state = self._add_round_key(state, round_keys[r])
            state = self._inv_mix_columns(state)
            state = self._inv_shift_rows_dynamic(state, shift_pattern)
            state = self._sub_bytes(state, inv_sbox)
        
        state = self._add_round_key(state, round_keys[0])
        return state
    
    def chaotic_preprocess(self, data_bytes):
        n = len(data_bytes)
        perm = self.logistic.generate_permutation(n)
        permuted = bytes([data_bytes[i] for i in perm])
        
        keystream = self.logistic.generate_keystream(n)
        result = bytearray()
        prev = 0
        for i in range(n):
            val = permuted[i] ^ keystream[i] ^ prev
            result.append(val)
            prev = val
        return bytes(result)
    
    def inverse_chaotic_preprocess(self, processed_bytes):
        n = len(processed_bytes)
        
        temp = bytearray()
        prev = 0
        for i in range(n):
            val = processed_bytes[i] ^ prev
            temp.append(val)
            prev = processed_bytes[i]
        
        keystream = self.logistic.generate_keystream(n)
        xor_result = bytes(temp[i] ^ keystream[i] for i in range(n))
        
        perm = self.logistic.generate_permutation(n)
        inv_perm = [0] * n
        for i, p in enumerate(perm):
            inv_perm[p] = i
        
        return bytes([xor_result[inv_perm[i]] for i in range(n)])
    
    def post_encrypt_diffusion(self, data_bytes):
        result = bytearray()
        prev = 0
        for b in data_bytes:
            val = b ^ prev
            result.append(val)
            prev = val
        return bytes(result)
    
    def inverse_post_diffusion(self, processed_bytes):
        result = bytearray()
        prev = 0
        for b in processed_bytes:
            val = b ^ prev
            result.append(val)
            prev = b
        return bytes(result)

class ColorImageEncryptor:
    
    def __init__(self, key=None):
        self.key = key or os.urandom(16)
    
    def encrypt(self, input_path, output_path):
        print("\n" + "="*60)
        print("CHAOTIC AES ENCRYPTION")
        print("="*60)
        
        
        img = Image.open(input_path)
        mode = img.mode 
        print(f"[1] Loaded: {input_path} ({img.size[0]}x{img.size[1]}, mode={mode})")
        
        # Chuyển ảnh thành bytes
        img_bytes = np.array(img).tobytes()
        
        print(f"[2] Key: {self.key.hex()}")
        
        chaotic = ChaoticAES_Full(self.key)
        
        print("[3] Chaotic preprocessing...")
        preprocessed = chaotic.chaotic_preprocess(img_bytes)
        
        print("[4] AES encryption with dynamic S-box...")
        iv = os.urandom(16)
        prev_block = iv
        encrypted_blocks = []
        
        for i in range(0, len(preprocessed), 16):
            block = preprocessed[i:i+16]
            if len(block) < 16:
                block = block + b'\x00' * (16 - len(block))
            
            xored = bytes(a ^ b for a, b in zip(block, prev_block))
            block_index = i // 16
            encrypted = chaotic.encrypt_block(xored, block_index)
            encrypted_blocks.append(encrypted)
            prev_block = encrypted
        
        ciphertext = b''.join(encrypted_blocks)[:len(img_bytes)]
        
        print("[5] Post-encryption diffusion...")
        final_cipher = chaotic.post_encrypt_diffusion(ciphertext)
        
        # Lưu ảnh với đúng mode gốc
        encrypted_img = Image.frombytes(mode, img.size, final_cipher)
        encrypted_img.save(output_path)
        print(f"[6] Saved: {output_path}")
        
        # Lưu metadata (key, iv, mode)
        with open(output_path + '.iv', 'wb') as f:
            f.write(iv)
        with open(output_path + '.key', 'w') as f:
            f.write(self.key.hex())
        with open(output_path + '.mode', 'w') as f:
            f.write(mode)
        
        print("[7] Encryption complete!")
        return self.key
    
    def decrypt(self, input_path, output_path, key_hex):
        print("\n" + "="*60)
        print("CHAOTIC AES DECRYPTION")
        print("="*60)
        
        key = bytes.fromhex(key_hex)
        
        # Đọc mode gốc
        mode_file = input_path + '.mode'
        if os.path.exists(mode_file):
            with open(mode_file, 'r') as f:
                mode = f.read().strip()
        else:
            mode = 'L'  # mặc định grayscale
        
        img = Image.open(input_path)
        img_bytes = np.array(img).tobytes()
        
        print(f"[1] Loaded: {input_path} ({img.size[0]}x{img.size[1]}, mode={mode})")
        print(f"[2] Key: {key.hex()}")
        
        with open(input_path + '.iv', 'rb') as f:
            iv = f.read(16)
        print(f"[3] IV loaded")
        
        chaotic = ChaoticAES_Full(key)
        
        print("[4] Inverse post-encryption diffusion...")
        post_inv = chaotic.inverse_post_diffusion(img_bytes)
        
        print("[5] AES decryption...")
        prev_block = iv
        decrypted_blocks = []
        
        for i in range(0, len(post_inv), 16):
            block = post_inv[i:i+16]
            if len(block) < 16:
                block = block + b'\x00' * (16 - len(block))
            
            block_index = i // 16
            decrypted = chaotic.decrypt_block(block, block_index)
            xored = bytes(a ^ b for a, b in zip(decrypted, prev_block))
            decrypted_blocks.append(xored)
            prev_block = block
        
        decrypted = b''.join(decrypted_blocks)[:len(img_bytes)]
        
        print("[6] Inverse chaotic preprocessing...")
        plain = chaotic.inverse_chaotic_preprocess(decrypted)
        
        # Lưu với đúng mode gốc
        decrypted_img = Image.frombytes(mode, img.size, plain)
        decrypted_img.save(output_path)
        print(f"[7] Saved: {output_path}")
        
        print("[8] Decryption complete!")
        return plain

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("="*60)
        print("CHAOTIC AES IMAGE ENCRYPTION")
        print("="*60)
        print("\nUSAGE:")
        print("  Encrypt: python Task02.py encrypt <input> <output>")
        print("  Decrypt: python Task02.py decrypt <input> <output> <key_hex>")
        print("  Demo:    python Task02.py demo")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "encrypt" and len(sys.argv) >= 4:
        enc = ColorImageEncryptor()
        key = enc.encrypt(sys.argv[2], sys.argv[3])
        print(f"\n✓ SAVE THIS KEY: {key.hex()}")
    
    elif cmd == "decrypt" and len(sys.argv) >= 5:
        enc = ColorImageEncryptor()
        enc.decrypt(sys.argv[2], sys.argv[3], sys.argv[4])
        print(f"\n✓ Decryption complete!")
    
    elif cmd == "demo":
        print("\n" + "="*60)
        print("DEMO MODE")
        print("="*60)
        
        # Tạo ảnh màu test
        test_img = "demo_test.png"
        if not os.path.exists(test_img):
            img = Image.new('RGB', (256, 256))
            for i in range(256):
                for j in range(256):
                    img.putpixel((i, j), (i % 255, j % 255, (i+j) % 255))
            img.save(test_img)
            print(f"Created: {test_img}")
        
        enc = ColorImageEncryptor()
        key = enc.encrypt(test_img, "demo_encrypted.png")
        enc.decrypt("demo_encrypted.png", "demo_decrypted.png", key.hex())
        
        original = np.array(Image.open(test_img)).tobytes()
        decrypted = np.array(Image.open("demo_decrypted.png")).tobytes()
        print(f"\n✓ Verification: {original == decrypted}")

