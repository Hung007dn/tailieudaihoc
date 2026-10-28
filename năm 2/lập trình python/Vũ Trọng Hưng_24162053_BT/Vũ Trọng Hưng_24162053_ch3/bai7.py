#Vũ Trọng Hưng_24162053
Thu=int(input("Nhập thứ trong tuần: "))
while Thu<1 or Thu>7:
    Thu=int(input("Vui lòng nhập lại thứ trong tuần (từ 1 đến 7): "))
else:
    if(Thu==1):
        print("Thứ Hai là Monday ")
    elif(Thu==2):
        print("Thứ Ba là Tuesday")
    elif(Thu==3):
        print("Thứ Tư là Wednesday")
    elif(Thu==4):
        print("Thứ Năm là Thursday")
    elif(Thu==5):
        print("Thứ Sáu là Friday")
    elif(Thu==6):
        print("Thứ Bảy là Saturday")
    else:
        print("Chủ Nhật là Sunday")