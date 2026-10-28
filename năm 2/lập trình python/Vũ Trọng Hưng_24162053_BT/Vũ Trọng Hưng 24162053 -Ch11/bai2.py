#24162053 Vũ Trọng Hưng
import numpy as np
arr = np.random.uniform(-10, 10, 20)
positive_integers = arr[(arr > 0) & (arr == arr.astype(int))].astype(int)

print("Mảng ban đầu:")
print(arr)

print("\nMảng số nguyên dương:")
print(positive_integers)
