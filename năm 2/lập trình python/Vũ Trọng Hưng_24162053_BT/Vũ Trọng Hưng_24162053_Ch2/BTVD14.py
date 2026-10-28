#Vũ Trọng Hưng_24162053
a = int(input("Nhập vào số a: "))
b = int(input("Nhập vào số b: "))
c = int(input("Nhập vào số c: "))

so_chan_lon_nhat = None

if a % 2 == 0:
    so_chan_lon_nhat = a
if b % 2 == 0:
    if so_chan_lon_nhat is None or b > so_chan_lon_nhat:
        so_chan_lon_nhat = b
if c % 2 == 0:
    if so_chan_lon_nhat is None or c > so_chan_lon_nhat:
        so_chan_lon_nhat = c

if so_chan_lon_nhat is None:
    print("Không có số chẵn")
else:
    print(so_chan_lon_nhat)