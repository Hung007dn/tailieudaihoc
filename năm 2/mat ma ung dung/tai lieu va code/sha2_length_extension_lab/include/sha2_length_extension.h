#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>

namespace sha2lenext {

using Bytes = std::vector<std::uint8_t>;

struct SHA256ForgeResult {
    Bytes forged_message;  // known_message || glue_padding || suffix
    Bytes forged_mac;      // SHA256(secret || forged_message), computed without secret
    Bytes glue_padding;    // SHA256 padding for secret || known_message
    std::uint64_t processed_before_suffix = 0;
};

struct SHA512ForgeResult {
    Bytes forged_message;
    Bytes forged_mac;
    Bytes glue_padding;
    std::uint64_t processed_before_suffix = 0;
};

/*
    Educational SHA-256 implementation.

    Important teaching feature:
        set_state_from_digest(...)
        set_state(...)

    These are intentionally dangerous/non-standard features used only to
    demonstrate Merkle-Damgard length extension.

    OpenSSL EVP does NOT expose these knobs, correctly.
*/
class SHA256 {
public:
    static constexpr std::size_t BLOCK_SIZE = 64;
    static constexpr std::size_t DIGEST_SIZE = 32;

    SHA256();

    void reset();

    /*
        Resume hashing from a custom internal state.

        processed_bytes means:
            the number of bytes already absorbed before the next update().

        For a real resumed SHA-256 state, processed_bytes should be a multiple
        of 64 because there is no partial block buffer in this API.
    */
    void set_state(
        const std::array<std::uint32_t, 8>& state,
        std::uint64_t processed_bytes
    );

    void set_state_from_digest(
        const Bytes& digest,
        std::uint64_t processed_bytes
    );

    void update(const std::uint8_t* data, std::size_t len);
    void update(const Bytes& data);
    void update(const std::string& text);

    Bytes final();

    static Bytes digest(const Bytes& data);
    static Bytes digest(const std::string& text);

    static std::array<std::uint32_t, 8> digest_to_state(const Bytes& digest);
    static Bytes state_to_digest(const std::array<std::uint32_t, 8>& state);

private:
    std::array<std::uint32_t, 8> h_{};
    std::array<std::uint8_t, BLOCK_SIZE> buffer_{};
    std::size_t buffer_len_ = 0;
    std::uint64_t total_len_ = 0;

    void transform(const std::uint8_t block[BLOCK_SIZE]);
};

/*
    Educational SHA-512 implementation.

    Same idea as SHA256 but with:
        block size 128 bytes
        digest size 64 bytes
        64-bit chaining words
*/
class SHA512 {
public:
    static constexpr std::size_t BLOCK_SIZE = 128;
    static constexpr std::size_t DIGEST_SIZE = 64;

    SHA512();

    void reset();

    void set_state(
        const std::array<std::uint64_t, 8>& state,
        std::uint64_t processed_bytes
    );

    void set_state_from_digest(
        const Bytes& digest,
        std::uint64_t processed_bytes
    );

    void update(const std::uint8_t* data, std::size_t len);
    void update(const Bytes& data);
    void update(const std::string& text);

    Bytes final();

    static Bytes digest(const Bytes& data);
    static Bytes digest(const std::string& text);

    static std::array<std::uint64_t, 8> digest_to_state(const Bytes& digest);
    static Bytes state_to_digest(const std::array<std::uint64_t, 8>& state);

private:
    std::array<std::uint64_t, 8> h_{};
    std::array<std::uint8_t, BLOCK_SIZE> buffer_{};
    std::size_t buffer_len_ = 0;
    std::uint64_t total_len_ = 0;

    void transform(const std::uint8_t block[BLOCK_SIZE]);
};

/*
    Glue padding for a secret-prefix message.

    original_total_len_bytes must include the unknown secret length:
        secret_len_guess + known_message.size()
*/
Bytes sha256_glue_padding(std::uint64_t original_total_len_bytes);
Bytes sha512_glue_padding(std::uint64_t original_total_len_bytes);

/*
    Length-extension attack for secret-prefix MAC:

        MAC = SHA256(secret || known_message)

    Attacker knows:
        known_message
        known_mac
        suffix to append
        guessed secret length

    Attacker computes:
        forged_message = known_message || glue_padding || suffix
        forged_mac     = SHA256-resume(known_mac_state, suffix)
*/
SHA256ForgeResult forge_sha256_secret_prefix_mac(
    const Bytes& known_message,
    const Bytes& known_mac,
    std::uint64_t guessed_secret_len,
    const Bytes& suffix
);

SHA512ForgeResult forge_sha512_secret_prefix_mac(
    const Bytes& known_message,
    const Bytes& known_mac,
    std::uint64_t guessed_secret_len,
    const Bytes& suffix
);

/*
    Demo helpers for verifying the attack in a controlled lab.
*/
Bytes secret_prefix_mac_sha256(
    const Bytes& secret,
    const Bytes& message
);

Bytes secret_prefix_mac_sha512(
    const Bytes& secret,
    const Bytes& message
);

bool verify_secret_prefix_mac_sha256(
    const Bytes& secret,
    const Bytes& message,
    const Bytes& mac
);

bool verify_secret_prefix_mac_sha512(
    const Bytes& secret,
    const Bytes& message,
    const Bytes& mac
);

/*
    Utilities.
*/
Bytes hex_to_bytes(const std::string& hex);
std::string bytes_to_hex(const Bytes& data, bool lowercase = true);
Bytes text_to_bytes(const std::string& text);
std::string bytes_to_text_lossy(const Bytes& data);
std::string bytes_to_c_escaped(const Bytes& data);

} // namespace sha2lenext
