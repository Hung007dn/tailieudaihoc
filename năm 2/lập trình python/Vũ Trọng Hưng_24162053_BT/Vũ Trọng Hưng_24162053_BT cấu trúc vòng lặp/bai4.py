#Vũ Trọng Hưng-24162053
def sum_ma_tran(ma_tran):
    tong=0
    for hang in ma_tran:
        for phan_tu in hang:
            tong+=phan_tu
    return tong
n=int(input('Nhap vao so nguyen n '))
ma_tran=[]
for i in range(n):
    hang_hien_tai=[]
    for j in range(n):
        phan_tu=int(input(f"Nhap phan tu A[{i}][{j}]"))
        hang_hien_tai.append(phan_tu)
    ma_tran.append(hang_hien_tai)
    
ket_qua=sum_ma_tran(ma_tran)
print(f"ket qua = {ket_qua}")