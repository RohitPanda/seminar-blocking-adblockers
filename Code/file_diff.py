with open('site_dot_de.txt', 'r') as file1:
    with open('1.txt', 'r') as file2:
        same = set(file1).difference(file2)

same.discard('\n')
for line in same:
    print(line.strip())
