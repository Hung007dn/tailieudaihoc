#Vũ Trọng Hưng-24162053
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Tạo lưới
x = np.linspace(-5, 5, 100)
y = np.linspace(-5, 5, 100)
X, Y = np.meshgrid(x, y)

# Tính Z
Z = np.sqrt(1 + 0.3*X**2 + 0.3*Y**2)

# Vẽ
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

surf1 = ax.plot_surface(X, Y, Z,
                         cmap='jet',
                         vmin=-5, vmax=5)

surf2 = ax.plot_surface(X, Y, -Z,
                         cmap='jet',
                         vmin=-5, vmax=5)

# Thanh màu
fig.colorbar(surf1)

ax.set_title('Hyperboloid')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('f(x,y)')

plt.show()
