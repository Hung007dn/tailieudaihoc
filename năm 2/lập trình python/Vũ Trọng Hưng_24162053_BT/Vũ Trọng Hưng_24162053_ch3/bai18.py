#Vũ Trọng Hưng - 24162053
while True:
    try:
        N = int(input("Nhập số nguyên N: "))
        break
    except ValueError:
        print("Vui lòng nhập số nguyên hợp lệ!")

print(f"Các ước số của {N} là:")

if N == 0:
    print("Số 0 có vô số ước số")
else:
    absolute_N = abs(N)
    divisors = []
    
    for i in range(1, absolute_N + 1):
        if absolute_N % i == 0:
            divisors.append(i)
    
    if N < 0:
        divisors.extend([-i for i in divisors if i != 0])
    
    divisors.sort()
    for divisor in divisors:
        print(divisor, end=" ")