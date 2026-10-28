#Vũ Trọng Hưng - 24162053
# Bài 22
n = int(input("Nhập số lượng phần tử: "))
lst = []
for i in range(n):
    item = input(f"Nhập phần tử thứ {i+1}: ")
    try:
        item = float(item)
    except ValueError:
        pass
    lst.append(item)

A = float(input("Nhập số thực A: "))

new_lst = []
for num in lst:
    if isinstance(num, (int, float)) and num <= A:
        new_lst.append(num)
    elif not isinstance(num, (int, float)):
        new_lst.append(num)

print(f"List sau khi xóa phần tử lớn hơn {A}: {new_lst}")