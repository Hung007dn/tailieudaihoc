#Vũ Trọng Hưng 24162053
import numpy as np
import matplotlib.pyplot as plt
 
x = np.linspace(-6, 4, 500)
y = 3*x**5 + 20*x**4 - 10*x**3 - 240*x**2 - 250*x + 200

plt.figure(figsize=(8, 5))
plt.plot(x, y, 'r-.', linewidth=3)

plt.title("Fifth Degree Polynomial")
plt.xlabel("x")
plt.ylabel("y")

plt.xlim(-6, 4)
plt.ylim(-1200, 400)

plt.grid(False)

plt.show()
