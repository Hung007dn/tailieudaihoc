#24162035 Trang Sĩ Hoàng
import math

class TamGiac:
    def __init__(self,a,b,c,color):
        self.a=a
        self.b=b
        self.c=c
        self.color=color
    
    def isvalid(self):
        return (self.a+self.b>self.c and self.a+self.c>self.b and self.b+self.c >self.a)
    
    def chu_vi(self):
        if not self.isvalid():
            return None
        return self.a+self.b+self.c
    
    def dien_tich(self):
        if not self.isvalid():
            return None
        p=self.chu_vi() / 2
        return math.sqrt(p * (p - self.a) * (p - self.b) * (p - self.c))
    
    def loai_tam_giac(self):
        if not self.isvalid():
            return "Không phải tam giác" 
        
        a,b,c=sorted([self.a,self.b,self.c])
        vuong=a*a + b*b == c*c
        can=(self.a==self.b or self.b==self.c or self.a==self.c)
        deu=(self.a==self.b==self.c)
        
        if deu:
            return "Tam giác đều"
        elif vuong and can:
            return "Tam giác vuông cân"
        elif vuong:
            return "Tam giác vuông"
        elif can:
            return "Tam giác cân"
        else:
            return "Tam giác thường"
        
    def hien_thi(self):
        print("===Thông tin tam giác===")
        print(f"Cạnh a:{self.a}")
        print(f"Cạnh b:{self.b}")
        print(f"Cạnh c:{self.c}")
        print(f"Màu sắc:{self.color}")
        
        if self.isvalid():
            print(f"Chu vi:{self.chu_vi()}")
            print(f"Diện tích:{self.dien_tich()}")
            print(f"Loại tam giác:{self.loai_tam_giac()}")
        else:
            print("Ba cạnh không tạo thành tam giác")

tg = TamGiac(3, 4, 5, "Xanh")
tg.hien_thi()
        
        