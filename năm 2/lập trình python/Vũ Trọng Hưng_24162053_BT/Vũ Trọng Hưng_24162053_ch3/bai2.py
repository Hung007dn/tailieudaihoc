#Vũ Trọng Hưng - 24162053
import math
n= int(input("Nhập số nguyên n: "))
#số chính phương
if n>=0:
    sqrt_n=math.isqrt (n)
    if sqrt_n*sqrt_n==n:
        print(n,"là số chính phương")
    else:
        print("Số chính phương gần nó là ",int(sqrt_n*sqrt_n))
        