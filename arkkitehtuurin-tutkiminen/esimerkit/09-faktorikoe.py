"""2^k-faktorikoe: kolmen tekijän pää- ja yhdysvaikutukset kahdeksalla
arvioinnilla (Jain 1991, luku 17)."""

from itertools import combinations, product

from arkki.siru import Kuorma, arvioi

# @alku tekijat
# Tekijä: (nimi, alataso, ylätaso). Kaksi ensimmäistä ovat kuorman
# oletuksia, kolmas suunnittelupäätös.
TEKIJAT: list[tuple[str, float, float]] = [
    ("kaista", 12.5, 50.0), ("mpki", 1.5, 6.0), ("ytimen koko", 1, 4)]


def vaste(kaista: float, mpki: float, r: float) -> float:
    """Suorituskyky (käskyä / ns); välimuisti 16 MiB ja jännite 0,8 V."""
    k = Kuorma(rinnakkainen=0.99, mpki=mpki, kaista=kaista)
    return arvioi(r, 16, 0.8, k).kaskyja_ns
# @loppu tekijat


# @alku vaikutukset
def vaikutukset(y: dict[tuple[int, ...], float], k: int
                ) -> dict[tuple[int, ...], float]:
    """Vaikutus = vasteen keskiarvo ylätasolla - keskiarvo alatasolla.
    Yhdysvaikutuksen merkki on tekijöiden merkkien tulo."""
    tulos = {}
    for koko in range(1, k + 1):
        for joukko in combinations(range(k), koko):
            summa = 0.0
            for tasot, arvo in y.items():
                merkki = 1
                for i in joukko:
                    merkki *= tasot[i]
                summa += merkki * arvo
            tulos[joukko] = summa / (len(y) / 2)
    return tulos
# @loppu vaikutukset


def main() -> None:
    k = len(TEKIJAT)
    y = {}
    for tasot in product((-1, 1), repeat=k):
        arvot = [t[1] if s < 0 else t[2]
                 for t, s in zip(TEKIJAT, tasot, strict=True)]
        y[tasot] = vaste(*arvot)
    v = vaikutukset(y, k)
    # Vaihtelun jako: neliösumma on verrannollinen vaikutuksen neliöön.
    yhteensa = sum(e * e for e in v.values())
    print(f"{'tekijät':<28} {'vaikutus':>9} {'osuus vaihtelusta':>18}")
    for joukko, e in sorted(v.items(), key=lambda p: -abs(p[1])):
        nimi = " x ".join(TEKIJAT[i][0] for i in joukko)
        print(f"{nimi:<28} {e:+9.2f} {e * e / yhteensa:18.1%}")


if __name__ == "__main__":
    main()
