#include "sha2_length_extension.h"

#include <algorithm>
#include <cctype>
#include <iomanip>
#include <sstream>

namespace sha2lenext {

namespace {

constexpr std::uint32_t SHA256_K[64] = {
    0x428a2f98u, 0x71374491u, 0xb5c0fbcfu, 0xe9b5dba5u,
    0x3956c25bu, 0x59f111f1u, 0x923f82a4u, 0xab1c5ed5u,
    0xd807aa98u, 0x12835b01u, 0x243185beu, 0x550c7dc3u,
    0x72be5d74u, 0x80deb1feu, 0x9bdc06a7u, 0xc19bf174u,
    0xe49b69c1u, 0xefbe4786u, 0x0fc19dc6u, 0x240ca1ccu,
    0x2de92c6fu, 0x4a7484aau, 0x5cb0a9dcu, 0x76f988dau,
    0x983e5152u, 0xa831c66du, 0xb00327c8u, 0xbf597fc7u,
    0xc6e00bf3u, 0xd5a79147u, 0x06ca6351u, 0x14292967u,
    0x27b70a85u, 0x2e1b2138u, 0x4d2c6dfcu, 0x53380d13u,
    0x650a7354u, 0x766a0abbu, 0x81c2c92eu, 0x92722c85u,
    0xa2bfe8a1u, 0xa81a664bu, 0xc24b8b70u, 0xc76c51a3u,
    0xd192e819u, 0xd6990624u, 0xf40e3585u, 0x106aa070u,
    0x19a4c116u, 0x1e376c08u, 0x2748774cu, 0x34b0bcb5u,
    0x391c0cb3u, 0x4ed8aa4au, 0x5b9cca4fu, 0x682e6ff3u,
    0x748f82eeu, 0x78a5636fu, 0x84c87814u, 0x8cc70208u,
    0x90befffau, 0xa4506cebu, 0xbef9a3f7u, 0xc67178f2u
};

constexpr std::uint64_t SHA512_K[80] = {
    0x428a2f98d728ae22ULL, 0x7137449123ef65cdULL,
    0xb5c0fbcfec4d3b2fULL, 0xe9b5dba58189dbbcULL,
    0x3956c25bf348b538ULL, 0x59f111f1b605d019ULL,
    0x923f82a4af194f9bULL, 0xab1c5ed5da6d8118ULL,
    0xd807aa98a3030242ULL, 0x12835b0145706fbeULL,
    0x243185be4ee4b28cULL, 0x550c7dc3d5ffb4e2ULL,
    0x72be5d74f27b896fULL, 0x80deb1fe3b1696b1ULL,
    0x9bdc06a725c71235ULL, 0xc19bf174cf692694ULL,
    0xe49b69c19ef14ad2ULL, 0xefbe4786384f25e3ULL,
    0x0fc19dc68b8cd5b5ULL, 0x240ca1cc77ac9c65ULL,
    0x2de92c6f592b0275ULL, 0x4a7484aa6ea6e483ULL,
    0x5cb0a9dcbd41fbd4ULL, 0x76f988da831153b5ULL,
    0x983e5152ee66dfabULL, 0xa831c66d2db43210ULL,
    0xb00327c898fb213fULL, 0xbf597fc7beef0ee4ULL,
    0xc6e00bf33da88fc2ULL, 0xd5a79147930aa725ULL,
    0x06ca6351e003826fULL, 0x142929670a0e6e70ULL,
    0x27b70a8546d22ffcULL, 0x2e1b21385c26c926ULL,
    0x4d2c6dfc5ac42aedULL, 0x53380d139d95b3dfULL,
    0x650a73548baf63deULL, 0x766a0abb3c77b2a8ULL,
    0x81c2c92e47edaee6ULL, 0x92722c851482353bULL,
    0xa2bfe8a14cf10364ULL, 0xa81a664bbc423001ULL,
    0xc24b8b70d0f89791ULL, 0xc76c51a30654be30ULL,
    0xd192e819d6ef5218ULL, 0xd69906245565a910ULL,
    0xf40e35855771202aULL, 0x106aa07032bbd1b8ULL,
    0x19a4c116b8d2d0c8ULL, 0x1e376c085141ab53ULL,
    0x2748774cdf8eeb99ULL, 0x34b0bcb5e19b48a8ULL,
    0x391c0cb3c5c95a63ULL, 0x4ed8aa4ae3418acbULL,
    0x5b9cca4f7763e373ULL, 0x682e6ff3d6b2b8a3ULL,
    0x748f82ee5defb2fcULL, 0x78a5636f43172f60ULL,
    0x84c87814a1f0ab72ULL, 0x8cc702081a6439ecULL,
    0x90befffa23631e28ULL, 0xa4506cebde82bde9ULL,
    0xbef9a3f7b2c67915ULL, 0xc67178f2e372532bULL,
    0xca273eceea26619cULL, 0xd186b8c721c0c207ULL,
    0xeada7dd6cde0eb1eULL, 0xf57d4f7fee6ed178ULL,
    0x06f067aa72176fbaULL, 0x0a637dc5a2c898a6ULL,
    0x113f9804bef90daeULL, 0x1b710b35131c471bULL,
    0x28db77f523047d84ULL, 0x32caab7b40c72493ULL,
    0x3c9ebe0a15c9bebcULL, 0x431d67c49c100d4cULL,
    0x4cc5d4becb3e42b6ULL, 0x597f299cfc657e2aULL,
    0x5fcb6fab3ad6faecULL, 0x6c44198c4a475817ULL
};

inline std::uint32_t rotr32(std::uint32_t x, unsigned n) {
    return (x >> n) | (x << (32 - n));
}

inline std::uint64_t rotr64(std::uint64_t x, unsigned n) {
    return (x >> n) | (x << (64 - n));
}

inline std::uint32_t load_be32(const std::uint8_t* p) {
    return (static_cast<std::uint32_t>(p[0]) << 24) |
           (static_cast<std::uint32_t>(p[1]) << 16) |
           (static_cast<std::uint32_t>(p[2]) << 8) |
           (static_cast<std::uint32_t>(p[3]));
}

inline std::uint64_t load_be64(const std::uint8_t* p) {
    return (static_cast<std::uint64_t>(p[0]) << 56) |
           (static_cast<std::uint64_t>(p[1]) << 48) |
           (static_cast<std::uint64_t>(p[2]) << 40) |
           (static_cast<std::uint64_t>(p[3]) << 32) |
           (static_cast<std::uint64_t>(p[4]) << 24) |
           (static_cast<std::uint64_t>(p[5]) << 16) |
           (static_cast<std::uint64_t>(p[6]) << 8) |
           (static_cast<std::uint64_t>(p[7]));
}

inline void store_be32(std::uint8_t* p, std::uint32_t x) {
    p[0] = static_cast<std::uint8_t>(x >> 24);
    p[1] = static_cast<std::uint8_t>(x >> 16);
    p[2] = static_cast<std::uint8_t>(x >> 8);
    p[3] = static_cast<std::uint8_t>(x);
}

inline void store_be64(std::uint8_t* p, std::uint64_t x) {
    p[0] = static_cast<std::uint8_t>(x >> 56);
    p[1] = static_cast<std::uint8_t>(x >> 48);
    p[2] = static_cast<std::uint8_t>(x >> 40);
    p[3] = static_cast<std::uint8_t>(x >> 32);
    p[4] = static_cast<std::uint8_t>(x >> 24);
    p[5] = static_cast<std::uint8_t>(x >> 16);
    p[6] = static_cast<std::uint8_t>(x >> 8);
    p[7] = static_cast<std::uint8_t>(x);
}

} // anonymous namespace

SHA256::SHA256() {
    reset();
}

void SHA256::reset() {
    h_ = {
        0x6a09e667u,
        0xbb67ae85u,
        0x3c6ef372u,
        0xa54ff53au,
        0x510e527fu,
        0x9b05688cu,
        0x1f83d9abu,
        0x5be0cd19u
    };

    buffer_.fill(0);
    buffer_len_ = 0;
    total_len_ = 0;
}

void SHA256::set_state(
    const std::array<std::uint32_t, 8>& state,
    std::uint64_t processed_bytes
) {
    if ((processed_bytes % BLOCK_SIZE) != 0) {
        throw std::invalid_argument("SHA256 set_state requires processed_bytes to be a multiple of 64");
    }

    h_ = state;
    buffer_.fill(0);
    buffer_len_ = 0;
    total_len_ = processed_bytes;
}

void SHA256::set_state_from_digest(
    const Bytes& digest,
    std::uint64_t processed_bytes
) {
    set_state(
        digest_to_state(digest),
        processed_bytes
    );
}

void SHA256::update(
    const std::uint8_t* data,
    std::size_t len
) {
    if (data == nullptr && len != 0) {
        throw std::invalid_argument("SHA256 update received null data with non-zero length");
    }

    for (std::size_t i = 0; i < len; ++i) {
        buffer_[buffer_len_++] = data[i];
        ++total_len_;

        if (buffer_len_ == BLOCK_SIZE) {
            transform(buffer_.data());
            buffer_len_ = 0;
        }
    }
}

void SHA256::update(const Bytes& data) {
    update(
        data.empty() ? nullptr : data.data(),
        data.size()
    );
}

void SHA256::update(const std::string& text) {
    update(
        reinterpret_cast<const std::uint8_t*>(text.data()),
        text.size()
    );
}

Bytes SHA256::final() {
    const std::uint64_t bit_len = total_len_ * 8u;

    buffer_[buffer_len_++] = 0x80u;

    if (buffer_len_ > 56) {
        while (buffer_len_ < BLOCK_SIZE) {
            buffer_[buffer_len_++] = 0x00u;
        }

        transform(buffer_.data());
        buffer_len_ = 0;
    }

    while (buffer_len_ < 56) {
        buffer_[buffer_len_++] = 0x00u;
    }

    store_be64(&buffer_[56], bit_len);
    transform(buffer_.data());

    Bytes out(DIGEST_SIZE);

    for (std::size_t i = 0; i < h_.size(); ++i) {
        store_be32(&out[i * 4], h_[i]);
    }

    reset();
    return out;
}

Bytes SHA256::digest(const Bytes& data) {
    SHA256 ctx;
    ctx.update(data);
    return ctx.final();
}

Bytes SHA256::digest(const std::string& text) {
    SHA256 ctx;
    ctx.update(text);
    return ctx.final();
}

std::array<std::uint32_t, 8> SHA256::digest_to_state(
    const Bytes& digest
) {
    if (digest.size() != DIGEST_SIZE) {
        throw std::invalid_argument("SHA256 digest_to_state requires a 32-byte digest");
    }

    std::array<std::uint32_t, 8> state{};

    for (std::size_t i = 0; i < state.size(); ++i) {
        state[i] = load_be32(&digest[i * 4]);
    }

    return state;
}

Bytes SHA256::state_to_digest(
    const std::array<std::uint32_t, 8>& state
) {
    Bytes out(DIGEST_SIZE);

    for (std::size_t i = 0; i < state.size(); ++i) {
        store_be32(&out[i * 4], state[i]);
    }

    return out;
}

void SHA256::transform(
    const std::uint8_t block[BLOCK_SIZE]
) {
    std::uint32_t w[64];

    for (std::size_t i = 0; i < 16; ++i) {
        w[i] = load_be32(block + i * 4);
    }

    for (std::size_t i = 16; i < 64; ++i) {
        const std::uint32_t s0 =
            rotr32(w[i - 15], 7) ^
            rotr32(w[i - 15], 18) ^
            (w[i - 15] >> 3);

        const std::uint32_t s1 =
            rotr32(w[i - 2], 17) ^
            rotr32(w[i - 2], 19) ^
            (w[i - 2] >> 10);

        w[i] = w[i - 16] + s0 + w[i - 7] + s1;
    }

    std::uint32_t a = h_[0];
    std::uint32_t b = h_[1];
    std::uint32_t c = h_[2];
    std::uint32_t d = h_[3];
    std::uint32_t e = h_[4];
    std::uint32_t f = h_[5];
    std::uint32_t g = h_[6];
    std::uint32_t h = h_[7];

    for (std::size_t i = 0; i < 64; ++i) {
        const std::uint32_t S1 =
            rotr32(e, 6) ^
            rotr32(e, 11) ^
            rotr32(e, 25);

        const std::uint32_t ch =
            (e & f) ^ ((~e) & g);

        const std::uint32_t temp1 =
            h + S1 + ch + SHA256_K[i] + w[i];

        const std::uint32_t S0 =
            rotr32(a, 2) ^
            rotr32(a, 13) ^
            rotr32(a, 22);

        const std::uint32_t maj =
            (a & b) ^ (a & c) ^ (b & c);

        const std::uint32_t temp2 =
            S0 + maj;

        h = g;
        g = f;
        f = e;
        e = d + temp1;
        d = c;
        c = b;
        b = a;
        a = temp1 + temp2;
    }

    h_[0] += a;
    h_[1] += b;
    h_[2] += c;
    h_[3] += d;
    h_[4] += e;
    h_[5] += f;
    h_[6] += g;
    h_[7] += h;
}

SHA512::SHA512() {
    reset();
}

void SHA512::reset() {
    h_ = {
        0x6a09e667f3bcc908ULL,
        0xbb67ae8584caa73bULL,
        0x3c6ef372fe94f82bULL,
        0xa54ff53a5f1d36f1ULL,
        0x510e527fade682d1ULL,
        0x9b05688c2b3e6c1fULL,
        0x1f83d9abfb41bd6bULL,
        0x5be0cd19137e2179ULL
    };

    buffer_.fill(0);
    buffer_len_ = 0;
    total_len_ = 0;
}

void SHA512::set_state(
    const std::array<std::uint64_t, 8>& state,
    std::uint64_t processed_bytes
) {
    if ((processed_bytes % BLOCK_SIZE) != 0) {
        throw std::invalid_argument("SHA512 set_state requires processed_bytes to be a multiple of 128");
    }

    h_ = state;
    buffer_.fill(0);
    buffer_len_ = 0;
    total_len_ = processed_bytes;
}

void SHA512::set_state_from_digest(
    const Bytes& digest,
    std::uint64_t processed_bytes
) {
    set_state(
        digest_to_state(digest),
        processed_bytes
    );
}

void SHA512::update(
    const std::uint8_t* data,
    std::size_t len
) {
    if (data == nullptr && len != 0) {
        throw std::invalid_argument("SHA512 update received null data with non-zero length");
    }

    for (std::size_t i = 0; i < len; ++i) {
        buffer_[buffer_len_++] = data[i];
        ++total_len_;

        if (buffer_len_ == BLOCK_SIZE) {
            transform(buffer_.data());
            buffer_len_ = 0;
        }
    }
}

void SHA512::update(const Bytes& data) {
    update(
        data.empty() ? nullptr : data.data(),
        data.size()
    );
}

void SHA512::update(const std::string& text) {
    update(
        reinterpret_cast<const std::uint8_t*>(text.data()),
        text.size()
    );
}

Bytes SHA512::final() {
    /*
        SHA-512 uses a 128-bit length field.
        For this teaching implementation we support total_len_ < 2^64 bytes.
        The high 64 bits of bit length are total_len_ >> 61.
    */
    const std::uint64_t bit_len_hi = total_len_ >> 61;
    const std::uint64_t bit_len_lo = total_len_ << 3;

    buffer_[buffer_len_++] = 0x80u;

    if (buffer_len_ > 112) {
        while (buffer_len_ < BLOCK_SIZE) {
            buffer_[buffer_len_++] = 0x00u;
        }

        transform(buffer_.data());
        buffer_len_ = 0;
    }

    while (buffer_len_ < 112) {
        buffer_[buffer_len_++] = 0x00u;
    }

    store_be64(&buffer_[112], bit_len_hi);
    store_be64(&buffer_[120], bit_len_lo);

    transform(buffer_.data());

    Bytes out(DIGEST_SIZE);

    for (std::size_t i = 0; i < h_.size(); ++i) {
        store_be64(&out[i * 8], h_[i]);
    }

    reset();
    return out;
}

Bytes SHA512::digest(const Bytes& data) {
    SHA512 ctx;
    ctx.update(data);
    return ctx.final();
}

Bytes SHA512::digest(const std::string& text) {
    SHA512 ctx;
    ctx.update(text);
    return ctx.final();
}

std::array<std::uint64_t, 8> SHA512::digest_to_state(
    const Bytes& digest
) {
    if (digest.size() != DIGEST_SIZE) {
        throw std::invalid_argument("SHA512 digest_to_state requires a 64-byte digest");
    }

    std::array<std::uint64_t, 8> state{};

    for (std::size_t i = 0; i < state.size(); ++i) {
        state[i] = load_be64(&digest[i * 8]);
    }

    return state;
}

Bytes SHA512::state_to_digest(
    const std::array<std::uint64_t, 8>& state
) {
    Bytes out(DIGEST_SIZE);

    for (std::size_t i = 0; i < state.size(); ++i) {
        store_be64(&out[i * 8], state[i]);
    }

    return out;
}

void SHA512::transform(
    const std::uint8_t block[BLOCK_SIZE]
) {
    std::uint64_t w[80];

    for (std::size_t i = 0; i < 16; ++i) {
        w[i] = load_be64(block + i * 8);
    }

    for (std::size_t i = 16; i < 80; ++i) {
        const std::uint64_t s0 =
            rotr64(w[i - 15], 1) ^
            rotr64(w[i - 15], 8) ^
            (w[i - 15] >> 7);

        const std::uint64_t s1 =
            rotr64(w[i - 2], 19) ^
            rotr64(w[i - 2], 61) ^
            (w[i - 2] >> 6);

        w[i] = w[i - 16] + s0 + w[i - 7] + s1;
    }

    std::uint64_t a = h_[0];
    std::uint64_t b = h_[1];
    std::uint64_t c = h_[2];
    std::uint64_t d = h_[3];
    std::uint64_t e = h_[4];
    std::uint64_t f = h_[5];
    std::uint64_t g = h_[6];
    std::uint64_t h = h_[7];

    for (std::size_t i = 0; i < 80; ++i) {
        const std::uint64_t S1 =
            rotr64(e, 14) ^
            rotr64(e, 18) ^
            rotr64(e, 41);

        const std::uint64_t ch =
            (e & f) ^ ((~e) & g);

        const std::uint64_t temp1 =
            h + S1 + ch + SHA512_K[i] + w[i];

        const std::uint64_t S0 =
            rotr64(a, 28) ^
            rotr64(a, 34) ^
            rotr64(a, 39);

        const std::uint64_t maj =
            (a & b) ^ (a & c) ^ (b & c);

        const std::uint64_t temp2 =
            S0 + maj;

        h = g;
        g = f;
        f = e;
        e = d + temp1;
        d = c;
        c = b;
        b = a;
        a = temp1 + temp2;
    }

    h_[0] += a;
    h_[1] += b;
    h_[2] += c;
    h_[3] += d;
    h_[4] += e;
    h_[5] += f;
    h_[6] += g;
    h_[7] += h;
}

Bytes sha256_glue_padding(
    std::uint64_t original_total_len_bytes
) {
    Bytes pad;
    pad.push_back(0x80u);

    while (((original_total_len_bytes + pad.size()) % 64) != 56) {
        pad.push_back(0x00u);
    }

    const std::uint64_t bit_len = original_total_len_bytes * 8u;

    for (int shift = 56; shift >= 0; shift -= 8) {
        pad.push_back(static_cast<std::uint8_t>(bit_len >> shift));
    }

    return pad;
}

Bytes sha512_glue_padding(
    std::uint64_t original_total_len_bytes
) {
    Bytes pad;
    pad.push_back(0x80u);

    while (((original_total_len_bytes + pad.size()) % 128) != 112) {
        pad.push_back(0x00u);
    }

    const std::uint64_t bit_len_hi = original_total_len_bytes >> 61;
    const std::uint64_t bit_len_lo = original_total_len_bytes << 3;

    for (int shift = 56; shift >= 0; shift -= 8) {
        pad.push_back(static_cast<std::uint8_t>(bit_len_hi >> shift));
    }

    for (int shift = 56; shift >= 0; shift -= 8) {
        pad.push_back(static_cast<std::uint8_t>(bit_len_lo >> shift));
    }

    return pad;
}

SHA256ForgeResult forge_sha256_secret_prefix_mac(
    const Bytes& known_message,
    const Bytes& known_mac,
    std::uint64_t guessed_secret_len,
    const Bytes& suffix
) {
    const std::uint64_t original_total =
        guessed_secret_len + known_message.size();

    Bytes glue =
        sha256_glue_padding(original_total);

    const std::uint64_t processed_before_suffix =
        original_total + glue.size();

    SHA256 attacker;
    attacker.set_state_from_digest(
        known_mac,
        processed_before_suffix
    );

    attacker.update(suffix);

    SHA256ForgeResult result;
    result.forged_message = known_message;
    result.forged_message.insert(
        result.forged_message.end(),
        glue.begin(),
        glue.end()
    );
    result.forged_message.insert(
        result.forged_message.end(),
        suffix.begin(),
        suffix.end()
    );
    result.forged_mac = attacker.final();
    result.glue_padding = std::move(glue);
    result.processed_before_suffix = processed_before_suffix;

    return result;
}

SHA512ForgeResult forge_sha512_secret_prefix_mac(
    const Bytes& known_message,
    const Bytes& known_mac,
    std::uint64_t guessed_secret_len,
    const Bytes& suffix
) {
    const std::uint64_t original_total =
        guessed_secret_len + known_message.size();

    Bytes glue =
        sha512_glue_padding(original_total);

    const std::uint64_t processed_before_suffix =
        original_total + glue.size();

    SHA512 attacker;
    attacker.set_state_from_digest(
        known_mac,
        processed_before_suffix
    );

    attacker.update(suffix);

    SHA512ForgeResult result;
    result.forged_message = known_message;
    result.forged_message.insert(
        result.forged_message.end(),
        glue.begin(),
        glue.end()
    );
    result.forged_message.insert(
        result.forged_message.end(),
        suffix.begin(),
        suffix.end()
    );
    result.forged_mac = attacker.final();
    result.glue_padding = std::move(glue);
    result.processed_before_suffix = processed_before_suffix;

    return result;
}

Bytes secret_prefix_mac_sha256(
    const Bytes& secret,
    const Bytes& message
) {
    Bytes input = secret;
    input.insert(
        input.end(),
        message.begin(),
        message.end()
    );

    return SHA256::digest(input);
}

Bytes secret_prefix_mac_sha512(
    const Bytes& secret,
    const Bytes& message
) {
    Bytes input = secret;
    input.insert(
        input.end(),
        message.begin(),
        message.end()
    );

    return SHA512::digest(input);
}

bool verify_secret_prefix_mac_sha256(
    const Bytes& secret,
    const Bytes& message,
    const Bytes& mac
) {
    return secret_prefix_mac_sha256(secret, message) == mac;
}

bool verify_secret_prefix_mac_sha512(
    const Bytes& secret,
    const Bytes& message,
    const Bytes& mac
) {
    return secret_prefix_mac_sha512(secret, message) == mac;
}

Bytes hex_to_bytes(
    const std::string& hex
) {
    std::string clean;
    clean.reserve(hex.size());

    for (std::size_t i = 0; i < hex.size();) {
        if (i + 1 < hex.size() &&
            hex[i] == '0' &&
            (hex[i + 1] == 'x' || hex[i + 1] == 'X')) {
            i += 2;
            continue;
        }

        const unsigned char c =
            static_cast<unsigned char>(hex[i]);

        if (std::isxdigit(c)) {
            clean.push_back(static_cast<char>(c));
        } else if (std::isspace(c) || c == ':' || c == '-' || c == '_') {
            // ignore common separators
        } else {
            throw std::invalid_argument("Invalid character in hex string");
        }

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

        if (hi < 0 || lo < 0) {
            throw std::invalid_argument("Invalid hex digit");
        }

        out.push_back(
            static_cast<std::uint8_t>((hi << 4) | lo)
        );
    }

    return out;
}

std::string bytes_to_hex(
    const Bytes& data,
    bool lowercase
) {
    std::ostringstream oss;

    if (!lowercase) {
        oss << std::uppercase;
    }

    oss << std::hex << std::setfill('0');

    for (std::uint8_t b : data) {
        oss << std::setw(2) << static_cast<int>(b);
    }

    return oss.str();
}

Bytes text_to_bytes(
    const std::string& text
) {
    return Bytes(text.begin(), text.end());
}

std::string bytes_to_text_lossy(
    const Bytes& data
) {
    return std::string(data.begin(), data.end());
}

std::string bytes_to_c_escaped(
    const Bytes& data
) {
    std::ostringstream oss;

    for (std::uint8_t b : data) {
        if (b == '\\') {
            oss << "\\\\";
        } else if (b == '"') {
            oss << "\\\"";
        } else if (b >= 0x20 && b <= 0x7e) {
            oss << static_cast<char>(b);
        } else {
            oss << "\\x"
                << std::hex
                << std::setw(2)
                << std::setfill('0')
                << static_cast<int>(b)
                << std::dec;
        }
    }

    return oss.str();
}

} // namespace sha2lenext
