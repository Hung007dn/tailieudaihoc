#Trang Sĩ Hoàng 24162035
n = int(input("Nhập số lượng phần tử n : "))
lst = []
for i in range(n):
    x = input(f"Nhập phần tử thứ {i+1}: ")
    lst.append(x)

k = input("Nhập giá trị k cần kiểm tra và xóa: ")

if k in lst:
    lst = [x for x in lst if x != k]
    print("Danh sách sau khi xóa tất cả phần tử bằng k:")
    print(lst)
else:
    print("Giá trị k không tồn tại trong danh sách.")