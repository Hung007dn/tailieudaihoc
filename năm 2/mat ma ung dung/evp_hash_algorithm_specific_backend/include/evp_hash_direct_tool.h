#pragma once

#include <cstddef>
#include <cstdint>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

#include <openssl/evp.h>

namespace hashlab_evp_direct {

using Bytes = std::vector<std::uint8_t>;

struct DigestInfo {
    std::string canonical_name;
    int output_size = 0;
    int block_size = 0;
    bool is_xof = false;
};

class OpenSSLError : public std::runtime_error {
public:
    explicit OpenSSLError(const std::string& message)
        : std::runtime_error(message) {}
};

struct MdCtxDeleter {
    void operator()(EVP_MD_CTX* p) const noexcept {
        EVP_MD_CTX_free(p);
    }
};

class DirectDigestContext {
public:
    explicit DirectDigestContext(const std::string& algorithm_name);

    DirectDigestContext(const DirectDigestContext&) = delete;
    DirectDigestContext& operator=(const DirectDigestContext&) = delete;

    DirectDigestContext(DirectDigestContext&&) noexcept = default;
    DirectDigestContext& operator=(DirectDigestContext&&) noexcept = default;

    void update(const Bytes& data);
    void update(const std::uint8_t* data, std::size_t data_len);

    Bytes final();
    Bytes final_xof(std::size_t output_len);

    DirectDigestContext clone() const;
    DigestInfo info() const;

private:
    DirectDigestContext(
        const std::string& canonical_name,
        const EVP_MD* md,
        EVP_MD_CTX* raw_ctx
    );

    std::string canonical_name_;
    const EVP_MD* md_ = nullptr;
    std::unique_ptr<EVP_MD_CTX, MdCtxDeleter> ctx_;
};

class EVPHashDirectTool {
public:
    static const EVP_MD* resolve_digest(const std::string& algorithm_name);
    static std::string canonical_name(const std::string& algorithm_name);

    static bool digest_available(const std::string& algorithm_name);
    static DigestInfo digest_info(const std::string& algorithm_name);

    static Bytes digest(
        const std::string& algorithm_name,
        const Bytes& input,
        std::size_t xof_output_len = 0
    );

    static Bytes digest_file(
        const std::string& algorithm_name,
        const std::string& path,
        std::size_t xof_output_len = 0
    );

    static std::vector<std::string> supported_algorithms();

    static Bytes hex_to_bytes(const std::string& hex);
    static std::string bytes_to_hex(const Bytes& data, bool lowercase = true);
    static Bytes text_to_bytes(const std::string& text);
    static std::string bytes_to_text_lossy(const Bytes& data);
};

} // namespace hashlab_evp_direct
