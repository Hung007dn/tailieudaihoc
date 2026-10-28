# Vũ Trọng Hưng - 24162053
import math

def is_prime(n):
    if n < 2: return False
    if n % 2 == 0: return n == 2
    for i in range(3, int(math.isqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

s = input("Nhập các số: ")
tokens = s.split()
a = []
for t in tokens:
    a.append(int(t))

primes = []
for x in a:
    if is_prime(x):
        primes.append(x)

print("Các số nguyên tố trong list:", primes)