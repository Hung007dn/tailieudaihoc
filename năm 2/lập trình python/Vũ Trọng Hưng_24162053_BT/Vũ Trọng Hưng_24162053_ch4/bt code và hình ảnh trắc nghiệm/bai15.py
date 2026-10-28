#Trang Sĩ Hoàng 24162035
uoc = []
boi = []

n = int(input("Nhap so phan tu cua mang : "))
k = int(input())

for i in range(n):
    x = int(input())
    if x % k  == 0:
        boi.append(x)  # x là bội của k
    if x != 0 and k % x == 0:
        uoc.append(x)  # x là ước của k

print("uoc la", uoc)
print("boi la", boi)