#Vũ Trọng Hưng-24162053
A=int(input("Nhập A: "))
B=int(input("Nhập B: "))
def nguyen_to(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True
count=0
if(nguyen_to(A) and nguyen_to(B)):
    for i in range(A, B + 1):
        if nguyen_to(i):
            count += 1
    print("Số lượng số nguyên tố trong khoảng từ", A, "đến", B, "là:", count)