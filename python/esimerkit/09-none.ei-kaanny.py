"""mypy löytää None-arvon käsittelyn unohtumisen ennen ajoa."""


def etsi_sahkoposti(kayttajat: dict[str, str], nimi: str) -> str | None:
    return kayttajat.get(nimi)


kayttajat = {"ada": "ada@example.com"}
osoite = etsi_sahkoposti(kayttajat, "ada")
print(osoite.upper())  # @virhe
if osoite is not None:
    print(osoite.upper())
