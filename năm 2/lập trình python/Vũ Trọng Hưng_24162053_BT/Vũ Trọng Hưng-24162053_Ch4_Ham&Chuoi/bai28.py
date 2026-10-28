#Vũ Trọng Hưng-24162053
def is_symmetrical(s):
    n = len(s)
    if n % 2 != 0:
        return False
    half = n // 2
    return s[:half] == s[half:]

print(is_symmetrical("khokho"))
print(is_symmetrical("amaama"))
print(is_symmetrical("abcdab"))
