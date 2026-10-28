#Vũ Trọng Hưng_24162053
binary=input("Nhập 1 số nhị phân: ")
dec=0
length=len(binary)
for i in range(length):
    bit=int(binary[i])
    dec+=bit*(2**(length-i-1))

print(dec)
