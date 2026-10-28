#Vũ Trọng Hưng-24162053
a = int(input("nhập chiều cao hình tam giác: "))
x = a

for i in range(a):
    for j in range(a - i - 1):
        print(" ", end="")
    for j in range(2 * i + 1):
        print("*", end="")
    print()
