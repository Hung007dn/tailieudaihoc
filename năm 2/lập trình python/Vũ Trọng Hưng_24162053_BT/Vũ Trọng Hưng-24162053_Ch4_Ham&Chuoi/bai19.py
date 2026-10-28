#Vũ Trọng Hưng-24162053
s = input("Nhập chuỗi: ")
ascii_list = [ord(ch) for ch in s]
print("Mã ASCII:", ascii_list)

ascii_input = input("Nhập danh sách mã ASCII (cách nhau bằng dấu cách): ")
nums = ascii_input.split()
result = ''.join(chr(int(n)) for n in nums)
print("Chuỗi sau khi chuyển:", result)
