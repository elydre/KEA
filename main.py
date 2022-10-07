# simple shell :         python3 main.py
# debug shell :          python3 main.py -d
# execute file :         python3 main.py -f <file>
# execute file & debug : python3 main.py -df <file>

import os
from sys import argv

####
def remove_strvide(liste): # sourcery skip: inline-immediately-returned-variable, list-comprehension
    new_liste = []
    for element in liste:
        if element != "":
            new_liste.append(element)
    return new_liste

def split_string(text):
    # decouper la chaine de caractere en liste au espaces mais pas dans les quotes
    in_quote = False
    sortie = [""]
    for c in text:
        if c == '"':
            in_quote = not in_quote
            sortie[-1] += c
        elif c == " " and not in_quote:
            sortie.append("")
        else:
            sortie[-1] += c
    return sortie

def get_type(elmt: str):
    if elmt.replace(".", "").isdigit():
        return "int", elmt
    elif elmt[0] == elmt[-1] and elmt[0] in ["'", '"']:
        return "str", elmt[1:-1].replace(" ", "_")
    elif elmt[0] == "$":
        return "var", elmt[1:]
    elif elmt in {"LOOP", "IF", "END", "BREAK", "FUNC", "RETURN"}:
        return "mc", elmt
    elif elmt in {"+", "-", "*", "/", "%", "^", "**"}:
        return "op", elmt
    elif elmt in {"==", "!=", "=", "=+", "=-", "==+", "==-"}:
        return "cpr", elmt
    else:
        return "func", elmt


def parse(e, i, is_pushed, ACTIVE_MCN): # sourcery no-metrics
    """
    e  =>        [nb in args, nb out args, [code]]
    i  =>        index de la partie a analyser
    is_pushed => longeur de la liste de code deja analyser
    """

    charge = 0
    Vstream = f"stream{i}"
    sortie = []

    def generate_func_args(e, i):
        return "&".join([f"stream{j+i+(i if e[0] - e[1] > 1 and e[1] > 0 else 0)}" for j in range((e[0] // e[1]) if e[1] != 0 else 1 if e[0] > 0 else 0)])

    for c in split_string(str(e[2][i])):

        etype, econt = get_type(c)

        if charge:
            if charge == "func_args":
                sortie.append(["F", ACTIVE_MCN[0][-1], econt.replace("$", "&")])
                charge = 0
                continue

            elif charge == "func_name":
                ACTIVE_MCN[0].append(econt)
                charge = "func_args"
                continue

            if etype in ["int", "str"]:
                sortie.append(["V", "temp", econt])
                temp = "temp"  

            elif etype == "var":
                temp = econt

            else:
                return 0, f"{etype} ne peut pas etre utilise apres un operateur\n-> {econt}"

            if get_type(charge)[0] == "op":
                sortie.append(["C", Vstream, Vstream, charge, temp])

            elif get_type(charge)[0] == "cpr":
                sortie.append(["B", Vstream, Vstream, charge, temp])
            
            charge = 0

        elif etype in ["int", "str"]:
            sortie.append(["V", Vstream, econt])

        elif etype == "var":
            # soit [VAR > STREAM]: (is_pushed == 0) soit [STREAM > VAR]
            sortie.append(["H", Vstream, econt] if is_pushed == 0 else ["H", econt, Vstream])

        elif etype == "mc":
            if econt == "LOOP":
                sortie.append(["L", f"loop{ACTIVE_MCN[1]}", Vstream])
                ACTIVE_MCN[0].append(f"loop{ACTIVE_MCN[1]}")
                ACTIVE_MCN[1] += 1

            elif econt == "IF":
                sortie.append(["X", f"if{ACTIVE_MCN[1]}", Vstream])
                ACTIVE_MCN[0].append(f"if{ACTIVE_MCN[1]}")
                ACTIVE_MCN[1] += 1

            elif econt == "END":
                sortie.append(["E", ACTIVE_MCN[0][-1]])
                ACTIVE_MCN[0].pop()

            elif econt == "BREAK":
                sortie.append(["Z", Vstream])

            elif econt == "FUNC":
                charge = "func_name"

            elif econt == "RETURN":
                sortie.append(["E", ACTIVE_MCN[0][-1], Vstream])
                ACTIVE_MCN[0].pop()

        elif etype in ["op", "cpr"]:
            charge = econt

        else:
            temp = ["T", c ,generate_func_args(e, i)]
            # si la fonction retourne une valeur
            if e[1] > 0:
                temp.append(Vstream)
            sortie.append(remove_strvide(temp))

    return sortie, ACTIVE_MCN
####

def isdown(var):
    return var == 0

class StatusDisplay:
    def __init__(self, discret = False):
        self.discret = discret

    def colorprint(self, text, color, end = "\n"):
        print(f"\033[{color}m{text}\033[0m", end=end)
    
    def error(self, text):
        self.colorprint(text, "36")
        return 0
    
    def statuprint(self, etat: bool, nom):
        if etat and not self.discret: self.colorprint(f"🟢 pass - {nom}", 32)
        elif not etat: self.colorprint(f"🔴 fail - {nom}", 31)
        return etat

class Decoupeur:
    def __init__(self, code, debug=False, discret=False):
        self.DEBUG_PRINT = bool(debug)
        self.active_mcn = [[],0] # nom des boucle / condition active
        self.brut = code
        self.sd = StatusDisplay(discret)
    
    def start(self):
        self.brut = self.polissage(self.brut)
        self.decouped = self.decoupe()
        self.analysed = self.analyse()
        return self.generer()

    def polissage(self, code) -> str:
        def replace_while(old, new, text):
            while old in text:
                text = text.replace(old, new)
            return text

        code = code.replace("\n", ";").replace("\t", " ").strip()
        code = replace_while("  ", " ", code)
        code = replace_while(";;", ";", code)

        if self.DEBUG_PRINT:
            print(f"Polissage :\n| {code}")
        
        self.sd.statuprint(1, "polissage")
        return code

    def decoupe(self) -> list:
        decouped = []
        analiser_codetemp = lambda code: [c.strip() for c in code.split(",")]

        for code in self.brut.split(";"):

            exit_list = []
            in_str = False
            codetemp = ""
            push = 0
            oldpush = 0
            for l in code:
                if l != ">" or in_str:
                    codetemp += l

                if l in ["\"", "'"]:
                    in_str = not in_str

                elif not in_str:
                    if l == ">":
                        push += 1

                    elif push > 0:
                        exit_list.append([oldpush ,push, analiser_codetemp(codetemp)])
                        oldpush, push = push, 0
                        codetemp = ""

            exit_list.append([oldpush, push, analiser_codetemp(codetemp)])
            decouped.append(exit_list)

        for d in decouped:
            for e in d:
                if len(e[2]) != e[1] and len(d) - 1 != d.index(e):
                    return self.sd.statuprint(self.sd.error(f"le nombre de chevron ne correspond pas au nombre de parametres\n-> {e[2]}"), "decoupe")
                if e[2] == [""]:
                    decouped.remove(d)

        if self.DEBUG_PRINT:
            print("\nDecoupe - [in args, out args, [code]] :")
            for d in decouped:
                print(f"| ligne {decouped.index(d)}")
                for e in d:
                    print(f"| | {e}")

        self.sd.statuprint(1, "decoupe")
        return decouped

    def analyse(self) -> list:
        if isdown(self.decouped):
            return self.sd.statuprint(0, "analyse")
        analysed = []
        for d in self.decouped:
            local_analyse = []
            is_pushed = False

            if d[0][2][0].startswith("#") or d[0][2][0].startswith("//"):
                analysed.append([" =+ ".join([e[2][0] for e in d])])
                continue

            for e in d:
                for i in range(len(e[2])):
                    sortie, self.active_mcn = parse(e, i, is_pushed, self.active_mcn)
                    if isdown(sortie): return self.sd.statuprint(self.sd.error(self.active_mcn), "analyse")
                    local_analyse.extend(iter(sortie))

                is_pushed = True
            analysed.extend(local_analyse)
            analysed.append([])

        if analysed: analysed.pop()

        if self.DEBUG_PRINT:
            print("\nAnalyse :")
            for a in analysed:
                print(f"| {a}")

        self.sd.statuprint(1, "analyse")
        return analysed

    def generer(self) -> str:
        if isdown(self.analysed):
            return self.sd.statuprint(0, "generation")
        self.sd.statuprint(1, "generation")
        return [[f.replace("=+", ">").replace("=-", "<") for f in e] for e in self.analysed]

####
import sys

def clear_last_line():
    go_up()
    clear_line()

def read_file(path):
    with open(path, "r") as f:
        return f.read()

def go_up():
    sys.stdout.write("\033[F")

def clear_line():
    sys.stdout.write("\033[K")
####

####
from random import randint

version = "0.0.8"

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
                    rand = randint(0, getvar(args[2], fonc_name))
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

####

debug = "d" in argv[1] if len(argv) > 1 else False
fmode = "f" in argv[1] if len(argv) > 1 else False

cp = StatusDisplay(not debug)

start(f"D {'on' if debug else 'off'}")

print("loading dependencies...")

for d in os.listdir("./ks_dep"):
    ks = read_file(f"./ks_dep/{d}")
    start(ks, 0)
    print(f" - {d} loaded")

def alias(code):
    liste_alias = read_file("./ks_alias.txt").split("\n")
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
    
    clear_last_line()

    try:    
        sortie = Decoupeur(alias("\n".join(code)), debug, not debug).start()

        if sortie != 0:
            parsed = "\n".join([" ".join(k) for k in sortie])

            start(parsed, 0)
    except Exception as e:
        print(e, "\n")

if fmode:
    start("\n".join([" ".join(k) for k in Decoupeur(alias(read_file(argv[2])), debug, not debug).start()]), 0)