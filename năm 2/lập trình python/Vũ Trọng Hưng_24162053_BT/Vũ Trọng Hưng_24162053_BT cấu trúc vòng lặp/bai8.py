#Vũ Trọng Hưng-24162053
n = int(input("Nhập số phần tử của mảng: "))
a = []
for i in range(n):
    x = int(input(f"Phần tử thứ {i+1}: "))
    a.append(x)
max_tong = a[0]
tong_hien_tai = a[0]

for i in range(1, n):
    if tong_hien_tai + a[i] > a[i]:
        tong_hien_tai = tong_hien_tai + a[i]
    else:
        tong_hien_tai = a[i]
    
    if tong_hien_tai > max_tong:
        max_tong = tong_hien_tai
print("Tổng lớn nhất của dãy con liên tiếp là:", max_tong)