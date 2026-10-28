A = set(map(int, input("Nhóm A: ").split()))
B = set(map(int, input("Nhóm B: ").split()))
C = set(map(int, input("Nhóm C: ").split()))
D = set(map(int, input("Nhóm D: ").split()))

all_sets = [A, B, C, D]

# 1️⃣ ID xuất hiện đúng trong 2 set
ids_2 = set()
for s1 in all_sets:
    for s2 in all_sets:
        if s1 != s2:
            ids_2 |= s1 & s2
ids_2 -= A & B & C & D
print("ID đúng 2 nhóm:", ids_2)

# 2️⃣ ID chỉ thuộc đúng 1 set và ID phổ biến (>=3 set)
id_count = {}
for s in all_sets:
    for x in s:
        id_count[x] = id_count.get(x, 0) + 1

only_1 = {x for x, c in id_count.items() if c == 1}
common = sum(1 for c in id_count.values() if c >= 3)
print("ID đúng 1 nhóm:", only_1)
print("Số ID phổ biến (>=3 nhóm):", common)

# 3️⃣ Đối xứng A với phần còn lại, loại ID âm
rest = B | C | D
sym = sorted(x for x in A ^ rest if x >= 0)
print("Đối xứng A:", sym)

# 4️⃣ Cập nhật thêm/xóa
nhom = input("Nhóm cần cập nhật (A/B/C/D): ")
id_new = int(input("ID cần thêm/xóa: "))
mode = input("Thêm hay xóa (them/xoa): ")

tap = {"A": A, "B": B, "C": C, "D": D}
if nhom in tap:
    if mode == "them":
        tap[nhom].add(id_new)
    elif mode == "xoa":
        tap[nhom].discard(id_new)
    print(f"{nhom} sau cập nhật:", tap[nhom])