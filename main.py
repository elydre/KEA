import kea.kea as kea
from kstream.decoupeur import Decoupeur
import os

kea.start("D off")

print("loading dependencies...")

for d in os.listdir("./ks_dep"):
    with open(f"./ks_dep/{d}", "r") as f:
        ks = f.read()
    kea.start(ks, 0)
    print(f" - {d} loaded")

while True:
    code = input("KS $ ")
    sortie = Decoupeur(code, 0).start()

    if sortie != 0:
        parsed = "\n".join([" ".join(k) for k in sortie])
        print(f"\n{parsed}\n")

        kea.start(parsed, 0)