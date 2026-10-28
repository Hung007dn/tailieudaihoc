#Vũ Trọng Hưng_24162053
nam = int(input("Nhập vào một năm: "))

if nam % 400 == 0:
    print("Năm nhuận")
elif nam % 100 == 0:
    print("Không phải năm nhuận")
elif nam % 4 == 0:
    print("Năm nhuận")
else:
    print("Không phải năm nhuận")