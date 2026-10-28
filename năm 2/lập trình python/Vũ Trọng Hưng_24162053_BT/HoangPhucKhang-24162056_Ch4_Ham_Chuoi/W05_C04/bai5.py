#PhucKhang 24162056
def is_strong_password(password):
    if len(password) < 8:
        return False

    has_lower = False
    has_upper = False
    has_digit = False

    for ch in password:
        if ch.islower():
            has_lower = True
        elif ch.isupper():
            has_upper = True
        elif ch.isdigit():
            has_digit = True

    return has_lower and has_upper and has_digit

pw = input("Nhập mật khẩu: ")

if is_strong_password(pw):
    print("Mật khẩu đạt tính bảo mật cao.")
else:
    print("Mật khẩu KHÔNG đạt tính bảo mật cao.")
