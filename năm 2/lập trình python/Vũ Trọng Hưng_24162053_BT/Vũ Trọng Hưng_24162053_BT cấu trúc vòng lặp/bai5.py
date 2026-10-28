#Vũ Trọng Hưng-24162053
n = int(input("Nhập số đĩa: "))
A, B, C = "A", "B", "C"

if n % 2 == 0:
    B, C = C, B

total_moves = 2**n - 1
pegs = {A: [], B: [], C: []}
for disk in range(n, 0, -1):
    pegs[A].append(disk)

def move(src, dst):
    disk = pegs[src].pop()
    pegs[dst].append(disk)
    print(f"Chuyển đĩa {disk} từ {src} sang {dst}")

for move_num in range(1, total_moves + 1):
    if move_num % 3 == 1:
        src, dst = A, C
    elif move_num % 3 == 2:
        src, dst = A, B
    else:
        src, dst = B, C
    if len(pegs[src]) == 0:
        move(dst, src)
    elif len(pegs[dst]) == 0:
        move(src, dst)
    elif pegs[src][-1] < pegs[dst][-1]:
        move(src, dst)
    else:
        move(dst, src)
