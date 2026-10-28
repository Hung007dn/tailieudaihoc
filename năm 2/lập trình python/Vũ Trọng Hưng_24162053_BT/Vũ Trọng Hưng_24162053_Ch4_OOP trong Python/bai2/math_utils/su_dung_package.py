from math_utils import giai_pt_bac_2, sap_xep_tang, sap_xep_giam

print(" SỬ DỤNG PACKAGE MATH_UTILS ")

ket_qua = giai_pt_bac_2(1, -5, 6)
print(f"1. Giải PT x² - 5x + 6 = 0: {ket_qua}")

arr = [5, 2, 8, 1, 9]
tang = sap_xep_tang(arr)
giam = sap_xep_giam(arr)
print(f"2. Mảng: {arr}")
print(f"   Tăng dần: {tang}")
print(f"   Giảm dần: {giam}")