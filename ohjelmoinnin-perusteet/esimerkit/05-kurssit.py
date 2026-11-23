"""Kurssien ilmoittautumiset joukkoina."""

ohjelmointi = {"Aino", "Eero", "Lumi", "Oskari", "Venla"}
tietokannat = {"Eero", "Mikael", "Venla", "Iida"}

molemmat = ohjelmointi & tietokannat          # leikkaus
jompikumpi = ohjelmointi | tietokannat        # yhdiste
vain_ohjelmointi = ohjelmointi - tietokannat  # erotus

print("Molemmilla:", sorted(molemmat))
print("Opiskelijoita yhteensä:", len(jompikumpi))
print("Vain ohjelmoinnissa:", sorted(vain_ohjelmointi))

ilmoittautumiset = ["Aino", "Eero", "Aino", "Lumi", "Eero"]
print("Tuplailmoittautumiset poistettu:", sorted(set(ilmoittautumiset)))
