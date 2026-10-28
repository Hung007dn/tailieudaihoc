#Vũ Trọng Hưng-24162053
n = int(input("Nhập số n: "))
hang_tram = n // 100
hang_chuc = (n // 10) % 10
hang_don_vi = n % 10
trung_binh = (hang_tram + hang_chuc + hang_don_vi) / 3
print(f"{trung_binh:.2f}")