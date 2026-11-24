"""Sekvenssin 101 tunnistin Moore- ja Mealy-tilakoneena.

Tilakaaviosta tehdään tilasiirtotaulu, tilat koodataan biteiksi, ja
seuraavan tilan ja lähdön logiikka sievennetään Quine–McCluskeyllä.
Lopuksi porttitason toteutusta verrataan taulukkoon.
"""

from itertools import product

from qm import kattaa, lauseke, sievenna

# @alku taulut
# Moore: lähtö riippuu vain tilasta. Tila = (seuraava 0:lla, 1:llä).
MOORE = {
    "S0": ("S0", "S1"),       # ei osumaa
    "S1": ("S2", "S1"),       # nähty 1
    "S2": ("S0", "S3"),       # nähty 10
    "S3": ("S2", "S1"),       # nähty 101: lähtö 1
}
MOORE_LAHTO = {"S0": 0, "S1": 0, "S2": 0, "S3": 1}

# Mealy: lähtö riippuu tilasta ja syötteestä. (seuraava, lähtö).
MEALY = {
    "A": (("A", 0), ("B", 0)),
    "B": (("C", 0), ("B", 0)),
    "C": (("A", 0), ("B", 1)),     # 10 + syöte 1 = 101
}
# @loppu taulut

# @alku koodaus
KOODI = {"S0": 0b00, "S1": 0b01, "S2": 0b10, "S3": 0b11}
NIMET = ["q1", "q0", "x"]


def yhtalot() -> dict[str, list[str]]:
    """Seuraavan tilan bitit funktioina (q1, q0, x)."""
    ykkoset: dict[str, list[int]] = {"d1": [], "d0": []}
    for tila, seuraavat in MOORE.items():
        for x, seuraava in enumerate(seuraavat):
            rivi = (KOODI[tila] << 1) | x
            if KOODI[seuraava] & 0b10:
                ykkoset["d1"].append(rivi)
            if KOODI[seuraava] & 0b01:
                ykkoset["d0"].append(rivi)
    return {bitti: sievenna(3, m) for bitti, m in ykkoset.items()}
# @loppu koodaus


def arvo(termit: list[str], q1: int, q0: int, x: int) -> int:
    rivi = (q1 << 2) | (q0 << 1) | x
    return int(any(kattaa(t, rivi) for t in termit))


def main() -> None:
    # @alku yhtalot
    yht = yhtalot()
    for bitti, termit in yht.items():
        print(f"{bitti} = {lauseke(termit, NIMET)}")
    print("z  = q1·q0")
    # @loppu yhtalot

    # @alku tarkistus
    virheet = 0
    for q1, q0, x in product((0, 1), repeat=3):
        tila = next(t for t, k in KOODI.items() if k == (q1 << 1 | q0))
        odotettu = KOODI[MOORE[tila][x]]
        laskettu = (arvo(yht["d1"], q1, q0, x) << 1) | arvo(
            yht["d0"], q1, q0, x)
        virheet += odotettu != laskettu
    print(f"logiikka vs. taulu: {virheet} virhettä 8 rivistä")
    # @loppu tarkistus

    # @alku vertailu
    syote = [1, 0, 1, 1, 0, 1, 0, 1, 0, 0]
    moore, mealy = "S0", "A"
    rivi_moore, rivi_mealy = [], []
    for x in syote:                           # yksi kierros = yksi jakso
        rivi_mealy.append(MEALY[mealy][x][1])  # tilasta ja syötteestä
        rivi_moore.append(MOORE_LAHTO[moore])  # vain nykyisestä tilasta
        mealy = MEALY[mealy][x][0]             # kellon reuna
        moore = MOORE[moore][x]
    print()
    print("jakso  " + " ".join(str(i) for i in range(len(syote))))
    print("syöte  " + " ".join(map(str, syote)))
    print("Mealy  " + " ".join(map(str, rivi_mealy)))
    print("Moore  " + " ".join(map(str, rivi_moore)))
    # @loppu vertailu


if __name__ == "__main__":
    main()
