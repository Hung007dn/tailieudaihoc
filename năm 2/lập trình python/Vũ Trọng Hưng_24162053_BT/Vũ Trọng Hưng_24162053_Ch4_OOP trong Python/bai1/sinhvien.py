#Vũ Trọng Hưng_24162053
class SinhVienManager:
    def __init__(self):
        self.danh_sach = []
    
    def them_sinh_vien(self, ma_sv, ten_sv):
        if not ma_sv.strip() or not ten_sv.strip():
            return False, "Mã và tên không được để trống"
        
        for sv in self.danh_sach:
            if sv['ma'] == ma_sv:
                return False, f"Mã {ma_sv} đã tồn tại"
        
        sv_moi = {'ma': ma_sv, 'ten': ten_sv}
        self.danh_sach.append(sv_moi)
        return True, f" Thêm thành công: {ma_sv} - {ten_sv}"
    
    def xoa_sinh_vien(self, ma_sv):
        for i, sv in enumerate(self.danh_sach):
            if sv['ma'] == ma_sv:
                sv_xoa = self.danh_sach.pop(i)
                return True, f" Đã xóa: {sv_xoa['ma']} - {sv_xoa['ten']}"
        return False, f"❌ Không tìm thấy sinh viên mã {ma_sv}"
    
    def sua_sinh_vien(self, ma_sv, ten_moi):
        for sv in self.danh_sach:
            if sv['ma'] == ma_sv:
                if not ten_moi.strip():
                    return False, "Tên mới không được để trống"
                ten_cu = sv['ten']
                sv['ten'] = ten_moi
                return True, f" Đã sửa {ma_sv}: '{ten_cu}' → '{ten_moi}'"
        return False, f" Không tìm thấy sinh viên mã {ma_sv}"
    
    def xem_danh_sach(self):
        return self.danh_sach.copy()
    
    def tim_sinh_vien(self, ma_sv):
        for sv in self.danh_sach:
            if sv['ma'] == ma_sv:
                return sv.copy()
        return None
    
    def so_luong(self):
        return len(self.danh_sach)