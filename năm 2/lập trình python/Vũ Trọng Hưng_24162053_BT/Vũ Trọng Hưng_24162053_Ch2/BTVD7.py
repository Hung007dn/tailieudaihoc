#Vũ Trọng Hưng_24162053
import math

year = int(input("Nhập vào một năm: "))

day_of_the_week = (year + math.floor((year - 1) / 4) - math.floor((year - 1) / 100) + math.floor((year - 1) / 400)) % 7

thu_dict = {
    0: "Chủ nhật",
    1: "Thứ hai", 
    2: "Thứ ba",
    3: "Thứ tư",
    4: "Thứ năm",
    5: "Thứ sáu",
    6: "Thứ bảy"
}

print(f"Ngày 1/1/{year} là {thu_dict[day_of_the_week]}")