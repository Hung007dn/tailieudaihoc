#Vũ Trọng Hưng 24162053
def replace_col(mat, col_ind):
    result = mat.copy()
    rows = result.shape[0]

    for i in range(rows):
        result[i, col_ind] = 1

    return result
A = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]])

print(replace_col(A, 1))
