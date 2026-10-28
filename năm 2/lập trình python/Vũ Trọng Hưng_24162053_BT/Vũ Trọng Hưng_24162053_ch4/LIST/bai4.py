#Vũ Trọng Hưng - 24162053
n = int(input("Nhập n: "))
a = []
for i in range(n):
    x = int(input("Enter: "))
    a.append(x)

k = int(input("Nhập k: "))

dem = 0
vi_tri = -1
for i in range(n):
    if a[i] < 0:
        dem += 1
        if dem == k:
            vi_tri = i
            break

if vi_tri == -1:
    print(f"Không có đủ {k} phần tử âm trong danh sách.")
else:
    print(f"Vị trí phần tử âm thứ {k} là: {vi_tri}")