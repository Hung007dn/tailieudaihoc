#PhucKhang 24162056
def replace_chars(s, old_char, new_char):
    result = ""
    for ch in s:
        if ch == old_char:
            result += new_char
        else:
            result += ch
    return result

s = input("Nhập xâu ký tự: ")
old = input("Nhập ký tự cần thay thế: ")
new = input("Nhập ký tự thay thế: ")

new_string = replace_chars(s, old, new)
print("Xâu mới sau khi thay thế:", new_string)
