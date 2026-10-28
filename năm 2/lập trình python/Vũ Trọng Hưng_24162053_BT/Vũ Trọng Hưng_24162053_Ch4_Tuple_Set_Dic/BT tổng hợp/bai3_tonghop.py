
time_minutes = {}

while True:
    print("\n==== Menu ====")
    print("1. Nhập thêm thời gian")
    print("2. Thống kê các hoạt động (giờ)")
    print("3. Xem 2 hoạt động nhiều nhất & 2 hoạt động ít nhất")
    print("0. Thoát")

    choice = input("Chọn chức năng: ").strip()

    if choice == "1":
        name = input("Nhập tên hoạt động: ").strip().lower()
        try:
            minutes = int(input("Nhập số phút: ").strip())
            if minutes < 0:
                print("Số phút không được âm. Vui lòng nhập lại!")
                continue
        except ValueError:
            print("Số phút phải là số nguyên.")
            continue

        time_minutes[name] = time_minutes.get(name, 0) + minutes
        print(f"Đã cộng dồn: {name} = {time_minutes[name]} phút")

    elif choice == "2":
        if not time_minutes:
            print("Chưa có dữ liệu.")
            continue

        print("\nThống kê thời gian hoạt động (giờ):")
        for name, mins in time_minutes.items():
            hours = mins / 60
            print(f"{name}: {hours:.1f} giờ")

    elif choice == "3":
        if not time_minutes:
            print("Chưa có dữ liệu.")
            continue

        items_sorted = sorted(time_minutes.items(), key=lambda x: x[1])  # tăng dần theo phút

        least = items_sorted[:2]                 # 2 ít nhất
        most = items_sorted[-2:][::-1]           # 2 nhiều nhất (đảo để giảm dần)

        print("\n2 hoạt động ít thời gian nhất:")
        for name, mins in least:
            print(f"{name}: {mins/60:.1f} giờ")

        print("\n2 hoạt động nhiều thời gian nhất:")
        for name, mins in most:
            print(f"{name}: {mins/60:.1f} giờ")

    elif choice == "0":
        print("Thoát chương trình.")
        break

    else:
        print("Lựa chọn không hợp lệ. Vui lòng chọn lại")
