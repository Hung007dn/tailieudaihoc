import math
class Diem:
    def __init__(self,x=0,y=0,color="Trắng"):
        self.x=x
        self.y=y
        self.color=color
    
    def hien_thi(self):
        print(f"Diem({self.x},{self.y}), Mau sac: {self.color}")
    
    #C tịnh tiến theo trục hoành OX
    def tinh_tien(self,dx,dy=None):
        #d  Hàm tịnh tiến(int x,int y)
        if dy is None:
            self.x+=dx
        else:
            self.x+=dx
            self.y+=dy
    # e. Hàm KhoangCach(): khoảng cách tới gốc O(0,0)
    
    def khoang_cach_goc(self):
        return math.sqrt(self.x**2 +self.y**2)
    
    def khoang_cach(self,d):
        return math.sqrt((self.x - d.x)**2 + (self.y - d.y)**2)

# Tạo hai điểm
d1 = Diem(3, 4, "Do")
d2 = Diem(1, 1, "Xanh")

# Hiển thị
d1.hien_thi()
d2.hien_thi()

# Tịnh tiến theo Ox
d1.tinh_tien(2)
d1.hien_thi()

# Tịnh tiến theo Ox và Oy
d1.tinh_tien(1, -3)
d1.hien_thi()

# Khoảng cách tới gốc tọa độ
print("Khoang cach d1 toi O:", d1.khoang_cach_goc())

# Khoảng cách giữa hai điểm
print("Khoang cach d1 va d2:", d1.khoang_cach(d2))
