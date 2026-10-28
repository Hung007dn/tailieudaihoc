# Vũ Trọng Hưng - 24162053
n=int(input("nhap vao so n: "))
a=[]
for i in range(n):
    x=int(input(f'nhap vao phan tu thu {i+1} = '))
    a.append(x)
max=-1e10
min=1e10
for i in a:
    if i>max:
        max=i
    if i<min:
        min=i
print(f'max la {max}')
print(f'min la {min}')