
import random
import string

def generate_random_file(filename, size_in_kb):
    content = ''.join(random.choices(string.ascii_letters + string.digits, k=size_in_kb ))
    with open(filename, 'w') as file:
        file.write(content)


mB_500 = 524288000
mB_800=800000000
mb_200= 209715200
mb_100= 104857600
mB_1=1000000
kB_500= 512000

for file in [kB_500, mB_1, mb_100, mb_200, mB_500, mB_800]:
    generate_random_file("file{}.txt".format(file), file)
