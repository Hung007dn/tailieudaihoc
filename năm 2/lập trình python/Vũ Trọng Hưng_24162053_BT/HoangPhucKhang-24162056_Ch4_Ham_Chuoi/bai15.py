#PhucKhang 24162056
def substrings_with_min_length(s, k):
    result = []
    n = len(s)
    for i in range(n):
        for j in range(i + k, n + 1):
            result.append(s[i:j])
    return result

s = input("Nhập xâu: ")
k = int(input("Nhập độ dài tối thiểu k: "))

res = substrings_with_min_length(s, k)
print("Các xâu con có độ dài ≥", k, ":")
for x in res:
    print(x)
