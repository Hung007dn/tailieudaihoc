#Vũ Trọng Hưng_24162053
result=""
q=int(input("Nhập số thập phân: "))
while q>0:
    r=q%2
    r=str(r)
    result=r+result
    q//=2
    
print("Số nhị phân là:",result)

