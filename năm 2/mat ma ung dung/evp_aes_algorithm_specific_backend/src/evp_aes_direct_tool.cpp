#include "evp_aes_direct_tool.h"

#include <algorithm>
#include <cctype>
#include <climits>
#include <cstring>
#include <iomanip>
#include <memory>
#include <sstream>

#include <openssl/err.h>

namespace aeslab_evp_direct {

namespace {

struct CtxDeleter {
    void operator()(EVP_CIPHER_CTX* p) const noexcept {
        EVP_CIPHER_CTX_free(p);
    }
};

using CtxPtr = std::unique_ptr<EVP_CIPHER_CTX, CtxDeleter>;

std::string openssl_error_stack() {
    std::ostringstream oss;
    bool first = true;

    while (unsigned long err = ERR_get_error()) {
        char buf[256];
        ERR_error_string_n(err, buf, sizeof(buf));

        if (!first) {
            oss << " | ";
        }

        oss << buf;
        first = false;
    }

    return oss.str();
}

[[noreturn]] void throw_openssl_error(const std::string& context) {
    const std::string stack = openssl_error_stack();

    if (stack.empty()) {
        throw OpenSSLError(context);
    }

    throw OpenSSLError(context + ": " + stack);
}

void check_1(int ok, const std::string& context) {
    if (ok != 1) {
        throw_openssl_error(context);
    }
}

int checked_int_size(std::size_t n, const char* label) {
    if (n > static_cast<std::size_t>(INT_MAX)) {
        throw std::invalid_argument(std::string(label) + " is too large for one EVP call");
    }

    return static_cast<int>(n);
}

CtxPtr make_ctx() {
    EVP_CIPHER_CTX* raw = EVP_CIPHER_CTX_new();

    if (!raw) {
        throw_openssl_error("EVP_CIPHER_CTX_new failed");
    }

    return CtxPtr(raw);
}

std::string normalize_cipher_name(std::string s) {
    std::string out;
    out.reserve(s.size());

    for (unsigned char c : s) {
        if (std::isalnum(c)) {
            out.push_back(static_cast<char>(std::toupper(c)));
        }
    }

    if (out.rfind("AES", 0) != 0) {
        throw std::invalid_argument("Cipher name must start with AES, e.g. AES-128-CBC");
    }

    out.erase(0, 3);

    std::string bits;

    if (out.rfind("128", 0) == 0) {
        bits = "128";
        out.erase(0, 3);
    } else if (out.rfind("192", 0) == 0) {
        bits = "192";
        out.erase(0, 3);
    } else if (out.rfind("256", 0) == 0) {
        bits = "256";
        out.erase(0, 3);
    } else {
        throw std::invalid_argument("Cipher name must include AES key size 128, 192, or 256");
    }

    std::string mode = out;

    if (mode == "CFB") {
        mode = "CFB128";
    } else if (mode == "WRAPPAD") {
        mode = "WRAP-PAD";
    } else if (mode == "GCMSIV") {
        mode = "GCM-SIV";
    } else if (mode == "CBCHMACSHA1") {
        mode = "CBC-HMAC-SHA1";
    } else if (mode == "CBCHMACSHA256") {
        mode = "CBC-HMAC-SHA256";
    }

    if (mode.empty()) {
        throw std::invalid_argument("Cipher name must include a mode");
    }

    return "AES-" + bits + "-" + mode;
}

bool contains_mode(const std::string& canonical, const std::string& mode) {
    return canonical.find("-" + mode) != std::string::npos;
}

bool is_ecb(const std::string& n) {
    return contains_mode(n, "ECB");
}

bool is_gcm(const std::string& n) {
    return contains_mode(n, "GCM") && !contains_mode(n, "GCM-SIV");
}

bool is_ccm(const std::string& n) {
    return contains_mode(n, "CCM");
}

bool is_ocb(const std::string& n) {
    return contains_mode(n, "OCB");
}

bool is_aead(const std::string& n) {
    return is_gcm(n) || is_ccm(n) || is_ocb(n);
}

bool is_wrap(const std::string& n) {
    return contains_mode(n, "WRAP");
}

void require_key_len(const EVP_CIPHER* cipher, const Bytes& key) {
    const int expected = EVP_CIPHER_get_key_length(cipher);

    if (expected <= 0) {
        throw std::invalid_argument("EVP reported invalid key length");
    }

    if (key.size() != static_cast<std::size_t>(expected)) {
        std::ostringstream oss;
        oss << "Wrong key length. Expected "
            << expected
            << " byte(s), got "
            << key.size()
            << " byte(s)";
        throw std::invalid_argument(oss.str());
    }
}

void require_iv_len(
    const EVP_CIPHER* cipher,
    const Bytes& iv,
    const std::string& canonical
) {
    if (is_ecb(canonical) || is_wrap(canonical)) {
        if (!iv.empty()) {
            throw std::invalid_argument(canonical + " does not use a caller-provided IV in this lab API");
        }

        return;
    }

    const int expected = EVP_CIPHER_get_iv_length(cipher);

    if (expected > 0 && iv.size() != static_cast<std::size_t>(expected)) {
        std::ostringstream oss;
        oss << canonical
            << " expects IV length "
            << expected
            << " byte(s), got "
            << iv.size();
        throw std::invalid_argument(oss.str());
    }
}

std::size_t evp_update(
    EVP_CIPHER_CTX* ctx,
    Bytes& out,
    std::size_t out_offset,
    const Bytes& in,
    const char* label,
    bool encrypt
) {
    if (in.empty()) {
        return 0;
    }

    int out_len = 0;

    int ok = encrypt
        ? EVP_EncryptUpdate(
              ctx,
              out.data() + out_offset,
              &out_len,
              in.data(),
              checked_int_size(in.size(), label)
          )
        : EVP_DecryptUpdate(
              ctx,
              out.data() + out_offset,
              &out_len,
              in.data(),
              checked_int_size(in.size(), label)
          );

    check_1(ok, std::string("EVP_") + (encrypt ? "EncryptUpdate" : "DecryptUpdate") + " failed");

    return static_cast<std::size_t>(out_len);
}

void evp_update_aad(EVP_CIPHER_CTX* ctx, const Bytes& aad, bool encrypt) {
    if (aad.empty()) {
        return;
    }

    int out_len = 0;

    int ok = encrypt
        ? EVP_EncryptUpdate(
              ctx,
              nullptr,
              &out_len,
              aad.data(),
              checked_int_size(aad.size(), "AAD")
          )
        : EVP_DecryptUpdate(
              ctx,
              nullptr,
              &out_len,
              aad.data(),
              checked_int_size(aad.size(), "AAD")
          );

    check_1(ok, "EVP AAD update failed");
}

void set_aead_iv_len(
    EVP_CIPHER_CTX* ctx,
    const Bytes& nonce,
    const std::string& canonical
) {
    if (nonce.empty()) {
        throw std::invalid_argument(canonical + " nonce/IV must not be empty");
    }

    if (is_ocb(canonical) && nonce.size() > 15) {
        throw std::invalid_argument("OCB nonce length must be at most 15 bytes");
    }

    check_1(
        EVP_CIPHER_CTX_ctrl(
            ctx,
            EVP_CTRL_AEAD_SET_IVLEN,
            checked_int_size(nonce.size(), "nonce"),
            nullptr
        ),
        "EVP_CTRL_AEAD_SET_IVLEN failed"
    );
}

void get_aead_tag(EVP_CIPHER_CTX* ctx, Bytes& tag) {
    if (tag.empty() || tag.size() > 16) {
        throw std::invalid_argument("AEAD tag length must be 1..16 bytes");
    }

    check_1(
        EVP_CIPHER_CTX_ctrl(
            ctx,
            EVP_CTRL_AEAD_GET_TAG,
            checked_int_size(tag.size(), "tag"),
            tag.data()
        ),
        "EVP_CTRL_AEAD_GET_TAG failed"
    );
}

void set_aead_tag(EVP_CIPHER_CTX* ctx, const Bytes& tag) {
    if (tag.empty() || tag.size() > 16) {
        throw std::invalid_argument("AEAD tag length must be 1..16 bytes");
    }

    check_1(
        EVP_CIPHER_CTX_ctrl(
            ctx,
            EVP_CTRL_AEAD_SET_TAG,
            checked_int_size(tag.size(), "tag"),
            const_cast<std::uint8_t*>(tag.data())
        ),
        "EVP_CTRL_AEAD_SET_TAG failed"
    );
}

AEADEncryptResult encrypt_gcm_ocb(
    const EVP_CIPHER* cipher,
    const std::string& canonical,
    const Bytes& key,
    const Bytes& nonce,
    const Bytes& aad,
    const Bytes& plaintext,
    std::size_t tag_len
) {
    if (tag_len == 0 || tag_len > 16) {
        throw std::invalid_argument("AEAD tag length must be 1..16 bytes");
    }

    CtxPtr ctx = make_ctx();

    check_1(EVP_EncryptInit_ex(ctx.get(), cipher, nullptr, nullptr, nullptr),
            "EVP_EncryptInit_ex cipher setup failed");

    if (is_ocb(canonical)) {
        check_1(
            EVP_CIPHER_CTX_ctrl(
                ctx.get(),
                EVP_CTRL_AEAD_SET_TAG,
                checked_int_size(tag_len, "tag length"),
                nullptr
            ),
            "OCB tag length setup failed"
        );
    }

    set_aead_iv_len(ctx.get(), nonce, canonical);

    check_1(EVP_EncryptInit_ex(ctx.get(), nullptr, nullptr, key.data(), nonce.data()),
            "EVP_EncryptInit_ex key/nonce setup failed");

    evp_update_aad(ctx.get(), aad, true);

    Bytes ciphertext(plaintext.size() + EVP_CIPHER_get_block_size(cipher));
    std::size_t written = evp_update(ctx.get(), ciphertext, 0, plaintext, "plaintext", true);

    int final_len = 0;
    check_1(EVP_EncryptFinal_ex(ctx.get(), ciphertext.data() + written, &final_len),
            "EVP_EncryptFinal_ex failed");

    written += static_cast<std::size_t>(final_len);
    ciphertext.resize(written);

    Bytes tag(tag_len);
    get_aead_tag(ctx.get(), tag);

    return {ciphertext, tag};
}

AEADDecryptResult decrypt_gcm_ocb(
    const EVP_CIPHER* cipher,
    const std::string& canonical,
    const Bytes& key,
    const Bytes& nonce,
    const Bytes& aad,
    const Bytes& ciphertext,
    const Bytes& tag
) {
    CtxPtr ctx = make_ctx();

    check_1(EVP_DecryptInit_ex(ctx.get(), cipher, nullptr, nullptr, nullptr),
            "EVP_DecryptInit_ex cipher setup failed");

    if (is_ocb(canonical) && tag.size() != 16) {
        check_1(
            EVP_CIPHER_CTX_ctrl(
                ctx.get(),
                EVP_CTRL_AEAD_SET_TAG,
                checked_int_size(tag.size(), "tag length"),
                nullptr
            ),
            "OCB tag length setup failed"
        );
    }

    set_aead_iv_len(ctx.get(), nonce, canonical);

    check_1(EVP_DecryptInit_ex(ctx.get(), nullptr, nullptr, key.data(), nonce.data()),
            "EVP_DecryptInit_ex key/nonce setup failed");

    evp_update_aad(ctx.get(), aad, false);

    Bytes plaintext(ciphertext.size() + EVP_CIPHER_get_block_size(cipher));
    std::size_t written = evp_update(ctx.get(), plaintext, 0, ciphertext, "ciphertext", false);

    set_aead_tag(ctx.get(), tag);

    int final_len = 0;
    const int ok = EVP_DecryptFinal_ex(ctx.get(), plaintext.data() + written, &final_len);

    if (ok != 1) {
        ERR_clear_error();
        return {{}, false};
    }

    written += static_cast<std::size_t>(final_len);
    plaintext.resize(written);

    return {plaintext, true};
}

AEADEncryptResult encrypt_ccm(
    const EVP_CIPHER* cipher,
    const Bytes& key,
    const Bytes& nonce,
    const Bytes& aad,
    const Bytes& plaintext,
    std::size_t tag_len
) {
    if (tag_len < 4 || tag_len > 16 || (tag_len % 2) != 0) {
        throw std::invalid_argument("CCM tag length must be 4, 6, 8, 10, 12, 14, or 16 bytes");
    }

    CtxPtr ctx = make_ctx();

    check_1(EVP_EncryptInit_ex(ctx.get(), cipher, nullptr, nullptr, nullptr),
            "CCM EncryptInit cipher setup failed");

    set_aead_iv_len(ctx.get(), nonce, "AES-CCM");

    check_1(
        EVP_CIPHER_CTX_ctrl(
            ctx.get(),
            EVP_CTRL_AEAD_SET_TAG,
            checked_int_size(tag_len, "tag length"),
            nullptr
        ),
        "CCM tag length setup failed"
    );

    check_1(EVP_EncryptInit_ex(ctx.get(), nullptr, nullptr, key.data(), nonce.data()),
            "CCM EncryptInit key/nonce setup failed");

    int len = 0;

    check_1(
        EVP_EncryptUpdate(
            ctx.get(),
            nullptr,
            &len,
            nullptr,
            checked_int_size(plaintext.size(), "plaintext length")
        ),
        "CCM plaintext length announcement failed"
    );

    evp_update_aad(ctx.get(), aad, true);

    Bytes ciphertext(plaintext.size());

    if (!plaintext.empty()) {
        check_1(
            EVP_EncryptUpdate(
                ctx.get(),
                ciphertext.data(),
                &len,
                plaintext.data(),
                checked_int_size(plaintext.size(), "plaintext")
            ),
            "CCM EncryptUpdate plaintext failed"
        );

        ciphertext.resize(static_cast<std::size_t>(len));
    }

    check_1(EVP_EncryptFinal_ex(ctx.get(), nullptr, &len), "CCM EncryptFinal failed");

    Bytes tag(tag_len);
    get_aead_tag(ctx.get(), tag);

    return {ciphertext, tag};
}

AEADDecryptResult decrypt_ccm(
    const EVP_CIPHER* cipher,
    const Bytes& key,
    const Bytes& nonce,
    const Bytes& aad,
    const Bytes& ciphertext,
    const Bytes& tag
) {
    if (tag.size() < 4 || tag.size() > 16 || (tag.size() % 2) != 0) {
        throw std::invalid_argument("CCM tag length must be 4, 6, 8, 10, 12, 14, or 16 bytes");
    }

    CtxPtr ctx = make_ctx();

    check_1(EVP_DecryptInit_ex(ctx.get(), cipher, nullptr, nullptr, nullptr),
            "CCM DecryptInit cipher setup failed");

    set_aead_iv_len(ctx.get(), nonce, "AES-CCM");
    set_aead_tag(ctx.get(), tag);

    check_1(EVP_DecryptInit_ex(ctx.get(), nullptr, nullptr, key.data(), nonce.data()),
            "CCM DecryptInit key/nonce setup failed");

    int len = 0;

    check_1(
        EVP_DecryptUpdate(
            ctx.get(),
            nullptr,
            &len,
            nullptr,
            checked_int_size(ciphertext.size(), "ciphertext length")
        ),
        "CCM ciphertext length announcement failed"
    );

    evp_update_aad(ctx.get(), aad, false);

    Bytes plaintext(ciphertext.size());

    if (!ciphertext.empty()) {
        const int ok = EVP_DecryptUpdate(
            ctx.get(),
            plaintext.data(),
            &len,
            ciphertext.data(),
            checked_int_size(ciphertext.size(), "ciphertext")
        );

        if (ok != 1) {
            ERR_clear_error();
            return {{}, false};
        }

        plaintext.resize(static_cast<std::size_t>(len));
    }

    return {plaintext, true};
}

} // anonymous namespace

const EVP_CIPHER* EVPAESDirectTool::resolve_cipher(
    const std::string& cipher_name
) {
    const std::string n = normalize_cipher_name(cipher_name);

    if (n == "AES-128-CBC") return EVP_aes_128_cbc();
    if (n == "AES-128-ECB") return EVP_aes_128_ecb();
    if (n == "AES-128-OFB") return EVP_aes_128_ofb();
    if (n == "AES-128-CFB128") return EVP_aes_128_cfb128();
    if (n == "AES-128-CFB1") return EVP_aes_128_cfb1();
    if (n == "AES-128-CFB8") return EVP_aes_128_cfb8();
    if (n == "AES-128-CTR") return EVP_aes_128_ctr();
    if (n == "AES-128-GCM") return EVP_aes_128_gcm();
    if (n == "AES-128-CCM") return EVP_aes_128_ccm();
    if (n == "AES-128-OCB") return EVP_aes_128_ocb();
    if (n == "AES-128-WRAP") return EVP_aes_128_wrap();
    if (n == "AES-128-WRAP-PAD") return EVP_aes_128_wrap_pad();
    if (n == "AES-128-XTS") return EVP_aes_128_xts();

    if (n == "AES-192-CBC") return EVP_aes_192_cbc();
    if (n == "AES-192-ECB") return EVP_aes_192_ecb();
    if (n == "AES-192-OFB") return EVP_aes_192_ofb();
    if (n == "AES-192-CFB128") return EVP_aes_192_cfb128();
    if (n == "AES-192-CFB1") return EVP_aes_192_cfb1();
    if (n == "AES-192-CFB8") return EVP_aes_192_cfb8();
    if (n == "AES-192-CTR") return EVP_aes_192_ctr();
    if (n == "AES-192-GCM") return EVP_aes_192_gcm();
    if (n == "AES-192-CCM") return EVP_aes_192_ccm();
    if (n == "AES-192-OCB") return EVP_aes_192_ocb();
    if (n == "AES-192-WRAP") return EVP_aes_192_wrap();
    if (n == "AES-192-WRAP-PAD") return EVP_aes_192_wrap_pad();

    if (n == "AES-256-CBC") return EVP_aes_256_cbc();
    if (n == "AES-256-ECB") return EVP_aes_256_ecb();
    if (n == "AES-256-OFB") return EVP_aes_256_ofb();
    if (n == "AES-256-CFB128") return EVP_aes_256_cfb128();
    if (n == "AES-256-CFB1") return EVP_aes_256_cfb1();
    if (n == "AES-256-CFB8") return EVP_aes_256_cfb8();
    if (n == "AES-256-CTR") return EVP_aes_256_ctr();
    if (n == "AES-256-GCM") return EVP_aes_256_gcm();
    if (n == "AES-256-CCM") return EVP_aes_256_ccm();
    if (n == "AES-256-OCB") return EVP_aes_256_ocb();
    if (n == "AES-256-WRAP") return EVP_aes_256_wrap();
    if (n == "AES-256-WRAP-PAD") return EVP_aes_256_wrap_pad();
    if (n == "AES-256-XTS") return EVP_aes_256_xts();

    throw std::invalid_argument("Unsupported algorithm-specific AES EVP cipher: " + cipher_name);
}

bool EVPAESDirectTool::cipher_available(const std::string& cipher_name) {
    try {
        return resolve_cipher(cipher_name) != nullptr;
    } catch (...) {
        return false;
    }
}

std::size_t EVPAESDirectTool::expected_key_length(const std::string& cipher_name) {
    const int len = EVP_CIPHER_get_key_length(resolve_cipher(cipher_name));
    if (len <= 0) throw std::invalid_argument("EVP reported invalid key length");
    return static_cast<std::size_t>(len);
}

std::size_t EVPAESDirectTool::expected_iv_length(const std::string& cipher_name) {
    const int len = EVP_CIPHER_get_iv_length(resolve_cipher(cipher_name));
    if (len < 0) throw std::invalid_argument("EVP reported invalid IV length");
    return static_cast<std::size_t>(len);
}

int EVPAESDirectTool::block_size(const std::string& cipher_name) {
    return EVP_CIPHER_get_block_size(resolve_cipher(cipher_name));
}

Bytes EVPAESDirectTool::encrypt(
    const std::string& cipher_name,
    const Bytes& key,
    const Bytes& iv,
    const Bytes& plaintext,
    bool padding
) {
    const std::string canonical = normalize_cipher_name(cipher_name);
    if (is_aead(canonical)) throw std::invalid_argument("Use aead_encrypt for GCM/CCM/OCB");

    const EVP_CIPHER* cipher = resolve_cipher(canonical);
    require_key_len(cipher, key);
    require_iv_len(cipher, iv, canonical);

    CtxPtr ctx = make_ctx();
    const unsigned char* iv_ptr = iv.empty() ? nullptr : iv.data();

    check_1(EVP_EncryptInit_ex(ctx.get(), cipher, nullptr, key.data(), iv_ptr),
            "EVP_EncryptInit_ex failed");

    check_1(EVP_CIPHER_CTX_set_padding(ctx.get(), padding ? 1 : 0),
            "EVP_CIPHER_CTX_set_padding failed");

    Bytes output(plaintext.size() + EVP_CIPHER_get_block_size(cipher) + 32);
    std::size_t written = evp_update(ctx.get(), output, 0, plaintext, "plaintext", true);

    int final_len = 0;
    check_1(EVP_EncryptFinal_ex(ctx.get(), output.data() + written, &final_len),
            "EVP_EncryptFinal_ex failed");

    written += static_cast<std::size_t>(final_len);
    output.resize(written);
    return output;
}

Bytes EVPAESDirectTool::decrypt(
    const std::string& cipher_name,
    const Bytes& key,
    const Bytes& iv,
    const Bytes& ciphertext,
    bool padding
) {
    const std::string canonical = normalize_cipher_name(cipher_name);
    if (is_aead(canonical)) throw std::invalid_argument("Use aead_decrypt for GCM/CCM/OCB");

    const EVP_CIPHER* cipher = resolve_cipher(canonical);
    require_key_len(cipher, key);
    require_iv_len(cipher, iv, canonical);

    CtxPtr ctx = make_ctx();
    const unsigned char* iv_ptr = iv.empty() ? nullptr : iv.data();

    check_1(EVP_DecryptInit_ex(ctx.get(), cipher, nullptr, key.data(), iv_ptr),
            "EVP_DecryptInit_ex failed");

    check_1(EVP_CIPHER_CTX_set_padding(ctx.get(), padding ? 1 : 0),
            "EVP_CIPHER_CTX_set_padding failed");

    Bytes output(ciphertext.size() + EVP_CIPHER_get_block_size(cipher) + 32);
    std::size_t written = evp_update(ctx.get(), output, 0, ciphertext, "ciphertext", false);

    int final_len = 0;
    check_1(EVP_DecryptFinal_ex(ctx.get(), output.data() + written, &final_len),
            "EVP_DecryptFinal_ex failed");

    written += static_cast<std::size_t>(final_len);
    output.resize(written);
    return output;
}

AEADEncryptResult EVPAESDirectTool::aead_encrypt(
    const std::string& cipher_name,
    const Bytes& key,
    const Bytes& nonce,
    const Bytes& aad,
    const Bytes& plaintext,
    std::size_t tag_len
) {
    const std::string canonical = normalize_cipher_name(cipher_name);
    if (!is_aead(canonical)) throw std::invalid_argument("Use encrypt for non-AEAD modes");

    const EVP_CIPHER* cipher = resolve_cipher(canonical);
    require_key_len(cipher, key);

    if (is_ccm(canonical)) {
        return encrypt_ccm(cipher, key, nonce, aad, plaintext, tag_len);
    }

    return encrypt_gcm_ocb(cipher, canonical, key, nonce, aad, plaintext, tag_len);
}

AEADDecryptResult EVPAESDirectTool::aead_decrypt(
    const std::string& cipher_name,
    const Bytes& key,
    const Bytes& nonce,
    const Bytes& aad,
    const Bytes& ciphertext,
    const Bytes& tag
) {
    const std::string canonical = normalize_cipher_name(cipher_name);
    if (!is_aead(canonical)) throw std::invalid_argument("Use decrypt for non-AEAD modes");

    const EVP_CIPHER* cipher = resolve_cipher(canonical);
    require_key_len(cipher, key);

    if (is_ccm(canonical)) {
        return decrypt_ccm(cipher, key, nonce, aad, ciphertext, tag);
    }

    return decrypt_gcm_ocb(cipher, canonical, key, nonce, aad, ciphertext, tag);
}

Bytes EVPAESDirectTool::hex_to_bytes(const std::string& hex) {
    std::string clean;
    clean.reserve(hex.size());

    for (std::size_t i = 0; i < hex.size();) {
        if (i + 1 < hex.size() && hex[i] == '0' && (hex[i + 1] == 'x' || hex[i + 1] == 'X')) {
            i += 2;
            continue;
        }

        const unsigned char c = static_cast<unsigned char>(hex[i]);

        if (std::isxdigit(c)) clean.push_back(static_cast<char>(c));
        else if (std::isspace(c) || c == ':' || c == '-' || c == '_') {}
        else throw std::invalid_argument("Invalid character in hex string");
        ++i;
    }

    if ((clean.size() % 2) != 0) throw std::invalid_argument("Hex string must contain an even number of digits");

    auto hex_value = [](char c) -> int {
        if (c >= '0' && c <= '9') return c - '0';
        if (c >= 'a' && c <= 'f') return 10 + c - 'a';
        if (c >= 'A' && c <= 'F') return 10 + c - 'A';
        return -1;
    };

    Bytes out;
    out.reserve(clean.size() / 2);

    for (std::size_t i = 0; i < clean.size(); i += 2) {
        const int hi = hex_value(clean[i]);
        const int lo = hex_value(clean[i + 1]);
        if (hi < 0 || lo < 0) throw std::invalid_argument("Invalid hex digit");
        out.push_back(static_cast<std::uint8_t>((hi << 4) | lo));
    }

    return out;
}

std::string EVPAESDirectTool::bytes_to_hex(const Bytes& data, bool lowercase) {
    std::ostringstream oss;
    if (!lowercase) oss << std::uppercase;
    oss << std::hex << std::setfill('0');
    for (std::uint8_t b : data) oss << std::setw(2) << static_cast<int>(b);
    return oss.str();
}

Bytes EVPAESDirectTool::text_to_bytes(const std::string& text) {
    return Bytes(text.begin(), text.end());
}

std::string EVPAESDirectTool::bytes_to_text_lossy(const Bytes& data) {
    return std::string(data.begin(), data.end());
}

} // namespace aeslab_evp_direct
