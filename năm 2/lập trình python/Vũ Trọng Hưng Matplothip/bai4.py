#Vũ Trọng Hưng-24162053
import numpy as np
import matplotlib.pyplot as plt

# Dữ liệu ngẫu nhiên
data = np.random.randn(1000)

# Vẽ histogram
plt.hist(data, bins=30, color='orange', edgecolor='black')

plt.xlabel('Value')
plt.ylabel('Frequency')
plt.title('Histogram Example')
plt.grid(True)

plt.show()
