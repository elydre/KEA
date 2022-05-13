import os

import kea.kea as kea
import mod.tools as tools
from kstream.decoupeur import Decoupeur, StatusDisplay

# debug mode
debug = 1
alias_debug = 1

cp = StatusDisplay(not debug)

kea.start("D on" if debug else "D off")

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
            if not alias_debug: continue
            print(f" - {alias[0]} replaced by {alias[1]}")
    return code

while True:
    code = []
    while not code or code[-1] != "":
        cp.colorprint("KS", "37" if code else "36", end="")
        code.append(input(" ~ "))
    
    tools.clear_last_line()
    
    sortie = Decoupeur(alias("\n".join(code)), debug, not debug).start()

    if sortie != 0:
        parsed = "\n".join([" ".join(k) for k in sortie])

        kea.start(parsed, 0)