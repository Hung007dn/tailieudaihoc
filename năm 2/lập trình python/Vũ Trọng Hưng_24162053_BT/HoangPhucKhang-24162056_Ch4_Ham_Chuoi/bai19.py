#PhucKhang 24162056

# Chuyển chuỗi thành mã ASCII
s = input("Nhập chuỗi: ")
ascii_list = [ord(ch) for ch in s]
print("Mã ASCII:", ascii_list)

# Chuyển danh sách ASCII về chuỗi
ascii_input = input("Nhập danh sách mã ASCII (cách nhau bằng dấu cách): ")
nums = ascii_input.split()
result = ''.join(chr(int(n)) for n in nums)
print("Chuỗi sau khi chuyển:", result)
