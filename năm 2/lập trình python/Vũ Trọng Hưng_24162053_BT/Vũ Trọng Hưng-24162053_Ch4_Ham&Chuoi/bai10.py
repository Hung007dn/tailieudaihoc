#Vũ Trọng Hưng 24162053
def most_freq_char(s):
    freq={}
    for ch in s:
        if ch not in freq:
            freq[ch]=1
        else:
            freq[ch]+=1
    max_count=max(freq.values())
    most_chars=[]
    for ch,count in freq.items():
        if count==max_count:
            most_chars.append(ch)
    return most_chars,max_count

s=input("Nhập xâu: ")
chars,count=most_freq_char(s)
print("Ký tự xuất hiện nhiều nhất:",', '.join(chars))
print("Số lần xuất hiện:",count)