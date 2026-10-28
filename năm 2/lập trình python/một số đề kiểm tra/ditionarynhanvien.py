nv = {}
n = int(input())
for _ in range(n):
    ma = input()
    ten = input()
    pb = input()
    basic = int(input())
    bonus = int(input())
    total = basic + bonus
    ca = int(input())
    nv[ma] = {
        "name": ten,
        "department": pb,
        "salary": {"basic": basic, "bonus": bonus, "total": total},
        "shift_count": ca
    }

for v in nv.values():
    s = v["salary"]
    v["avg_salary"] = (s["basic"] + s["bonus"]) / 2

ds = [v for v in nv.values() if v["salary"]["bonus"] > v["salary"]["basic"] and v["shift_count"] > 5]
ds.sort(key=lambda x: x["avg_salary"], reverse=True)
for v in ds:
    print(v["name"], v["avg_salary"])

ma = input("Mã NV cần cập nhật: ")
new_ca = int(input("Số ca mới: "))
if ma in nv:
    nv[ma]["shift_count"] = new_ca
    if new_ca > 20:
        print("Cảnh báo: overtime")