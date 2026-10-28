#Vũ Trọng Hưng_24162053
n = int(input("Nhap vao so luong so nguyen to can tim : "))
a = []
def ktra_snt(x):
    if x<2:
        return False
    for i in range(2,int(x**0.5)+1):
        if x%i==0:
            return False
    return True
so=2
while len(a)<n:
    if ktra_snt(so):
        a.append(so)
    so+=1
print (a)