
numbers_list1 = input().split(",")
numbers_tuple1 = tuple(input().split(","))
combined_list = numbers_list1 + list(numbers_tuple1)
combined_tuple = tuple(numbers_list1) + numbers_tuple1
print(combined_list)
print(combined_tuple)

