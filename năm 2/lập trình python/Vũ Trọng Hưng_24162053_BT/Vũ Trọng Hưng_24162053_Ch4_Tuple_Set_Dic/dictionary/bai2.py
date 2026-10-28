
my_dict = {}
n = int(input("Nhập vào số n:"))
for i in range(n):
    key = input(f"Nhập key thứ {i+1}: ")
    value = int(input(f"Nhập số cho key '{key}': "))
    my_dict[key] = value
total = sum(my_dict.values())

print("Dictionary vừa tạo:", my_dict)
print("Tổng các số trong dictionary là:", total)






