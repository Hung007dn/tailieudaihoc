#PhucKhang 24162056
s = "An eye for an eye makes the whole world blind – Mahatma Gandhi"

s = s.lower()
words = s.split()

freq = {}
for w in words:
    if w not in freq:
        freq[w] = 1
    else:
        freq[w] += 1

print(freq)
