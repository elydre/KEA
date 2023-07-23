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
 - Licence : MIT
'''

from kstream.parse import parse

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
        self.active_mcn = [[], 0] # nom des boucle / condition active
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
        code = replace_while(";;", ";", replace_while("  ", " ", code))

        if self.DEBUG_PRINT:
            print(f"Polissage :\n| {code}")
        
        self.sd.statuprint(1, "polissage")
        return code

    def decoupe(self) -> list:
        decouped = []
        analiser_codetemp = lambda code: [c.strip() for c in code.split(",")]

        for code in self.brut.split(";"):
            exit_list, in_str, codetemp, push, oldpush = [], False, "", 0, 0
            for l in code:
                if l != ">" or in_str:
                    codetemp += l

                if l in ["\"", "'"]:
                    in_str = not in_str

                elif not in_str:
                    if l == ">":
                        push += 1

                    elif push > 0:
                        exit_list.append([oldpush, push, analiser_codetemp(codetemp)])
                        oldpush, push, codetemp = push, 0, ""

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
            local_analyse, is_pushed = [], False

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
