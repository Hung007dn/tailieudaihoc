#pragma once

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#if defined(EVPHASHDIRECT_STATIC)
    #define EVPHASHDIRECT_API
#elif defined(_WIN32) || defined(__CYGWIN__)
    #if defined(EVPHASHDIRECT_EXPORTS)
        #define EVPHASHDIRECT_API __declspec(dllexport)
    #else
        #define EVPHASHDIRECT_API __declspec(dllimport)
    #endif
#else
    #if defined(__GNUC__) || defined(__clang__)
        #define EVPHASHDIRECT_API __attribute__((visibility("default")))
    #else
        #define EVPHASHDIRECT_API
    #endif
#endif

typedef enum EVPHashDirectStatus {
    EVPHASHDIRECT_OK = 0,
    EVPHASHDIRECT_ERR_INVALID_ARGUMENT = -1,
    EVPHASHDIRECT_ERR_BUFFER_TOO_SMALL = -2,
    EVPHASHDIRECT_ERR_UNAVAILABLE      = -3,
    EVPHASHDIRECT_ERR_OPENSSL          = -4,
    EVPHASHDIRECT_ERR_EXCEPTION        = -100
} EVPHashDirectStatus;

typedef struct EVPHASHDIRECT_CTX EVPHASHDIRECT_CTX;

EVPHASHDIRECT_API const char* evphashdirect_version(void);
EVPHASHDIRECT_API const char* evphashdirect_last_error(void);
EVPHASHDIRECT_API void evphashdirect_clear_error(void);

EVPHASHDIRECT_API int evphashdirect_digest_available(const char* algorithm_name);

EVPHASHDIRECT_API int evphashdirect_digest_info(
    const char* algorithm_name,
    int* output_size_out,
    int* block_size_out,
    int* is_xof_out
);

EVPHASHDIRECT_API int evphashdirect_digest(
    const char* algorithm_name,
    const uint8_t* input,
    size_t input_len,
    size_t xof_output_len,
    uint8_t* output,
    size_t output_capacity,
    size_t* output_len
);

EVPHASHDIRECT_API int evphashdirect_ctx_new(
    const char* algorithm_name,
    EVPHASHDIRECT_CTX** ctx_out
);

EVPHASHDIRECT_API int evphashdirect_ctx_update(
    EVPHASHDIRECT_CTX* ctx,
    const uint8_t* input,
    size_t input_len
);

EVPHASHDIRECT_API int evphashdirect_ctx_copy(
    const EVPHASHDIRECT_CTX* src,
    EVPHASHDIRECT_CTX** dst_out
);

EVPHASHDIRECT_API int evphashdirect_ctx_final(
    EVPHASHDIRECT_CTX* ctx,
    uint8_t* output,
    size_t output_capacity,
    size_t* output_len
);

EVPHASHDIRECT_API int evphashdirect_ctx_final_xof(
    EVPHASHDIRECT_CTX* ctx,
    size_t xof_output_len,
    uint8_t* output,
    size_t output_capacity,
    size_t* output_len
);

EVPHASHDIRECT_API void evphashdirect_ctx_free(EVPHASHDIRECT_CTX* ctx);

EVPHASHDIRECT_API int evphashdirect_hex_to_bytes(
    const char* hex,
    uint8_t* output,
    size_t output_capacity,
    size_t* output_len
);

EVPHASHDIRECT_API int evphashdirect_bytes_to_hex(
    const uint8_t* input,
    size_t input_len,
    char* output_hex,
    size_t output_hex_capacity,
    size_t* output_hex_len
);

#ifdef __cplusplus
}
#endif
