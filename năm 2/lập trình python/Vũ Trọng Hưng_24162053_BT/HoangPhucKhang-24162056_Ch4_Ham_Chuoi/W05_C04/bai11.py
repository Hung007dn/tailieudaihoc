#PhucKhang 24162056

import math

def giai_pt_bac_hai(a, b, c):
    if a == 0:           # Phương trình bậc nhất
        if b == 0:
            return []   # vô nghiệm
        return [-c / b] # nghiệm bậc nhất

    delta = b*b - 4*a*c

    if delta < 0:
        return []       # vô nghiệm
    elif delta == 0:
        return [-b / (2*a)]
    else:
        x1 = (-b + math.sqrt(delta)) / (2*a)
        x2 = (-b - math.sqrt(delta)) / (2*a)
        return [x1, x2]

# Test
print(giai_pt_bac_hai(1, -3, 2))   # [2, 1]
print(giai_pt_bac_hai(1, 2, 1))    # [-1]
print(giai_pt_bac_hai(1, 1, 5))    # []
