# Vũ Trọng Hưng - 24162053
n=int(input('nhap vap so tu nhien n = '))
a=[]
for i in range (n):
    a.append(i)
b=[x**2 for x in a if x<n ]
print(a)
print(b)