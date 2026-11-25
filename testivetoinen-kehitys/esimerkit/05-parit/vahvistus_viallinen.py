"""Tilausvahvistus, josta yhden yhdistelmän teksti on unohtunut."""

PARAMETRIT = {
    "maksutapa": ["kortti", "lasku", "mobiili"],
    "toimitus": ["nouto", "posti", "automaatti"],
    "asiakas": ["yksityinen", "yritys"],
    "kieli": ["fi", "sv", "en"],
}

OTSIKKO = {"fi": "Tilausvahvistus", "sv": "Orderbekräftelse",
           "en": "Order confirmation"}
TOIMITUSOHJE = {
    ("nouto", "fi"): "Nouda tilaus myymälästä.",
    ("nouto", "sv"): "Hämta din order i butiken.",
    ("nouto", "en"): "Collect your order at the store.",
    ("posti", "fi"): "Tilaus toimitetaan postitse.",
    ("posti", "sv"): "Ordern levereras per post.",
    ("posti", "en"): "Your order is delivered by mail.",
    ("automaatti", "fi"): "Saat noutokoodin tekstiviestinä.",
    ("automaatti", "en"): "You will get a pickup code by text.",
}
ERAPAIVA = {"fi": "Eräpäivä 14 päivää.", "sv": "Förfallodag 14 dagar.",
            "en": "Payment due in 14 days."}


def vahvistus(maksutapa: str, toimitus: str, asiakas: str,
              kieli: str) -> str:
    rivit = [OTSIKKO[kieli], TOIMITUSOHJE[(toimitus, kieli)]]
    if maksutapa == "lasku":
        rivit.append(ERAPAIVA[kieli])
    if asiakas == "yritys":
        rivit.append("ALV 0 %" if kieli == "en" else "ALV 25,5 %")
    return "\n".join(rivit)
