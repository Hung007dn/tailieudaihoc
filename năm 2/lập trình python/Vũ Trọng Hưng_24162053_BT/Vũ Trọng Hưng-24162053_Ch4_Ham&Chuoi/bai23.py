#Vũ Trọng Hưng-24162053

email = input("Nhập địa chỉ email: ")


if email.count("@") != 1:
    print("Email không hợp lệ!")
else:
  
    a, rest = email.split("@")

   
    if "." not in rest:
        print("Email không hợp lệ!")
    else:
        parts = rest.split(".")

    
        if len(parts) < 2:
            print("Email không hợp lệ!")
        else:
            b = parts[0]
            c = parts[1]

            if a == "" or b == "" or c == "":
                print("Email không hợp lệ!")
            else:
                print("Email hợp lệ!")
