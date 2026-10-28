#Vũ Trọng Hung-24162053
n = int(input("Nhập số bit: "))

total = 2**n
for x in range(total):
    s = bin(x)[2:].zfill(n)
    print(s)
