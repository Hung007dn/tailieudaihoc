#pragma once

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
    Algorithm-specific OpenSSL EVP AES C ABI.

    This DLL API uses EVP_aes_128_cbc(), EVP_aes_256_gcm(), etc.
    It is intentionally separate from the provider-fetch backend.

    Build DLL:
        define EVPAESDIRECT_EXPORTS

    Build/use static library:
        define EVPAESDIRECT_STATIC

    Consumer of DLL:
        do not define EVPAESDIRECT_EXPORTS
*/

#if defined(EVPAESDIRECT_STATIC)
    #define EVPAESDIRECT_API
#elif defined(_WIN32) || defined(__CYGWIN__)
    #if defined(EVPAESDIRECT_EXPORTS)
        #define EVPAESDIRECT_API __declspec(dllexport)
    #else
        #define EVPAESDIRECT_API __declspec(dllimport)
    #endif
#else
    #if defined(__GNUC__) || defined(__clang__)
        #define EVPAESDIRECT_API __attribute__((visibility("default")))
    #else
        #define EVPAESDIRECT_API
    #endif
#endif

typedef enum EVPAESDirectStatus {
    EVPAESDIRECT_OK = 0,

    EVPAESDIRECT_ERR_INVALID_ARGUMENT = -1,
    EVPAESDIRECT_ERR_BUFFER_TOO_SMALL = -2,
    EVPAESDIRECT_ERR_AUTH_FAILED      = -3,
    EVPAESDIRECT_ERR_UNAVAILABLE      = -4,
    EVPAESDIRECT_ERR_OPENSSL          = -5,
    EVPAESDIRECT_ERR_EXCEPTION        = -100
} EVPAESDirectStatus;

EVPAESDIRECT_API const char* evpaesdirect_version(void);
EVPAESDIRECT_API const char* evpaesdirect_last_error(void);
EVPAESDIRECT_API void evpaesdirect_clear_error(void);

/*
    cipher_name examples:
        aes-128-cbc
        aes-128-ctr
        aes-128-gcm
        aes-256-ocb
        aes-128-wrap
        aes-256-xts

    Returns:
        1 = available
        0 = unavailable
       <0 = error status
*/
EVPAESDIRECT_API int evpaesdirect_cipher_available(
    const char* cipher_name
);

EVPAESDIRECT_API int evpaesdirect_cipher_expected_key_len(
    const char* cipher_name,
    size_t* key_len_out
);

EVPAESDIRECT_API int evpaesdirect_cipher_expected_iv_len(
    const char* cipher_name,
    size_t* iv_len_out
);

EVPAESDIRECT_API int evpaesdirect_cipher_block_size(
    const char* cipher_name,
    int* block_size_out
);

/*
    Classical/general encryption/decryption.

    Supported:
        ECB, CBC, CTR, OFB, CFB/CFB128, CFB8, CFB1
        XTS
        WRAP, WRAP-PAD

    padding:
        0 = EVP padding disabled
        1 = EVP padding enabled

    Usually:
        ECB/CBC -> padding can be 1
        CTR/OFB/CFB/XTS/WRAP -> padding should be 0

    For ECB and WRAP/WRAP-PAD:
        iv may be NULL and iv_len must be 0.
*/
EVPAESDIRECT_API int evpaesdirect_encrypt(
    const char* cipher_name,

    const uint8_t* key,
    size_t key_len,

    const uint8_t* iv,
    size_t iv_len,

    const uint8_t* plaintext,
    size_t plaintext_len,

    int padding,

    uint8_t* ciphertext,
    size_t ciphertext_capacity,
    size_t* ciphertext_len
);

EVPAESDIRECT_API int evpaesdirect_decrypt(
    const char* cipher_name,

    const uint8_t* key,
    size_t key_len,

    const uint8_t* iv,
    size_t iv_len,

    const uint8_t* ciphertext,
    size_t ciphertext_len,

    int padding,

    uint8_t* plaintext,
    size_t plaintext_capacity,
    size_t* plaintext_len
);

/*
    AEAD encryption/decryption.

    Supported by algorithm-specific accessors:
        AES-*-GCM
        AES-*-CCM
        AES-*-OCB

    Not supported here:
        EAX
        SIV
        GCM-SIV

    Use the provider-fetch backend for provider-dependent modes such as
    GCM-SIV and SIV.
*/
EVPAESDIRECT_API int evpaesdirect_aead_encrypt(
    const char* cipher_name,

    const uint8_t* key,
    size_t key_len,

    const uint8_t* nonce,
    size_t nonce_len,

    const uint8_t* aad,
    size_t aad_len,

    const uint8_t* plaintext,
    size_t plaintext_len,

    size_t tag_len,

    uint8_t* ciphertext,
    size_t ciphertext_capacity,
    size_t* ciphertext_len,

    uint8_t* tag,
    size_t tag_capacity,
    size_t* tag_out_len
);

EVPAESDIRECT_API int evpaesdirect_aead_decrypt(
    const char* cipher_name,

    const uint8_t* key,
    size_t key_len,

    const uint8_t* nonce,
    size_t nonce_len,

    const uint8_t* aad,
    size_t aad_len,

    const uint8_t* ciphertext,
    size_t ciphertext_len,

    const uint8_t* tag,
    size_t tag_len,

    uint8_t* plaintext,
    size_t plaintext_capacity,
    size_t* plaintext_len
);

/*
    Hex helpers for C/Python/C# wrappers.
*/
EVPAESDIRECT_API int evpaesdirect_hex_to_bytes(
    const char* hex,
    uint8_t* output,
    size_t output_capacity,
    size_t* output_len
);

EVPAESDIRECT_API int evpaesdirect_bytes_to_hex(
    const uint8_t* input,
    size_t input_len,
    char* output_hex,
    size_t output_hex_capacity,
    size_t* output_hex_len
);

#ifdef __cplusplus
}
#endif
