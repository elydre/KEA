'''
~|--|~|--|~|--|~|--|~|--|~|--

██  ████        ██████        ██
████    ██     ██           ████
██      ██   ████████     ██  ██
████████       ██       ██    ██
██             ██       █████████
██             ██             ██
██
 - codé en : UTF-8
 - langage : python 3
 - GitHub  : github.com/pf4-DEV
 - Licence : MIT
--|~|--|~|--|~|--|~|--|~|--|~|--
'''

version = "0.0.7"

def debug_print(texte, blue = False):
    global DEBUG
    if DEBUG:
        if blue: print(end = f"\033[0;1;30m{texte}\033[0m")
        else: print(end = texte)

def setvar(name, valeur, active):
    if type(valeur) == str:
        if valeur.isdigit():
            valeur = int(valeur)
        elif "." in valeur and valeur.replace(".", "").isdigit():
            valeur = float(valeur)
    name = makename(name, active)
    debug_print(f"{name} → {valeur}\n")
    VAR[name] = valeur


def user_input(var, ACTIVE):
    setvar(var, input(), ACTIVE)


def debug_print_all():
    print("\nVARIABLES:")
    global VAR
    for key, value in VAR.items():
        print(f"- {key} = {value}")
    print("\nFONCTIONS:")
    global FUNCTIONS
    for key, value in FUNCTIONS.items():
        print(f"- {key} ~ i{value[1]}")


def compar(comparateur, a, b):
    if comparateur == "==":
        return a == b
    elif comparateur == "=":
        return a == b
    elif comparateur == "!=":
        return a != b
    elif comparateur == ">":
        return a > b
    elif comparateur == "<":
        return a < b
    elif comparateur == ">=":
        return a >= b
    elif comparateur == "<=":
        return a <= b
    else:
        print(f"Erreur de comparaison : '{comparateur}' \n")


def calc(calcul, var1, var2):
    if calcul == "+":
        return var1 + var2
    elif calcul == "-":
        return var1 - var2
    elif calcul == "*":
        return var1 * var2
    elif calcul == "^":
        return var1 ** var2
    elif calcul == "**":
        return var1 ** var2
    elif calcul == "/":
        return var1 / var2
    elif calcul == "%":
        return var1 % var2
    else:
        print(f"Erreur de calcul : '{calcul}'")


def makename(name, active):
    return f"{active}_{name}" if name[0] != "!" else name

def getvar(name, active):
    name = makename(name, active)
    if name in VAR:
        return VAR[name]
    print(f"Variable {name} non trouvée")
    return ""


def setsauter(valeur, nom):
    debug_print(f"{nom} → sauter = '{valeur}'\n")
    return valeur


def file_get_contents(path):
    with open(path, "r") as f:
        return f.read()


def add_sharp(code):
    to_add = []
    names = []
    for i in range(len(code)):
        args = code[i].split(" ")
        if args[0] != "#":
            break
        elif args[1] == "add":
            code.pop(0)
            to_add.append(file_get_contents(args[2]).replace("\r", "").replace(";", "\n").split("\n"))
            names.append(args[2])
    for k in range(len(to_add)):
        code = code + to_add[k].split("\n")
        print(f"merge de '{names[k]}' avec succès!")
    return code


def start(code, reset = True):
    global VAR, DEBUG, FUNCTIONS
    if reset:
        DEBUG = False
        VAR = {}
        FUNCTIONS = {}

    code = str(code).replace(";", "\n").replace("\r", "")
    code = code.split("\n")

    code = add_sharp(code)

    codeinloop(code, "main", 1, "main")


def start_fonction(args, fonc_name):
    global FUNCTIONS

    fonction = args[1]

    if fonction in FUNCTIONS:

        fonc_code = FUNCTIONS[fonction][0]
        oldi = FUNCTIONS[fonction][1]
        in_fonc_args = FUNCTIONS[fonction][2]

        out_args = args[2].split("&") if len(args) > 2 else []

        for j in range(len(in_fonc_args)):
            if len(out_args) > j:
                setvar(in_fonc_args[j], getvar(out_args[j], fonc_name), args[1])
                debug_print(f"création de la variable '{in_fonc_args[j]}' = '{getvar(out_args[j], fonc_name)}' dans la fonction '{args[1]}'")
            else:
                print(f"Erreur: fonction '{args[1]}' : argument {j} non défini")

        return bcl_ctrl(fonc_code, oldi, args[1], 1, args[1])[1]

    print(f"Fonction {fonction} non trouvée")


def save_fonction(name, code, i, args):
    global FUNCTIONS
    FUNCTIONS[name] = [code, i, args]


def bcl_ctrl(code, i, nom, nb, fonc_name):
    codetoloop = [code[j] for j in range(i+1, len(code))]
    return codeinloop(codetoloop, nom, nb, fonc_name)


def codeinloop(code, nom, max, fonc_name):  # sourcery no-metrics
    global VAR, DEBUG, FUNCTIONS
    debug_print(f"DEMARAGE DE LA BOUCLE '{nom}'\n")
    sauter = setsauter("", nom)
    dobreak = 0
    for rep in range(int(max)):
        for i in range(len(code)):
            ligne = code[i]
            ligne = ligne.strip()

            debug_print(f"[{fonc_name} | {nom}]({rep}~{i}) *** {ligne} ***\n", True)

            args = ligne.split(" ")
            mode = args[0]

            if sauter == "" or (mode == "E" and args[1] == sauter):
                if sauter != "":
                    sauter = setsauter("", nom)
                
                if mode == "":
                    continue
                
                elif mode == "V":
                    var = args[1]
                    val = args[2]
                    setvar(var, val, fonc_name)
                
                elif mode == "L":
                    dobreak = bcl_ctrl(code, i, args[1], getvar(args[2], fonc_name), fonc_name)[0]
                    sauter = setsauter(args[1], nom)
                
                elif mode == "E":
                    if args[1] == nom:
                        debug_print(f"ARRET DE LA BOUCLE '{nom}'")
                        if len(args) > 2:
                            debug_print(" PAR RETURN\n")
                            return [0, getvar(args[2], fonc_name)]
                        debug_print(" PAR BREAK\n")
                        break
                
                elif mode == "C":
                    result = calc(args[3], getvar(args[2], fonc_name), getvar(args[4], fonc_name))
                    setvar(args[1], result, fonc_name)
                
                elif mode == "Z":
                    dobreak = getvar(args[1], fonc_name) if len(args) > 1 else 1
                
                elif mode == "B":
                    setvar(args[1], compar(args[3], getvar(args[2], fonc_name), getvar(args[4], fonc_name)), fonc_name)
                
                elif mode == "H":
                    setvar(args[1], getvar(args[2], fonc_name), fonc_name)
                
                elif mode == "F":
                    fonc_args = []
                    if len(args) > 2:
                        fonc_args = args[2].split("&")
                    save_fonction(args[1], code, i, fonc_args)
                    sauter = setsauter(args[1], nom)
                
                elif mode == "T":
                    sortie = start_fonction(args, fonc_name)
                    if len(args) > 3:
                        setvar(args[3], sortie, fonc_name)
                
                elif mode == "D":
                    if args[1] == "on":
                        DEBUG = True
                    elif args[1] == "off":
                        DEBUG = False
                    else:
                        debug_print_all()
                
                elif mode == "R":
                    rand = rand(0, getvar(args[2], fonc_name))
                    setvar(args[1], rand, fonc_name)
                
                elif mode == "X":
                    if getvar(args[2], fonc_name) == True:
                        dobreak = bcl_ctrl(code, i, args[1], 1, fonc_name)[0]
                        sauter = setsauter(args[1], nom)
                    else:
                        sauter = setsauter(args[1], nom)
                        debug_print(f"condition non remplie: {sauter}\n")
                
                elif mode == "S":
                    print(end = f"\033[0;0;33m{args[1].replace('_', ' ')}\033[0m" if len(args) > 1 else "\n")
                
                elif mode == "I":
                    user_input(args[1], fonc_name)
                
                elif mode == "A":
                    print(end = f"\033[0;1;33m{getvar(args[1], fonc_name)}\033[0m")
                
                elif mode != "//":
                    print(f"Erreur de mode: {mode}")
                if DEBUG and mode in ["S", "A"]:
                    print()
            else:
                debug_print(f"{nom} → passer '{ligne}'")
            if dobreak > 0:
                return [dobreak - 1, 0]
    return [0, 0]