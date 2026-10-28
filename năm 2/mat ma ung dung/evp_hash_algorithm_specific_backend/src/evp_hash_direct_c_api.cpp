#include "evp_hash_direct_c_api.h"

#include <cstring>
#include <exception>
#include <memory>
#include <stdexcept>
#include <string>

#include "evp_hash_direct_tool.h"

struct EVPHASHDIRECT_CTX {
    std::unique_ptr<hashlab_evp_direct::DirectDigestContext> impl;
};

namespace {

thread_local std::string g_last_error;

void clear_error() { g_last_error.clear(); }
void set_error(const std::string& message) { g_last_error = message; }

int set_error_return(int code, const std::string& message) {
    set_error(message);
    return code;
}

std::string require_string(const char* s, const char* name) {
    if (!s || std::string(s).empty()) {
        throw std::invalid_argument(std::string(name) + " is null or empty");
    }
    return std::string(s);
}

bool ptr_invalid_when_len_nonzero(const void* p, std::size_t len) {
    return p == nullptr && len != 0;
}

hashlab_evp_direct::Bytes make_bytes(const uint8_t* p, std::size_t len, const char* name) {
    if (ptr_invalid_when_len_nonzero(p, len)) {
        throw std::invalid_argument(std::string(name) + " pointer is null but length is non-zero");
    }
    if (len == 0) return {};
    return hashlab_evp_direct::Bytes(p, p + len);
}

int map_exception(const std::exception& e) {
    set_error(e.what());
    const std::string msg = e.what();

    if (msg.find("Unsupported") != std::string::npos ||
        msg.find("unsupported") != std::string::npos ||
        msg.find("unavailable") != std::string::npos) {
        return EVPHASHDIRECT_ERR_UNAVAILABLE;
    }

    if (msg.find("OpenSSL") != std::string::npos ||
        msg.find("EVP_") != std::string::npos ||
        msg.find("Digest") != std::string::npos) {
        return EVPHASHDIRECT_ERR_OPENSSL;
    }

    if (dynamic_cast<const std::invalid_argument*>(&e) != nullptr) {
        return EVPHASHDIRECT_ERR_INVALID_ARGUMENT;
    }

    return EVPHASHDIRECT_ERR_EXCEPTION;
}

int copy_bytes_to_output(
    const hashlab_evp_direct::Bytes& src,
    uint8_t* dst,
    std::size_t dst_capacity,
    std::size_t* dst_len,
    const char* output_name
) {
    if (dst_len) *dst_len = src.size();
    if (src.empty()) return EVPHASHDIRECT_OK;

    if (!dst || dst_capacity < src.size()) {
        return set_error_return(EVPHASHDIRECT_ERR_BUFFER_TOO_SMALL, std::string(output_name) + " buffer is too small");
    }

    std::memcpy(dst, src.data(), src.size());
    return EVPHASHDIRECT_OK;
}

int copy_string_to_output(
    const std::string& src,
    char* dst,
    std::size_t dst_capacity,
    std::size_t* dst_len,
    const char* output_name
) {
    if (dst_len) *dst_len = src.size();
    const std::size_t required = src.size() + 1;

    if (!dst || dst_capacity < required) {
        return set_error_return(EVPHASHDIRECT_ERR_BUFFER_TOO_SMALL, std::string(output_name) + " buffer is too small");
    }

    std::memcpy(dst, src.c_str(), required);
    return EVPHASHDIRECT_OK;
}

EVPHASHDIRECT_CTX* require_ctx(EVPHASHDIRECT_CTX* ctx) {
    if (!ctx || !ctx->impl) throw std::invalid_argument("Digest context is null");
    return ctx;
}

const EVPHASHDIRECT_CTX* require_ctx_const(const EVPHASHDIRECT_CTX* ctx) {
    if (!ctx || !ctx->impl) throw std::invalid_argument("Digest context is null");
    return ctx;
}

} // anonymous namespace

extern "C" {

EVPHASHDIRECT_API const char* evphashdirect_version(void) {
    return "EVP Hash Direct Tool 0.1.0";
}

EVPHASHDIRECT_API const char* evphashdirect_last_error(void) {
    return g_last_error.c_str();
}

EVPHASHDIRECT_API void evphashdirect_clear_error(void) {
    clear_error();
}

EVPHASHDIRECT_API int evphashdirect_digest_available(const char* algorithm_name) {
    try {
        clear_error();
        return hashlab_evp_direct::EVPHashDirectTool::digest_available(require_string(algorithm_name, "algorithm_name")) ? 1 : 0;
    } catch (const std::exception& e) {
        return map_exception(e);
    }
}

EVPHASHDIRECT_API int evphashdirect_digest_info(
    const char* algorithm_name,
    int* output_size_out,
    int* block_size_out,
    int* is_xof_out
) {
    try {
        clear_error();
        const auto info = hashlab_evp_direct::EVPHashDirectTool::digest_info(require_string(algorithm_name, "algorithm_name"));
        if (output_size_out) *output_size_out = info.output_size;
        if (block_size_out) *block_size_out = info.block_size;
        if (is_xof_out) *is_xof_out = info.is_xof ? 1 : 0;
        return EVPHASHDIRECT_OK;
    } catch (const std::exception& e) {
        return map_exception(e);
    }
}

EVPHASHDIRECT_API int evphashdirect_digest(
    const char* algorithm_name,
    const uint8_t* input,
    size_t input_len,
    size_t xof_output_len,
    uint8_t* output,
    size_t output_capacity,
    size_t* output_len
) {
    try {
        clear_error();
        const auto out = hashlab_evp_direct::EVPHashDirectTool::digest(
            require_string(algorithm_name, "algorithm_name"),
            make_bytes(input, input_len, "input"),
            xof_output_len
        );
        return copy_bytes_to_output(out, output, output_capacity, output_len, "digest output");
    } catch (const std::exception& e) {
        return map_exception(e);
    }
}

EVPHASHDIRECT_API int evphashdirect_ctx_new(const char* algorithm_name, EVPHASHDIRECT_CTX** ctx_out) {
    try {
        clear_error();
        if (!ctx_out) return set_error_return(EVPHASHDIRECT_ERR_INVALID_ARGUMENT, "ctx_out is null");
        *ctx_out = nullptr;
        std::unique_ptr<EVPHASHDIRECT_CTX> wrapper(new EVPHASHDIRECT_CTX);
        wrapper->impl.reset(new hashlab_evp_direct::DirectDigestContext(require_string(algorithm_name, "algorithm_name")));
        *ctx_out = wrapper.release();
        return EVPHASHDIRECT_OK;
    } catch (const std::exception& e) {
        return map_exception(e);
    }
}

EVPHASHDIRECT_API int evphashdirect_ctx_update(EVPHASHDIRECT_CTX* ctx, const uint8_t* input, size_t input_len) {
    try {
        clear_error();
        require_ctx(ctx)->impl->update(input, input_len);
        return EVPHASHDIRECT_OK;
    } catch (const std::exception& e) {
        return map_exception(e);
    }
}

EVPHASHDIRECT_API int evphashdirect_ctx_copy(const EVPHASHDIRECT_CTX* src, EVPHASHDIRECT_CTX** dst_out) {
    try {
        clear_error();
        if (!dst_out) return set_error_return(EVPHASHDIRECT_ERR_INVALID_ARGUMENT, "dst_out is null");
        *dst_out = nullptr;
        const EVPHASHDIRECT_CTX* checked = require_ctx_const(src);
        auto copy_ctx = checked->impl->clone();
        std::unique_ptr<EVPHASHDIRECT_CTX> wrapper(new EVPHASHDIRECT_CTX);
        wrapper->impl.reset(new hashlab_evp_direct::DirectDigestContext(std::move(copy_ctx)));
        *dst_out = wrapper.release();
        return EVPHASHDIRECT_OK;
    } catch (const std::exception& e) {
        return map_exception(e);
    }
}

EVPHASHDIRECT_API int evphashdirect_ctx_final(EVPHASHDIRECT_CTX* ctx, uint8_t* output, size_t output_capacity, size_t* output_len) {
    try {
        clear_error();
        const auto out = require_ctx(ctx)->impl->final();
        return copy_bytes_to_output(out, output, output_capacity, output_len, "digest output");
    } catch (const std::exception& e) {
        return map_exception(e);
    }
}

EVPHASHDIRECT_API int evphashdirect_ctx_final_xof(EVPHASHDIRECT_CTX* ctx, size_t xof_output_len, uint8_t* output, size_t output_capacity, size_t* output_len) {
    try {
        clear_error();
        const auto out = require_ctx(ctx)->impl->final_xof(xof_output_len);
        return copy_bytes_to_output(out, output, output_capacity, output_len, "XOF output");
    } catch (const std::exception& e) {
        return map_exception(e);
    }
}

EVPHASHDIRECT_API void evphashdirect_ctx_free(EVPHASHDIRECT_CTX* ctx) {
    delete ctx;
}

EVPHASHDIRECT_API int evphashdirect_hex_to_bytes(const char* hex, uint8_t* output, size_t output_capacity, size_t* output_len) {
    try {
        clear_error();
        const auto out = hashlab_evp_direct::EVPHashDirectTool::hex_to_bytes(require_string(hex, "hex"));
        return copy_bytes_to_output(out, output, output_capacity, output_len, "hex output");
    } catch (const std::exception& e) {
        return map_exception(e);
    }
}

EVPHASHDIRECT_API int evphashdirect_bytes_to_hex(const uint8_t* input, size_t input_len, char* output_hex, size_t output_hex_capacity, size_t* output_hex_len) {
    try {
        clear_error();
        const std::string out = hashlab_evp_direct::EVPHashDirectTool::bytes_to_hex(make_bytes(input, input_len, "input"));
        return copy_string_to_output(out, output_hex, output_hex_capacity, output_hex_len, "hex output");
    } catch (const std::exception& e) {
        return map_exception(e);
    }
}

} // extern "C"
