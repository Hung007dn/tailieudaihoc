# Algorithm-Specific OpenSSL EVP Hash Backend

This backend demonstrates OpenSSL's algorithm-specific digest accessors, such as:

```cpp
EVP_sha1()
EVP_sha256()
EVP_sha3_256()
EVP_shake128()
```

It is different from provider-fetch style:

```cpp
EVP_MD_fetch(nullptr, "SHA256", "fips=yes")
```

## Files

```text
evp_hash_algorithm_specific_backend/
├── README.md
├── include/
│   ├── evp_hash_direct_tool.h
│   └── evp_hash_direct_c_api.h
├── src/
│   ├── evp_hash_direct_tool.cpp
│   ├── evp_hash_direct_c_api.cpp
│   └── evp_hash_direct_main.cpp
└── tests/
    └── evp_hash_direct_demo.cpp
```

## Supported Digest Accessors

```text
EVP_sha1
EVP_sha224
EVP_sha256
EVP_sha384
EVP_sha512
EVP_sha512_224
EVP_sha512_256

EVP_sha3_224
EVP_sha3_256
EVP_sha3_384
EVP_sha3_512

EVP_shake128
EVP_shake256

EVP_md5_sha1, legacy TLS combined digest
```

## Main C++ Classes

```cpp
EVPHashDirectTool
DirectDigestContext
DigestInfo
```

## Build Demo on Windows / MinGW

```bat
g++ -std=c++17 -O2 -Wall -Wextra ^
  -Iinclude ^
  src\evp_hash_direct_tool.cpp ^
  tests\evp_hash_direct_demo.cpp ^
  -LD:\utecrypto\lib64 ^
  -lcrypto ^
  -lws2_32 -lcrypt32 ^
  -o evp_hash_direct_demo.exe
```

## Build CLI

```bat
g++ -std=c++17 -O2 -Wall -Wextra ^
  -Iinclude ^
  src\evp_hash_direct_tool.cpp ^
  src\evp_hash_direct_main.cpp ^
  -LD:\utecrypto\lib64 ^
  -lcrypto ^
  -lws2_32 -lcrypt32 ^
  -o evp_hash_direct_lab.exe
```

## Build DLL

```bat
g++ -std=c++17 -O2 -Wall -Wextra ^
  -DEVPHASHDIRECT_EXPORTS ^
  -Iinclude ^
  src\evp_hash_direct_tool.cpp ^
  src\evp_hash_direct_c_api.cpp ^
  -shared ^
  -LD:\utecrypto\lib64 ^
  -lcrypto ^
  -lws2_32 -lcrypt32 ^
  -o evphashdirect.dll ^
  -Wl,--out-implib,libevphashdirect.dll.a
```

## CLI Examples

List algorithms:

```bat
evp_hash_direct_lab.exe --list
```

SHA-256 of text:

```bat
evp_hash_direct_lab.exe hash --alg sha256 --text abc
```

Expected:

```text
ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
```

SHA3-256 of text:

```bat
evp_hash_direct_lab.exe hash --alg sha3-256 --text abc
```

SHAKE128 with 32-byte output:

```bat
evp_hash_direct_lab.exe hash --alg shake128 --text abc --xof-len 32
```

Hash a file and write raw digest bytes:

```bat
evp_hash_direct_lab.exe hash --alg sha256 --in message.bin --out digest.bin
```

Streaming copy demo:

```bat
evp_hash_direct_lab.exe stream-demo --alg sha256
```

## C API Design

The DLL API exports only C-safe types:

```text
const char*
uint8_t*
size_t
int status codes
opaque EVPHASHDIRECT_CTX*
```

Main exported APIs:

```text
evphashdirect_digest_available
evphashdirect_digest_info
evphashdirect_digest

evphashdirect_ctx_new
evphashdirect_ctx_update
evphashdirect_ctx_copy
evphashdirect_ctx_final
evphashdirect_ctx_final_xof
evphashdirect_ctx_free

evphashdirect_hex_to_bytes
evphashdirect_bytes_to_hex
```

## Teaching Notes

1. SHA-1 is included for legacy/interoperability labs, not recommended for collision-resistant signatures.
2. MD5-SHA1 is legacy TLS material and not a modern digest choice.
3. SHAKE128/SHAKE256 are XOFs, so output length is caller-selected.
4. For password hashing, use dedicated KDFs such as PBKDF2, scrypt, or Argon2, not raw SHA-256.
