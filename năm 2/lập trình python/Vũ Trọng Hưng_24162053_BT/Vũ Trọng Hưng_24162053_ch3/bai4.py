#Vũ Trọng Hưng_24162053
Diem_LT=float(input("Nhập điểm Lý Thuyết: "))
Diem_TH=float(input("Nhập điểm Thực Hành: "))

while Diem_LT<0 or Diem_LT>10 and Diem_TH<0 or Diem_TH>10:
    print("Điểm không hợp lệ. Vui lòng nhập lại.")
    Diem_LT=float(input("Nhập điểm Lý Thuyết: "))
    Diem_TH=float(input("Nhập điểm Thực Hành: "))
else:
    Diem_TB=(Diem_LT+Diem_TH)/2
    print("Điểm Trung Bình là: ",Diem_TB)