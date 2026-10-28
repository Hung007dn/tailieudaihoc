#Vũ Trọng Hưng 24162053
import numpy as np
def product(mat_a, mat_b):
    # Tích ma trận
    if mat_a.shape[1] == mat_b.shape[0]:
        print("Tich ma tran:")
        print(np.dot(mat_a, mat_b))
    else:
        print("Khong co tich ma tran")

    # Tích Hadamard
    if mat_a.shape == mat_b.shape:
        print("Tich Hadamard:")
        print(mat_a * mat_b)
    else:
        print("Khong co tich Hadamard")

A = np.array([[1, 2],
              [3, 4]])

B = np.array([[5, 6],
              [7, 8]])

product(A, B)
