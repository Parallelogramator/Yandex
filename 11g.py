A = []

def f(i):
    binn = bin(i)[2:]
    strn = str(binn)
    if len(bin(i % 3)[2:]) == 2:
        binost1 = str(bin(i % 3)[2:])
    else:
        return False
    strn = strn + binost1
    if len(bin(int(strn, 2) % 5)[2:]) == 3:
        binost2 = str(bin(int(strn, 2) % 5)[2:])
    else:
        return False
    strn = strn + binost2

    return int(strn, 2)


for i in range(1111111110, 1444444417):
    if f(i):
        print(i)
        A.append(i)
print(len(A))