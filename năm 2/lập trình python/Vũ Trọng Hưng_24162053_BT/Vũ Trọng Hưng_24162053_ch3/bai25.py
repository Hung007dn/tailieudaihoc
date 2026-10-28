#Vũ Trọng Hưng_24162053
x=float(input("Nhập số: "))
if x==0:
    print(0.0)
else:
    guess=x/2
    while abs((guess*guess)-x)>1e-12:
        guess=(guess+x/guess)/2
    print(guess)