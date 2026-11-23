"""Pikaoppaan koodinäytteet."""

from dataclasses import dataclass
from pathlib import Path

# @alku arvot
hinta = 4.90                    # float
kpl = 3                         # int
nimi = "Kahvi"                  # str
alennus = kpl >= 3              # bool
summa = hinta * kpl * (0.9 if alennus else 1)
print(f"{nimi}: {kpl} kpl, {summa:.2f} €")   # Kahvi: 3 kpl, 13.23 €
print(7 // 2, 7 % 2, 7 / 2, 2**10)          # 3 1 3.5 1024
print(int("42") + 1, str(42) + "!", float("2.5"))
# @loppu arvot

# @alku ohjaus
for i in range(3):              # 0, 1, 2
    if i == 0:
        continue                # seuraavaan kierrokseen
    elif i > 5:
        break                   # ulos silmukasta
    print(i, end=" ")
print()
n = 10
while n > 1:
    n //= 2
# @loppu ohjaus


# @alku funktiot
def keskiarvo(luvut: list[float], oletus: float = 0.0) -> float:
    """Palauttaa keskiarvon tai oletuksen, jos lista on tyhjä."""
    if not luvut:
        return oletus
    return sum(luvut) / len(luvut)


print(keskiarvo([2, 4, 9]), keskiarvo([], oletus=-1))
# @loppu funktiot

# @alku kokoelmat
lista = [3, 1, 2]
lista.append(5)                 # [3, 1, 2, 5]
lista.sort()                    # [1, 2, 3, 5]
parilliset = [x for x in lista if x % 2 == 0]
puhelin = {"Aino": "040 123", "Eero": "050 456"}
puhelin["Lumi"] = "044 789"
for avain, arvo in puhelin.items():
    print(avain, arvo)
print(puhelin.get("Iida", "ei numeroa"), "Aino" in puhelin)
joukko = {1, 2, 3} & {2, 3, 4}  # {2, 3}
pari = (60.17, 24.94)           # monikko
lev, pit = pari                 # purku
print(lista[0], lista[-1], lista[1:3], parilliset, joukko)
# @loppu kokoelmat

# @alku merkkijonot
teksti = "  Aino Virtanen;aino@example.org "
nimi, sposti = teksti.strip().split(";")
print(nimi.upper(), sposti.endswith(".org"), "@" in sposti)
print(", ".join(["a", "b", "c"]), nimi[:4], len(nimi))
# @loppu merkkijonot

# @alku tiedostot
polku = Path("muistio.txt")
with open(polku, "w", encoding="utf-8") as f:
    f.write("rivi 1\nrivi 2\n")
with open(polku, encoding="utf-8") as f:
    for rivi in f:
        print(rivi.rstrip())
# @loppu tiedostot

# @alku virheet
try:
    maara = int("kolme")
except ValueError as virhe:
    print(f"Virhe: {virhe}")
    maara = 0
# @loppu virheet


# @alku luokat
@dataclass
class Tuote:
    nimi: str
    hinta_snt: int

    def alennettu(self, prosentti: int) -> int:
        return self.hinta_snt * (100 - prosentti) // 100


kahvi = Tuote("Kahvi", 690)
print(kahvi, kahvi.alennettu(20))
# @loppu luokat
