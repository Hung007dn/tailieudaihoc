#Vũ Trọng Hưng 24162053
import numpy as np

def broadcast(vec, n):
    m = len(vec)
    result = np.zeros((m, n))

    for i in range(m):
        for j in range(n):
            result[i, j] = vec[i]

    return result

vec = np.array([6, 7])
n = 3

print(broadcast(vec, n))
