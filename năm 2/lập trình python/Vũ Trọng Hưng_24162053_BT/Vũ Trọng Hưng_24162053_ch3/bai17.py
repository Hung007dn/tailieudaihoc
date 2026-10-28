#Vũ Trọng Hưng - 24162053
while True:
    while True:
        try:
            N = int(input("Nhập số nguyên dương N: "))
            if N > 0:
                break
            else:
                print("Vui lòng nhập số nguyên dương!")
        except ValueError:
            print("Vui lòng nhập số nguyên hợp lệ!")
    
    numbers = []
    print(f"Nhập {N} số nguyên:")
    for i in range(N):
        while True:
            try:
                num = int(input(f"Số thứ {i + 1}: "))
                numbers.append(num)
                break
            except ValueError:
                print("Vui lòng nhập số nguyên hợp lệ!")
    
    odd_numbers = [num for num in numbers if num % 2 != 0]
    
    if odd_numbers:
        max_odd = max(odd_numbers)
        print(f"Số lẻ lớn nhất trong các số đã nhập là: {max_odd}")
    else:
        print("Không có số lẻ nào trong các số đã nhập!")
    
    continue_choice = input("\nBạn có muốn tiếp tục không? (Nhấn 'c' để tiếp tục, nhấn phím khác để thoát): ")
    if continue_choice.lower() != 'c':
        print("Chương trình kết thúc!")
        break

