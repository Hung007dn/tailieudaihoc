#PhucKhang 24162056
def longest_unique_substring(s):
    left = 0
    seen = set()
    max_len = 0
    start_index = 0

    for right in range(len(s)):

        while s[right] in seen:
            seen.remove(s[left])
            left += 1

        seen.add(s[right])
        
        if right - left + 1 > max_len:
            max_len = right - left + 1
            start_index = left


    return s[start_index:start_index + max_len]

s = input("Nhập xâu: ")
result = longest_unique_substring(s)
print("Xâu con dài nhất không lặp ký tự:", result)
print("Độ dài:", len(result))
