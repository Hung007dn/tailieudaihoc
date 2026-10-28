#PhucKhang 24162056
import random

def random_strong_password(length=10):
    pw = ""
    while True:
        pw = ""
        for _ in range(length):
            pw += chr(random.randint(33, 126))  # từ ! đến ~
        if (any(c.isalpha() for c in pw)
            and any(c.isdigit() for c in pw)
            and any(not c.isalnum() for c in pw)):
            return pw

print(random_strong_password())
