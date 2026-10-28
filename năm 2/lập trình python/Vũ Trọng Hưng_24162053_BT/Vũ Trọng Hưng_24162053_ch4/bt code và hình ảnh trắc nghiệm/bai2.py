#Trang Sĩ Hoàng 24162035
n=int(input("Nhập n phần tử số thực: "))
a=[]
tong=0
trung_binh=0
count=0
for i in range(n):
    x=int(input("Enter: "))
    a.append(x)
    if(x%2!=0):
        tong+=x
        count+=1
trung_binh=tong/count
print(trung_binh)
