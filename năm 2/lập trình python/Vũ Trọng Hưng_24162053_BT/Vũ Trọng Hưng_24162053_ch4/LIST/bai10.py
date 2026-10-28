# Vũ Trọng Hưng - 24162053
n = int(input("Nhập số lượng phần tử n (n ≥ 0): "))
lst = []
for i in range(n):
    x = float(input(f"Nhập phần tử thứ {i+1}: "))
    lst.append(x)
negative_numbers = [x for x in lst if x < 0]
negative_numbers.sort(reverse=True)
print("Các phần tử âm sau khi sắp xếp giảm dần:")
print(negative_numbers)