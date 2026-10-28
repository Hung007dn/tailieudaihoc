#Vũ Trọng Hưng-24162053

def cos_taylor(x):
    term = 1       
    cosx = 0
    n = 0
    
    while abs(term) > 1e-10:
        cosx += term
        n += 1
        
        
        term = (-1)**n * (x**(2*n)) / math.factorial(2*n)
    
    return cosx
import math
print(cos_taylor(0))
print(cos_taylor(math.pi/3), " ~ ", math.cos(math.pi/3))
