#include <iostream>

#include "evp_aes_direct_tool.h"

int main() {
    using namespace aeslab_evp_direct;

    try {
        const Bytes key = EVPAESDirectTool::hex_to_bytes("00000000000000000000000000000000");
        const Bytes nonce = EVPAESDirectTool::hex_to_bytes("000000000000000000000000");
        const Bytes plaintext = EVPAESDirectTool::hex_to_bytes("00000000000000000000000000000000");
        const Bytes aad;

        std::cout << "Algorithm-specific EVP AES demo\n";
        std::cout << "Cipher available AES-128-GCM: "
                  << (EVPAESDirectTool::cipher_available("aes-128-gcm") ? "yes" : "no")
                  << "\n";

        std::cout << "AES-128-GCM key length: "
                  << EVPAESDirectTool::expected_key_length("aes-128-gcm")
                  << " byte(s)\n";

        auto enc = EVPAESDirectTool::aead_encrypt("aes-128-gcm", key, nonce, aad, plaintext, 16);

        std::cout << "ciphertext: " << EVPAESDirectTool::bytes_to_hex(enc.ciphertext) << "\n";
        std::cout << "tag       : " << EVPAESDirectTool::bytes_to_hex(enc.tag) << "\n";

        auto dec = EVPAESDirectTool::aead_decrypt("aes-128-gcm", key, nonce, aad, enc.ciphertext, enc.tag);

        std::cout << "tag valid : " << (dec.tag_valid ? "yes" : "no") << "\n";
        std::cout << "plaintext : " << EVPAESDirectTool::bytes_to_hex(dec.plaintext) << "\n";

        const Bytes cbc_key = EVPAESDirectTool::hex_to_bytes("000102030405060708090a0b0c0d0e0f");
        const Bytes iv = EVPAESDirectTool::hex_to_bytes("101112131415161718191a1b1c1d1e1f");
        const Bytes msg = EVPAESDirectTool::text_to_bytes("Hello algorithm-specific EVP AES-CBC");

        const Bytes cbc_ct = EVPAESDirectTool::encrypt("aes-128-cbc", cbc_key, iv, msg, true);
        const Bytes cbc_pt = EVPAESDirectTool::decrypt("aes-128-cbc", cbc_key, iv, cbc_ct, true);

        std::cout << "CBC recovered: " << EVPAESDirectTool::bytes_to_text_lossy(cbc_pt) << "\n";

        return dec.tag_valid && dec.plaintext == plaintext && cbc_pt == msg ? 0 : 2;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }
}
