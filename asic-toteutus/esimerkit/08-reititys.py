"""Sokkeloreititys (Lee): aaltorintama lähteestä kohteeseen.

Reititysalue on ruudukko, jossa # on este (esim. muistilohko).
Leveyshaku löytää lyhimmän reitin, jos sellainen on. Johtimet
reititetään yksi kerrallaan, ja aiemmat reitit ovat esteitä
myöhemmille. Yhdellä metallikerroksella ristikkäiset johtimet eivät
mahdu; toinen kerros ja kerrosten väliset läpiviennit (via) ratkaisevat.
"""

from collections import deque

Ruutu = tuple[int, int, int]          # x, y, kerros

# @alku alue
ALUE = [
    "..............",
    "..............",
    ".....####.....",
    ".....####.....",
    ".....####.....",
    "..............",
    "..............",
]
JOHTIMET = {                       # nimi: (lähde, kohde) kerroksella 0
    "A": ((0, 3), (13, 3)),
    "B": ((4, 0), (10, 6)),
    "C": ((4, 6), (10, 0)),
}
# @loppu alue


# @alku lee
def reitita(varatut: dict[Ruutu, str], alku: Ruutu, loppu: Ruutu,
            kerroksia: int) -> list[Ruutu] | None:
    """Leveyshaku kolmessa ulottuvuudessa; via on siirto kerrokselta
    toiselle samassa ruudussa."""
    korkeus, leveys = len(ALUE), len(ALUE[0])
    edellinen: dict[Ruutu, Ruutu] = {}
    jono = deque([alku])
    nahty = {alku}
    while jono:
        r = jono.popleft()
        if r == loppu:
            reitti = [r]
            while r != alku:
                r = edellinen[r]
                reitti.append(r)
            return reitti[::-1]
        x, y, z = r
        for n in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                  (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
            nx, ny, nz = n
            if (0 <= nx < leveys and 0 <= ny < korkeus
                    and 0 <= nz < kerroksia and ALUE[ny][nx] == "."
                    and n not in nahty
                    and (n not in varatut or n == loppu)):
                nahty.add(n)
                edellinen[n] = r
                jono.append(n)
    return None
# @loppu lee


def reitita_kaikki(kerroksia: int) -> tuple[dict[Ruutu, str], list[str]]:
    varatut: dict[Ruutu, str] = {}
    for nimi, (a, b) in JOHTIMET.items():   # nastat ovat varattuja
        varatut[(*a, 0)] = varatut[(*b, 0)] = nimi.lower()
    epaonnistui = []
    for nimi, (a, b) in JOHTIMET.items():
        reitti = reitita(varatut, (*a, 0), (*b, 0), kerroksia)
        if reitti is None:
            epaonnistui.append(nimi)
            continue
        for r in reitti[1:-1]:
            varatut[r] = nimi
    return varatut, epaonnistui


def piirra(varatut: dict[Ruutu, str], kerroksia: int) -> list[str]:
    rivit = []
    for y, rivi in enumerate(ALUE):
        osat = ["".join(varatut.get((x, y, z), c)
                        for x, c in enumerate(rivi))
                for z in range(kerroksia)]
        rivit.append("   ".join(osat))
    return rivit


def main() -> None:
    # @alku ajo
    for kerroksia in [1, 2]:
        varatut, virheet = reitita_kaikki(kerroksia)
        tila = f"ei reittiä: {', '.join(virheet)}" if virheet else "kaikki"
        print(f"{kerroksia} kerros(ta): {tila}")
        for rivi in piirra(varatut, kerroksia):
            print("  " + rivi)
    # @loppu ajo


if __name__ == "__main__":
    main()
