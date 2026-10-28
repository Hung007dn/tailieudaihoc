#PhucKhang 24162056

def capitalize_words(s):
    s = s.lower()
    parts = s.split()
    result = []
    
    for w in parts:
        if len(w) > 0:
            w = w[0].upper() + w[1:]
        result.append(w)
    
    return " ".join(result)

print(capitalize_words("nGuyeN hiEu NGhiA"))
