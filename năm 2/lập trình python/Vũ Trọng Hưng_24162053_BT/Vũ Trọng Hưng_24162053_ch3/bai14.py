#Vũ Trọng Hưng_24162053
import math
x = float(input("Enter the first x-coordinate: "))
y = float(input("Enter the first y-coordinate: "))
first_x=x
first_y=y
prev_x=x
prev_y=y
tong_cv=0
while True:
    next_x=input("Enter the next x-coordinate (blank to quit): ")
    if next_x=="":
        break
    
    next_y=input("Enter the next y-coordinate: ")
    next_x=float(next_x)
    next_y=float(next_y)
    
    d=math.sqrt((next_x-prev_x)**2 + (next_y-prev_y)**2)
    tong_cv+=d
    
    #cap nhat diem hien tai thanh prev
    prev_x=next_x
    prev_y=next_y
    
#Khoang cach diem cuoi quay ve diem dau
d= math.sqrt((prev_x-first_x)**2 + (prev_y-first_y)**2)
tong_cv+=d

print("The perimeter of that polygon is", tong_cv)