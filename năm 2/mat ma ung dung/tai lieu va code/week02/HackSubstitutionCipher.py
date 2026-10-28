from collections import Counter
import string

# Known English letter frequencies (from most frequent to least frequent)
english_frequencies = 'MNBVCXZLKJHGFDSAPOIUYTREWQ'

cipher_text = ("✦✩◈◈◍ ◕●⊟⊟◆◈ ◔○ ✩ ○◆◈◔◆○ ●◉ ○◆∆◆◇ ⊞✦◔⊠◓◈◆◇'○ ◉✩◇⊟✩○◍ ◇●∆◆⊠○ ⊡◈◔⊟⊟◆◇ ◑◍ ◑◈◔⊟◔○✦ ✩★⊟✦●◈ ◎. ◐. ◈●⊡⊠◔◇□. ⊟✦◆ ◇●∆◆⊠○ ⊞✦◈●◇◔⊞⊠◆ ⊟✦◆ ⊠◔∆◆○ ●◉ ✩ ◍●★◇□ ⊡◔✧✩◈◓, ✦✩◈◈◍ ◕●⊟⊟◆◈, ✩◇◓ ✦◔○ ◉◈◔◆◇◓○, ◈●◇ ⊡◆✩○⊠◆◍ ✩◇◓ ✦◆◈✫◔●◇◆ □◈✩◇□◆◈, ✩⊠⊠ ●◉ ⊡✦●✫ ✩◈◆ ○⊟★◓◆◇⊟○ ✩⊟ ✦●□⊡✩◈⊟○ ○⊞✦●●⊠ ●◉ ⊡◔⊟⊞✦⊞◈✩◉⊟ ✩◇◓ ⊡◔✧✩◈◓◈◍. ⊟✦◆ ✫✩◔◇ ○⊟●◈◍ ✩◈⊞ ⊞●◇⊞◆◈◇○ ✦✩◈◈◍'○ ⊞●◇◉⊠◔⊞⊟ ⊡◔⊟✦ ⊠●◈◓ ∆●⊠◓◆✫●◈⊟, ✩ ◓✩◈◐ ⊡◔✧✩◈◓ ⊡✦● ◔◇⊟◆◇◓○ ⊟● ◑◆⊞●✫◆ ◔✫✫●◈⊟✩⊠, ●∆◆◈⊟✦◈●⊡ ⊟✦◆ ⊡◔✧✩◈◓ □●∆◆◈◇◔◇□ ◑●◓◍ ◐◇●⊡◇ ✩○ ⊟✦◆ ✫◔◇◔○⊟◈◍ ●◉ ✫✩□◔⊞, ✩◇◓ ○★◑◎★□✩⊟◆ ✩⊠⊠ ⊡◔✧✩◈◓○ ✩◇◓ ◇●◇-✫✩□◔⊞✩⊠ ◕◆●◕⊠◆, ◐◇●⊡◇ ◔◇-★◇◔∆◆◈○◆ ✩○ ✫★□□⊠◆○.⊟✦◆ ○◆◈◔◆○ ⊡✩○ ●◈◔□◔◇✩⊠⊠◍ ◕★◑⊠◔○✦◆◓ ◔◇ ◆◇□⊠◔○✦ ◑◍ ◑⊠●●✫○◑★◈◍ ◔◇ ⊟✦◆ ★◇◔⊟◆◓ ◐◔◇□◓●✫ ✩◇◓ ○⊞✦●⊠✩○⊟◔⊞ ◕◈◆○○ ◔◇ ⊟✦◆ ★◇◔⊟◆◓ ○⊟✩⊟◆○. ✩ ○◆◈◔◆○ ●◉ ✫✩◇◍ □◆◇◈◆○, ◔◇⊞⊠★◓◔◇□ ◉✩◇⊟✩○◍, ◓◈✩✫✩, ⊞●✫◔◇□-●◉-✩□◆ ◉◔⊞⊟◔●◇, ✩◇◓ ⊟✦◆ ◑◈◔⊟◔○✦ ○⊞✦●●⊠ ○⊟●◈◍ (⊡✦◔⊞✦ ◔◇⊞⊠★◓◆○ ◆⊠◆✫◆◇⊟○ ●◉ ✫◍○⊟◆◈◍, ⊟✦◈◔⊠⊠◆◈, ✩◓∆◆◇⊟★◈◆, ✦●◈◈●◈, ✩◇◓ ◈●✫✩◇⊞◆), ⊟✦◆ ⊡●◈⊠◓ ●◉ ✦✩◈◈◍ ◕●⊟⊟◆◈ ◆✪◕⊠●◈◆○ ◇★✫◆◈●★○ ⊟✦◆✫◆○ ✩◇◓ ◔◇⊞⊠★◓◆○ ✫✩◇◍ ⊞★⊠⊟★◈✩⊠ ✫◆✩◇◔◇□○ ✩◇◓ ◈◆◉◆◈◆◇⊞◆○. ✫✩◎●◈ ⊟✦◆✫◆○ ◔◇ ⊟✦◆ ○◆◈◔◆○ ◔◇⊞⊠★◓◆ ◕◈◆◎★◓◔⊞◆, ⊞●◈◈★◕⊟◔●◇, ✫✩◓◇◆○○, ⊠●∆◆, ✩◇◓ ◓◆✩⊟✦.")
# Count letter frequencies in the ciphertext (ignoring non-alphabet characters)
cipher_counts = Counter(''.join(filter(str.isalpha, cipher_text.upper())))

# Sort the ciphertext letters by frequency (most frequent first)
sorted_cipher = ''.join([item[0] for item in cipher_counts.most_common()])

# Create an initial mapping from ciphertext letters to the English frequency order
mapping = {}
for i, letter in enumerate(sorted_cipher):
    mapping[letter] = english_frequencies[i]

# For any letters not present in the ciphertext, add an identity mapping
for letter in string.ascii_uppercase:
    if letter not in mapping:
        mapping[letter] = letter

# Optional manual adjustments to improve decryption quality

mapping['M'] = 'O'  # Adjusting based on context
def print_key_mapping_table(mapping):
    """
    Displays the key mapping in the requested table format:
    
     A  B  C  D  E  F  G  H  I  J  K  L  M  N  O  P  Q  R  S  T  U  V  W  X  Y  Z
     --+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--
     R  A  T  X  U  K  E  Y  H  O  I  D  V  F  G  M  P  L  Z  W  S  Q  J  C  B  N
    """
    plain_letters = list(string.ascii_uppercase)
    # Build the first row: plain letters with a fixed width (2 characters per letter)
    row1 = " ".join(f"{letter:2}" for letter in plain_letters)
    # Build the border row: "--+--+...+--"
    row2 = " " + "--" + "+--"*(len(plain_letters)-1) + " "
    # Build the third row: corresponding cipher letters from the mapping
    row3 = " ".join(f"{mapping[letter]:2}" for letter in plain_letters)
    
    print(row1)
    print(row2)
    print(row3)

# Display the final mapping using the desired table format
print_key_mapping_table(mapping)

# Decrypt the ciphertext using the mapping (preserving letter case)
decrypted_text = []
for char in cipher_text:
    if char.isalpha():
        if char.isupper():
            decrypted_text.append(mapping.get(char, char))
        else:
            decrypted_text.append(mapping.get(char.upper(), char.upper()).lower())
    else:
        decrypted_text.append(char)
decrypted_text = ''.join(decrypted_text)

print("\nDecrypted Text:")
print(decrypted_text)
