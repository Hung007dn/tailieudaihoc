#Vũ Trọng Hưng-24162053
#Bài 3
while True:
    a = int(input("Nhập a: "))
    b = int(input("Nhập b: "))
    c = int(input("Nhập c: "))

    if a == 0 or b == 0 or c == 0:
        print("Kết thúc chương trình.")
        break

    delta = b**2 - 4*a*c

    if delta > 0:
        x1 = (-b + delta**0.5) / (2*a)
        x2 = (-b - delta**0.5) / (2*a)
        print("Phương trình có hai nghiệm phân biệt:", x1, ",", x2)
    elif delta == 0:
        x = -b / (2*a)
        print("Phương trình có nghiệm kép:", x)
    else:
        print("Phương trình vô nghiệm.")