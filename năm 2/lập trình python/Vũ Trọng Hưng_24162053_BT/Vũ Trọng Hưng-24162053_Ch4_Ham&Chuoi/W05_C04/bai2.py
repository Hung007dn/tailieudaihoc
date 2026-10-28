#Vũ Trọng Hưng-24162053
def median(a, b, c):
   
    lst = [a, b, c]
    lst.sort()
    return lst[1]

def main():
    print("Nhập 3 số để tính trung vị:")
    x = float(input("Nhập số thứ 1: "))
    y = float(input("Nhập số thứ 2: "))
    z = float(input("Nhập số thứ 3: "))

    result = median(x, y, z)
    print("Trung vị là:", result)

main()
