#Vũ Trọng Hưng-24162053
def is_prime(number):
    if number < 2:
        return False
    
    for i in range(2, int(number ** 0.5) + 1):
        if number % i == 0:
            return False
    
    return True

def nextPrime(n):
    candidate = n + 1
    
    while True:
        if is_prime(candidate):
            return candidate
        candidate += 1

def main():
    print("CHƯƠNG TRÌNH TÌM SỐ NGUYÊN TỐ TIẾP THEO")
    print("=" * 40)
    
    try:
        n = int(input("Nhập một số nguyên: "))
        
        next_prime = nextPrime(n)
        
        print(f"\nSố đã nhập: {n}")
        print(f"Số nguyên tố đầu tiên lớn hơn {n} là: {next_prime}")
            
    except ValueError:
        print("Lỗi: Vui lòng nhập số nguyên hợp lệ!")

if __name__ == "__main__":
    main()