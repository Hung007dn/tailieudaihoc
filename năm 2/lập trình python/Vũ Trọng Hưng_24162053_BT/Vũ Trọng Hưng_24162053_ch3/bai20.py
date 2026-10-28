#Vũ Trọng Hưng - 24162053
n = int(input("Nhập số nguyên dương n: "))

s1 = 0
for i in range(1, n + 1):
    s1 += 1 / (i * (i + 1))
print(f"S1 = {s1}")

s2 = 0
for i in range(n + 1):
    s2 += (2 * i + 1) / (2 * i + 2)
print(f"S2 = {s2}")
