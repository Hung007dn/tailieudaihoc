#Vũ Trọng Hưng-24162053


province_codes = {
    "079": "TP. Hồ Chí Minh",
    "001": "Hà Nội",
    "031": "Hải Phòng",
    "048": "Đà Nẵng",
    "056": "Khánh Hòa",
    "092": "Cần Thơ"
}

cccd = input("Nhập CCCD: ")


if not cccd.isdigit() or len(cccd) != 12:
    print("CCCD không hợp lệ!")
else:
 
    province = cccd[:3]
    gender_code = int(cccd[3])
    year = int(cccd[4:6])

    
    province_name = province_codes.get(province, "Không rõ tỉnh")


    if gender_code <= 4:
        gender = "Nam"
        year += 1900
    else:
        gender = "Nữ"
        year += 1900  

  
    print("CCCD hợp lệ!")
    print("Tỉnh:", province_name)
    print("Giới tính:", gender)
    print("Năm sinh:", year)
