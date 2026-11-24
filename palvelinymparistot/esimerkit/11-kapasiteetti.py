"""Kapasiteetin ennustaminen: milloin levytila loppuu?

Kuukausittaisesta käyttöhistoriasta sovitetaan suora (pienimmän
neliösumman menetelmä), ja ennuste kertoo, milloin käyttö ylittää
hälytysrajan. Hankinta on aloitettava hankinta-ajan verran ennen
sitä. Lineaarinen malli sopii tasaiseen kasvuun; kausivaihtelu ja
kertaluonteiset siirrot on huomioitava erikseen.
"""

from statistics import linear_regression

KAPASITEETTI_TT = 120
RAJA = 0.80                 # laajennus ennen kuin käyttö ylittää 80 %
HANKINTA_KK = 3             # tilaus, toimitus ja asennus

# Käyttö teratavuina kuukausittain (tammikuu 2026 = kuukausi 0).
KAYTTO = [61.0, 63.1, 64.8, 67.2, 69.0, 70.9, 73.4, 75.0, 77.1, 79.3,
          81.0]


# @alku ennuste
def kuukausi_jolloin(kaytto: list[float], kynnys: float) -> float:
    kuukaudet = list(range(len(kaytto)))
    kulmakerroin, vakio = linear_regression(kuukaudet, kaytto)
    return (kynnys - vakio) / kulmakerroin
# @loppu ennuste


def nimi(kuukausi: float) -> str:
    vuosi, kk = divmod(int(kuukausi), 12)
    return f"{kk + 1}/{2026 + vuosi}"


def main() -> None:
    kulmakerroin, _ = linear_regression(range(len(KAYTTO)), KAYTTO)
    print(f"kasvu {kulmakerroin:.2f} Tt/kk, nyt "
          f"{KAYTTO[-1] / KAPASITEETTI_TT:.0%} käytössä")
    raja = kuukausi_jolloin(KAYTTO, RAJA * KAPASITEETTI_TT)
    taysi = kuukausi_jolloin(KAYTTO, KAPASITEETTI_TT)
    print(f"{RAJA:.0%} raja ylittyy:  {nimi(raja)}")
    print(f"tila loppuu:        {nimi(taysi)}")
    print(f"tilaa viimeistään:  {nimi(raja - HANKINTA_KK)}")


if __name__ == "__main__":
    main()
