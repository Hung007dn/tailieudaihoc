#PhucKhang 24162056
def binary_to_decimal(b):
    dec = 0
    power = 0
    for digit in b[::-1]:
        dec += int(digit) * (2 ** power)
        power += 1
    return dec


def hex_to_decimal(h):
    dec = 0
    power = 0
    hex_digits = "0123456789ABCDEF"
    h = h.upper()

    for digit in h[::-1]:
        value = hex_digits.index(digit)
        dec += value * (16 ** power)
        power += 1

    return dec


def decimal_to_binary(d):
    if d == 0:
        return "0"
    result = ""
    while d > 0:
        result = str(d % 2) + result
        d //= 2
    return result


def decimal_to_hex(d):
    if d == 0:
        return "0"
    hex_digits = "0123456789ABCDEF"
    result = ""
    while d > 0:
        result = hex_digits[d % 16] + result
        d //= 16
    return result


print("Chương trình chuyển đổi hệ số (KHÔNG dùng hàm có sẵn)")
base = int(input("Nhập hệ của số (2, 10, 16): "))
value = input("Nhập giá trị: ")

if base == 2:
    dec = binary_to_decimal(value)
    print("→ Hệ 10:", dec)
    print("→ Hệ 16:", decimal_to_hex(dec))

elif base == 10:
    dec = int(value)
    print("→ Hệ 2:", decimal_to_binary(dec))
    print("→ Hệ 16:", decimal_to_hex(dec))

elif base == 16:
    dec = hex_to_decimal(value)
    print("→ Hệ 2:", decimal_to_binary(dec))
    print("→ Hệ 10:", dec)

else:
    print("Hệ bạn nhập không được hỗ trợ.")
