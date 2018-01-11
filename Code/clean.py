lines_seen = set()

outfile = open("negative_samples.txt", "w")
with open('Anti-Adblock.txt') as file:
  content= file.readlines()
  for lines in content:
    line = lines.lower().rstrip().rstrip('//')
    if line not in lines_seen:
        outfile.write(line + '\n')
        lines_seen.add(line)
outfile.close()
