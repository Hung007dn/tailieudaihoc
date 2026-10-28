#Vũ Trọng Hưng 24162053
import numpy as np

def transpose(mat):
    rows, cols = mat.shape
    result = np.zeros((cols, rows))

    for i in range(rows):
        for j in range(cols):
            result[j, i] = mat[i, j]

    return result
A = np.array([[1, 2],
              [3, 4],
              [5, 6]])

print(transpose(A))
