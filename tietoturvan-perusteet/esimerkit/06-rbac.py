"""Roolipohjainen pääsynhallinta (RBAC): oikeudet rooleille."""

# @alku rbac
ROOLIT: dict[str, set[str]] = {
    "asiakaspalvelu": {"tilaus:lue", "asiakas:lue"},
    "varasto": {"tilaus:lue", "tilaus:toimita"},
    "talous": {"tilaus:lue", "lasku:lue", "lasku:hyvita"},
    "yllapito": {"kayttaja:hallitse"},
}
KAYTTAJIEN_ROOLIT = {
    "aino": {"asiakaspalvelu"},
    "pekka": {"varasto"},
    "liisa": {"talous", "asiakaspalvelu"},
}


def oikeudet(kayttaja: str) -> set[str]:
    roolit = KAYTTAJIEN_ROOLIT.get(kayttaja, set())
    return set().union(*(ROOLIT[r] for r in roolit))


def sallittu(kayttaja: str, oikeus: str) -> bool:
    return oikeus in oikeudet(kayttaja)   # oletuksena kielletty
# @loppu rbac


for kayttaja, oikeus in [("aino", "asiakas:lue"),
                         ("aino", "lasku:hyvita"),
                         ("liisa", "lasku:hyvita"),
                         ("pekka", "kayttaja:hallitse"),
                         ("vieras", "tilaus:lue")]:
    print(f"{kayttaja:<7} {oikeus:<18} {sallittu(kayttaja, oikeus)}")
print("Liisan oikeudet:", sorted(oikeudet("liisa")))
