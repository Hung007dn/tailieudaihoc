#Vũ Trọng Hưng_24162053
a = int(input("Nhập vào số a: "))
b = int(input("Nhập vào số b: "))

if b == 0:
    print("Không thể chia cho 0")
elif a % b == 0:
    print(f"{a} la boi so cua {b}")
else:
    print(f"{a} la KHONG boi so cua {b}")