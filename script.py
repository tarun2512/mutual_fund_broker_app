# nums = [2, 1, 2, 4, 3]
nums = [2, 5, 7, 4, 10]
# output = [4, 2, 4, -1, -1]

output = []
for index in range(len(nums) - 1):
    num = nums[index]
    next_greater = -1
    for i in range(index + 1, len(nums)):
        current_num = nums[i]
        if current_num > num:
            next_greater = current_num
            break
    output.append(next_greater)
output.append(-1)

print(output)


# Next greater element
