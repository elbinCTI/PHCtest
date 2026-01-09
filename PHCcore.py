
# ----PHCcore.py-----

import string,random,pickle as P
def enc(a,f):
    gs1=""
    fn=r"{nf}".format(nf=f)
    file=r"{}.dat".format(fn)
    p=1
    cs=list()
    try:
         
         with open(file, mode="rb") as f:
            while True:
                try:
                    y=P.load(f)
                    if y[0]=='ch':
                        pass
                    else:
                        cs.append(y)
                except EOFError:
                    break
    except FileNotFoundError:
        print("File does not exist.")
        return
    for i in a:
        if i==' ':
            gs1+=' '
            continue
        for r in cs:
            if r[0] == i:
                gs1+=r[p]
                p+=1
                break
        if p==95:
            p=1
    return gs1

def dec(a,f):
    gs2=""
    fn=r"{nf}".format(nf=f)
    file=r"{}.dat".format(fn)
    p=1
    cs=list()
    try:
        with open(file, mode="rb") as f:
            while True:
                try:
                    y=P.load(f)
                    if y[0]=='ch':
                        pass
                    else:
                        cs.append(y) 
                except EOFError:
                    break
    except FileNotFoundError:
        print("File does not exist.")
        return
    for i in a:
        if i==' ':
            gs2+=' '
            continue
        for r in cs:
            if r[p] == i:
                gs2+=r[0]
                p+=1
                break
        if p==95:
            p=1
    return gs2

def sheetgen(f):
    fn=r"{nf}".format(nf=f)
    file=r"{}.dat".format(fn)

    h=["ch"] + [str(i) for i in range(1, 96)]
    ch=list((string.ascii_letters + string.digits + string.punctuation).replace(",", ""))
    allch = list((string.ascii_letters + string.digits + string.punctuation).replace(",", ""))
    if len(allch) < len(ch):
        raise ValueError("Not enough unique characters available.")
    rows=[h]

    for c in ch:
        rows.append([c])
    num_columns= len(h)
    num_rows=len(rows)

    for col in range(1, num_columns):
        used = set()
        for r in range(1, num_rows):
            c=random.choice(allch)
            while c in used:
                c=random.choice(allch)
            used.add(c)
            rows[r].append(c)

    with open(file, "wb") as f:
        for i in rows:
            P.dump(i,f)
    print(f"New character set made in '{file}'\n")