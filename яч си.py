import sys

skr = {}

n = sys.stdin.readlines()

for line in n:
    ls = line.split()
    ln = ls[-1]
    if len(ls) == 0:
        break
    else:
        if ln in skr.keys():
            skr[ln].add(str(''.join(ls[:-1])))
        else:
            skr[ln] = set(ls[:-1])

skr = dict(sorted(skr.items()))
for i in skr.keys():
    print(f'{i}: {", ".join(skr[i])}')
