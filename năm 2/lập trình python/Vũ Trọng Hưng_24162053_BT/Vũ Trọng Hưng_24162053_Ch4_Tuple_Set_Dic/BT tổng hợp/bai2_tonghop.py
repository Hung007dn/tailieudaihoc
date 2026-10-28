
s=input("Nhập 1 câu: ")
freq={}
for ch in s:
    if ch.isalpha():
        if ch in freq:
            freq[ch]+=1
        else:
            freq[ch]=1

for ch, count in freq.items():
    print(f"Số lần xuất hiện của từ '{ch}': {count} ")