#PhucKhang 24162056
def is_reverse(s1, s2):
    # So sánh s2 với phiên bản đảo ngược của s1
    return s2 == s1[::-1]

s1 = input("Nhập xâu thứ nhất: ")
s2 = input("Nhập xâu thứ hai: ")

if is_reverse(s1, s2):
    print("Hai xâu là đảo ngược của nhau.")
else:
    print("Hai xâu KHÔNG phải đảo ngược của nhau.")
