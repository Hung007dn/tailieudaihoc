#include <iostream>
#include <stdexcept>

#include "sha2_length_extension.h"

static void expect_eq(
    const char* label,
    const std::string& got,
    const std::string& expected
) {
    if (got != expected) {
        std::cerr << label << " FAILED\n";
        std::cerr << "got     : " << got << "\n";
        std::cerr << "expected: " << expected << "\n";
        throw std::runtime_error(label);
    }

    std::cout << label << " PASSED\n";
}

int main() {
    using namespace sha2lenext;

    try {
        expect_eq(
            "SHA256 empty",
            bytes_to_hex(SHA256::digest("")),
            "e3b0c44298fc1c149afbf4c8996fb924"
            "27ae41e4649b934ca495991b7852b855"
        );

        expect_eq(
            "SHA256 abc",
            bytes_to_hex(SHA256::digest("abc")),
            "ba7816bf8f01cfea414140de5dae2223"
            "b00361a396177a9cb410ff61f20015ad"
        );

        expect_eq(
            "SHA512 empty",
            bytes_to_hex(SHA512::digest("")),
            "cf83e1357eefb8bdf1542850d66d8007"
            "d620e4050b5715dc83f4a921d36ce9ce"
            "47d0d13c5d85f2b0ff8318d2877eec2f"
            "63b931bd47417a81a538327af927da3e"
        );

        expect_eq(
            "SHA512 abc",
            bytes_to_hex(SHA512::digest("abc")),
            "ddaf35a193617abacc417349ae204131"
            "12e6fa4e89a97ea20a9eeee64b55d39a"
            "2192992a274fc1a836ba3c23a3feebbd"
            "454d4423643ce80e2a9ac94fa54ca49f"
        );

        const Bytes secret = text_to_bytes("YELLOW SUBMARINE");
        const Bytes msg = text_to_bytes("user=alice&role=user");
        const Bytes suffix = text_to_bytes("&role=admin");

        const Bytes mac = secret_prefix_mac_sha256(secret, msg);

        const SHA256ForgeResult forged =
            forge_sha256_secret_prefix_mac(
                msg,
                mac,
                secret.size(),
                suffix
            );

        if (!verify_secret_prefix_mac_sha256(secret, forged.forged_message, forged.forged_mac)) {
            throw std::runtime_error("SHA256 length extension verification failed");
        }

        std::cout << "SHA256 length extension PASSED\n";

        const Bytes mac512 = secret_prefix_mac_sha512(secret, msg);

        const SHA512ForgeResult forged512 =
            forge_sha512_secret_prefix_mac(
                msg,
                mac512,
                secret.size(),
                suffix
            );

        if (!verify_secret_prefix_mac_sha512(secret, forged512.forged_message, forged512.forged_mac)) {
            throw std::runtime_error("SHA512 length extension verification failed");
        }

        std::cout << "SHA512 length extension PASSED\n";

        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Test error: " << e.what() << "\n";
        return 1;
    }
}
