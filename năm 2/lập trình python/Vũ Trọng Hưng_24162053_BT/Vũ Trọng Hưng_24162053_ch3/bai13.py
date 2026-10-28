#Vũ Trọng Hưng_24162053
n=int(input('Nhap vao 1 so nguyen duong'))
dem=0
while n>0:
    digit=n%10
    if digit==7:
        dem+=1
    n=n//10
print('co',dem,'so 7')