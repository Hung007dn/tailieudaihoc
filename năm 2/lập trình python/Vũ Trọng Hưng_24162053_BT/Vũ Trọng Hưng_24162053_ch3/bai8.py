#Vũ Trọng Hưng_24162053
n = int(input("Nhập số: "))
max_val = n  

while n != 0:
    if n > max_val:
        max_val = n
    n = int(input("Nhập số: "))  # cập nhật n mới

print("Số lớn nhất là:", max_val)
