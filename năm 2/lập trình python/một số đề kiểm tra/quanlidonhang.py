#Quản lý đơn hàng khách hàng
from collections import defaultdict
from datetime import datetime

n=int(input());dh=[]
for _ in range(n):
    mk=input();ng=input();ct={};s=int(input())
    for _ in range(s):sp=input();sl=int(input());ct[sp]=sl
    if not ct:print("Cảnh báo");continue
    dh.append((mk,ng,ct))

tsl=defaultdict(int)
for mk,_,ct in dh:
    for sl in ct.values():tsl[mk]+=sl
for mk,t in tsl.items():print(mk,t)

dl=defaultdict(list)
for mk,ng,ct in dh:
    if sum(ct.values())>=10:dl[mk].append((ng,ct))
for mk in dl:
    dl[mk].sort(key=lambda x:datetime.strptime(x[0],"%Y-%m-%d"))
    for ng,ct in dl[mk]:print(mk,ng,ct)

print(len(dh))
print(max(tsl.items(),key=lambda x:x[1]))