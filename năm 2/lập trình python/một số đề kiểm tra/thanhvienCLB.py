tt = set(input("Thể thao: ").split())
nt = set(input("Nghệ thuật: ").split())
kh = set(input("Khoa học: ").split())

print("Số lượng:", len(tt), len(nt), len(kh))

ca3 = tt & nt & kh
print("Cả 3 CLB:", ca3)

dung2 = (tt & nt | tt & kh | nt & kh) - ca3
print("Đúng 2 CLB:", dung2)

chi_tt = tt - nt - kh
chi_nt = nt - tt - kh
chi_kh = kh - tt - nt
print("Chỉ TT:", chi_tt)
print("Chỉ NT:", chi_nt)
print("Chỉ KH:", chi_kh)

clb = input("Thêm vào CLB nào (tt/nt/kh): ")
ma = input("Mã thành viên mới: ")
tap = {"tt": tt, "nt": nt, "kh": kh}
if ma in tap[clb]:
    print("Đã tồn tại")
else:
    tap[clb].add(ma)
    print("Đã thêm:", tap[clb])