"""Vaatimusten jäljitys: ETSI EN 303 645 ja EU:n kyberkestävyyssäädös.

Ohjelma vertaa laitteen ominaisuuksia kuluttajalaitteiden
kyberturvastandardin ETSI EN 303 645 lukuun 5 ja laskee
kyberkestävyyssäädöksen (CRA, asetus (EU) 2024/2847) ilmoitusten
määräajat aktiivisesti hyödynnetylle haavoittuvuudelle. Tarkista
tulkinnat aina voimassa olevista teksteistä: tämä on muistilista,
ei oikeudellinen arvio.
"""

from datetime import date, datetime, timedelta

# @alku etsi
ETSI = {
    "5.1": ("ei yleisiä oletussalasanoja", "laitekohtainen salasana"),
    "5.2": ("haavoittuvuusilmoitusten käsittely", "julkaistu käytäntö"),
    "5.3": ("ohjelmiston päivittäminen", "allekirjoitetut päivitykset"),
    "5.4": ("turvaparametrien suojattu tallennus", "avaimet suojassa"),
    "5.5": ("turvallinen tietoliikenne", "tls"),
    "5.6": ("hyökkäyspinnan minimointi", "debug lukittu"),
    "5.7": ("ohjelmiston eheys", "turvallinen käynnistys"),
    "5.8": ("henkilötietojen suojaus", "tls"),
    "5.9": ("häiriönsieto katkoksissa", "toimii ilman pilveä"),
    "5.10": ("telemetrian tarkastelu", "poikkeamien seuranta"),
    "5.11": ("käyttäjätietojen poistaminen", "tehdasasetukset"),
    "5.12": ("helppo asennus ja ylläpito", "asennusohje"),
    "5.13": ("syötteiden validointi", "syötteet tarkistetaan"),
}
# @loppu etsi

# @alku laite
LAITE = {
    "laitekohtainen salasana", "allekirjoitetut päivitykset",
    "tls", "turvallinen käynnistys", "tehdasasetukset",
    "asennusohje", "syötteet tarkistetaan",
}
# @loppu laite


# @alku cra
def ilmoitukset(havaittu: datetime,
                korjaus_saatavilla: datetime) -> list[tuple[str, datetime]]:
    """CRA 14 artikla: aktiivisesti hyödynnetty haavoittuvuus."""
    return [
        ("varhainen varoitus", havaittu + timedelta(hours=24)),
        ("haavoittuvuusilmoitus", havaittu + timedelta(hours=72)),
        ("loppuraportti", korjaus_saatavilla + timedelta(days=14)),
    ]


def tukiaika_paattyy(markkinoille: date, kayttoika_vuotta: int) -> date:
    """Tukiaika vastaa odotettua käyttöaikaa ja on vähintään viisi
    vuotta; lyhyempi se voi olla vain, jos tuotetta odotetusti käytetään
    alle viisi vuotta (CRA 13 artikla)."""
    vuosia = kayttoika_vuotta
    return markkinoille.replace(year=markkinoille.year + vuosia)
# @loppu cra


def main() -> None:
    puuttuu = [(k, nimi) for k, (nimi, ehto) in ETSI.items()
               if ehto not in LAITE]
    print(f"ETSI EN 303 645: {len(ETSI) - len(puuttuu)}/{len(ETSI)} "
          "täyttyy, puuttuu:")
    for kohta, nimi in puuttuu:
        print(f"  {kohta:5} {nimi}")
    havaittu = datetime(2027, 3, 1, 9, 30)
    for nimi, aika in ilmoitukset(havaittu, datetime(2027, 3, 8, 12, 0)):
        print(f"{nimi:22} viimeistään {aika:%d.%m.%Y klo %H.%M}")
    print("Tukiaika (markkinoille 1.6.2028, käyttöikä 8 v) päättyy",
          f"{tukiaika_paattyy(date(2028, 6, 1), 8):%d.%m.%Y}")


if __name__ == "__main__":
    main()
