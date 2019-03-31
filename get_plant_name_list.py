import re

with open('常见植物名录.txt', 'r') as f:
    data = f.read()

# print(data.split('\n'))
name_list = data.split('\n')
flag = 0
plant_name = []
for i in name_list:
    # print(i)
    if '．' in i:
        name = i.split('．')[1].split('（')[0].strip()
        # print(flag, name)
        plant_name.append(name)
        flag += 1
print(plant_name)