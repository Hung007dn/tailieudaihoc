#Vũ Trọng Hưng-24162053

import math

def giai_pt_bac_hai(a, b, c):
    if a == 0:           
        if b == 0:
            return []   
        return [-c / b] 

    delta = b*b - 4*a*c

    if delta < 0:
        return []      
    elif delta == 0:
        return [-b / (2*a)]
    else:
        x1 = (-b + math.sqrt(delta)) / (2*a)
        x2 = (-b - math.sqrt(delta)) / (2*a)
        return [x1, x2]

print(giai_pt_bac_hai(1, -3, 2))   
print(giai_pt_bac_hai(1, 2, 1))    
print(giai_pt_bac_hai(1, 1, 5))    
