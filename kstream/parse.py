def remove_strvide(liste):
    while "" in liste:
        liste.remove("")
    return liste

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
