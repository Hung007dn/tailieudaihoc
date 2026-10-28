#PhucKhang 24162056

def get_filename(path):
    return path.split("\\")[-1]

def get_name_without_ext(path):
    filename = get_filename(path)
    return filename.split(".")[0]

path = "D:\\music\\muabui.mp3"

print(get_filename(path))        # muabui.mp3
print(get_name_without_ext(path)) # muabui
