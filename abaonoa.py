f = open('24.txt', mode='r', encoding='utf-8')
S = f.readline().strip()
data = []
for i in range(len(S)):
    if S[i] == 'AB':
        data.append([i, S[i]])
print(data)
