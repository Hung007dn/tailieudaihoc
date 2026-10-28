#PhucKhang 24162056
def repeated_substrings(s):
    seen = set()
    repeated = set()
    n = len(s)

    for i in range(n):
        for j in range(i + 1, n + 1):
            sub = s[i:j]
            if sub in seen:
                repeated.add(sub)
            else:
                seen.add(sub)

    return repeated

s = input("Nhập xâu: ")
res = repeated_substrings(s)

print("Các xâu con lặp lại:")
for x in sorted(res):
    print(x)
