"""Riippuvuusverkko tiimirajojen yli: kaaret ja syklit tiimien välillä."""

from collections.abc import Callable

from organisaatio import JAOT, riippuvuudet


# @alku tiimiverkko
def tiimiverkko(jako: Callable[[str], str]) -> dict[str, set[str]]:
    """Tiimi A riippuu tiimistä B, jos jokin A:n osa kutsuu B:n osaa."""
    verkko: dict[str, set[str]] = {}
    for osa, kutsutut in riippuvuudet().items():
        verkko.setdefault(jako(osa), set())
        for kohde in kutsutut:
            if jako(kohde) != jako(osa):
                verkko[jako(osa)].add(jako(kohde))
    return verkko
# @loppu tiimiverkko


# @alku syklit
def syklit(verkko: dict[str, set[str]]) -> list[list[str]]:
    """Tiimiryhmät, joissa jokainen riippuu toisistaan (vahvat
    komponentit, joissa on yli yksi tiimi)."""
    def tavoittaa(alku: str) -> set[str]:
        nahty: set[str] = set()
        pino = [alku]
        while pino:
            for naapuri in verkko[pino.pop()]:
                if naapuri not in nahty:
                    nahty.add(naapuri)
                    pino.append(naapuri)
        return nahty

    ulottuu = {tiimi: tavoittaa(tiimi) for tiimi in verkko}
    ryhmat = {tuple(sorted(t for t in verkko
                           if t in ulottuu[tiimi] and tiimi in ulottuu[t]))
              for tiimi in verkko if tiimi in ulottuu[tiimi]}
    return [list(ryhma) for ryhma in sorted(ryhmat)]
# @loppu syklit


for nimi, jako in JAOT.items():
    kutsut = riippuvuudet()
    ylittavat = sum(jako(osa) != jako(kohde)
                    for osa, kohteet in kutsut.items() for kohde in kohteet)
    kaikki = sum(len(kohteet) for kohteet in kutsut.values())
    verkko = tiimiverkko(jako)
    print(f"{nimi}: {ylittavat}/{kaikki} riippuvuutta ylittää tiimirajan")
    for tiimi in sorted(verkko):
        kohteet = ", ".join(sorted(verkko[tiimi])) or "-"
        print(f"  {tiimi} -> {kohteet}")
    for ryhma in syklit(verkko):
        print(f"  sykli: {' <-> '.join(ryhma)}")
