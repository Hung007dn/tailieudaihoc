x = [0.4]  # key
r = 3.81111   # key

for i in range(1, 200):
    x.append(r * x[i - 1] * (1 - x[i - 1]))  # x(n) = r * x(n-1) * (1 - x(n-1))
    print(f"x[{i}] = {x[i]:.16f}")
