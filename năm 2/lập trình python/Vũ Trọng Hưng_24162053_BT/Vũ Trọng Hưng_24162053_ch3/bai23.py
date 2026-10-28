#Vũ Trọng Hưng_24162053
n = int(input("Nhap vao so phan tu: "))
x = int(input("Nhap vao so can chen: "))
a = []
for i in range(n):
    val = int(input(f"Nhap phan tu {i+1}: "))
    a.append(val)
pos = n  
for i in range(n):
    if x < a[i]:
        pos = i
        break

b = []
for i in range(n + 1):
    if i < pos:
        b.append(a[i])
    elif i == pos:
        b.append(x)
    else:
        b.append(a[i - 1])

print("Mang sau khi chen:", b)
