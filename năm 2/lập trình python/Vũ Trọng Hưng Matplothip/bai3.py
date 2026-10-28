#Vũ Trọng Hưng-24162053
import matplotlib.pyplot as plt

# Dữ liệu
categories = ['A', 'B', 'C', 'D']
values = [10, 25, 15, 30]

# Vẽ biểu đồ cột
plt.bar(categories, values, color='skyblue')

plt.xlabel('Category')
plt.ylabel('Value')
plt.title('Simple Bar Chart')
plt.grid(axis='y')

plt.show()
