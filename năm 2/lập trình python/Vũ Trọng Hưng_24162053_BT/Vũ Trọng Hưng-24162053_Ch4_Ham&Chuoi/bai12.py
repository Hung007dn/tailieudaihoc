#Vũ Trọng Hưng 24162053
def count_words(s):
    words=s.split()
    return len(words)
s=input("Nhập xâu ký tự: ")
print("Số từ trong xâu là:",count_words(s))