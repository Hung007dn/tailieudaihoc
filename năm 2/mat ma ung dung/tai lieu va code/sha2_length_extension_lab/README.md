# SHA-2 Length Extension Lab

This package demonstrates SHA-2 length-extension attacks in a controlled educational setting.

## Core Idea

A vulnerable secret-prefix MAC is:

```text
MAC = SHA256(secret || message)
```

If an attacker knows:

```text
message
MAC
a guess for len(secret)
suffix to append
```

then the attacker can compute:

```text
forged_message = message || SHA256_glue_padding(secret || message) || suffix
forged_mac     = SHA256(secret || forged_message)
```

without knowing `secret`.

This works because SHA-256 and SHA-512 are Merkle-Damgard hashes: the public digest is the final internal chaining state. If we allow a teaching implementation to set:

```text
internal state / IV
already processed byte count
```

then we can resume hashing from the known digest.

OpenSSL EVP correctly hides this internal state, so we implement SHA-256/SHA-512 ourselves for this lab.

## Files

```text
sha2_length_extension_lab/
├── README.md
├── include/
│   └── sha2_length_extension.h
├── src/
│   ├── sha2_length_extension.cpp
│   └── sha2_lenext_main.cpp
└── tests/
    └── test_sha2_lenext.cpp
```

## Supported Algorithms

Implemented:

```text
SHA-256
SHA-512
```

Directly exploitable with full digest known:

```text
SHA-256
SHA-512
```

Not directly demonstrated here:

```text
SHA-224
SHA-384
SHA-512/224
SHA-512/256
```

Reason: those variants truncate the final internal state, so the attacker does not know the complete chaining state from the published digest.

## Build Test

```bat
g++ -std=c++17 -O2 -Wall -Wextra ^
  -Iinclude ^
  src\sha2_length_extension.cpp ^
  tests\test_sha2_lenext.cpp ^
  -o test_sha2_lenext.exe
```

Run:

```bat
test_sha2_lenext.exe
```

Expected:

```text
SHA256 empty PASSED
SHA256 abc PASSED
SHA512 empty PASSED
SHA512 abc PASSED
SHA256 length extension PASSED
SHA512 length extension PASSED
```

## Build CLI

```bat
g++ -std=c++17 -O2 -Wall -Wextra ^
  -Iinclude ^
  src\sha2_length_extension.cpp ^
  src\sha2_lenext_main.cpp ^
  -o sha2_lenext_lab.exe
```

## Demo SHA-256

```bat
sha2_lenext_lab.exe demo-sha256
```

Default demo uses:

```text
secret  = "YELLOW SUBMARINE"
message = "user=alice&role=user"
suffix  = "&role=admin"
```

Expected behavior:

```text
Server verification      : PASSED
```

The printed forged message contains binary SHA-256 padding bytes, so the CLI prints both hex and C-style escaped output.

## Demo SHA-512

```bat
sha2_lenext_lab.exe demo-sha512
```

## Attacker-Only Forge Mode

Suppose the attacker knows:

```text
message = "user=alice&role=user"
mac     = known SHA256(secret || message)
guess secret length = 16
suffix  = "&role=admin"
```

Run:

```bat
sha2_lenext_lab.exe forge-sha256 ^
  --message-text "user=alice&role=user" ^
  --mac <known_mac_hex> ^
  --guess-secret-len 16 ^
  --suffix-text "&role=admin"
```

Output:

```text
forged message hex
forged message escaped form
forged MAC
```

Send to a vulnerable server:

```text
message = forged_message
mac     = forged_mac
```

The server verifies:

```text
SHA256(secret || forged_message) == forged_mac
```

## Important Teaching Notes

### Why `set_state()` Is the Plug-and-Play Knob

The attack needs:

```cpp
SHA256 attacker;
attacker.set_state_from_digest(known_mac, processed_before_suffix);
attacker.update(suffix);
Bytes forged_mac = attacker.final();
```

where:

```text
processed_before_suffix =
    guessed_secret_len
  + known_message.length
  + glue_padding.length
```

This value must be a full SHA-256 block boundary.

### Why HMAC Is Safe

Do not build MACs like this:

```text
SHA256(secret || message)
SHA256(message || secret)
```

Use HMAC:

```text
HMAC-SHA256(secret, message)
```

HMAC prevents this extension attack by hashing with inner and outer keyed pads.

### Why This Is Not an OpenSSL EVP Feature

OpenSSL EVP is designed for correct cryptographic use. It does not let users set arbitrary SHA-256 internal state because that would be unsafe and unnecessary for normal applications.

This lab intentionally exposes that internal state to explain the attack.

## Suggested Lab Flow

1. Show SHA-256 normal hashing.
2. Show `MAC = SHA256(secret || message)`.
3. Reveal only `message` and `MAC` to the attacker.
4. Guess `len(secret)`.
5. Compute glue padding.
6. Parse digest into SHA-256 internal state.
7. Resume SHA-256 from that state.
8. Verify forged request on the simulated server.
9. Replace the vulnerable MAC with HMAC-SHA256 and explain why the attack fails.
