#PhucKhang 24162056
BASE_FARE = 4.0
FARE_PER_140M = 0.25

def calculate_taxi_fare(distance_km):
    distance_m = distance_km * 1000
    num_140m_units = distance_m / 140
    total_fare = BASE_FARE + (num_140m_units * FARE_PER_140M)
    return total_fare

def main():
    print("CHƯƠNG TRÌNH TÍNH GIÁ TAXI")
    print("=" * 30)
    
    try:
        distance = float(input("Nhập quãng đường di chuyển (km): "))
        
        if distance < 0:
            print("Lỗi: Quãng đường không thể âm!")
            return
        
        fare = calculate_taxi_fare(distance)
        
        print(f"\nQuãng đường: {distance} km")
        print(f"Chi phí cơ sở: ${BASE_FARE:.2f}")
        print(f"Phụ phí di chuyển: ${(fare - BASE_FARE):.2f}")
        print(f"Tổng giá tiền: ${fare:.2f} USD")
        
    except ValueError:
        print("Lỗi: Vui lòng nhập số hợp lệ!")

if __name__ == "__main__":
    main()