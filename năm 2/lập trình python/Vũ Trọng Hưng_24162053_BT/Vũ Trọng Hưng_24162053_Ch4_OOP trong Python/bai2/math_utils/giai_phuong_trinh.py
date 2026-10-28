#Vũ Trọng Hưng_24162053
import math

def giai_pt_bac_2(a, b, c):
    if a == 0:
        if b == 0:
            if c == 0:
                return "Vô số nghiệm"
            return "Vô nghiệm"
        x = -c / b
        return f"x = {x}"
    
    delta = b**2 - 4*a*c
    
    if delta < 0:
        return "Vô nghiệm"
    elif delta == 0:
        x = -b / (2*a)
        return f"x = {x}"
    else:
        x1 = (-b + math.sqrt(delta)) / (2*a)
        x2 = (-b - math.sqrt(delta)) / (2*a)
        return f"x1 = {x1:.2f}, x2 = {x2:.2f}"