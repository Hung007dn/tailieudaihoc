#Vũ Trọng Hưng_24162053
a = int(input("Nhập vào số a: "))
b = int(input("Nhập vào số b: "))

if a % 2 == 0 and b % 2 == 0:
    print("a và b là 2 so chan")
elif a % 2 == 0 or b % 2 == 0:
    print("chỉ co mot so chan")
else:
    print("a, b là hai so le")