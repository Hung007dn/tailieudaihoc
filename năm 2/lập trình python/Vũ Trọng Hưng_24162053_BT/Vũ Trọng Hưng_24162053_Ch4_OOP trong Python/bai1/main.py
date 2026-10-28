#Vũ Trọng Hưng_24162053
from sinhvien import SinhVienManager

def hien_thi_menu():
    print("\n" + "="*50)
    print("CHƯƠNG TRÌNH QUẢN LÝ SINH VIÊN")
    print("="*50)
    print("1. Thêm sinh viên")
    print("2. Xóa sinh viên")
    print("3. Sửa sinh viên")
    print("4. Xem danh sách sinh viên")
    print("5. Tìm sinh viên")
    print("6. Thoát chương trình")
    print("="*50)

def main():
    ql_sv = SinhVienManager()
    
    print(" CHƯƠNG TRÌNH QUẢN LÝ SINH VIÊN ")
    
    while True:
        hien_thi_menu()
        lua_chon = input(" Nhập lựa chọn (1-6): ").strip()
        
        if lua_chon == "1":
            print("\n" + "="*30)
            print("THÊM SINH VIÊN MỚI")
            print("="*30)
            ma_sv = input("Nhập mã sinh viên: ")
            ten_sv = input("Nhập tên sinh viên: ")
            thanh_cong, thong_bao = ql_sv.them_sinh_vien(ma_sv, ten_sv)
            print(thong_bao)
        
        elif lua_chon == "2":
            print("\n" + "="*30)
            print("XÓA SINH VIÊN")
            print("="*30)
            ma_sv = input("Nhập mã sinh viên cần xóa: ")
            sv_can_xoa = ql_sv.tim_sinh_vien(ma_sv)
            if sv_can_xoa:
                print(f"Tìm thấy: {sv_can_xoa['ma']} - {sv_can_xoa['ten']}")
                xac_nhan = input("Bạn có chắc chắn muốn xóa? (y/n): ").lower()
                if xac_nhan == 'y':
                    thanh_cong, thong_bao = ql_sv.xoa_sinh_vien(ma_sv)
                    print(thong_bao)
                else:
                    print("  Đã hủy thao tác xóa")
            else:
                print(f" Không tìm thấy sinh viên với mã: {ma_sv}")
        
        elif lua_chon == "3":
            print("\n" + "="*30)
            print("SỬA THÔNG TIN SINH VIÊN")
            print("="*30)
            ma_sv = input("Nhập mã sinh viên cần sửa: ")
            sv_can_sua = ql_sv.tim_sinh_vien(ma_sv)
            if sv_can_sua:
                print(f"Sinh viên hiện tại: {sv_can_sua['ma']} - {sv_can_sua['ten']}")
                ten_moi = input("Nhập tên mới: ")
                thanh_cong, thong_bao = ql_sv.sua_sinh_vien(ma_sv, ten_moi)
                print(thong_bao)
            else:
                print(f" Không tìm thấy sinh viên với mã: {ma_sv}")
        
        elif lua_chon == "4":
            print("\n" + "="*50)
            print("DANH SÁCH SINH VIÊN")
            print("="*50)
            danh_sach = ql_sv.xem_danh_sach()
            so_luong = ql_sv.so_luong()
            if so_luong == 0:
                print(" Danh sách sinh viên trống!")
            else:
                print(f" Tổng số: {so_luong} sinh viên")
                print("-"*50)
                for i, sv in enumerate(danh_sach, 1):
                    print(f"{i:3}. {sv['ma']:15} - {sv['ten']}")
                print("-"*50)
        
        elif lua_chon == "5":
            print("\n" + "="*30)
            print("TÌM SINH VIÊN")
            print("="*30)
            ma_sv = input("Nhập mã sinh viên cần tìm: ")
            sv = ql_sv.tim_sinh_vien(ma_sv)
            if sv:
                print(f" Tìm thấy sinh viên:")
                print(f"   Mã: {sv['ma']}")
                print(f"   Tên: {sv['ten']}")
            else:
                print(f" Không tìm thấy sinh viên với mã: {ma_sv}")
        
        elif lua_chon == "6":
            print("\n" + "="*50)
            print("TỔNG KẾT")
            print("="*50)
            print(f" Tổng số sinh viên: {ql_sv.so_luong()}")
            print(" Cảm ơn bạn đã sử dụng chương trình!")
            print("="*50)
            break
        
        else:
            print(" Lựa chọn không hợp lệ! Vui lòng chọn từ 1 đến 6")
        
        input("\n⏎ Nhấn Enter để tiếp tục...")

if __name__ == "__main__":
    main()