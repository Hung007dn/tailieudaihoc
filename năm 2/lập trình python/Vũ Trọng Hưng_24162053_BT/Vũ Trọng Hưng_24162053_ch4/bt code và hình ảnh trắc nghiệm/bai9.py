#Trang Sĩ Hoàng 24162035
n = int(input("Nhập số lượng phần tử n : "))
lst = []
for i in range(n):
    x = float(input(f"Nhập phần tử thứ {i+1}: "))
    lst.append(x)

lst.sort()

print("Danh sách sau khi sắp xếp tăng dần:")
print(lst)