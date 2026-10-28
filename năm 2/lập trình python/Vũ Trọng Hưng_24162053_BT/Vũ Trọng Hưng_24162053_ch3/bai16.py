#Vũ Trọng Hưng_24162053
n=int(input("Nhập n: "))
S=0
i=1
tong_1=0
while i <= n:
    tong_1 += i
    S += 1 / tong_1
    i += 1

S2=0
i2=1
while i2 <= n:
    S2+=1/(i2*(i2+1))
    i2+=1

S3=0
i3=1
while i3 <= n:
    S3+=i3/(i3+1)
    i3+=1

S4=0
i4=1
while i4 <= n:
    S4+=(2*i4+1)/(2*i4+2)
    i4+=1
    
print("Công thức 1 là: ",S)
print("Công thức 2 là: ",S2)
print("Công thức 3 là: ",S3)
print("Công thức 4 là: ",S4)