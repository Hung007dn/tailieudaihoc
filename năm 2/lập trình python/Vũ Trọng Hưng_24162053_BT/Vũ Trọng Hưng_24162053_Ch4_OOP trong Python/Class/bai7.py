
class GiaoDich:
    def __init__(self, ma, ngay, don_gia, so_luong):
        self.ma = ma
        self.ngay = ngay           
        self.don_gia = don_gia
        self.so_luong = so_luong

    def thanh_tien(self):
        return 0  

    def __str__(self):
        return f"{self.ma} | {self.ngay} | SL: {self.so_luong} | ĐG: {self.don_gia}"



class GiaoDichVang(GiaoDich):
    def __init__(self, ma, ngay, don_gia, so_luong, loai_vang):
        super().__init__(ma, ngay, don_gia, so_luong)
        self.loai_vang = loai_vang  

    def thanh_tien(self):
        return self.so_luong * self.don_gia

    def __str__(self):
        return super().__str__() + f" | Vàng: {self.loai_vang} | TT: {self.thanh_tien()}"


class GiaoDichTienTe(GiaoDich):
    def __init__(self, ma, ngay, ty_gia, so_luong, loai_tien, loai_gd):
        super().__init__(ma, ngay, ty_gia, so_luong)
        self.loai_tien = loai_tien  
        self.loai_gd = loai_gd      

    def thanh_tien(self):
        if self.loai_gd.lower() == "mua":
            return self.so_luong * self.don_gia
        else:  # bán
            return self.so_luong * self.don_gia * 1.05

    def __str__(self):
        return (super().__str__() +
                f" | {self.loai_tien} | {self.loai_gd} | TT: {self.thanh_tien()}")



def main():
    ds = []

  
    ds.append(GiaoDichVang("V01", "01/12/2025", 7000000, 2, "24k"))
    ds.append(GiaoDichVang("V02", "01/12/2025", 6800000, 1, "18k"))

    ds.append(GiaoDichTienTe("T01", "01/12/2025", 25000, 100, "USD", "mua"))
    ds.append(GiaoDichTienTe("T02", "01/12/2025", 26000, 50, "EUR", "ban"))

    print("DANH SÁCH GIAO DỊCH:")
    for gd in ds:
        print(gd)

    tong_sl_vang = 0
    tong_sl_tiente = 0

    for gd in ds:
        if isinstance(gd, GiaoDichVang):
            tong_sl_vang += gd.so_luong
        elif isinstance(gd, GiaoDichTienTe):
            tong_sl_tiente += gd.so_luong

    print("\nTổng số lượng vàng:", tong_sl_vang)
    print("Tổng số lượng tiền tệ:", tong_sl_tiente)

    tong_tt_vang = 0
    tong_tt_tiente = 0

    for gd in ds:
        if isinstance(gd, GiaoDichVang):
            tong_tt_vang += gd.thanh_tien()
        elif isinstance(gd, GiaoDichTienTe):
            tong_tt_tiente += gd.thanh_tien()

    print("\nTổng thành tiền vàng:", tong_tt_vang)
    print("Tổng thành tiền tiền tệ:", tong_tt_tiente)

    
    ngay = "01/12/2025"
    tong_ngay = sum(gd.thanh_tien() for gd in ds if gd.ngay == ngay)
    print(f"\nTổng thành tiền ngày {ngay}:", tong_ngay)

if __name__ == "__main__":
    main()
