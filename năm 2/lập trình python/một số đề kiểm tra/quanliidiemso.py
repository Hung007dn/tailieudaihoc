lop = []
n = int(input("Nhập số lớp: "))

for _ in range(n):
    ds = []
    m = int(input("Số học sinh trong lớp: "))
    
    for _ in range(m):
        ten = input("Tên học sinh: ")
        tuoi = int(input("Tuổi: "))
        
        diem = {}
        mon = int(input("Số môn: "))
        
        for _ in range(mon):
            ten_mon = input("Tên môn: ")
            diem_mon = list(map(float, input("3 cột điểm: ").split()))
            
            if len(diem_mon) != 3 or any(d < 0 for d in diem_mon):
                print("Lỗi dữ liệu – bỏ qua môn này")
                continue
                
            diem[ten_mon] = diem_mon
        
        ds.append((ten, tuoi, diem))
    lop.append(ds)


# ==== TÍNH TẤT CẢ ĐIỂM TRUNG BÌNH ====

def diem_tb_mon(d):
    return d[0]*0.3 + d[1]*0.4 + d[2]*0.3

all_hs = []
for ds in lop:
    for ten, tuoi, diem in ds:
        if len(diem) == 0:
            tb = 0
        else:
            tb = sum(diem_tb_mon(d) for d in diem.values()) / len(diem)
        
        all_hs.append((ten, tuoi, tb))


# ==== TÌM HỌC SINH XUẤT SẮC MỖI LỚP ====

for i, ds in enumerate(lop):
    def score(hs):
        ten, tuoi, diem = hs
        if len(diem) == 0:
            return -999
        tb = sum(diem_tb_mon(d) for d in diem.values()) / len(diem)
        return tb - tuoi * 0.01   # trừ tuổi theo logic của bạn

    xuat_sac = max(ds, key=score)
    print(f"Lớp {i+1} xuất sắc:", xuat_sac[0])


# ==== ĐẾM HS TB > 8.0 ====
print("Số HS TB > 8.0:", sum(tb > 8.0 for _, _, tb in all_hs))


# ==== SẮP XẾP TẤT CẢ HỌC SINH ====

all_hs.sort(key=lambda x: (-x[2], x[0], x[1]))

for hs in all_hs:
    print(hs)
