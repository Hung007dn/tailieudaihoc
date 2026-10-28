#Vũ Trọng Hưng_24162053
while True:
    n=input("Nhập số nguyên dương: ")
    if n.isdigit() and int(n)>0:
        break
    else:
        print("Vui lòng nhập số nguyên dương.")

tong=0
for ch in n:
    tong+=int(ch)
    
print("Tổng các chữ số là:",tong)