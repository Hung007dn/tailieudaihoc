#Vũ Trọng Hưng_24162053
month=int(input("Nhập tháng (1-12): "))
while month<1 or month>12:
    month=int(input("Tháng không hợp lệ. Vui lòng nhập lại tháng (1-12): "))
else:   
    if(month==1 or month==3 or month==5):
        print("Tháng",month,"là mùa xuân")
    elif(month==6 or month==7 or month==8):
        print("Tháng",month,"là mùa hạ")
    elif(month==9 or month==10 or month==11):
        print("Tháng",month,"là mùa thu")
    else:
        print("Tháng",month,"là mùa đông")
    