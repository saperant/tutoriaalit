#!/usr/bin/env python3
"""Satunnaisia Kide-ohjelmia differentiaalitestaukseen.

Käyttö: satunnainen.py SIEMEN > ohjelma.kide

Ohjelmat ovat aina oikeellisia ja päättyvät: funktio kutsuu vain
aiemmin määriteltyjä funktioita, ja silmukat ovat laskurisilmukoita,
joiden laskuria runko ei muuta. Kaikki aritmetiikka on Kidessä
määriteltyä (myös ylivuoto ja nollalla jakaminen), joten tulkin ja
käännetyn ohjelman tulosteiden on oltava samat.
"""

import random
import sys

# @alku lausekkeet
OPERAATTORIT = ["+", "-", "*", "/", "%"]
VERTAILUT = ["==", "!=", "<", "<=", ">", ">="]


class Generaattori:
    def __init__(self, siemen: int) -> None:
        self.r = random.Random(siemen)
        self.funktiot: list[tuple[str, int]] = []   # nimi, parametreja
        self.laskureita = 0

    def lauseke(self, muuttujat: list[str], syvyys: int) -> str:
        """Satunnainen int-lauseke."""
        valinta = self.r.random()
        if syvyys <= 0 or valinta < 0.3:
            if muuttujat and self.r.random() < 0.7:
                return self.r.choice(muuttujat)
            return str(self.r.choice([0, 1, 2, 3, 7, 10, 255, -1, -8,
                                      9223372036854775807]))
        if valinta < 0.4 and self.funktiot:
            nimi, n = self.r.choice(self.funktiot)
            argumentit = [self.lauseke(muuttujat, syvyys - 2)
                          for _ in range(n)]
            return f"{nimi}({', '.join(argumentit)})"
        if valinta < 0.45:
            return f"-{self.lauseke(muuttujat, syvyys - 1)}"
        vasen = self.lauseke(muuttujat, syvyys - 1)
        oikea = self.lauseke(muuttujat, syvyys - 1)
        return f"({vasen} {self.r.choice(OPERAATTORIT)} {oikea})"

    def ehto(self, muuttujat: list[str], syvyys: int) -> str:
        """Satunnainen bool-lauseke."""
        valinta = self.r.random()
        if syvyys > 0 and valinta < 0.2:
            op = self.r.choice(["&&", "||"])
            return (f"({self.ehto(muuttujat, syvyys - 1)} {op} "
                    f"{self.ehto(muuttujat, syvyys - 1)})")
        if syvyys > 0 and valinta < 0.3:
            return f"!({self.ehto(muuttujat, syvyys - 1)})"
        return (f"{self.lauseke(muuttujat, 2)} {self.r.choice(VERTAILUT)} "
                f"{self.lauseke(muuttujat, 2)}")
    # @loppu lausekkeet

    def lohko(self, muuttujat: list[str], sisennys: int,
              syvyys: int) -> list[str]:
        """Lauseita; muuttujat on näkyvissä olevat sijoitettavat nimet."""
        rivit: list[str] = []
        omat = list(muuttujat)
        tila = "    " * sisennys
        for _ in range(self.r.randint(1, 4)):
            valinta = self.r.random()
            if valinta < 0.25:
                nimi = f"m{len(omat)}_{sisennys}"
                if nimi not in omat:
                    rivit.append(f"{tila}var {nimi} = "
                                 f"{self.lauseke(omat, 3)};")
                    omat.append(nimi)
            elif valinta < 0.5 and omat:
                rivit.append(f"{tila}{self.r.choice(omat)} = "
                             f"{self.lauseke(omat, 3)};")
            elif valinta < 0.65:
                rivit.append(f"{tila}print({self.lauseke(omat, 3)});")
            elif valinta < 0.8 and syvyys > 0:
                rivit.append(f"{tila}if {self.ehto(omat, 2)} {{")
                rivit += self.lohko(omat, sisennys + 1, syvyys - 1)
                if self.r.random() < 0.5:
                    rivit.append(f"{tila}}} else {{")
                    rivit += self.lohko(omat, sisennys + 1, syvyys - 1)
                rivit.append(f"{tila}}}")
            elif syvyys > 0:
                # Laskurisilmukka: laskuria ei lisätä sijoitettaviin.
                self.laskureita += 1
                i = f"i{self.laskureita}"
                rivit.append(f"{tila}var {i} = 0;")
                rivit.append(f"{tila}while {i} < {self.r.randint(1, 4)} {{")
                rivit += self.lohko(omat, sisennys + 1, syvyys - 1)
                rivit.append(f"{tila}    {i} = {i} + 1;")
                rivit.append(f"{tila}}}")
        return rivit

    def funktio(self, nimi: str, parametreja: int) -> list[str]:
        parametrit = [f"p{i}" for i in range(parametreja)]
        otsikko = ", ".join(f"{p}: int" for p in parametrit)
        rivit = [f"fn {nimi}({otsikko}) -> int {{"]
        rivit += self.lohko(parametrit, 1, 2)
        rivit.append(f"    return {self.lauseke(parametrit, 3)};")
        rivit.append("}")
        return rivit

    def ohjelma(self) -> str:
        rivit: list[str] = []
        for k in range(self.r.randint(1, 4)):
            nimi = f"f{k}"
            n = self.r.randint(0, 3)
            rivit += self.funktio(nimi, n) + [""]
            self.funktiot.append((nimi, n))
        rivit.append("fn main() -> int {")
        rivit += self.lohko([], 1, 2)
        rivit.append(f"    print({self.lauseke([], 4)});")
        rivit += ["    return 0;", "}"]
        return "\n".join(rivit) + "\n"


if __name__ == "__main__":
    sys.stdout.write(Generaattori(int(sys.argv[1])).ohjelma())
