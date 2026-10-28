# Algorithm-Specific OpenSSL EVP AES Backend

This backend demonstrates OpenSSL's algorithm-specific EVP cipher accessors, such as:

```cpp
EVP_aes_128_cbc()
EVP_aes_128_gcm()
EVP_aes_256_ocb()
```

This is different from the provider-fetch backend:

```cpp
EVP_CIPHER_fetch(nullptr, "AES-128-CBC", "fips=yes")
```

Both are high-level EVP APIs. The difference is mainly how the cipher implementation is selected.

## Why Add This Backend?

This backend is useful for learning because your static library clearly exposes these symbols:

```text
EVP_aes_128_cbc
EVP_aes_128_gcm
EVP_aes_128_ocb
EVP_aes_256_xts
EVP_aes_256_wrap
...
```

So students can directly connect the C function names to AES modes.

## Files

```text
evp_aes_algorithm_specific_backend/
├── README.md
├── include/
│   └── evp_aes_direct_tool.h
├── src/
│   └── evp_aes_direct_tool.cpp
└── tests/
    └── evp_aes_direct_demo.cpp
```

## Supported Direct Accessors

The resolver maps friendly names such as `aes-128-cbc` to specific OpenSSL functions such as `EVP_aes_128_cbc()`.

Supported groups:

```text
CBC, ECB, OFB, CFB128/CFB, CFB1, CFB8, CTR
GCM, CCM, OCB
WRAP, WRAP-PAD
XTS for AES-128 and AES-256
```

AES-192-XTS is not exposed because XTS uses two AES keys and standard OpenSSL exposes AES-128-XTS and AES-256-XTS.

## Intentionally Not Exposed as Normal Ciphers

Your `nm` output also shows:

```text
EVP_aes_128_cbc_hmac_sha1
EVP_aes_256_cbc_hmac_sha1
EVP_aes_128_cbc_hmac_sha256
EVP_aes_256_cbc_hmac_sha256
```

These are TLS-record optimized combined ciphers. They require protocol-specific controls and should not be presented as ordinary AES-CBC file-encryption modes in a beginner lab.

## Build Demo on Windows / MinGW

If OpenSSL is available through MSYS2 MinGW:

```bat
g++ -std=c++17 -O2 -Wall -Wextra ^
  -Iinclude ^
  src\evp_aes_direct_tool.cpp ^
  tests\evp_aes_direct_demo.cpp ^
  -lcrypto ^
  -lws2_32 -lcrypt32 ^
  -o evp_aes_direct_demo.exe
```

With custom OpenSSL paths:

```bat
g++ -std=c++17 -O2 -Wall -Wextra ^
  -Iinclude ^
  -ID:\utecrypto\include ^
  src\evp_aes_direct_tool.cpp ^
  tests\evp_aes_direct_demo.cpp ^
  -LD:\utecrypto\lib64 ^
  -lcrypto ^
  -lws2_32 -lcrypt32 ^
  -o evp_aes_direct_demo.exe
```

## Expected Demo Output

```text
Algorithm-specific EVP AES demo
Cipher available AES-128-GCM: yes
AES-128-GCM key length: 16 byte(s)
ciphertext: 0388dace60b6a392f328c2b971b2fe78
tag       : ab6e47d42cec13bdf53a67b21257bddf
tag valid : yes
plaintext : 00000000000000000000000000000000
CBC recovered: Hello algorithm-specific EVP AES-CBC
```

## Teaching Comparison

| Backend | API style | Best for |
|---|---|---|
| Educational AES backend | Manual AES implementation | Learning AES internals |
| EVP provider backend | `EVP_CIPHER_fetch()` | Product deployment, providers, FIPS, supply chain |
| Algorithm-specific EVP backend | `EVP_aes_128_cbc()` | Learning OpenSSL convenience APIs and mode mapping |

## Important Notes

1. These direct accessors are still high-level EVP APIs.
2. They are easier for students to read than provider fetch calls.
3. They do not expose provider/property-query selection as clearly as `EVP_CIPHER_fetch()`.
4. For production policy enforcement, prefer the provider-fetch backend.
5. For teaching mode names and OpenSSL symbol mapping, this backend is excellent.


## CLI and DLL API

Additional files:

```text
include/evp_aes_direct_c_api.h
src/evp_aes_direct_c_api.cpp
src/evp_aes_direct_main.cpp
```

### Build CLI

```bat
g++ -std=c++17 -O2 -Wall -Wextra ^
  -Iinclude ^
  src\evp_aes_direct_tool.cpp ^
  src\evp_aes_direct_main.cpp ^
  -LD:\utecrypto\lib64 ^
  -lcrypto ^
  -lws2_32 -lcrypt32 ^
  -o evp_aes_direct_lab.exe
```

### Build DLL

```bat
g++ -std=c++17 -O2 -Wall -Wextra ^
  -DEVPAESDIRECT_EXPORTS ^
  -Iinclude ^
  src\evp_aes_direct_tool.cpp ^
  src\evp_aes_direct_c_api.cpp ^
  -shared ^
  -LD:\utecrypto\lib64 ^
  -lcrypto ^
  -lws2_32 -lcrypt32 ^
  -o evpaesdirect.dll ^
  -Wl,--out-implib,libevpaesdirect.dll.a
```

### CLI Examples

List direct AES accessors supported by this lab wrapper:

```bat
evp_aes_direct_lab.exe --list
```

Check one cipher:

```bat
evp_aes_direct_lab.exe --available --cipher aes-256-xts
```

AES-GCM known vector:

```bat
evp_aes_direct_lab.exe enc ^
  --cipher aes-128-gcm ^
  --key 00000000000000000000000000000000 ^
  --nonce 000000000000000000000000 ^
  --hex-input 00000000000000000000000000000000 ^
  --out-hex
```

Expected:

```text
0388dace60b6a392f328c2b971b2fe78
tag: ab6e47d42cec13bdf53a67b21257bddf
```

AES-CBC with EVP padding:

```bat
evp_aes_direct_lab.exe enc ^
  --cipher aes-128-cbc ^
  --key 000102030405060708090a0b0c0d0e0f ^
  --iv 101112131415161718191a1b1c1d1e1f ^
  --text "Hello AES-CBC direct EVP" ^
  --padding ^
  --out-hex
```

### C API Design

The DLL API exports only C-safe types:

```text
const char*
uint8_t*
size_t
int status codes
```

Main C API groups:

```text
evpaesdirect_cipher_available
evpaesdirect_cipher_expected_key_len
evpaesdirect_cipher_expected_iv_len
evpaesdirect_encrypt
evpaesdirect_decrypt
evpaesdirect_aead_encrypt
evpaesdirect_aead_decrypt
evpaesdirect_hex_to_bytes
evpaesdirect_bytes_to_hex
```
