"""Parametrilajit, argumenttien purku ja dokumentaatiomerkkijono."""

import math
from functools import partial


# @alku parametrit
def siirto(lahde: str, kohde: str, /, *, ylikirjoita: bool = False,
           yritykset: int = 3) -> str:
    """lahde ja kohde vain paikan mukaan, asetukset vain nimellä."""
    tila = "ylikirjoittaen" if ylikirjoita else "turvallisesti"
    return f"{lahde} -> {kohde} {tila}, {yritykset} yritystä"


print(siirto("a.txt", "b.txt"))
print(siirto("a.txt", "b.txt", ylikirjoita=True, yritykset=1))
# @loppu parametrit


# @alku vaihteleva
def keskiarvo(*luvut: float, pyoristys: int = 2) -> float:
    return round(sum(luvut) / len(luvut), pyoristys)


def kirjaa(viesti: str, **kentat: object) -> str:
    lisat = " ".join(f"{k}={v}" for k, v in sorted(kentat.items()))
    return f"{viesti} {lisat}".strip()


mittaukset = [21.5, 22.0, 19.75]
print(keskiarvo(*mittaukset))                 # lista argumenteiksi
konteksti = {"kayttaja": "ada", "kesto_ms": 12}
print(kirjaa("pyyntö käsitelty", **konteksti))
# @loppu vaihteleva

# @alku partial
varmuuskopio = partial(siirto, ylikirjoita=False, yritykset=5)
print(varmuuskopio("tietokanta.db", "tietokanta.bak"))
# @loppu partial


# @alku docstring
def betonimaara(leveys_m: float, pituus_m: float, paksuus_cm: float) -> float:
    """Palauttaa laatan valuun tilattavan betonin määrän kuutiometreinä.

    Paksuus annetaan senttimetreinä kuten rakennepiirustuksissa. Tulos
    pyöristetään ylöspäin 0,1 m³:n tarkkuuteen, koska betoni tilataan
    sen kokoisissa erissä.

    Raises:
        ValueError: jos jokin mitta ei ole positiivinen.
    """
    if min(leveys_m, pituus_m, paksuus_cm) <= 0:
        raise ValueError("mittojen on oltava positiivisia")
    tilavuus = leveys_m * pituus_m * paksuus_cm / 100
    return math.ceil(round(tilavuus * 10, 6)) / 10


print(betonimaara(4.0, 6.5, 12))
print((betonimaara.__doc__ or "").splitlines()[0])
# @loppu docstring
