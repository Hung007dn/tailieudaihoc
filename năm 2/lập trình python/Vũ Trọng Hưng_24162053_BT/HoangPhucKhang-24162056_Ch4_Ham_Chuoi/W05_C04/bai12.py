#PhucKhang 24162056

def cos_taylor(x):
    term = 1       # số hạng đầu
    cosx = 0
    n = 0
    
    while abs(term) > 1e-10:
        cosx += term
        n += 1
        
        # Tính số hạng tiếp theo
        term = (-1)**n * (x**(2*n)) / math.factorial(2*n)
    
    return cosx
import math
print(cos_taylor(0))
print(cos_taylor(math.pi/3), " ~ ", math.cos(math.pi/3))
