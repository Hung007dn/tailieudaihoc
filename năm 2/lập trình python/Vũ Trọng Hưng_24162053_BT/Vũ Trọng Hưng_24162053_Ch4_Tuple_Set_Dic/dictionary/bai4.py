
a = input("Nhập danh sách a: ").split()
b = input("Nhập danh sách b: ").split()

if len(a) != len(b):
    print("Hai danh sách phải có cùng số phần tử!")
else:
    mydict = dict(zip(a, b))
    print(mydict)