#include <iostream>

#include "evp_hash_direct_tool.h"

int main() {
    using namespace hashlab_evp_direct;

    try {
        const Bytes abc = EVPHashDirectTool::text_to_bytes("abc");
        std::cout << "Algorithm-specific EVP Hash demo\n";

        for (const auto& alg : {"sha1", "sha256", "sha512", "sha3-256", "shake128"}) {
            const DigestInfo info = EVPHashDirectTool::digest_info(alg);
            std::cout << "\nAlgorithm: " << alg << "\n";
            std::cout << "  size : " << info.output_size << "\n";
            std::cout << "  block: " << info.block_size << "\n";
            std::cout << "  xof  : " << (info.is_xof ? "yes" : "no") << "\n";
            Bytes out = info.is_xof ? EVPHashDirectTool::digest(alg, abc, 32) : EVPHashDirectTool::digest(alg, abc);
            std::cout << "  digest(abc): " << EVPHashDirectTool::bytes_to_hex(out) << "\n";
        }

        DirectDigestContext ctx1("sha256");
        ctx1.update(EVPHashDirectTool::text_to_bytes("abc"));
        DirectDigestContext ctx2 = ctx1.clone();
        ctx1.update(EVPHashDirectTool::text_to_bytes("def"));
        ctx2.update(EVPHashDirectTool::text_to_bytes("XYZ"));

        std::cout << "\nStreaming copy demo:\n";
        std::cout << "  sha256(abcdef): " << EVPHashDirectTool::bytes_to_hex(ctx1.final()) << "\n";
        std::cout << "  sha256(abcXYZ): " << EVPHashDirectTool::bytes_to_hex(ctx2.final()) << "\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }
}
