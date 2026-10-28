
mydict = {}
n = int(input("Nhập số lượng học sinh: "))

for _ in range(n):
    name = input("Nhập tên học sinh: ")
    score = int(input("Nhập điểm (0-10): "))
    mydict[name] = score

stats = {}
for score in mydict.values():
    stats[score] = stats.get(score, 0) + 1

print("Thống kê điểm:")
for score in sorted(stats.keys(), reverse=True):
    print(f"Điểm {score}: {stats[score]} học sinh")