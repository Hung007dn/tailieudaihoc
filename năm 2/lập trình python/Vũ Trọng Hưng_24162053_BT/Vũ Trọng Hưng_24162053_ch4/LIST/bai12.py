# Vũ Trọng Hưng - 24162053
count = 0 
pos =[]
neg =[]
n = int ( input ( " Nhap so phan tu cua mang : " ) )
for i in range ( n ):
    x = int ( input() )
    if x % 2 != 0 :
        neg.append ( x )
    else :
        pos.append ( x )
neg.sort()
pos.sort()
pos.reverse()
print(neg + pos)