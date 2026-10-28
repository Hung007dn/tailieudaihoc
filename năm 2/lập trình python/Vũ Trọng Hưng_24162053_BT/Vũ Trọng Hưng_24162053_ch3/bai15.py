#Vũ Trọng Hưng_24162053
while True:
    binary=input("Nhập 1 chuỗi 8 bit nhị phân (nhập khoảng trắng để dừng): ")
    
    if binary==" ":
        print("Kết thúc")
        break
    
    length=len(binary)
    if length>8:
        print("Không được nhập chuỗi lớn hơn 8 bit")
        continue
    
    count=0
    for i in binary:
        if i=='1':
            count+=1
    mode = input("Bạn muốn tính parity chẵn hay lẻ(evan or odd)? : ").lower()
    if mode=="evan":
        if count%2==0:
            parity=0
        else:
            parity=1
    elif mode=="odd":
        if count%2!=0:
            parity=0
        else:
            parity=1
    else:
        print("Lựa chọn không hợp lệ!")
        continue
    
    print("Bit parity =", parity)
    print("Chuỗi truyền đi:", binary, parity)
    print("----------------------------")