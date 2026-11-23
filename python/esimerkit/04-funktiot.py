"""Parametrilajit ja argumenttien purku."""

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
