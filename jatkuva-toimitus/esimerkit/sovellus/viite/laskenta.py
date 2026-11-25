"""Suomalaisen viitenumeron tarkiste.

Runko-osan numerot kerrotaan oikealta alkaen kertoimilla 7, 3, 1, 7, 3,
1, ... ja tulot lasketaan yhteen. Tarkiste on luku, joka täydentää
summan seuraavaan täyteen kymmeneen.
"""

KERTOIMET = (7, 3, 1)


# @alku tarkiste
def tarkiste(runko: str) -> int:
    """Palauttaa runko-osan tarkistenumeron."""
    if not runko.isascii() or not runko.isdigit():
        raise ValueError(f"runko ei ole numerosarja: {runko!r}")
    if not 3 <= len(runko) <= 19:
        raise ValueError("rungossa on oltava 3-19 numeroa")
    summa = sum(int(numero) * KERTOIMET[i % 3]
                for i, numero in enumerate(reversed(runko)))
    return (10 - summa % 10) % 10
# @loppu tarkiste


def muodosta(runko: str) -> str:
    """Palauttaa viitenumeron: runko ja tarkiste."""
    return runko + str(tarkiste(runko))


def kelpaa(viite: str) -> bool:
    """Tarkistaa, että viitenumeron viimeinen numero on oikea tarkiste."""
    tiivis = viite.replace(" ", "")
    try:
        return tiivis[-1:] == str(tarkiste(tiivis[:-1]))
    except ValueError:
        return False


def ryhmittele(viite: str) -> str:
    """Jakaa viitenumeron viiden numeron ryhmiin oikealta alkaen."""
    ryhmat = []
    loppu = len(viite)
    while loppu > 0:
        ryhmat.append(viite[max(0, loppu - 5):loppu])
        loppu -= 5
    return " ".join(reversed(ryhmat))
