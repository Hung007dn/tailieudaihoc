from collections import defaultdict

sp = {}
n = int(input())
for _ in range(n):
    ma = input()
    ten = input()
    loai = input()
    retail = float(input())
    wholesale = float(input())
    discount = float(input())
    ton = int(input())
    sp[ma] = {
        "name": ten,
        "category": loai,
        "prices": {"retail": retail, "wholesale": wholesale, "discount": discount},
        "inventory": ton
    }

for v in sp.values():
    p = v["prices"]
    tong = p["retail"] + p["wholesale"]
    if p["discount"] > p["wholesale"]:
        tong += p["discount"] * 0.8
    v["total_price"] = tong
    v["potential_profit"] = tong * v["inventory"]

cat_map = defaultdict(list)
for ma, v in sp.items():
    cat_map[v["category"]].append((ma, v["name"], v["potential_profit"], v["inventory"]))

for cat, ds in cat_map.items():
    ds.sort(key=lambda x: (-x[2], -x[3]))
    for ma, ten, loi, _ in ds[:3]:
        print(ma, ten, round(loi,2))

ma = input()
if ma in sp:
    loai = input()
    if loai in sp[ma]["prices"]:
        gia_moi = float(input())
        ban = int(input())
        if ban <= sp[ma]["inventory"]:
            sp[ma]["prices"][loai] = gia_moi
            sp[ma]["inventory"] -= ban
            p = sp[ma]["prices"]
            tong = p["retail"] + p["wholesale"]
            if p["discount"] > p["wholesale"]:
                tong += p["discount"] * 0.8
            sp[ma]["total_price"] = tong
            sp[ma]["potential_profit"] = tong * sp[ma]["inventory"]

for cat in sorted(cat_map):
    ds = cat_map[cat]
    ds.sort(key=lambda x: -x[2])
    for ma, ten, loi, ton in ds:
        print(cat, ma, ten, round(loi,2), ton)