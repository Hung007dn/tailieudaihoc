n,m=map(int,input().split())
a=[list(map(int,input().split())) for _ in range(n)]

def nhom(lst):
    res=[]
    for i in range(len(lst)):
        s=set();tong=0
        for j in range(i,len(lst)):
            if lst[j] in s:break
            s.add(lst[j]);tong+=lst[j]
            res.append((i,j,tong,len(s)))
    return res

best=None
for i in range(n):
    for b in nhom(a[i]):
        if not best or b[3]>best[3] or (b[3]==best[3] and b[2]>best[2]):
            best=(b[0],b[1],b[2],b[3],'row',i)

for j in range(m):
    col=[a[i][j] for i in range(n)]
    for b in nhom(col):
        if not best or b[3]>best[3] or (b[3]==best[3] and b[2]>best[2]):
            best=(b[0],b[1],b[2],b[3],'col',j)

if best[4]=='row':
    print((best[5],best[0]),(best[5],best[1]),best[2],best[3])
else:
    print((best[0],best[5]),(best[1],best[5]),best[2],best[3])