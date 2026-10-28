import math

class HinhTron:
    def __init__(self, ban_kinh):
        self.ban_kinh = ban_kinh

    def tinh_chu_vi(self):
        return 2 * math.pi * self.ban_kinh

    def tinh_dien_tich(self):
        return math.pi * (self.ban_kinh ** 2)

    def hien_thi_thong_tin(self):
        print(f"Hình tròn có bán kính: {self.ban_kinh}")
        print(f"Chu vi: {self.tinh_chu_vi():.2f}")
        print(f"Diện tích: {self.tinh_dien_tich():.2f}")



ban_kinh = float(input("Nhập bán kính hình tròn: "))
hinh_tron = HinhTron(ban_kinh)
hinh_tron.hien_thi_thong_tin()