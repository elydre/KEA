import kea.kea as kea
from kstream.decoupeur import Decoupeur, StatusDisplay
import os

ks_debug = False
ks_discret = True

cp = StatusDisplay(ks_discret)

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
        code.append(input("KS $ "))

    sortie = Decoupeur("\n".join(code), ks_debug, ks_discret).start()

    if sortie != 0:
        parsed = "\n".join([" ".join(k) for k in sortie])

        kea.start(parsed, 0)