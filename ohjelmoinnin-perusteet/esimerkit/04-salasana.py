"""Salasanan tarkistus: funktio palauttaa tuloksen, ei tulosta sitä."""


def salasanan_ongelmat(salasana: str, min_pituus: int = 12) -> list[str]:
    """Palauttaa listan salasanan puutteista. Tyhjä lista: kelpaa."""
    ongelmat = []
    if len(salasana) < min_pituus:
        ongelmat.append(f"alle {min_pituus} merkkiä")
    if salasana.lower() == salasana or salasana.upper() == salasana:
        ongelmat.append("ei sekä pieniä että isoja kirjaimia")
    if not any(merkki.isdigit() for merkki in salasana):
        ongelmat.append("ei numeroita")
    return ongelmat


for ehdokas in ["kissa123", "Kesäpäivä2026", "PITKÄJAKUMMALLINEN"]:
    ongelmat = salasanan_ongelmat(ehdokas)
    if ongelmat:
        print(f"{ehdokas}: hylätty ({', '.join(ongelmat)})")
    else:
        print(f"{ehdokas}: kelpaa")

# Avainsana-argumentti tekee kutsusta luettavan.
print(salasanan_ongelmat("Kissa123", min_pituus=8))
