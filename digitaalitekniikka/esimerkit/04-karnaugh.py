"""Neljän muuttujan Karnaugh-kartta ja sen ryhmät.

Rivit ja sarakkeet ovat Gray-järjestyksessä (00, 01, 11, 10), joten
vierekkäiset ruudut eroavat yhdessä bitissä, myös reunojen yli.
"""

from qm import kattaa, lauseke, sievenna

GRAY = ["00", "01", "11", "10"]


# @alku kartta
def kartta(ykkoset: set[int], yhdentekevat: set[int]) -> str:
    rivit = ["ab\\cd  " + "  ".join(GRAY)]
    for ab in GRAY:
        ruudut = []
        for cd in GRAY:
            m = int(ab + cd, 2)
            merkki = ("1" if m in ykkoset
                      else "x" if m in yhdentekevat else ".")
            ruudut.append(f"{merkki:>2}")
        rivit.append(f"  {ab}   " + "  ".join(ruudut))
    return "\n".join(rivit)
# @loppu kartta


def main() -> None:
    # @alku bcd
    ykkoset = {2, 3, 5, 7}                 # alkuluku, BCD-syöte
    yhdentekevat = set(range(10, 16))      # koodit 10–15 eivät esiinny
    print(kartta(ykkoset, yhdentekevat))
    for termi in sievenna(4, sorted(ykkoset), sorted(yhdentekevat)):
        ruudut = [m for m in range(16) if kattaa(termi, m)]
        print(f"ryhmä {lauseke([termi]):4} kattaa ruudut {ruudut}")
    # @loppu bcd


if __name__ == "__main__":
    main()
