#Vũ Trọng Hưng-24162053
import numpy as np
import matplotlib.pyplot as plt


x1 = np.linspace(-3*np.pi, 0, 300)
y1 = 1.5 * np.sin(x1)


x2 = np.linspace(0, 3*np.pi, 300)
y2 = 1.5 * np.sin(x2)


theta = np.linspace(0, 2*np.pi, 800)
r = 2 + np.cos(10*theta) + 2*np.sin(5*theta)
x_polar = r * np.cos(theta)
y_polar = r * np.sin(theta)

plt.figure(figsize=(8, 6))

plt.plot(x1, y1, 'r:', linewidth=3,
         label='y = 1.5sin(x) with x in [-3pi; 0]')

plt.plot(x_polar, y_polar, 'g-', linewidth=2.5,
         label='r = 2 + cos(10*theta) + 2sin(5*theta)')

plt.plot(x2, y2, 'b:', linewidth=3,
         label='y = 1.5sin(x) with x in [0; 3pi]')

plt.axis('equal')             
plt.xlim(-10, 10)
plt.ylim(-6.5, 6.5)

plt.grid(True)
plt.legend(loc='upper center')

plt.xlabel('x')
plt.ylabel('y')

plt.show()
