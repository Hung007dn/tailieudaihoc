#PhucKhang 24162056
def is_symmetrical(s):
    n = len(s)
    if n % 2 != 0:
        return False
    half = n // 2
    return s[:half] == s[half:]

print(is_symmetrical("khokho"))
print(is_symmetrical("amaama"))
print(is_symmetrical("abcdab"))
