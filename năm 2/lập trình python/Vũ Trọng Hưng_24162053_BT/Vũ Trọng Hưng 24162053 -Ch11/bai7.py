#Vũ Trọng Hưng 24162053
import numpy as np
sales=np.random.randint(10,100,size=(2,7))
days=["Thứ 2","Thứ 3","Thứ 4","Thứ 5","Thứ 6","Thứ 7","Chủ Nhật"]
sessions=["Sáng","Chiều"]

print("Bảng số lượng hàng bán ra:")
print("         ",days)
print("Sáng    :",sales[0])
print("Chiều:",sales[1])

#a
max_total=0
best_day=0
for j in range(7):
    total=sales[0][j]+sales[1][j]
    if total>max_total:
        max_total=total
        best_day=j

print("\na) Ngày bán được nhiều hàng nhất:", days[best_day])
print("Tổng số hàng:", max_total)

# =========================
# b. Thời điểm bán được nhiều nhất (buổi + ngày)
# =========================
max_sale = sales[0][0]
best_session = 0
best_day2 = 0

for i in range(2):          # duyệt buổi
    for j in range(7):      # duyệt ngày
        if sales[i][j] > max_sale:
            max_sale = sales[i][j]
            best_session = i
            best_day2 = j

print("\nb) Thời điểm bán được nhiều nhất:")
print("Buổi:", sessions[best_session], "- Ngày:", days[best_day2])
print("Số hàng:", max_sale)

# =========================
# c. Buổi nào bán nhiều hơn
# =========================
morning_more = 0
afternoon_more = 0

for j in range(7):
    if sales[0][j] > sales[1][j]:
        morning_more += 1
    elif sales[0][j] < sales[1][j]:
        afternoon_more += 1

print("\nc) Kết luận:")
if morning_more > afternoon_more:
    print("Buổi sáng bán được nhiều hàng hơn")
elif morning_more < afternoon_more:
    print("Buổi chiều bán được nhiều hàng hơn")
else:
    print("Hai buổi bán tương đương nhau")