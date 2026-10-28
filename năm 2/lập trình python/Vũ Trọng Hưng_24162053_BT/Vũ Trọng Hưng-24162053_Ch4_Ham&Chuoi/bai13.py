#Vũ Trọng Hưng-24162053
def is_reverse(s1, s2):
  
    return s2 == s1[::-1]

s1 = input("Nhập xâu thứ nhất: ")
s2 = input("Nhập xâu thứ hai: ")

if is_reverse(s1, s2):
    print("Hai xâu là đảo ngược của nhau.")
else:
    print("Hai xâu KHÔNG phải đảo ngược của nhau.")
