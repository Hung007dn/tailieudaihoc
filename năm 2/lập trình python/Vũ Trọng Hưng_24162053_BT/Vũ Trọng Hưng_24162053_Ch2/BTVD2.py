n = float(input("Nhập vào số n:"))

if n == 0.0:
    print("Unacceptable Performance")
    print("Tiền thưởng: $0")
elif n == 0.4:
    print("Acceptable Performance")
    print("Tiền thưởng: $", 2400 * n)
elif n >= 0.6:
    print("Meritorious Performance")
    print("Tiền thưởng: $", 2400 * n)
else:
    print("vui lòng nhập lại")