#Vũ Trọng Hưng - 24162053
n = int(input("Nhập số lượng phần tử: "))
lst = []
for i in range(n):
    item = input(f"Nhập phần tử thứ {i+1}: ")
    try:
        item = int(item)
    except ValueError:
        try:
            item = float(item)
        except ValueError:
            pass
    lst.append(item)

max_divisible = None
for num in lst:
    if isinstance(num, (int, float)) and num % 5 == 0:
        if max_divisible is None or num > max_divisible:
            max_divisible = num

if max_divisible is not None:
    print(f"Phần tử chia hết cho 5 lớn nhất: {max_divisible}")
else:
    print("Không có phần tử nào chia hết cho 5")