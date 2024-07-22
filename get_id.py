def main():
    data = []
    with open('blobbers.txt', 'r') as file:
        for line in file:
            if 'url:' in line:
                line = line.replace("url:","")
                data.append(line.strip() + "\n")
    with open ('blobbers.txt', 'w') as file:

        file.writelines(sorted(data))


main()