from abc import ABC, abstractmethod
import math

class Hinh(ABC):

    @abstractmethod
    def chu_vi(self):
        pass

    @abstractmethod
    def dien_tich(self):
        pass


class HinhTron(Hinh):
    def __init__(self, r):
        self.r = r

    def chu_vi(self):
        return 2 * math.pi * self.r

    def dien_tich(self):
        return math.pi * self.r ** 2


class HinhChuNhat(Hinh):
    def __init__(self, dai, rong):
        self.dai = dai
        self.rong = rong

    def chu_vi(self):
        return 2 * (self.dai + self.rong)

    def dien_tich(self):
        return self.dai * self.rong


class HinhTamGiac(Hinh):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def chu_vi(self):
        return self.a + self.b + self.c

    def dien_tich(self):
        p = self.chu_vi() / 2
        return math.sqrt(p * (p - self.a) * (p - self.b) * (p - self.c))


# Test chương trình
ht = HinhTron(5)
hcn = HinhChuNhat(4, 6)
htg = HinhTamGiac(3, 4, 5)

print("Hinh tron:")
print("Chu vi:", ht.chu_vi())
print("Dien tich:", ht.dien_tich())

print("\nHinh chu nhat:")
print("Chu vi:", hcn.chu_vi())
print("Dien tich:", hcn.dien_tich())

print("\nHinh tam giac:")
print("Chu vi:", htg.chu_vi())
print("Dien tich:", htg.dien_tich())
