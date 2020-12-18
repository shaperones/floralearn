with open("determinant.txt", encoding="UTF-8") as fin:
    txt = fin.read().split("\n")

this = {}
prethis = {}
i = 0
print(len(txt))
while i < len(txt):
    prethis[int(txt[i])] = (txt[i + 1], txt[i + 2])
    i += 3

g = {}
txt = {}
for ind, item in prethis.items():
    if item[0].count(":") != 1 or item[1].count(":") != 1:
        print("achtung!")
    # assert item[0].count(":") == 1
    s1 = item[0].split(":")[-1]
    s2 = item[1].split(":")[-1]
    g[ind] = ((s1, ":".join(item[0].split(":")[:-1])), (s2, ":".join(item[1].split(":")[:-1])))


def scan(index):
    ret = {}
    if not g[index][0][0].isdigit():
        ret[g[index][0][1]] = {
            "__id__": "end_node",
            "name": g[index][0][0]
        }
    else:
        ret[g[index][0][1]] = scan(int(g[index][0][0]))
    if not g[index][1][0].isdigit():
        ret[g[index][1][1]] = {
            "__id__": "end_node",
            "name": g[index][1][0]
        }
    else:
        ret[g[index][1][1]] = scan(int(g[index][1][0]))
    return ret


this = scan(1)

print("ok)")


import json
with open("floralearn/db.json", "wt") as fout:
    fout.write(json.dumps(this))

