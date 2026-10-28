#Vũ Trọng Hưng_24162053
from random_array import tao_day_ngau_nhien
from math_utils import giai_pt_bac_2, sap_xep_tang, sap_xep_giam

def main():
    print("=== BÀI 2: TỔNG HỢP TẤT CẢ CHỨC NĂNG ===")
    
    print("\n1. Tạo dãy số ngẫu nhiên:")
    day_so = tao_day_ngau_nhien(8, 10, 50)
    print(f"   {day_so}")
    
    print("\n2. Giải phương trình bậc 2:")
    pt1 = giai_pt_bac_2(1, -3, 2)
    print(f"   x² - 3x + 2 = 0 → {pt1}")
    
    pt2 = giai_pt_bac_2(1, 2, 5)
    print(f"   x² + 2x + 5 = 0 → {pt2}")
    
    print("\n3. Sắp xếp mảng:")
    arr = [34, 7, 23, 32, 5, 62]
    print(f"   Mảng gốc: {arr}")
    print(f"   Tăng dần: {sap_xep_tang(arr)}")
    print(f"   Giảm dần: {sap_xep_giam(arr)}")

if __name__ == "__main__":
    main()