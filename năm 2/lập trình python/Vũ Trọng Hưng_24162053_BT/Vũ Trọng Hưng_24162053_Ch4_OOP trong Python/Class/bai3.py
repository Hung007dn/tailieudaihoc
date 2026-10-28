#24162035 Trang Sĩ Hoàng
class ToanHoc:
    def __init__(self,*nso):
        self.nso=nso
        
    def tinh_tong(self,*nso):
        return sum(nso)
    def tinh_tb(self,*nso):
        if(len(nso)==0):
            return None
        return sum(nso)/len(nso)
    def tim_max(self,*nso):
        return max(nso)
    def tim_min(self,*nso):
        return min(nso)
    
    def hien_thi(self):
        print("=== THÔNG TIN CÁC SỐ ===")
        print("Các số:", self.nso)
        print("Tổng:", self.tinh_tong(*self.nso))
        print("Trung bình:", self.tinh_tb(*self.nso))
        print("Số lớn nhất:", self.tim_max(*self.nso))
        print("Số nhỏ nhất:", self.tim_min(*self.nso))

th = ToanHoc(3, 7, 2, 9, 5)
th.hien_thi()