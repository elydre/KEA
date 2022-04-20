import kea.kea as kea
from ks.decoupeur import Decoupeur

kea.start("""
D on

// dependance KEA 2022
// uf.kea  -  pf4

F print var
    A var
    S
    E print var

F cout var
    A var
    E cout var

F input var
    A var
    I sortie
    E input sortie

F random max
    R sortie max
    E random sortie

F pass var
    E pass var

F debug_on
    D on
    E debug_on

F debug_off
    D off
    E debug_off

F debug_print
    D print
    E debug_print
""")

while True:
    code = input("KS $ ")
    sortie = Decoupeur(code, 0).start()

    if sortie != 0:
        parsed = "\n".join([" ".join(k) for k in sortie])
        print(f"\n{parsed}\n")

        kea.start(parsed, 0)