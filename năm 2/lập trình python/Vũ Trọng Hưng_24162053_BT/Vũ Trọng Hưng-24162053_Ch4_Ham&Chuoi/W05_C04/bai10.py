#Vũ Trọng Hưng-24162053
def loc_toc_do(toc_do_list, min_value):
    toc_do_nho = []
    indices = []
    
    for i, toc_do in enumerate(toc_do_list):
        if toc_do < min_value:
            toc_do_nho.append(toc_do)
            indices.append(i)
    
    return toc_do_nho, indices

def main():
    print("CHƯƠNG TRÌNH LỌC TỐC ĐỘ QUAY")
    print("=" * 40)
    
    try:
        n = int(input("Nhập số lượng tốc độ quay: "))
        
        if n <= 0:
            print("Lỗi: Số lượng phải lớn hơn 0!")
            return
        
        toc_do_list = []
        for i in range(n):
            toc_do = int(input(f"Nhập tốc độ quay thứ {i+1}: "))
            toc_do_list.append(toc_do)
        
        min_value = int(input("Nhập giá trị min để lọc: "))
        
        toc_do_nho, indices = loc_toc_do(toc_do_list, min_value)
        
        print(f"\nDanh sách tốc độ ban đầu: {toc_do_list}")
        print(f"Giá trị min: {min_value}")
        print(f"Tốc độ nhỏ hơn min: {toc_do_nho}")
        print(f"Vị trí (indices) của các tốc độ này: {indices}")
        
    except ValueError:
        print("Lỗi: Vui lòng nhập số nguyên hợp lệ!")

if __name__ == "__main__":
    main()