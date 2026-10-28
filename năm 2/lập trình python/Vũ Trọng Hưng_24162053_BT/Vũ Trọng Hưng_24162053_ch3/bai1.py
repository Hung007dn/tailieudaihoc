#Vũ Trọng Hưng - 24162053
n = int(input("Nhập một số nguyên dương có 5 chữ số: "))
while n < 10000 or n > 99999:
    n = int(input("Vui lòng nhập lại n (5 chữ số): "))

count_chan = 0
count_le = 0

while n > 0:
    digit = n % 10   # Lấy chữ số cuối
    if digit % 2 == 0:
        count_chan += 1
    else:
        count_le += 1
    n //= 10          # Bỏ chữ số cuối

print("Số chữ số chẵn là:", count_chan)
print("Số chữ số lẻ là:", count_le)
