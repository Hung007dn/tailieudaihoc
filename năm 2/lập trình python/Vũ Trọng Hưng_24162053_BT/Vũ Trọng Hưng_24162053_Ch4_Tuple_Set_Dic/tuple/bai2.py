
data = []
while True:
    entry = input()
    if not entry:
        break
    parts = entry.split(",")
    data.append((parts[0], int(parts[1]), int(parts[2])))
data.sort(key=lambda x: (x[0], x[1], x[2]))
print(data)