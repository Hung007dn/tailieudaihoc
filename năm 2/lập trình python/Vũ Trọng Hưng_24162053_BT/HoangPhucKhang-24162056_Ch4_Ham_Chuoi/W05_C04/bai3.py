#PhucKhang 24162056
def is_prime(number):
    if number < 2:
        return False
    
    for i in range(2, int(number ** 0.5) + 1):
        if number % i == 0:
            return False
    
    return True

def main():
    print("CHƯƠNG TRÌNH KIỂM TRA SỐ NGUYÊN TỐ")
    print("=" * 35)
    
    try:
        n = int(input("Nhập một số nguyên: "))
        
        if is_prime(n):
            print(f"\n{n} LÀ số nguyên tố")
        else:
            print(f"\n{n} KHÔNG PHẢI là số nguyên tố")
            
    except ValueError:
        print("Lỗi: Vui lòng nhập số nguyên hợp lệ!")

if __name__ == "__main__":
    main()