#Vũ Trọng Hưng-24162053
def distinct_substrings(s):
    result = set()
    n = len(s)
    for i in range(n):
        for j in range(i + 1, n + 1):
            result.add(s[i:j])
    return result

s = input("Nhập xâu: ")

res = distinct_substrings(s)
print("Các xâu con khác nhau:")
for x in sorted(res):
    print(x)
