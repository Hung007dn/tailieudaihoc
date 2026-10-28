import sys
import ctypes
import re
import base64
import secrets
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog

# ---------- LOAD DLL ----------
dll_path = Path(__file__).parent / "evp_aes_direct.dll"
if not dll_path.exists():
    raise FileNotFoundError(f"Không tìm thấy {dll_path}")
lib = ctypes.CDLL(str(dll_path))

# ---------- CONSTANTS ----------
EVPAESDIRECT_OK = 0

# ---------- DECLARE FUNCTIONS ----------
lib.evpaesdirect_encrypt.restype = ctypes.c_int
lib.evpaesdirect_decrypt.restype = ctypes.c_int
lib.evpaesdirect_hex_to_bytes.restype = ctypes.c_int
lib.evpaesdirect_bytes_to_hex.restype = ctypes.c_int
lib.evpaesdirect_last_error.restype = ctypes.c_char_p

def last_error():
    err = lib.evpaesdirect_last_error()
    return err.decode() if err else "Unknown error"

def check_status(status, msg):
    if status != EVPAESDIRECT_OK:
        raise RuntimeError(f"{msg}: {last_error()} (code {status})")

# ---------- WRAPPER ----------
class EVP:
    @staticmethod
    def hex_to_bytes(hex_str):
        hex_str = re.sub(r'[\s\-:]', '', hex_str)
        if not hex_str:
            return b''
        if len(hex_str) % 2 != 0:
            raise ValueError("Hex length must be even")
        out_size = len(hex_str)//2 + 16
        out_buf = (ctypes.c_uint8 * out_size)()
        out_len = ctypes.c_size_t()
        status = lib.evpaesdirect_hex_to_bytes(
            hex_str.encode(),
            ctypes.cast(out_buf, ctypes.c_void_p),
            out_size,
            ctypes.byref(out_len)
        )
        check_status(status, "hex_to_bytes")
        return bytes(out_buf[:out_len.value])

    @staticmethod
    def bytes_to_hex(data):
        if not data:
            return ''
        hex_buf = ctypes.create_string_buffer(len(data)*2 + 1)
        out_len = ctypes.c_size_t()
        status = lib.evpaesdirect_bytes_to_hex(
            ctypes.cast(data, ctypes.c_void_p), len(data),
            hex_buf, len(hex_buf),
            ctypes.byref(out_len)
        )
        check_status(status, "bytes_to_hex")
        return hex_buf.value.decode()

    @staticmethod
    def encrypt(cipher, key, iv, plaintext, padding):
        out_size = len(plaintext) + 128
        out_buf = (ctypes.c_uint8 * out_size)()
        out_len = ctypes.c_size_t()
        status = lib.evpaesdirect_encrypt(
            cipher.encode(),
            ctypes.cast(key, ctypes.c_void_p), len(key),
            ctypes.cast(iv, ctypes.c_void_p), len(iv),
            ctypes.cast(plaintext, ctypes.c_void_p), len(plaintext),
            1 if padding else 0,
            ctypes.cast(out_buf, ctypes.c_void_p), out_size,
            ctypes.byref(out_len)
        )
        check_status(status, "encrypt")
        return bytes(out_buf[:out_len.value])

    @staticmethod
    def decrypt(cipher, key, iv, ciphertext, padding):
        out_size = len(ciphertext) + 128
        out_buf = (ctypes.c_uint8 * out_size)()
        out_len = ctypes.c_size_t()
        status = lib.evpaesdirect_decrypt(
            cipher.encode(),
            ctypes.cast(key, ctypes.c_void_p), len(key),
            ctypes.cast(iv, ctypes.c_void_p), len(iv),
            ctypes.cast(ciphertext, ctypes.c_void_p), len(ciphertext),
            1 if padding else 0,
            ctypes.cast(out_buf, ctypes.c_void_p), out_size,
            ctypes.byref(out_len)
        )
        check_status(status, "decrypt")
        return bytes(out_buf[:out_len.value])

# ---------- GUI ----------
class AESTool:
    def __init__(self, root):
        self.root = root
        root.title("AES Encryption Tool - OpenSSL EVP Direct API")
        root.geometry("1500x700")
        root.configure(bg='#f0f0f0')

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#f0f0f0')
        style.configure('TLabelframe', background='#f0f0f0')
        style.configure('TLabelframe.Label', background='#f0f0f0')

        # Main container with 3 columns using grid
        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1, uniform='col')
        main_frame.columnconfigure(1, weight=1, uniform='col')
        main_frame.columnconfigure(2, weight=1, uniform='col')
        main_frame.rowconfigure(0, weight=1)

        self.create_encrypt_panel(main_frame, 0)
        self.create_utils_panel(main_frame, 1)
        self.create_decrypt_panel(main_frame, 2)

        self.status = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    # ---------- LEFT PANEL: ENCRYPT ----------
    def create_encrypt_panel(self, parent, col):
        frame = ttk.LabelFrame(parent, text="Encrypt", padding=10)
        frame.grid(row=0, column=col, sticky=tk.NSEW, padx=5)

        # Cipher settings
        cipher_frame = ttk.LabelFrame(frame, text="Cipher Settings", padding=5)
        cipher_frame.pack(fill=tk.X, pady=5)
        ttk.Label(cipher_frame, text="Cipher:").grid(row=0, column=0, sticky=tk.W)
        self.cipher_var = tk.StringVar(value="aes-128-cbc")
        cipher_combo = ttk.Combobox(cipher_frame, textvariable=self.cipher_var,
                                    values=["aes-128-cbc", "aes-192-cbc", "aes-256-cbc",
                                            "aes-128-ecb", "aes-192-ecb", "aes-256-ecb",
                                            "aes-128-ctr", "aes-192-ctr", "aes-256-ctr",
                                            "aes-128-gcm", "aes-192-gcm", "aes-256-gcm"])
        cipher_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        self.padding_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(cipher_frame, text="Enable PKCS#7 Padding", variable=self.padding_var).grid(row=1, column=0, columnspan=2, sticky=tk.W)

        # Key & IV
        keyiv_frame = ttk.LabelFrame(frame, text="Key & IV", padding=5)
        keyiv_frame.pack(fill=tk.X, pady=5)
        ttk.Label(keyiv_frame, text="Key (hex):").grid(row=0, column=0, sticky=tk.W)
        self.key_entry = ttk.Entry(keyiv_frame, width=50)
        self.key_entry.grid(row=0, column=1, padx=5)
        self.key_entry.insert(0, "000102030405060708090a0b0c0d0e0f")
        ttk.Label(keyiv_frame, text="IV (hex):").grid(row=1, column=0, sticky=tk.W)
        self.iv_entry = ttk.Entry(keyiv_frame, width=50)
        self.iv_entry.grid(row=1, column=1, padx=5)
        self.iv_entry.insert(0, "101112131415161718191a1b1c1d1e1f")

        # Plaintext
        plain_frame = ttk.LabelFrame(frame, text="Plaintext", padding=5)
        plain_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.plain_text = scrolledtext.ScrolledText(plain_frame, height=6)
        self.plain_text.pack(fill=tk.BOTH, expand=True)
        self.plain_text.insert('1.0', "hello 123")

        ttk.Button(frame, text="ENCRYPT", command=self.do_encrypt).pack(fill=tk.X, pady=5)

        result_frame = ttk.LabelFrame(frame, text="Ciphertext (hex)", padding=5)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.ciphertext_display = scrolledtext.ScrolledText(result_frame, height=4)
        self.ciphertext_display.pack(fill=tk.BOTH, expand=True)

        action_frame = ttk.Frame(frame)
        action_frame.pack(fill=tk.X, pady=5)
        ttk.Button(action_frame, text="Copy Hex", command=self.copy_cipher_hex).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Copy Base64", command=self.copy_cipher_base64).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Save to File", command=self.save_cipher_to_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Clear", command=self.clear_encrypt).pack(side=tk.LEFT, padx=2)

    # ---------- CENTER PANEL: UTILITIES ----------
    def create_utils_panel(self, parent, col):
        frame = ttk.LabelFrame(parent, text="File Operations & Tools", padding=10)
        frame.grid(row=0, column=col, sticky=tk.NSEW, padx=5)

        file_frame = ttk.LabelFrame(frame, text="File Encryption", padding=5)
        file_frame.pack(fill=tk.X, pady=5)
        ttk.Button(file_frame, text="Encrypt File", command=self.encrypt_file).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="Decrypt File", command=self.decrypt_file).pack(fill=tk.X, pady=2)

        gen_frame = ttk.LabelFrame(frame, text="Key/IV Generator", padding=5)
        gen_frame.pack(fill=tk.X, pady=5)
        ttk.Button(gen_frame, text="Generate Random Key", command=self.gen_key).pack(fill=tk.X, pady=2)
        ttk.Button(gen_frame, text="Generate Random IV", command=self.gen_iv).pack(fill=tk.X, pady=2)

        info_frame = ttk.LabelFrame(frame, text="Information", padding=5)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.info_text = scrolledtext.ScrolledText(info_frame, height=12, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.insert('1.0', "AES Tool using evp_aes_direct.dll\n\n"
                                     "- Supports CBC, ECB, CTR, GCM modes\n"
                                     "- Padding PKCS#7 for CBC/ECB\n"
                                     "- Key/IV must be hex strings\n"
                                     "- For GCM, use separate nonce (not yet in UI)\n"
                                     "  but you can extend easily.")
        self.info_text.config(state=tk.DISABLED)

    # ---------- RIGHT PANEL: DECRYPT ----------
    def create_decrypt_panel(self, parent, col):
        frame = ttk.LabelFrame(parent, text="Decrypt", padding=10)
        frame.grid(row=0, column=col, sticky=tk.NSEW, padx=5)

        ct_frame = ttk.LabelFrame(frame, text="Ciphertext (hex)", padding=5)
        ct_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.ciphertext_input = scrolledtext.ScrolledText(ct_frame, height=4)
        self.ciphertext_input.pack(fill=tk.BOTH, expand=True)

        ttk.Button(frame, text="DECRYPT", command=self.do_decrypt).pack(fill=tk.X, pady=5)

        result_frame = ttk.LabelFrame(frame, text="Decrypted Plaintext", padding=5)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.decrypted_display = scrolledtext.ScrolledText(result_frame, height=6)
        self.decrypted_display.pack(fill=tk.BOTH, expand=True)

        action_frame = ttk.Frame(frame)
        action_frame.pack(fill=tk.X, pady=5)
        ttk.Button(action_frame, text="Copy Text", command=self.copy_plain_text).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Save to File", command=self.save_plain_to_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Clear", command=self.clear_decrypt).pack(side=tk.LEFT, padx=2)

    # ---------- Các hàm xử lý (giữ nguyên) ----------
    def get_key_iv(self):
        key_hex = self.key_entry.get().strip()
        iv_hex = self.iv_entry.get().strip()
        try:
            key = EVP.hex_to_bytes(key_hex)
            iv = EVP.hex_to_bytes(iv_hex)
        except Exception as e:
            raise ValueError(f"Key/IV hex error: {e}")
        cipher = self.cipher_var.get()
        if '128' in cipher and len(key) != 16:
            raise ValueError(f"AES-128 requires 16-byte key, got {len(key)}")
        if '192' in cipher and len(key) != 24:
            raise ValueError(f"AES-192 requires 24-byte key, got {len(key)}")
        if '256' in cipher and len(key) != 32:
            raise ValueError(f"AES-256 requires 32-byte key, got {len(key)}")
        if 'ecb' not in cipher and len(iv) != 16:
            raise ValueError(f"IV must be 16 bytes for {cipher}, got {len(iv)}")
        return key, iv

    def do_encrypt(self):
        try:
            cipher = self.cipher_var.get()
            key, iv = self.get_key_iv()
            plain = self.plain_text.get('1.0', tk.END).strip().encode('utf-8')
            if not plain:
                raise ValueError("Plaintext is empty")
            padding = self.padding_var.get()
            ct = EVP.encrypt(cipher, key, iv, plain, padding)
            hex_ct = EVP.bytes_to_hex(ct)
            self.ciphertext_display.delete('1.0', tk.END)
            self.ciphertext_display.insert('1.0', hex_ct)
            self.status.config(text="Encryption completed successfully!")
            messagebox.showinfo("Success", "Encryption completed!")
        except Exception as e:
            messagebox.showerror("Encryption Error", str(e))
            self.status.config(text="Encryption failed")

    def copy_cipher_hex(self):
        ct = self.ciphertext_display.get('1.0', tk.END).strip()
        if ct:
            self.root.clipboard_clear()
            self.root.clipboard_append(ct)
            self.status.config(text="Copied hex to clipboard")
        else:
            messagebox.showwarning("Nothing to copy", "No ciphertext available")

    def copy_cipher_base64(self):
        ct_hex = self.ciphertext_display.get('1.0', tk.END).strip()
        if ct_hex:
            try:
                ct_bytes = EVP.hex_to_bytes(ct_hex)
                b64 = base64.b64encode(ct_bytes).decode()
                self.root.clipboard_clear()
                self.root.clipboard_append(b64)
                self.status.config(text="Copied base64 to clipboard")
            except:
                messagebox.showerror("Error", "Invalid ciphertext hex")

    def save_cipher_to_file(self):
        ct_hex = self.ciphertext_display.get('1.0', tk.END).strip()
        if not ct_hex:
            messagebox.showwarning("Nothing to save", "No ciphertext")
            return
        path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("Binary files", "*.bin"), ("All files", "*.*")])
        if path:
            try:
                ct_bytes = EVP.hex_to_bytes(ct_hex)
                with open(path, "wb") as f:
                    f.write(ct_bytes)
                self.status.config(text=f"Saved to {path}")
            except Exception as e:
                messagebox.showerror("Save error", str(e))

    def clear_encrypt(self):
        self.ciphertext_display.delete('1.0', tk.END)
        self.plain_text.delete('1.0', tk.END)
        self.status.config(text="Cleared")

    def do_decrypt(self):
        try:
            cipher = self.cipher_var.get()
            key, iv = self.get_key_iv()
            ct_hex = self.ciphertext_input.get('1.0', tk.END).strip()
            if not ct_hex:
                raise ValueError("Ciphertext hex is empty")
            ct = EVP.hex_to_bytes(ct_hex)
            padding = self.padding_var.get()
            plain = EVP.decrypt(cipher, key, iv, ct, padding)
            try:
                plain_text = plain.decode('utf-8')
                self.decrypted_display.delete('1.0', tk.END)
                self.decrypted_display.insert('1.0', plain_text)
            except UnicodeDecodeError:
                self.decrypted_display.delete('1.0', tk.END)
                self.decrypted_display.insert('1.0', f"(Binary data, hex: {EVP.bytes_to_hex(plain)})")
            self.status.config(text="Decryption completed successfully!")
            messagebox.showinfo("Success", "Decryption completed!")
        except Exception as e:
            messagebox.showerror("Decryption Error", str(e))
            self.status.config(text="Decryption failed")

    def copy_plain_text(self):
        text = self.decrypted_display.get('1.0', tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.status.config(text="Copied plaintext to clipboard")
        else:
            messagebox.showwarning("Nothing to copy", "No decrypted text")

    def save_plain_to_file(self):
        text = self.decrypted_display.get('1.0', tk.END).strip()
        if not text:
            messagebox.showwarning("Nothing to save", "No plaintext")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text)
                self.status.config(text=f"Saved to {path}")
            except Exception as e:
                messagebox.showerror("Save error", str(e))

    def clear_decrypt(self):
        self.ciphertext_input.delete('1.0', tk.END)
        self.decrypted_display.delete('1.0', tk.END)
        self.status.config(text="Cleared")

    def gen_key(self):
        cipher = self.cipher_var.get()
        if '128' in cipher:
            size = 16
        elif '192' in cipher:
            size = 24
        else:
            size = 32
        key = secrets.token_bytes(size)
        key_hex = EVP.bytes_to_hex(key)
        self.key_entry.delete(0, tk.END)
        self.key_entry.insert(0, key_hex)
        self.status.config(text="Generated new random key")

    def gen_iv(self):
        iv = secrets.token_bytes(16)
        iv_hex = EVP.bytes_to_hex(iv)
        self.iv_entry.delete(0, tk.END)
        self.iv_entry.insert(0, iv_hex)
        self.status.config(text="Generated new random IV")

    def encrypt_file(self):
        path = filedialog.askopenfilename(title="Select file to encrypt")
        if not path:
            return
        try:
            with open(path, "rb") as f:
                plain = f.read()
            cipher = self.cipher_var.get()
            key, iv = self.get_key_iv()
            padding = self.padding_var.get()
            ct = EVP.encrypt(cipher, key, iv, plain, padding)
            out_path = path + ".enc"
            with open(out_path, "wb") as f:
                f.write(ct)
            self.status.config(text=f"Encrypted to {out_path}")
            messagebox.showinfo("File Encrypted", f"Saved as {out_path}")
        except Exception as e:
            messagebox.showerror("File encryption error", str(e))

    def decrypt_file(self):
        path = filedialog.askopenfilename(title="Select .enc file to decrypt", filetypes=[("Encrypted files", "*.enc"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, "rb") as f:
                ct = f.read()
            cipher = self.cipher_var.get()
            key, iv = self.get_key_iv()
            padding = self.padding_var.get()
            plain = EVP.decrypt(cipher, key, iv, ct, padding)
            out_path = path.replace(".enc", ".dec")
            with open(out_path, "wb") as f:
                f.write(plain)
            self.status.config(text=f"Decrypted to {out_path}")
            messagebox.showinfo("File Decrypted", f"Saved as {out_path}")
        except Exception as e:
            messagebox.showerror("File decryption error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = AESTool(root)
    root.mainloop()