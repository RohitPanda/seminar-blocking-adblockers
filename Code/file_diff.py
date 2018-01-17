with open('all', 'r') as file1:
    with open('done', 'r') as file2:
        same = set(file1).difference(file2)

same.discard('\n')
for line in same:
    print(line.strip())
