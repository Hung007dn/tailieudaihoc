import hashlib

def compute_file_hash(file_path, hash_type='sha256'):
    if not hasattr(hashlib, hash_type):
        raise ValueError(f"Invalid hash type: {hash_type}")

    hash_func = getattr(hashlib, hash_type)()

    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)

    return hash_func.hexdigest()

# === Example Usage ===
if __name__ == '__main__':
    print("Supported hash types:")
    print("md5, sha1, sha224, sha256, sha384, sha512")
    print("sha3_224, sha3_256, sha3_384, sha3_512")
    print()

    file_path = input("Enter the file path: ").strip()
    hash_type = input("Enter hash type: ").strip().lower() or 'sha256'

    try:
        file_hash = compute_file_hash(file_path, hash_type)
        print(f"\n{hash_type.upper()} hash of '{file_path}':\n{file_hash}")
    except FileNotFoundError:
        print("File not found. Please check the path.")
    except (AttributeError, ValueError):
        print("Invalid hash type. Please use a supported one.")
