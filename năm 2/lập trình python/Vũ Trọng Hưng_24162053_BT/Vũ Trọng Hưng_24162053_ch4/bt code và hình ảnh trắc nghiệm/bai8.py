#Trang Sĩ Hoàng 24162035
n = int(input("Nhập vào n: "))
lst = []
for i in range(n):
    x = input(f"Nhập phần tử thứ {i+1}: ")
    lst.append(x)
khonglap = [x for x in lst if lst.count(x) == 1]

print("Danh sách các phần tử không trùng lặp:")
print(khonglap)