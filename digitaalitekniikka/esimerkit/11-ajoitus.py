"""Staattinen ajoitusanalyysi: kriittinen polku ja maksimitaajuus.

Rekisteristä lähtevät signaalit ehtivät logiikan läpi seuraavaan
rekisteriin. Pisin polku (kriittinen polku) määrää kellojakson:

    T >= t_cq + t_logiikka + t_setup

Lyhin polku taas ei saa olla niin lyhyt, että uusi arvo ehtii
seuraavaan kiikkuun ennen pitoajan loppua (t_cq + t_min >= t_hold).
"""

from dataclasses import dataclass

# @alku parametrit
VIIVE = {"XOR": 60, "AND": 40, "OR": 40}     # porttien viiveet (ps)
T_CQ, T_SETUP, T_HOLD = 50, 30, 20           # kiikun ajat (ps)
# @loppu parametrit


@dataclass
class Portti:
    tyyppi: str
    tulot: list[str]
    lahto: str


# @alku summain
def summain(n: int, alku: int = 0) -> list[Portti]:
    """Ripple-carry-summain biteille alku … alku+n-1."""
    portit = []
    for i in range(alku, alku + n):
        a, b, c = f"a{i}", f"b{i}", f"c{i}"
        portit += [Portti("XOR", [a, b], f"x{i}"),
                   Portti("XOR", [f"x{i}", c], f"s{i}"),
                   Portti("AND", [a, b], f"g{i}"),
                   Portti("AND", [f"x{i}", c], f"t{i}"),
                   Portti("OR", [f"g{i}", f"t{i}"], f"c{i + 1}")]
    return portit
# @loppu summain


# @alku sta
def analyysi(portit: list[Portti]) -> tuple[int, list[str], int]:
    """Palauttaa pisimmän polun viiveen ja signaalit sekä lyhimmän
    polun viiveen. Tulot (rekisterien lähdöt) saapuvat hetkellä 0."""
    myohin: dict[str, int] = {}
    aikaisin: dict[str, int] = {}
    edeltaja: dict[str, str] = {}
    lahdot = {p.lahto: p for p in portit}

    def laske(s: str) -> None:
        if s in myohin:
            return
        if s not in lahdot:                  # rekisterin lähtö
            myohin[s] = aikaisin[s] = 0
            return
        p = lahdot[s]
        for t in p.tulot:
            laske(t)
        hitain = max(p.tulot, key=lambda t: myohin[t])
        myohin[s] = myohin[hitain] + VIIVE[p.tyyppi]
        aikaisin[s] = min(aikaisin[t] for t in p.tulot) + VIIVE[p.tyyppi]
        edeltaja[s] = hitain

    for s in lahdot:
        laske(s)
    # Polut päättyvät signaaleihin, joita mikään portti ei käytä.
    kaytetyt = {t for p in portit for t in p.tulot}
    loput = [s for s in lahdot if s not in kaytetyt]
    pisin = max(loput, key=lambda s: myohin[s])
    polku = [pisin]
    while polku[-1] in edeltaja:
        polku.append(edeltaja[polku[-1]])
    return myohin[pisin], polku[::-1], min(aikaisin[s] for s in loput)
# @loppu sta


def raportti(nimi: str, portit: list[Portti]) -> None:
    viive, polku, lyhin = analyysi(portit)
    jakso = T_CQ + viive + T_SETUP
    print(f"{nimi}:")
    print(f"  kriittinen polku {viive} ps: " + " → ".join(polku[:4])
          + " … " + " → ".join(polku[-3:]))
    print(f"  jakso >= {T_CQ} + {viive} + {T_SETUP} = {jakso} ps"
          f"  =>  f_max = {1e6 / jakso:.0f} MHz")
    pito = T_CQ + lyhin - T_HOLD
    print(f"  pitoajan marginaali {T_CQ} + {lyhin} - {T_HOLD} = {pito} ps")


def main() -> None:
    # @alku vertailu
    raportti("16-bittinen summain yhdessä jaksossa", summain(16))
    # Liukuhihna: rekisteri bittien 7 ja 8 välissä. Kumpikin vaihe on
    # erillinen kahdeksan bitin ketju; latenssi kasvaa yhteen jaksoon.
    raportti("sama kahtena liukuhihnavaiheena", summain(8, alku=8))
    # @loppu vertailu


if __name__ == "__main__":
    main()
