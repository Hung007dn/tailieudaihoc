#include <cstddef>
#include <cstdint>
#include <exception>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#include "evp_aes_direct_tool.h"

namespace {

struct CLIOptions {
    bool help = false;
    bool list = false;
    bool available = false;

    bool encrypt = false;
    bool decrypt = false;

    std::string cipher;
    std::string key_hex;
    std::string iv_hex;
    std::string nonce_hex;

    std::string aad_hex;
    std::string aad_text;

    std::size_t tag_len = 16;
    std::string tag_hex;
    std::string tag_in_file;
    std::string tag_out_file;

    std::string input_file;
    std::string output_file;
    std::string hex_input;
    std::string text_input;
    bool empty_input = false;

    bool out_hex = false;
    bool padding = false;
    bool padding_set = false;
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

std::size_t parse_size(const std::string& s) {
    std::size_t pos = 0;
    unsigned long v = std::stoul(s, &pos, 0);

    if (pos != s.size()) {
        throw std::invalid_argument("Invalid numeric value: " + s);
    }

    return static_cast<std::size_t>(v);
}

std::string lower_copy(std::string s) {
    for (char& c : s) {
        c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    }

    return s;
}

bool is_aead_name(const std::string& cipher) {
    const std::string c = lower_copy(cipher);
    return c.find("gcm") != std::string::npos ||
           c.find("ccm") != std::string::npos ||
           c.find("ocb") != std::string::npos;
}

bool mode_uses_iv_classical(const std::string& cipher) {
    const std::string c = lower_copy(cipher);

    if (c.find("ecb") != std::string::npos) {
        return false;
    }

    if (c.find("wrap") != std::string::npos) {
        return false;
    }

    return !is_aead_name(c);
}

bool default_padding_for_cipher(const std::string& cipher) {
    const std::string c = lower_copy(cipher);
    return c.find("ecb") != std::string::npos ||
           c.find("cbc") != std::string::npos;
}

std::vector<std::uint8_t> read_file(const std::string& path) {
    std::ifstream in(path, std::ios::binary);

    if (!in) {
        throw std::runtime_error("Cannot open input file: " + path);
    }

    in.seekg(0, std::ios::end);
    const std::streamoff size = in.tellg();

    if (size < 0) {
        throw std::runtime_error("Cannot determine file size: " + path);
    }

    in.seekg(0, std::ios::beg);

    std::vector<std::uint8_t> data(static_cast<std::size_t>(size));

    if (!data.empty()) {
        in.read(reinterpret_cast<char*>(data.data()), size);

        if (!in) {
            throw std::runtime_error("Failed to read input file: " + path);
        }
    }

    return data;
}

void write_file(const std::string& path, const std::vector<std::uint8_t>& data) {
    std::ofstream out(path, std::ios::binary);

    if (!out) {
        throw std::runtime_error("Cannot open output file: " + path);
    }

    if (!data.empty()) {
        out.write(
            reinterpret_cast<const char*>(data.data()),
            static_cast<std::streamsize>(data.size())
        );

        if (!out) {
            throw std::runtime_error("Failed to write output file: " + path);
        }
    }
}

std::vector<std::uint8_t> text_to_bytes(const std::string& text) {
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

std::vector<std::uint8_t> read_input(const CLIOptions& opt) {
    int count = 0;

    if (!opt.input_file.empty()) ++count;
    if (!opt.hex_input.empty()) ++count;
    if (!opt.text_input.empty()) ++count;
    if (opt.empty_input) ++count;

    if (count != 1) {
        throw std::invalid_argument("Choose exactly one input source: --in, --hex-input, --text, or --empty-input");
    }

    if (!opt.input_file.empty()) {
        return read_file(opt.input_file);
    }

    if (!opt.hex_input.empty()) {
        return aeslab_evp_direct::EVPAESDirectTool::hex_to_bytes(opt.hex_input);
    }

    if (!opt.text_input.empty()) {
        return text_to_bytes(opt.text_input);
    }

    return {};
}

void write_output(const CLIOptions& opt, const std::vector<std::uint8_t>& data) {
    if (!opt.output_file.empty()) {
        write_file(opt.output_file, data);
    }

    if (opt.out_hex || opt.output_file.empty()) {
        std::cout << aeslab_evp_direct::EVPAESDirectTool::bytes_to_hex(data) << "\n";
    }
}

std::vector<std::uint8_t> read_aad(const CLIOptions& opt) {
    if (!opt.aad_hex.empty() && !opt.aad_text.empty()) {
        throw std::invalid_argument("Use only one AAD source");
    }

    if (!opt.aad_hex.empty()) {
        return aeslab_evp_direct::EVPAESDirectTool::hex_to_bytes(opt.aad_hex);
    }

    if (!opt.aad_text.empty()) {
        return text_to_bytes(opt.aad_text);
    }

    return {};
}

std::vector<std::uint8_t> read_tag(const CLIOptions& opt) {
    const bool has_hex = !opt.tag_hex.empty();
    const bool has_file = !opt.tag_in_file.empty();

    if (has_hex == has_file) {
        throw std::invalid_argument("AEAD decryption requires exactly one tag source: --tag or --tag-in");
    }

    if (has_hex) {
        return aeslab_evp_direct::EVPAESDirectTool::hex_to_bytes(opt.tag_hex);
    }

    return read_file(opt.tag_in_file);
}

void print_usage() {
    std::cout
        << "Algorithm-specific OpenSSL EVP AES Tool\n"
        << "\n"
        << "Usage:\n"
        << "  evp_aes_direct_lab.exe enc --cipher aes-128-cbc --key <hex> --iv <hex> --text \"hello\" --out-hex\n"
        << "  evp_aes_direct_lab.exe dec --cipher aes-128-gcm --key <hex> --nonce <hex> --tag <hex> --hex-input <ct> --out-hex\n"
        << "\n"
        << "Commands:\n"
        << "  enc / encrypt\n"
        << "  dec / decrypt\n"
        << "  --list\n"
        << "  --available --cipher <name>\n"
        << "\n"
        << "Input options, choose one:\n"
        << "  --in <file>\n"
        << "  --hex-input <hex>\n"
        << "  --text <string>\n"
        << "  --empty-input\n"
        << "\n"
        << "Output options:\n"
        << "  --out <file>\n"
        << "  --out-hex\n"
        << "\n"
        << "Classical options:\n"
        << "  --iv <hex>\n"
        << "  --padding\n"
        << "  --nopad\n"
        << "\n"
        << "AEAD options:\n"
        << "  --nonce <hex>\n"
        << "  --aad-hex <hex>\n"
        << "  --aad-text <text>\n"
        << "  --tag-len <n>\n"
        << "  --tag <hex>\n"
        << "  --tag-in <file>\n"
        << "  --tag-out <file>\n"
        << "\n"
        << "Examples:\n"
        << "  evp_aes_direct_lab.exe enc --cipher aes-128-gcm --key 00000000000000000000000000000000 --nonce 000000000000000000000000 --hex-input 00000000000000000000000000000000 --out-hex\n"
        << "  evp_aes_direct_lab.exe --available --cipher aes-256-xts\n";
}

CLIOptions parse_args(int argc, char* argv[]) {
    CLIOptions opt;

    if (argc <= 1) {
        opt.help = true;
        return opt;
    }

    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];

        if (arg == "enc" || arg == "encrypt" || arg == "-e" || arg == "--encrypt") {
            opt.encrypt = true;
        } else if (arg == "dec" || arg == "decrypt" || arg == "-d" || arg == "--decrypt") {
            opt.decrypt = true;
        } else if (arg == "--help" || arg == "-h" || arg == "/?") {
            opt.help = true;
        } else if (arg == "--list") {
            opt.list = true;
        } else if (arg == "--available") {
            opt.available = true;
        } else if (option_matches(arg, "--cipher")) {
            opt.cipher = require_value(i, argc, argv, arg, "--cipher");
        } else if (option_matches(arg, "--key")) {
            opt.key_hex = require_value(i, argc, argv, arg, "--key");
        } else if (option_matches(arg, "--iv")) {
            opt.iv_hex = require_value(i, argc, argv, arg, "--iv");
        } else if (option_matches(arg, "--nonce")) {
            opt.nonce_hex = require_value(i, argc, argv, arg, "--nonce");
        } else if (option_matches(arg, "--aad-hex")) {
            opt.aad_hex = require_value(i, argc, argv, arg, "--aad-hex");
        } else if (option_matches(arg, "--aad-text")) {
            opt.aad_text = require_value(i, argc, argv, arg, "--aad-text");
        } else if (option_matches(arg, "--tag-len")) {
            opt.tag_len = parse_size(require_value(i, argc, argv, arg, "--tag-len"));
        } else if (option_matches(arg, "--tag")) {
            opt.tag_hex = require_value(i, argc, argv, arg, "--tag");
        } else if (option_matches(arg, "--tag-in")) {
            opt.tag_in_file = require_value(i, argc, argv, arg, "--tag-in");
        } else if (option_matches(arg, "--tag-out")) {
            opt.tag_out_file = require_value(i, argc, argv, arg, "--tag-out");
        } else if (option_matches(arg, "--in")) {
            opt.input_file = require_value(i, argc, argv, arg, "--in");
        } else if (option_matches(arg, "--out")) {
            opt.output_file = require_value(i, argc, argv, arg, "--out");
        } else if (option_matches(arg, "--hex-input")) {
            opt.hex_input = require_value(i, argc, argv, arg, "--hex-input");
        } else if (option_matches(arg, "--text")) {
            opt.text_input = require_value(i, argc, argv, arg, "--text");
        } else if (arg == "--empty-input") {
            opt.empty_input = true;
        } else if (arg == "--out-hex") {
            opt.out_hex = true;
        } else if (arg == "--padding") {
            opt.padding = true;
            opt.padding_set = true;
        } else if (arg == "--nopad") {
            opt.padding = false;
            opt.padding_set = true;
        } else {
            throw std::invalid_argument("Unknown argument: " + arg);
        }
    }

    return opt;
}

void print_list() {
    const char* ciphers[] = {
        "aes-128-ecb", "aes-128-cbc", "aes-128-ctr", "aes-128-ofb", "aes-128-cfb", "aes-128-cfb8", "aes-128-cfb1",
        "aes-192-ecb", "aes-192-cbc", "aes-192-ctr", "aes-192-ofb", "aes-192-cfb", "aes-192-cfb8", "aes-192-cfb1",
        "aes-256-ecb", "aes-256-cbc", "aes-256-ctr", "aes-256-ofb", "aes-256-cfb", "aes-256-cfb8", "aes-256-cfb1",
        "aes-128-gcm", "aes-192-gcm", "aes-256-gcm",
        "aes-128-ccm", "aes-192-ccm", "aes-256-ccm",
        "aes-128-ocb", "aes-192-ocb", "aes-256-ocb",
        "aes-128-wrap", "aes-192-wrap", "aes-256-wrap",
        "aes-128-wrap-pad", "aes-192-wrap-pad", "aes-256-wrap-pad",
        "aes-128-xts", "aes-256-xts"
    };

    for (const char* c : ciphers) {
        std::cout << c << " : "
                  << (aeslab_evp_direct::EVPAESDirectTool::cipher_available(c) ? "available" : "not available")
                  << "\n";
    }
}

} // anonymous namespace

int main(int argc, char* argv[]) {
    try {
        const CLIOptions opt = parse_args(argc, argv);

        if (opt.help) {
            print_usage();
            return 0;
        }

        if (opt.list) {
            print_list();
            return 0;
        }

        if (opt.cipher.empty()) {
            throw std::invalid_argument("Missing --cipher");
        }

        if (opt.available) {
            const bool ok =
                aeslab_evp_direct::EVPAESDirectTool::cipher_available(opt.cipher);

            std::cout << opt.cipher << " : " << (ok ? "available" : "not available") << "\n";
            return ok ? 0 : 2;
        }

        if (opt.encrypt == opt.decrypt) {
            throw std::invalid_argument("Choose exactly one operation: enc or dec");
        }

        if (opt.key_hex.empty()) {
            throw std::invalid_argument("Missing --key");
        }

        const auto key =
            aeslab_evp_direct::EVPAESDirectTool::hex_to_bytes(opt.key_hex);

        const auto input =
            read_input(opt);

        if (is_aead_name(opt.cipher)) {
            const auto nonce =
                aeslab_evp_direct::EVPAESDirectTool::hex_to_bytes(opt.nonce_hex);

            const auto aad =
                read_aad(opt);

            if (opt.encrypt) {
                const auto enc =
                    aeslab_evp_direct::EVPAESDirectTool::aead_encrypt(
                        opt.cipher,
                        key,
                        nonce,
                        aad,
                        input,
                        opt.tag_len
                    );

                write_output(opt, enc.ciphertext);

                if (!opt.tag_out_file.empty()) {
                    write_file(opt.tag_out_file, enc.tag);
                } else {
                    std::cout << "tag: "
                              << aeslab_evp_direct::EVPAESDirectTool::bytes_to_hex(enc.tag)
                              << "\n";
                }
            } else {
                const auto tag =
                    read_tag(opt);

                const auto dec =
                    aeslab_evp_direct::EVPAESDirectTool::aead_decrypt(
                        opt.cipher,
                        key,
                        nonce,
                        aad,
                        input,
                        tag
                    );

                if (!dec.tag_valid) {
                    throw std::runtime_error("AEAD authentication failed");
                }

                write_output(opt, dec.plaintext);
            }

            return 0;
        }

        std::vector<std::uint8_t> iv;

        if (mode_uses_iv_classical(opt.cipher)) {
            if (opt.iv_hex.empty()) {
                throw std::invalid_argument("This mode requires --iv");
            }

            iv = aeslab_evp_direct::EVPAESDirectTool::hex_to_bytes(opt.iv_hex);
        }

        bool padding = opt.padding_set
            ? opt.padding
            : default_padding_for_cipher(opt.cipher);

        if (opt.encrypt) {
            const auto out =
                aeslab_evp_direct::EVPAESDirectTool::encrypt(
                    opt.cipher,
                    key,
                    iv,
                    input,
                    padding
                );

            write_output(opt, out);
        } else {
            const auto out =
                aeslab_evp_direct::EVPAESDirectTool::decrypt(
                    opt.cipher,
                    key,
                    iv,
                    input,
                    padding
                );

            write_output(opt, out);
        }

        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        std::cerr << "Use --help for usage.\n";
        return 1;
    }
}
