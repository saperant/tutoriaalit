"""Ehtolausekkeen sieventäminen ja sen oikeellisuuden tarkistus.

Toimitusmaksu on ilmainen, jos asiakas on kanta-asiakas tai tilaus on
suuri, paitsi jos toimitus menee ulkomaille ilman kanta-asiakkuutta.
"""

from itertools import product


# @alku alkuperainen
def ilmainen_toimitus_vanha(kanta: bool, suuri: bool,
                            ulkomaa: bool) -> bool:
    if kanta:
        if ulkomaa:
            return True
        return True
    if suuri and not ulkomaa:
        return True
    if suuri and ulkomaa and kanta:  # noqa: SIM103 (tarkoituksella sotkuinen)
        return True
    return False
# @loppu alkuperainen


# @alku sievennetty
def ilmainen_toimitus(kanta: bool, suuri: bool, ulkomaa: bool) -> bool:
    return kanta or (suuri and not ulkomaa)
# @loppu sievennetty


# @alku tarkistus
erot = [a for a in product([False, True], repeat=3)
        if ilmainen_toimitus_vanha(*a) != ilmainen_toimitus(*a)]
print("eroavat syötteet:", erot)

# Disjunktiivinen normaalimuoto suoraan totuustaulusta: jokainen rivi,
# jolla tulos on tosi, on yksi konjunktio.
nimet = ("kanta", "suuri", "ulkomaa")
termit = []
for arvot in product([False, True], repeat=3):
    if ilmainen_toimitus(*arvot):
        osat = [n if a else f"¬{n}" for n, a in zip(nimet, arvot,
                                                    strict=True)]
        termit.append("(" + " ∧ ".join(osat) + ")")
print(f"DNF: {len(termit)} termiä")
for t in termit:
    print("  ", t)
# @loppu tarkistus
