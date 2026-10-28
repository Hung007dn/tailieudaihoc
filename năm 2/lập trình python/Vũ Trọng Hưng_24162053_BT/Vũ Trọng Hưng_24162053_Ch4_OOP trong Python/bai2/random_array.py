#Vũ Trọng Hưng_24162053
import random

def tao_day_ngau_nhien(n, min_val, max_val):
    if n <= 0:
        return []
    if min_val > max_val:
        min_val, max_val = max_val, min_val
    return [random.randint(min_val, max_val) for _ in range(n)]