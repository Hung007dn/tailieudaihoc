#Vũ Trọng Hưng-24162053
def is_strong_password(pw):
    if len(pw) < 8:
        return False
    
    has_letter = False
    has_digit = False
    has_special = False
    
    for ch in pw:
        if ch.isalpha():
            has_letter = True
        elif ch.isdigit():
            has_digit = True
        else:
            has_special = True
    
    return has_letter and has_digit and has_special

# Test
print(is_strong_password("SPKT1122@"))
print(is_strong_password("123456789"))
