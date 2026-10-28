#Trang Sĩ Hoàng 24162035
n=int(input("Nhập n: "))
a=[]
lst_a=[]#chan
lst_b=[]#le
for i in range(n):
    x=int(input("Enter: "))
    a.append(x)
    if(x%2==0):
        lst_a.append(x)
    else:
        lst_b.append(x)
        
print(lst_a)
print(lst_b)
