#Vũ Trọng Hưng-24162053
def tinh_so_sao(dien_nang):
    if dien_nang < 2:
        return 5
    elif dien_nang < 4:
        return 4
    elif dien_nang < 6:
        return 3
    elif dien_nang < 10:
        return 2
    else:
        return 1

def kiem_tra_tiet_kiem_dien(dien_nang):
    so_sao = tinh_so_sao(dien_nang)
    
    if so_sao < 3:
        return False
    else:
        return True

def main():
    print("CHƯƠNG TRÌNH KIỂM TRA TIẾT KIỆM ĐIỆN")
    print("=" * 40)
    
    try:
        dien_nang = float(input("Nhập điện năng tiêu thụ mỗi ngày (kWh): "))
        
        if dien_nang < 0:
            print("Lỗi: Điện năng không thể âm!")
            return
        
        so_sao = tinh_so_sao(dien_nang)
        
        print(f"\nĐiện năng tiêu thụ: {dien_nang} kWh/ngày")
        print(f"Số sao tiết kiệm năng lượng: {so_sao} sao")
        
        if kiem_tra_tiet_kiem_dien(dien_nang):
            print("Thiết bị CÓ tiết kiệm điện!")
        else:
            print("Thiết bị KHÔNG tiết kiệm điện!")
        
    except ValueError:
        print("Lỗi: Vui lòng nhập số hợp lệ!")

if __name__ == "__main__":
    main()