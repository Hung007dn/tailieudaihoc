#include "evp_hash_direct_tool.h"

#include <algorithm>
#include <cctype>
#include <climits>
#include <fstream>
#include <iomanip>
#include <sstream>

#include <openssl/err.h>
#include <openssl/opensslv.h>

namespace hashlab_evp_direct {

namespace {

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

std::string normalize_digest_name(std::string s) {
    std::string out;
    out.reserve(s.size());

    for (unsigned char c : s) {
        if (std::isalnum(c)) {
            out.push_back(static_cast<char>(std::toupper(c)));
        }
    }

    if (out == "SHA") return "SHA1";
    if (out == "SHA512224") return "SHA512-224";
    if (out == "SHA512256") return "SHA512-256";
    if (out == "SHA3224") return "SHA3-224";
    if (out == "SHA3256") return "SHA3-256";
    if (out == "SHA3384") return "SHA3-384";
    if (out == "SHA3512") return "SHA3-512";
    if (out == "SHAKE128") return "SHAKE128";
    if (out == "SHAKE256") return "SHAKE256";
    if (out == "MD5SHA1") return "MD5-SHA1";

    return out;
}

bool md_is_xof(const EVP_MD* md) {
#if OPENSSL_VERSION_NUMBER >= 0x30000000L
    return EVP_MD_xof(md) != 0;
#else
    (void)md;
    return false;
#endif
}

EVP_MD_CTX* make_raw_ctx() {
    EVP_MD_CTX* ctx = EVP_MD_CTX_new();

    if (!ctx) {
        throw_openssl_error("EVP_MD_CTX_new failed");
    }

    return ctx;
}

Bytes read_binary_file(const std::string& path) {
    std::ifstream in(path, std::ios::binary);

    if (!in) {
        throw std::runtime_error("Cannot open file for reading: " + path);
    }

    in.seekg(0, std::ios::end);
    const std::streamoff size = in.tellg();

    if (size < 0) {
        throw std::runtime_error("Cannot determine file size: " + path);
    }

    in.seekg(0, std::ios::beg);

    Bytes data(static_cast<std::size_t>(size));

    if (!data.empty()) {
        in.read(reinterpret_cast<char*>(data.data()), size);

        if (!in) {
            throw std::runtime_error("Failed to read file: " + path);
        }
    }

    return data;
}

} // anonymous namespace

DirectDigestContext::DirectDigestContext(const std::string& algorithm_name)
    : canonical_name_(EVPHashDirectTool::canonical_name(algorithm_name)),
      md_(EVPHashDirectTool::resolve_digest(algorithm_name)),
      ctx_(make_raw_ctx()) {
    check_1(EVP_DigestInit_ex(ctx_.get(), md_, nullptr), "EVP_DigestInit_ex failed");
}

DirectDigestContext::DirectDigestContext(
    const std::string& canonical_name,
    const EVP_MD* md,
    EVP_MD_CTX* raw_ctx
)
    : canonical_name_(canonical_name), md_(md), ctx_(raw_ctx) {}

void DirectDigestContext::update(const Bytes& data) {
    update(data.empty() ? nullptr : data.data(), data.size());
}

void DirectDigestContext::update(const std::uint8_t* data, std::size_t data_len) {
    if (data == nullptr && data_len != 0) {
        throw std::invalid_argument("Digest update data is null but length is non-zero");
    }

    if (data_len == 0) return;

    check_1(EVP_DigestUpdate(ctx_.get(), data, data_len), "EVP_DigestUpdate failed");
}

Bytes DirectDigestContext::final() {
    if (md_is_xof(md_)) {
        throw std::invalid_argument("Use final_xof() for SHAKE/XOF digests");
    }

    const int size = EVP_MD_get_size(md_);
    if (size <= 0) {
        throw std::invalid_argument("EVP_MD_get_size returned invalid digest size");
    }

    Bytes out(static_cast<std::size_t>(size));
    unsigned int out_len = 0;

    check_1(EVP_DigestFinal_ex(ctx_.get(), out.data(), &out_len), "EVP_DigestFinal_ex failed");
    out.resize(out_len);
    return out;
}

Bytes DirectDigestContext::final_xof(std::size_t output_len) {
    if (!md_is_xof(md_)) {
        throw std::invalid_argument("final_xof() is only valid for SHAKE/XOF digests");
    }

    if (output_len == 0) {
        const int default_len = EVP_MD_get_size(md_);
        if (default_len <= 0) {
            throw std::invalid_argument("XOF output length must be non-zero");
        }
        output_len = static_cast<std::size_t>(default_len);
    }

    Bytes out(output_len);
    check_1(EVP_DigestFinalXOF(ctx_.get(), out.data(), output_len), "EVP_DigestFinalXOF failed");
    return out;
}

DirectDigestContext DirectDigestContext::clone() const {
    EVP_MD_CTX* raw = make_raw_ctx();
    const int ok = EVP_MD_CTX_copy_ex(raw, ctx_.get());

    if (ok != 1) {
        EVP_MD_CTX_free(raw);
        throw_openssl_error("EVP_MD_CTX_copy_ex failed");
    }

    return DirectDigestContext(canonical_name_, md_, raw);
}

DigestInfo DirectDigestContext::info() const {
    DigestInfo info;
    info.canonical_name = canonical_name_;
    info.output_size = EVP_MD_get_size(md_);
    info.block_size = EVP_MD_get_block_size(md_);
    info.is_xof = md_is_xof(md_);
    return info;
}

std::string EVPHashDirectTool::canonical_name(const std::string& algorithm_name) {
    return normalize_digest_name(algorithm_name);
}

const EVP_MD* EVPHashDirectTool::resolve_digest(const std::string& algorithm_name) {
    const std::string n = normalize_digest_name(algorithm_name);

    if (n == "SHA1") return EVP_sha1();
    if (n == "SHA224") return EVP_sha224();
    if (n == "SHA256") return EVP_sha256();
    if (n == "SHA384") return EVP_sha384();
    if (n == "SHA512") return EVP_sha512();
    if (n == "SHA512-224") return EVP_sha512_224();
    if (n == "SHA512-256") return EVP_sha512_256();

    if (n == "SHA3-224") return EVP_sha3_224();
    if (n == "SHA3-256") return EVP_sha3_256();
    if (n == "SHA3-384") return EVP_sha3_384();
    if (n == "SHA3-512") return EVP_sha3_512();

    if (n == "SHAKE128") return EVP_shake128();
    if (n == "SHAKE256") return EVP_shake256();

    if (n == "MD5-SHA1") return EVP_md5_sha1();

    throw std::invalid_argument("Unsupported algorithm-specific EVP digest: " + algorithm_name);
}

bool EVPHashDirectTool::digest_available(const std::string& algorithm_name) {
    try {
        return resolve_digest(algorithm_name) != nullptr;
    } catch (...) {
        return false;
    }
}

DigestInfo EVPHashDirectTool::digest_info(const std::string& algorithm_name) {
    const EVP_MD* md = resolve_digest(algorithm_name);

    DigestInfo info;
    info.canonical_name = canonical_name(algorithm_name);
    info.output_size = EVP_MD_get_size(md);
    info.block_size = EVP_MD_get_block_size(md);
    info.is_xof = md_is_xof(md);
    return info;
}

Bytes EVPHashDirectTool::digest(
    const std::string& algorithm_name,
    const Bytes& input,
    std::size_t xof_output_len
) {
    DirectDigestContext ctx(algorithm_name);
    ctx.update(input);

    DigestInfo info = ctx.info();
    if (info.is_xof) {
        return ctx.final_xof(xof_output_len);
    }

    if (xof_output_len != 0) {
        throw std::invalid_argument("xof_output_len must be zero for non-XOF digests");
    }

    return ctx.final();
}

Bytes EVPHashDirectTool::digest_file(
    const std::string& algorithm_name,
    const std::string& path,
    std::size_t xof_output_len
) {
    return digest(algorithm_name, read_binary_file(path), xof_output_len);
}

std::vector<std::string> EVPHashDirectTool::supported_algorithms() {
    return {
        "sha1", "sha224", "sha256", "sha384", "sha512",
        "sha512-224", "sha512-256",
        "sha3-224", "sha3-256", "sha3-384", "sha3-512",
        "shake128", "shake256", "md5-sha1"
    };
}

Bytes EVPHashDirectTool::hex_to_bytes(const std::string& hex) {
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

    if ((clean.size() % 2) != 0) {
        throw std::invalid_argument("Hex string must contain an even number of digits");
    }

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

std::string EVPHashDirectTool::bytes_to_hex(const Bytes& data, bool lowercase) {
    std::ostringstream oss;
    if (!lowercase) oss << std::uppercase;
    oss << std::hex << std::setfill('0');
    for (std::uint8_t b : data) oss << std::setw(2) << static_cast<int>(b);
    return oss.str();
}

Bytes EVPHashDirectTool::text_to_bytes(const std::string& text) {
    return Bytes(text.begin(), text.end());
}

std::string EVPHashDirectTool::bytes_to_text_lossy(const Bytes& data) {
    return std::string(data.begin(), data.end());
}

} // namespace hashlab_evp_direct
