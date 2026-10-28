#Vũ Trọng Hưng-24162053
def check_energy(kwh):
    if kwh < 10:
        print("Thiết bị tiết kiệm điện.")
    else:
        print("Thiết bị KHÔNG tiết kiệm điện.")

energy = float(input("Nhập điện năng tiêu thụ mỗi ngày (kWh): "))
check_energy(energy)
