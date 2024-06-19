
import random
import string

def generate_random_file(filename, size_in_kb):
    content = ''.join(random.choices(string.ascii_letters + string.digits, k=size_in_kb * 1024))
    with open(filename, 'w') as file:
        file.write(content)


    mB_500 = 524288000
    mb_100= 104857600
    GB_1= 1073741824
    kB_500= 512000
    for file in [kB_500, mB_500, mb_100]:
        generate_random_file("file{}.txt".format(file), file)