#Vũ Trọng Hưng-24162053
n = int(input("Nhập số n: "))
hang_chuc_nghin = n // 10000
hang_nghin = (n // 1000) % 10
hang_tram = (n // 100) % 10
hang_chuc = (n // 10) % 10
hang_don_vi = n % 10
tong = hang_chuc_nghin + hang_nghin + hang_tram + hang_chuc + hang_don_vi
nut = tong % 10
print(nut)