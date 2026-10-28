# Vũ Trọng Hưng - 24162053
nhiet_do_trong_tuan=[]
so_ngay=7
for i in range(so_ngay):
    x=int(input(f'nhap vao nhiet do ngay {i+1} :'))
    nhiet_do_trong_tuan.append(x)
sum=0
for i in nhiet_do_trong_tuan:
    sum+=i
avg=sum/7
dem=0
for i in nhiet_do_trong_tuan:
    if i>avg:
        dem+=1
print (dem)
