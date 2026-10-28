#PhucKhang 24162056

# Bảng mã tỉnh (rút gọn – có thể thêm vào)
province_codes = {
    "079": "TP. Hồ Chí Minh",
    "001": "Hà Nội",
    "031": "Hải Phòng",
    "048": "Đà Nẵng",
    "056": "Khánh Hòa",
    "092": "Cần Thơ"
}

cccd = input("Nhập CCCD: ")

# --- Kiểm tra hợp lệ ---
if not cccd.isdigit() or len(cccd) != 12:
    print("CCCD không hợp lệ!")
else:
    # --- Phân tích thông tin ---
    province = cccd[:3]
    gender_code = int(cccd[3])
    year = int(cccd[4:6])

    # --- Tỉnh ---
    province_name = province_codes.get(province, "Không rõ tỉnh")

    # --- Giới tính ---
    if gender_code <= 4:
        gender = "Nam"
        year += 1900
    else:
        gender = "Nữ"
        year += 1900  # hoặc 2000 tùy theo batch – đề không nêu rõ

    # --- Xuất thông tin ---
    print("CCCD hợp lệ!")
    print("Tỉnh:", province_name)
    print("Giới tính:", gender)
    print("Năm sinh:", year)
