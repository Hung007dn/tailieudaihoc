#Vũ Trọng Hưng-24162053
def NegativeNumberInStrings(s):
    result = []
    num = ""
    
    for ch in s:
        if ch == "-" or ch.isdigit():
            num += ch
        else:
            if num.startswith("-") and len(num) > 1:
                result.append(int(num))
            num = ""
    
    if num.startswith("-") and len(num) > 1:
        result.append(int(num))
    
    return result

print(NegativeNumberInStrings("abc-5xyz-12k9l--p"))
