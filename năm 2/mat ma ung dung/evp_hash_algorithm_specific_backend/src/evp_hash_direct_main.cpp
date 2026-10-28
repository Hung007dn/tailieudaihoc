#include <cstddef>
#include <cstdint>
#include <exception>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#include "evp_hash_direct_tool.h"

namespace {

struct CLIOptions {
    bool help = false;
    bool list = false;
    std::string command = "hash";
    std::string algorithm = "sha256";
    std::string input_file;
    std::string output_file;
    std::string hex_input;
    std::string text_input;
    bool empty_input = false;
    bool out_hex = true;
    std::size_t xof_len = 0;
};

bool starts_with(const std::string& s, const std::string& prefix) {
    return s.size() >= prefix.size() && s.compare(0, prefix.size(), prefix) == 0;
}

bool option_matches(const std::string& arg, const std::string& opt) {
    return arg == opt || starts_with(arg, opt + "=");
}

std::string require_value(int& i, int argc, char* argv[], const std::string& arg, const std::string& opt) {
    const std::string prefix = opt + "=";
    if (starts_with(arg, prefix)) return arg.substr(prefix.size());
    if (arg == opt) {
        if (i + 1 >= argc) throw std::invalid_argument("Missing value for " + opt);
        ++i;
        return argv[i];
    }
    throw std::logic_error("require_value called for wrong option");
}

std::size_t parse_size(const std::string& s) {
    std::size_t pos = 0;
    unsigned long v = std::stoul(s, &pos, 0);
    if (pos != s.size()) throw std::invalid_argument("Invalid numeric value: " + s);
    return static_cast<std::size_t>(v);
}

std::string lower_copy(std::string s) {
    for (char& c : s) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    return s;
}

std::vector<std::uint8_t> read_file(const std::string& path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) throw std::runtime_error("Cannot open input file: " + path);
    in.seekg(0, std::ios::end);
    const std::streamoff size = in.tellg();
    if (size < 0) throw std::runtime_error("Cannot determine input file size: " + path);
    in.seekg(0, std::ios::beg);
    std::vector<std::uint8_t> data(static_cast<std::size_t>(size));
    if (!data.empty()) {
        in.read(reinterpret_cast<char*>(data.data()), size);
        if (!in) throw std::runtime_error("Failed to read input file: " + path);
    }
    return data;
}

void write_file(const std::string& path, const std::vector<std::uint8_t>& data) {
    std::ofstream out(path, std::ios::binary);
    if (!out) throw std::runtime_error("Cannot open output file: " + path);
    if (!data.empty()) {
        out.write(reinterpret_cast<const char*>(data.data()), static_cast<std::streamsize>(data.size()));
        if (!out) throw std::runtime_error("Failed to write output file: " + path);
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
    if (count != 1) throw std::invalid_argument("Choose exactly one input source: --in, --hex-input, --text, or --empty-input");
    if (!opt.input_file.empty()) return read_file(opt.input_file);
    if (!opt.hex_input.empty()) return hashlab_evp_direct::EVPHashDirectTool::hex_to_bytes(opt.hex_input);
    if (!opt.text_input.empty()) return text_to_bytes(opt.text_input);
    return {};
}

void print_usage() {
    std::cout
        << "Algorithm-specific OpenSSL EVP Hash Tool\n\n"
        << "Usage:\n"
        << "  evp_hash_direct_lab.exe hash --alg sha256 --text abc\n"
        << "  evp_hash_direct_lab.exe hash --alg shake128 --text abc --xof-len 32\n"
        << "  evp_hash_direct_lab.exe info --alg sha3-256\n"
        << "  evp_hash_direct_lab.exe --list\n\n"
        << "Input options: --in <file> | --hex-input <hex> | --text <string> | --empty-input\n"
        << "Output options: --out <file> writes raw digest bytes; --out-hex prints hex\n";
}

CLIOptions parse_args(int argc, char* argv[]) {
    CLIOptions opt;
    if (argc <= 1) { opt.help = true; return opt; }
    int i = 1;
    const std::string first = argv[i];
    if (first == "-h" || first == "--help" || first == "/?") { opt.help = true; return opt; }
    if (!starts_with(first, "-")) { opt.command = lower_copy(first); ++i; }
    for (; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--help" || arg == "-h" || arg == "/?") opt.help = true;
        else if (arg == "--list") opt.list = true;
        else if (option_matches(arg, "--alg")) opt.algorithm = require_value(i, argc, argv, arg, "--alg");
        else if (option_matches(arg, "--algorithm")) opt.algorithm = require_value(i, argc, argv, arg, "--algorithm");
        else if (option_matches(arg, "--in")) opt.input_file = require_value(i, argc, argv, arg, "--in");
        else if (option_matches(arg, "--out")) opt.output_file = require_value(i, argc, argv, arg, "--out");
        else if (option_matches(arg, "--hex-input")) opt.hex_input = require_value(i, argc, argv, arg, "--hex-input");
        else if (option_matches(arg, "--text")) opt.text_input = require_value(i, argc, argv, arg, "--text");
        else if (arg == "--empty-input") opt.empty_input = true;
        else if (arg == "--out-hex") opt.out_hex = true;
        else if (option_matches(arg, "--xof-len")) opt.xof_len = parse_size(require_value(i, argc, argv, arg, "--xof-len"));
        else throw std::invalid_argument("Unknown argument: " + arg);
    }
    return opt;
}

void print_list() {
    for (const auto& alg : hashlab_evp_direct::EVPHashDirectTool::supported_algorithms()) {
        const auto info = hashlab_evp_direct::EVPHashDirectTool::digest_info(alg);
        std::cout << alg << " : available, size=" << info.output_size << ", block=" << info.block_size << ", xof=" << (info.is_xof ? "yes" : "no") << "\n";
    }
}

void print_info(const CLIOptions& opt) {
    const auto info = hashlab_evp_direct::EVPHashDirectTool::digest_info(opt.algorithm);
    std::cout << "Algorithm   : " << info.canonical_name << "\n";
    std::cout << "Available   : yes\n";
    std::cout << "Output size : " << info.output_size << " byte(s)\n";
    std::cout << "Block size  : " << info.block_size << " byte(s)\n";
    std::cout << "XOF         : " << (info.is_xof ? "yes" : "no") << "\n";
}

void stream_demo(const CLIOptions& opt) {
    hashlab_evp_direct::DirectDigestContext ctx(opt.algorithm);
    ctx.update(hashlab_evp_direct::EVPHashDirectTool::text_to_bytes("abc"));
    auto copy = ctx.clone();
    ctx.update(hashlab_evp_direct::EVPHashDirectTool::text_to_bytes("def"));
    copy.update(hashlab_evp_direct::EVPHashDirectTool::text_to_bytes("XYZ"));
    const auto info = ctx.info();
    hashlab_evp_direct::Bytes digest1, digest2;
    if (info.is_xof) {
        const std::size_t n = opt.xof_len == 0 ? 32 : opt.xof_len;
        digest1 = ctx.final_xof(n);
        digest2 = copy.final_xof(n);
    } else {
        digest1 = ctx.final();
        digest2 = copy.final();
    }
    std::cout << "stream 1 input: abcdef\n";
    std::cout << "stream 2 input: abcXYZ\n";
    std::cout << "digest 1: " << hashlab_evp_direct::EVPHashDirectTool::bytes_to_hex(digest1) << "\n";
    std::cout << "digest 2: " << hashlab_evp_direct::EVPHashDirectTool::bytes_to_hex(digest2) << "\n";
}

} // anonymous namespace

int main(int argc, char* argv[]) {
    try {
        CLIOptions opt = parse_args(argc, argv);
        if (opt.help) { print_usage(); return 0; }
        if (opt.list) { print_list(); return 0; }
        if (opt.command == "info") { print_info(opt); return 0; }
        if (opt.command == "stream-demo") { stream_demo(opt); return 0; }
        if (opt.command != "hash") throw std::invalid_argument("Unsupported command: " + opt.command);
        const auto digest = hashlab_evp_direct::EVPHashDirectTool::digest(opt.algorithm, read_input(opt), opt.xof_len);
        if (!opt.output_file.empty()) write_file(opt.output_file, digest);
        if (opt.out_hex || opt.output_file.empty()) std::cout << hashlab_evp_direct::EVPHashDirectTool::bytes_to_hex(digest) << "\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\nUse --help for usage.\n";
        return 1;
    }
}
