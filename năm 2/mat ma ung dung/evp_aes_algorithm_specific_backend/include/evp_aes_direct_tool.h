#pragma once

#include <cstddef>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>

#include <openssl/evp.h>

namespace aeslab_evp_direct {

using Bytes = std::vector<std::uint8_t>;

struct AEADEncryptResult {
    Bytes ciphertext;
    Bytes tag;
};

struct AEADDecryptResult {
    Bytes plaintext;
    bool tag_valid = false;
};

class OpenSSLError : public std::runtime_error {
public:
    explicit OpenSSLError(const std::string& message)
        : std::runtime_error(message) {}
};

class EVPAESDirectTool {
public:
    /*
        Algorithm-specific EVP backend.

        This class uses OpenSSL functions such as:
            EVP_aes_128_cbc()
            EVP_aes_256_gcm()
            EVP_aes_128_ocb()

        It is different from provider-fetch style:
            EVP_CIPHER_fetch(nullptr, "AES-128-CBC", "fips=yes")

        Use this class to teach the convenient algorithm-specific EVP API.
        Use the provider-fetch backend to teach OpenSSL 3 provider/property
        queries and product deployment policy.
    */

    static bool cipher_available(const std::string& cipher_name);

    static std::size_t expected_key_length(const std::string& cipher_name);
    static std::size_t expected_iv_length(const std::string& cipher_name);
    static int block_size(const std::string& cipher_name);

    /*
        Classical/general encryption/decryption.

        Supported examples:
            aes-128-ecb
            aes-128-cbc
            aes-128-cfb / aes-128-cfb128
            aes-128-cfb8
            aes-128-cfb1
            aes-128-ofb
            aes-128-ctr
            aes-128-xts
            aes-128-wrap
            aes-128-wrap-pad

        Padding:
            true  -> EVP padding enabled, useful for ECB/CBC
            false -> EVP padding disabled

        For CTR/OFB/CFB/XTS/WRAP, normally use padding=false.
    */
    static Bytes encrypt(
        const std::string& cipher_name,
        const Bytes& key,
        const Bytes& iv,
        const Bytes& plaintext,
        bool padding
    );

    static Bytes decrypt(
        const std::string& cipher_name,
        const Bytes& key,
        const Bytes& iv,
        const Bytes& ciphertext,
        bool padding
    );

    /*
        AEAD:
            aes-128/192/256-gcm
            aes-128/192/256-ccm
            aes-128/192/256-ocb

        Note:
            AES-EAX is not provided by OpenSSL's built-in algorithm-specific
            AES EVP functions.
            AES-GCM-SIV is provider-fetched in newer OpenSSL versions, not
            normally available as EVP_aes_128_gcm_siv() in the function list.
            AES-SIV may be provider-fetched, not listed in classic e_aes symbols.
    */
    static AEADEncryptResult aead_encrypt(
        const std::string& cipher_name,
        const Bytes& key,
        const Bytes& nonce,
        const Bytes& aad,
        const Bytes& plaintext,
        std::size_t tag_len
    );

    static AEADDecryptResult aead_decrypt(
        const std::string& cipher_name,
        const Bytes& key,
        const Bytes& nonce,
        const Bytes& aad,
        const Bytes& ciphertext,
        const Bytes& tag
    );

    /*
        Direct resolver for classroom inspection.

        Returned pointer is owned by OpenSSL.
        Do not free it.
    */
    static const EVP_CIPHER* resolve_cipher(
        const std::string& cipher_name
    );

    static Bytes hex_to_bytes(const std::string& hex);
    static std::string bytes_to_hex(const Bytes& data, bool lowercase = true);
    static Bytes text_to_bytes(const std::string& text);
    static std::string bytes_to_text_lossy(const Bytes& data);
};

} // namespace aeslab_evp_direct
