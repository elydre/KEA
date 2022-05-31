'''    _             _
  ___ | | _   _   __| | _ __   ___
 / _ \| || | | | / _` || '__| / _ |
|  __/| || |_| || (_| || |   |  __/
 \___||_| \__, | \__,_||_|    \___|
          |___/
___________________________________

 - codé en : UTF-8
 - langage : python3
 - GitHub  : github.com/elydre
 - Licence : GNU GPL v3
'''

# simple shell :         python3 main.py
# debug shell :          python3 main.py -d
# execute file :         python3 main.py -f <file>
# execute file & debug : python3 main.py -df <file>

import os

from sys import argv

import kea.kea as kea
import mod.tools as tools
from kstream.decoupeur import Decoupeur, StatusDisplay

debug = "d" in argv[1] if len(argv) > 1 else False
fmode = "f" in argv[1] if len(argv) > 1 else False

cp = StatusDisplay(not debug)

kea.start(f"D {'on' if debug else 'off'}")

print("loading dependencies...")

for d in os.listdir("./ks_dep"):
    ks = tools.read_file(f"./ks_dep/{d}")
    kea.start(ks, 0)
    print(f" - {d} loaded")

def alias(code):
    liste_alias = tools.read_file("./ks_alias.txt").split("\n")
    for e in liste_alias:
        if "=" not in e:
            continue
        alias = e.split("=")
        if alias[0] in code:
            code = code.replace(alias[0], alias[1])
            if debug: print(f" - {alias[0]} replaced by {alias[1]}")

    return code

while not fmode:
    code = []
    while not code or code[-1] != "":
        cp.colorprint("KS", "37" if code else "36", end="")
        code.append(input(" ~ "))
    
    tools.clear_last_line()

    try:    
        sortie = Decoupeur(alias("\n".join(code)), debug, not debug).start()

        if sortie != 0:
            parsed = "\n".join([" ".join(k) for k in sortie])

            kea.start(parsed, 0)
    except Exception as e:
        print(e, "\n")

if fmode:
    kea.start("\n".join([" ".join(k) for k in Decoupeur(alias(tools.read_file(argv[2])), debug, not debug).start()]), 0)