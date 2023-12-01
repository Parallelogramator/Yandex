s = open('k8-10.txt').readline()
global_max = 1
count = 1
for i in range(1, len(s)):
    if s[i-1] != s[i]:
        count += 1
        if count > global_max:
            global_max = count

    else:
        count = 1
print(global_max)
