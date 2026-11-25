"""Laskun tulostus refaktoroituna: sama käytös, nimetyt säännöt."""

from dataclasses import dataclass

KANTA_ASIAKAS = 2
PALJOUSRAJA = 10
ILMAISEN_TOIMITUKSEN_RAJA = 5_000
KANTA_ASIAKKAAN_RAJA = 3_000
TOIMITUSMAKSU = 590


def euroina(sentit: int) -> str:
    return f"{sentit // 100},{sentit % 100:02d}"


# @alku saannot
@dataclass(frozen=True)
class Rivi:
    tuote: str
    yksikkohinta: int
    maara: int

    def hinta(self) -> int:
        perus = self.yksikkohinta * self.maara
        if self.maara >= PALJOUSRAJA:
            return perus - perus // 10
        return perus


def alennusprosentti(kanta_asiakas: bool, valisumma: int,
                     koodi: str) -> int:
    prosentti = 0
    if kanta_asiakas:
        prosentti = 10 if valisumma > 10_000 else 5
    if koodi == "KESA":
        prosentti = 10 if prosentti < 10 else 15
    return prosentti


def toimitusmaksu(kanta_asiakas: bool, summa: int, riveja: int) -> int:
    if riveja == 0 or summa >= ILMAISEN_TOIMITUKSEN_RAJA:
        return 0
    if kanta_asiakas and summa >= KANTA_ASIAKKAAN_RAJA:
        return 0
    return TOIMITUSMAKSU
# @loppu saannot


# @alku lasku
def lasku(nimi: str, asiakastyyppi: int, rivit: list[tuple[str, int, int]],
          koodi: str) -> str:
    kanta_asiakas = asiakastyyppi == KANTA_ASIAKAS
    ostokset = [Rivi(*rivi) for rivi in rivit]
    summa = sum(rivi.hinta() for rivi in ostokset)

    tuloste = [f"LASKU {nimi}"]
    tuloste += [f"{r.tuote} x{r.maara}  {euroina(r.hinta())}"
                for r in ostokset]
    if koodi not in ("", "KESA"):
        tuloste.append(f"Tuntematon koodi {koodi}")
    prosentti = alennusprosentti(kanta_asiakas, summa, koodi)
    if prosentti > 0:
        alennus = summa * prosentti // 100
        tuloste.append(f"Alennus {prosentti} %  -{euroina(alennus)}")
        summa -= alennus
    toimitus = toimitusmaksu(kanta_asiakas, summa, len(ostokset))
    tuloste.append(f"Toimitus  {euroina(toimitus)}")
    tuloste.append(f"YHTEENSÄ  {euroina(summa + toimitus)}")
    return "\n".join(tuloste) + "\n"
# @loppu lasku
