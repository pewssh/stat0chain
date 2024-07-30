
import random
import string

def generate_random_file(filename, size_in_b):
    content = ''.join(random.choices(string.ascii_letters + string.digits, k=size_in_b ))
    with open(filename, 'w') as file:
        file.write(content)


mB_500 = 524288000
mB_800=800000000
mb_200= 209715200
mb_100= 104857600
mB_1=1000000
# kB_500= 512000
# gb_1 = 1073741824
# gb_2 = 2147483648
# gb_5 = 5368709120
# gb_10= 10737418240


for file in [mb_100, mb_200, mB_500, mB_800, mB_800]:
    generate_random_file("dummy{}.txt".format(file), file)
