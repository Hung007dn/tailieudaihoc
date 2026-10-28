#include <cstddef>
#include <cstdint>
#include <exception>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#include "sha2_length_extension.h"

namespace {

struct CLIOptions {
    bool help = false;
    std::string command = "demo-sha256";

    std::string alg = "sha256";

    std::string secret_text = "YELLOW SUBMARINE";
    std::string secret_hex;

    std::string message_text = "user=alice&role=user";
    std::string message_hex;

    std::string suffix_text = "&role=admin";
    std::string suffix_hex;

    std::string mac_hex;

    std::uint64_t guessed_secret_len = 16;

    bool print_escaped = true;
};

bool starts_with(const std::string& s, const std::string& prefix) {
    return s.size() >= prefix.size() && s.compare(0, prefix.size(), prefix) == 0;
}

bool option_matches(const std::string& arg, const std::string& opt) {
    return arg == opt || starts_with(arg, opt + "=");
}

std::string require_value(
    int& i,
    int argc,
    char* argv[],
    const std::string& arg,
    const std::string& opt
) {
    const std::string prefix = opt + "=";

    if (starts_with(arg, prefix)) {
        return arg.substr(prefix.size());
    }

    if (arg == opt) {
        if (i + 1 >= argc) {
            throw std::invalid_argument("Missing value for " + opt);
        }

        ++i;
        return argv[i];
    }

    throw std::logic_error("require_value called for wrong option");
}

std::uint64_t parse_u64(const std::string& s, const char* label) {
    std::size_t pos = 0;
    unsigned long long value = std::stoull(s, &pos, 0);

    if (pos != s.size()) {
        throw std::invalid_argument(std::string("Invalid integer for ") + label + ": " + s);
    }

    return static_cast<std::uint64_t>(value);
}

std::string lower_copy(std::string s) {
    for (char& c : s) {
        c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    }

    return s;
}

void print_usage() {
    std::cout
        << "SHA-2 Length Extension Lab\n"
        << "\n"
        << "Commands:\n"
        << "  demo-sha256       Full controlled SHA-256 demo with known secret\n"
        << "  demo-sha512       Full controlled SHA-512 demo with known secret\n"
        << "  forge-sha256      Attacker forge using known message, known MAC, guessed secret length\n"
        << "  forge-sha512      Same for SHA-512\n"
        << "  hash-sha256       Compute SHA-256 using this teaching implementation\n"
        << "  hash-sha512       Compute SHA-512 using this teaching implementation\n"
        << "\n"
        << "Common options:\n"
        << "  --secret-text <text>       Demo secret text\n"
        << "  --secret-hex <hex>         Demo secret bytes\n"
        << "  --message-text <text>      Known message text\n"
        << "  --message-hex <hex>        Known message bytes\n"
        << "  --suffix-text <text>       Appended attacker suffix\n"
        << "  --suffix-hex <hex>         Appended attacker suffix bytes\n"
        << "  --mac <hex>                Known MAC for forge command\n"
        << "  --guess-secret-len <n>     Guessed secret length in bytes\n"
        << "\n"
        << "Examples:\n"
        << "  sha2_lenext_lab.exe demo-sha256\n"
        << "\n"
        << "  sha2_lenext_lab.exe forge-sha256 ^\n"
        << "    --message-text \"user=alice&role=user\" ^\n"
        << "    --mac <known_mac_hex> ^\n"
        << "    --guess-secret-len 16 ^\n"
        << "    --suffix-text \"&role=admin\"\n";
}

CLIOptions parse_args(int argc, char* argv[]) {
    CLIOptions opt;

    if (argc <= 1) {
        return opt;
    }

    int i = 1;

    const std::string first = argv[i];

    if (first == "-h" || first == "--help" || first == "/?") {
        opt.help = true;
        return opt;
    }

    if (!starts_with(first, "-")) {
        opt.command = lower_copy(first);
        ++i;
    }

    for (; i < argc; ++i) {
        const std::string arg = argv[i];

        if (arg == "--help" || arg == "-h" || arg == "/?") {
            opt.help = true;
        } else if (option_matches(arg, "--secret-text")) {
            opt.secret_text = require_value(i, argc, argv, arg, "--secret-text");
            opt.secret_hex.clear();
        } else if (option_matches(arg, "--secret-hex")) {
            opt.secret_hex = require_value(i, argc, argv, arg, "--secret-hex");
        } else if (option_matches(arg, "--message-text")) {
            opt.message_text = require_value(i, argc, argv, arg, "--message-text");
            opt.message_hex.clear();
        } else if (option_matches(arg, "--message-hex")) {
            opt.message_hex = require_value(i, argc, argv, arg, "--message-hex");
        } else if (option_matches(arg, "--suffix-text")) {
            opt.suffix_text = require_value(i, argc, argv, arg, "--suffix-text");
            opt.suffix_hex.clear();
        } else if (option_matches(arg, "--suffix-hex")) {
            opt.suffix_hex = require_value(i, argc, argv, arg, "--suffix-hex");
        } else if (option_matches(arg, "--mac")) {
            opt.mac_hex = require_value(i, argc, argv, arg, "--mac");
        } else if (option_matches(arg, "--guess-secret-len")) {
            opt.guessed_secret_len =
                parse_u64(
                    require_value(i, argc, argv, arg, "--guess-secret-len"),
                    "guess-secret-len"
                );
        } else if (arg == "--no-escaped") {
            opt.print_escaped = false;
        } else {
            throw std::invalid_argument("Unknown argument: " + arg);
        }
    }

    return opt;
}

sha2lenext::Bytes choose_bytes(
    const std::string& text,
    const std::string& hex
) {
    if (!hex.empty()) {
        return sha2lenext::hex_to_bytes(hex);
    }

    return sha2lenext::text_to_bytes(text);
}

void print_bytes_report(
    const char* label,
    const sha2lenext::Bytes& data,
    bool escaped
) {
    std::cout << label << " length: " << data.size() << " byte(s)\n";
    std::cout << label << " hex   : " << sha2lenext::bytes_to_hex(data) << "\n";

    if (escaped) {
        std::cout << label << " escaped: \"" << sha2lenext::bytes_to_c_escaped(data) << "\"\n";
    }
}

void demo_sha256(const CLIOptions& opt) {
    const auto secret = choose_bytes(opt.secret_text, opt.secret_hex);
    const auto message = choose_bytes(opt.message_text, opt.message_hex);
    const auto suffix = choose_bytes(opt.suffix_text, opt.suffix_hex);

    const auto mac =
        sha2lenext::secret_prefix_mac_sha256(secret, message);

    const auto forged =
        sha2lenext::forge_sha256_secret_prefix_mac(
            message,
            mac,
            secret.size(),
            suffix
        );

    const bool verified =
        sha2lenext::verify_secret_prefix_mac_sha256(
            secret,
            forged.forged_message,
            forged.forged_mac
        );

    std::cout << "=== Controlled SHA-256 Length Extension Demo ===\n";
    std::cout << "Secret length            : " << secret.size() << "\n";
    std::cout << "Known message            : " << sha2lenext::bytes_to_text_lossy(message) << "\n";
    std::cout << "Original MAC             : " << sha2lenext::bytes_to_hex(mac) << "\n";
    std::cout << "Attacker suffix          : " << sha2lenext::bytes_to_text_lossy(suffix) << "\n";
    std::cout << "Glue padding length      : " << forged.glue_padding.size() << "\n";
    std::cout << "Processed before suffix  : " << forged.processed_before_suffix << "\n";
    std::cout << "Forged MAC               : " << sha2lenext::bytes_to_hex(forged.forged_mac) << "\n";
    std::cout << "Server verification      : " << (verified ? "PASSED" : "FAILED") << "\n\n";

    print_bytes_report("Forged message", forged.forged_message, opt.print_escaped);

    std::cout << "\nWhy it works:\n";
    std::cout << "  1. SHA-256 digest is the final chaining state.\n";
    std::cout << "  2. We parse the digest into eight 32-bit state words.\n";
    std::cout << "  3. We resume hashing from that state after the original SHA-256 padding.\n";
    std::cout << "  4. The server computes SHA256(secret || forged_message), which matches.\n";
}

void demo_sha512(const CLIOptions& opt) {
    const auto secret = choose_bytes(opt.secret_text, opt.secret_hex);
    const auto message = choose_bytes(opt.message_text, opt.message_hex);
    const auto suffix = choose_bytes(opt.suffix_text, opt.suffix_hex);

    const auto mac =
        sha2lenext::secret_prefix_mac_sha512(secret, message);

    const auto forged =
        sha2lenext::forge_sha512_secret_prefix_mac(
            message,
            mac,
            secret.size(),
            suffix
        );

    const bool verified =
        sha2lenext::verify_secret_prefix_mac_sha512(
            secret,
            forged.forged_message,
            forged.forged_mac
        );

    std::cout << "=== Controlled SHA-512 Length Extension Demo ===\n";
    std::cout << "Secret length            : " << secret.size() << "\n";
    std::cout << "Known message            : " << sha2lenext::bytes_to_text_lossy(message) << "\n";
    std::cout << "Original MAC             : " << sha2lenext::bytes_to_hex(mac) << "\n";
    std::cout << "Attacker suffix          : " << sha2lenext::bytes_to_text_lossy(suffix) << "\n";
    std::cout << "Glue padding length      : " << forged.glue_padding.size() << "\n";
    std::cout << "Processed before suffix  : " << forged.processed_before_suffix << "\n";
    std::cout << "Forged MAC               : " << sha2lenext::bytes_to_hex(forged.forged_mac) << "\n";
    std::cout << "Server verification      : " << (verified ? "PASSED" : "FAILED") << "\n\n";

    print_bytes_report("Forged message", forged.forged_message, opt.print_escaped);
}

void forge_sha256(const CLIOptions& opt) {
    if (opt.mac_hex.empty()) {
        throw std::invalid_argument("forge-sha256 requires --mac <hex>");
    }

    const auto message = choose_bytes(opt.message_text, opt.message_hex);
    const auto suffix = choose_bytes(opt.suffix_text, opt.suffix_hex);
    const auto mac = sha2lenext::hex_to_bytes(opt.mac_hex);

    const auto forged =
        sha2lenext::forge_sha256_secret_prefix_mac(
            message,
            mac,
            opt.guessed_secret_len,
            suffix
        );

    std::cout << "=== SHA-256 Length Extension Forge ===\n";
    std::cout << "Guessed secret length    : " << opt.guessed_secret_len << "\n";
    std::cout << "Glue padding length      : " << forged.glue_padding.size() << "\n";
    std::cout << "Processed before suffix  : " << forged.processed_before_suffix << "\n";
    std::cout << "Forged MAC               : " << sha2lenext::bytes_to_hex(forged.forged_mac) << "\n\n";

    print_bytes_report("Forged message", forged.forged_message, opt.print_escaped);
}

void forge_sha512(const CLIOptions& opt) {
    if (opt.mac_hex.empty()) {
        throw std::invalid_argument("forge-sha512 requires --mac <hex>");
    }

    const auto message = choose_bytes(opt.message_text, opt.message_hex);
    const auto suffix = choose_bytes(opt.suffix_text, opt.suffix_hex);
    const auto mac = sha2lenext::hex_to_bytes(opt.mac_hex);

    const auto forged =
        sha2lenext::forge_sha512_secret_prefix_mac(
            message,
            mac,
            opt.guessed_secret_len,
            suffix
        );

    std::cout << "=== SHA-512 Length Extension Forge ===\n";
    std::cout << "Guessed secret length    : " << opt.guessed_secret_len << "\n";
    std::cout << "Glue padding length      : " << forged.glue_padding.size() << "\n";
    std::cout << "Processed before suffix  : " << forged.processed_before_suffix << "\n";
    std::cout << "Forged MAC               : " << sha2lenext::bytes_to_hex(forged.forged_mac) << "\n\n";

    print_bytes_report("Forged message", forged.forged_message, opt.print_escaped);
}

} // anonymous namespace

int main(int argc, char* argv[]) {
    try {
        const CLIOptions opt = parse_args(argc, argv);

        if (opt.help) {
            print_usage();
            return 0;
        }

        if (opt.command == "demo-sha256") {
            demo_sha256(opt);
            return 0;
        }

        if (opt.command == "demo-sha512") {
            demo_sha512(opt);
            return 0;
        }

        if (opt.command == "forge-sha256") {
            forge_sha256(opt);
            return 0;
        }

        if (opt.command == "forge-sha512") {
            forge_sha512(opt);
            return 0;
        }

        if (opt.command == "hash-sha256") {
            const auto message = choose_bytes(opt.message_text, opt.message_hex);
            std::cout << sha2lenext::bytes_to_hex(sha2lenext::SHA256::digest(message)) << "\n";
            return 0;
        }

        if (opt.command == "hash-sha512") {
            const auto message = choose_bytes(opt.message_text, opt.message_hex);
            std::cout << sha2lenext::bytes_to_hex(sha2lenext::SHA512::digest(message)) << "\n";
            return 0;
        }

        throw std::invalid_argument("Unsupported command: " + opt.command);
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        std::cerr << "Use --help for usage.\n";
        return 1;
    }
}
