#PhucKhang 24162056

email = input("Nhập địa chỉ email: ")

# Kiểm tra có đúng 1 dấu @
if email.count("@") != 1:
    print("Email không hợp lệ!")
else:
    # Tách thành phần trước và sau @
    a, rest = email.split("@")

    # rest phải có dạng b.c
    if "." not in rest:
        print("Email không hợp lệ!")
    else:
        parts = rest.split(".")

        # Cần b và c, và c phải khác rỗng
        if len(parts) < 2:
            print("Email không hợp lệ!")
        else:
            b = parts[0]
            c = parts[1]

            # Kiểm tra a, b, c có rỗng không
            if a == "" or b == "" or c == "":
                print("Email không hợp lệ!")
            else:
                print("Email hợp lệ!")
