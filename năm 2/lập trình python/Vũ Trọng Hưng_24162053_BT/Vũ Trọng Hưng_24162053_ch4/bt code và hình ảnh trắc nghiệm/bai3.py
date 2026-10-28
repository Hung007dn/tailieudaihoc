# Vũ Trọng Hưng - 24162053
n = int(input("Nhập số lượng phần tử n: "))

a = []
for i in range(n):
    i = int(input("Enter: "))
    a.append(i)

index = -1
for i in range(n):
    if a[i] < 0:
        index = i
        break
if index == -1:
    print("Không có phần tử âm trong list.")
else:
    print(f"Vị trí phần tử âm đầu tiên: {index}")
