#Vũ Trọng Hưng 24162053
import numpy as np
a=float(input("Nhập a: "))
b=float(input("Nhập b: "))

a,b=min(a,b),max(a,b)
arr=a+(b-a)*np.random.rand(10)
arr=np.random.uniform(a,b,10)

print(arr)