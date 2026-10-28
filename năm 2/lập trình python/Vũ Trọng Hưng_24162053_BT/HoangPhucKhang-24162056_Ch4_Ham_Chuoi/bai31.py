#PhucKhang 24162056
def optimize_name(s):
    s = s.strip()
    parts = s.split()
    parts = [word.capitalize() for word in parts]
    return " ".join(parts)

print(optimize_name("  TRần   duY   thAnH "))
