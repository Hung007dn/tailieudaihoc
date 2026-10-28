#24162053 Vũ Trọng Hưng
import numpy as np

def combine_rooms(room_1, room_2):
    result = []

    for i in range(len(room_1)):
        if room_1[i] > 0:
            result.append(room_1[i])
        elif room_2[i] > 0:
            result.append(room_2[i])
        else:
            result.append(None)

    return np.array(result, dtype=object)


# =========================
# Ví dụ kiểm tra
# =========================
room_1 = np.array([1, 2, -3, 4, 5, 6, -7])
room_2 = np.array([8, 9, 10, 11, 12, -13, -14])

final_list = combine_rooms(room_1, room_2)

print("Danh sách thí sinh cuối cùng:")
print(final_list)
