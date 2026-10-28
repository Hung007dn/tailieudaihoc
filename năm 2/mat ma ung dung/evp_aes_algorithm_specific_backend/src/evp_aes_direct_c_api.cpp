#include "evp_aes_direct_c_api.h"

#include <cstring>
#include <exception>
#include <stdexcept>
#include <string>
#include <vector>

#include "evp_aes_direct_tool.h"

namespace {

thread_local std::string g_last_error;

void clear_error() {
    g_last_error.clear();
}

void set_error(const std::string& message) {
    g_last_error = message;
}

int set_error_return(int code, const std::string& message) {
    set_error(message);
    return code;
}

bool ptr_invalid_when_len_nonzero(const void* p, std::size_t len) {
    return p == nullptr && len != 0;
}

std::string require_string(const char* s, const char* name) {
    if (!s || std::string(s).empty()) {
        throw std::invalid_argument(std::string(name) + " is null or empty");
    }

    return std::string(s);
}

aeslab_evp_direct::Bytes make_bytes(
    const uint8_t* p,
    std::size_t len,
    const char* name
) {
    if (ptr_invalid_when_len_nonzero(p, len)) {
        throw std::invalid_argument(
            std::string(name) + " pointer is null but length is non-zero"
        );
    }

    if (len == 0) {
        return {};
    }

    return aeslab_evp_direct::Bytes(p, p + len);
}

int map_exception(const std::exception& e) {
    set_error(e.what());

    const std::string msg = e.what();

    if (msg.find("Unsupported") != std::string::npos ||
        msg.find("unsupported") != std::string::npos ||
        msg.find("not supported") != std::string::npos ||
        msg.find("unavailable") != std::string::npos) {
        return EVPAESDIRECT_ERR_UNAVAILABLE;
    }

    if (msg.find("OpenSSL") != std::string::npos ||
        msg.find("EVP_") != std::string::npos ||
        msg.find("CTRL") != std::string::npos) {
        return EVPAESDIRECT_ERR_OPENSSL;
    }

    if (dynamic_cast<const std::invalid_argument*>(&e) != nullptr) {
        return EVPAESDIRECT_ERR_INVALID_ARGUMENT;
    }

    return EVPAESDIRECT_ERR_EXCEPTION;
}

int copy_bytes_to_output(
    const aeslab_evp_direct::Bytes& src,
    uint8_t* dst,
    std::size_t dst_capacity,
    std::size_t* dst_len,
    const char* output_name
) {
    if (dst_len) {
        *dst_len = src.size();
    }

    if (src.empty()) {
        return EVPAESDIRECT_OK;
    }

    if (!dst || dst_capacity < src.size()) {
        return set_error_return(
            EVPAESDIRECT_ERR_BUFFER_TOO_SMALL,
            std::string(output_name) + " buffer is too small"
        );
    }

    std::memcpy(dst, src.data(), src.size());
    return EVPAESDIRECT_OK;
}

int copy_string_to_output(
    const std::string& src,
    char* dst,
    std::size_t dst_capacity,
    std::size_t* dst_len,
    const char* output_name
) {
    if (dst_len) {
        *dst_len = src.size();
    }

    const std::size_t required = src.size() + 1;

    if (!dst || dst_capacity < required) {
        return set_error_return(
            EVPAESDIRECT_ERR_BUFFER_TOO_SMALL,
            std::string(output_name) + " buffer is too small"
        );
    }

    std::memcpy(dst, src.c_str(), required);
    return EVPAESDIRECT_OK;
}

} // anonymous namespace

extern "C" {

EVPAESDIRECT_API const char* evpaesdirect_version(void) {
    return "EVP AES Direct Tool 0.1.0";
}

EVPAESDIRECT_API const char* evpaesdirect_last_error(void) {
    return g_last_error.c_str();
}

EVPAESDIRECT_API void evpaesdirect_clear_error(void) {
    clear_error();
}

EVPAESDIRECT_API int evpaesdirect_cipher_available(
    const char* cipher_name
) {
    try {
        clear_error();

        return aeslab_evp_direct::EVPAESDirectTool::cipher_available(
            require_string(cipher_name, "cipher_name")
        ) ? 1 : 0;
    } catch (const std::exception& e) {
        return map_exception(e);
    }
}

EVPAESDIRECT_API int evpaesdirect_cipher_expected_key_len(
    const char* cipher_name,
    size_t* key_len_out
) {
    try {
        clear_error();

        if (!key_len_out) {
            return set_error_return(
                EVPAESDIRECT_ERR_INVALID_ARGUMENT,
                "key_len_out is null"
            );
        }

        *key_len_out =
            aeslab_evp_direct::EVPAESDirectTool::expected_key_length(
                require_string(cipher_name, "cipher_name")
            );

        return EVPAESDIRECT_OK;
    } catch (const std::exception& e) {
        return map_exception(e);
    }
}

EVPAESDIRECT_API int evpaesdirect_cipher_expected_iv_len(
    const char* cipher_name,
    size_t* iv_len_out
) {
    try {
        clear_error();

        if (!iv_len_out) {
            return set_error_return(
                EVPAESDIRECT_ERR_INVALID_ARGUMENT,
                "iv_len_out is null"
            );
        }

        *iv_len_out =
            aeslab_evp_direct::EVPAESDirectTool::expected_iv_length(
                require_string(cipher_name, "cipher_name")
            );

        return EVPAESDIRECT_OK;
    } catch (const std::exception& e) {
        return map_exception(e);
    }
}

EVPAESDIRECT_API int evpaesdirect_cipher_block_size(
    const char* cipher_name,
    int* block_size_out
) {
    try {
        clear_error();

        if (!block_size_out) {
            return set_error_return(
                EVPAESDIRECT_ERR_INVALID_ARGUMENT,
                "block_size_out is null"
            );
        }

        *block_size_out =
            aeslab_evp_direct::EVPAESDirectTool::block_size(
                require_string(cipher_name, "cipher_name")
            );

        return EVPAESDIRECT_OK;
    } catch (const std::exception& e) {
        return map_exception(e);
    }
}

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
) {
    try {
        clear_error();

        const aeslab_evp_direct::Bytes out =
            aeslab_evp_direct::EVPAESDirectTool::encrypt(
                require_string(cipher_name, "cipher_name"),
                make_bytes(key, key_len, "key"),
                make_bytes(iv, iv_len, "iv"),
                make_bytes(plaintext, plaintext_len, "plaintext"),
                padding != 0
            );

        return copy_bytes_to_output(
            out,
            ciphertext,
            ciphertext_capacity,
            ciphertext_len,
            "ciphertext"
        );
    } catch (const std::exception& e) {
        return map_exception(e);
    }
}

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
) {
    try {
        clear_error();

        const aeslab_evp_direct::Bytes out =
            aeslab_evp_direct::EVPAESDirectTool::decrypt(
                require_string(cipher_name, "cipher_name"),
                make_bytes(key, key_len, "key"),
                make_bytes(iv, iv_len, "iv"),
                make_bytes(ciphertext, ciphertext_len, "ciphertext"),
                padding != 0
            );

        return copy_bytes_to_output(
            out,
            plaintext,
            plaintext_capacity,
            plaintext_len,
            "plaintext"
        );
    } catch (const std::exception& e) {
        return map_exception(e);
    }
}

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
) {
    try {
        clear_error();

        const aeslab_evp_direct::AEADEncryptResult result =
            aeslab_evp_direct::EVPAESDirectTool::aead_encrypt(
                require_string(cipher_name, "cipher_name"),
                make_bytes(key, key_len, "key"),
                make_bytes(nonce, nonce_len, "nonce"),
                make_bytes(aad, aad_len, "aad"),
                make_bytes(plaintext, plaintext_len, "plaintext"),
                tag_len
            );

        if (ciphertext_len) {
            *ciphertext_len = result.ciphertext.size();
        }

        if (tag_out_len) {
            *tag_out_len = result.tag.size();
        }

        bool too_small = false;

        if (!result.ciphertext.empty() &&
            (!ciphertext || ciphertext_capacity < result.ciphertext.size())) {
            too_small = true;
        }

        if (!result.tag.empty() &&
            (!tag || tag_capacity < result.tag.size())) {
            too_small = true;
        }

        if (too_small) {
            return set_error_return(
                EVPAESDIRECT_ERR_BUFFER_TOO_SMALL,
                "ciphertext or tag buffer is too small"
            );
        }

        if (!result.ciphertext.empty()) {
            std::memcpy(
                ciphertext,
                result.ciphertext.data(),
                result.ciphertext.size()
            );
        }

        if (!result.tag.empty()) {
            std::memcpy(
                tag,
                result.tag.data(),
                result.tag.size()
            );
        }

        return EVPAESDIRECT_OK;
    } catch (const std::exception& e) {
        return map_exception(e);
    }
}

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
) {
    try {
        clear_error();

        const aeslab_evp_direct::AEADDecryptResult result =
            aeslab_evp_direct::EVPAESDirectTool::aead_decrypt(
                require_string(cipher_name, "cipher_name"),
                make_bytes(key, key_len, "key"),
                make_bytes(nonce, nonce_len, "nonce"),
                make_bytes(aad, aad_len, "aad"),
                make_bytes(ciphertext, ciphertext_len, "ciphertext"),
                make_bytes(tag, tag_len, "tag")
            );

        if (!result.tag_valid) {
            if (plaintext_len) {
                *plaintext_len = 0;
            }

            return set_error_return(
                EVPAESDIRECT_ERR_AUTH_FAILED,
                "AEAD authentication failed"
            );
        }

        return copy_bytes_to_output(
            result.plaintext,
            plaintext,
            plaintext_capacity,
            plaintext_len,
            "plaintext"
        );
    } catch (const std::exception& e) {
        return map_exception(e);
    }
}

EVPAESDIRECT_API int evpaesdirect_hex_to_bytes(
    const char* hex,
    uint8_t* output,
    size_t output_capacity,
    size_t* output_len
) {
    try {
        clear_error();

        const aeslab_evp_direct::Bytes out =
            aeslab_evp_direct::EVPAESDirectTool::hex_to_bytes(
                require_string(hex, "hex")
            );

        return copy_bytes_to_output(
            out,
            output,
            output_capacity,
            output_len,
            "hex output"
        );
    } catch (const std::exception& e) {
        return map_exception(e);
    }
}

EVPAESDIRECT_API int evpaesdirect_bytes_to_hex(
    const uint8_t* input,
    size_t input_len,
    char* output_hex,
    size_t output_hex_capacity,
    size_t* output_hex_len
) {
    try {
        clear_error();

        const std::string out =
            aeslab_evp_direct::EVPAESDirectTool::bytes_to_hex(
                make_bytes(input, input_len, "input")
            );

        return copy_string_to_output(
            out,
            output_hex,
            output_hex_capacity,
            output_hex_len,
            "hex output"
        );
    } catch (const std::exception& e) {
        return map_exception(e);
    }
}

} // extern "C"
