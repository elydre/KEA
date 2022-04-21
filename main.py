import kea.kea as kea
import mod.tools as tools
from kstream.decoupeur import Decoupeur, StatusDisplay
import os

ks_debug = 0

cp = StatusDisplay(not ks_debug)

kea.start("D off")

print("loading dependencies...")

for d in os.listdir("./ks_dep"):
    with open(f"./ks_dep/{d}", "r") as f:
        ks = f.read()
    kea.start(ks, 0)
    print(f" - {d} loaded")

while True:
    code = []
    while not code or code[-1] != "":
        cp.colorprint("KS", "37" if code else "36", end="")
        code.append(input(" $ "))
    
    tools.clear_last_line()
    
    sortie = Decoupeur("\n".join(code), ks_debug, not ks_debug).start()

    if sortie != 0:
        parsed = "\n".join([" ".join(k) for k in sortie])

        kea.start(parsed, 0)