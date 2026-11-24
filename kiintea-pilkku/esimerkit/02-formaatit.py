"""Q-formaattien arvoalue ja tarkkuus taulukkona."""

from fractions import Fraction


# @alku formaatti
def formaatti(m: int, n: int, etumerkki: bool = True) -> str:
    """Qm.n: m kokonaisbittiä (etumerkki mukaan lukien) ja n murtobittiä.

    Etumerkittömästä muodosta käytetään merkintää UQm.n.
    """
    bitit = m + n
    lsb = Fraction(1, 2**n)
    if etumerkki:
        pienin = -(2 ** (bitit - 1)) * lsb
        suurin = (2 ** (bitit - 1) - 1) * lsb
        nimi = f"Q{m}.{n}"
    else:
        pienin = Fraction(0)
        suurin = (2**bitit - 1) * lsb
        nimi = f"UQ{m}.{n}"
    return (f"{nimi:8} {bitit:5} {float(pienin):>12.6g} "
            f"{float(suurin):>14.10g} {float(lsb):>12.6g}")
# @loppu formaatti


print(f"{'muoto':8} {'bitit':>5} {'pienin':>12} {'suurin':>14} "
      f"{'LSB':>12}")
# @alku taulukko
for m, n, etumerkki in [(1, 7, True), (1, 15, True), (1, 31, True),
                        (8, 8, True), (4, 12, True), (2, 30, True),
                        (0, 16, False), (12, 4, False)]:
    print(formaatti(m, n, etumerkki))
# @loppu taulukko
