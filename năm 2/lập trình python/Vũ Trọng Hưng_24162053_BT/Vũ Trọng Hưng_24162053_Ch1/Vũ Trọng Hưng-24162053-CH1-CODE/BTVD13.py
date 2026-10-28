import math

giatri_x = [math.pi, math.pi/2, (4*math.pi)/3]
for x in giatri_x:
    ket_qua = math.sin(x)**2 + math.cos(x)**2
    print(f"x = {x:.2f}: {ket_qua == 1} (giá trị = {ket_qua})")