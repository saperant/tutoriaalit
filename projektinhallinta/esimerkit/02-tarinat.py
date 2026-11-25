"""Vaatimukset datana: tuotejonon tarinat tarkistetaan koneellisesti.

Tarkistin ei arvioi, onko tarina oikea, mutta se löytää puuttuvat
hyväksymiskriteerit, liian suuret tarinat ja kehäriippuvuudet.
"""

from dataclasses import dataclass, field


# @alku tarina
@dataclass(frozen=True)
class Tarina:
    tunnus: str
    rooli: str            # kuka tarvitsee
    tavoite: str          # mitä hän haluaa tehdä
    hyoty: str            # miksi
    kriteerit: tuple[str, ...] = ()
    koko: int | None = None           # arvio päivinä
    edellyttaa: tuple[str, ...] = ()
    vaihe: str = ""                   # käyttäjän toiminto tarinakartassa
    julkaisu: int = 1


@dataclass
class Tuotejono:
    tarinat: list[Tarina] = field(default_factory=list)
# @loppu tarina


JONO = Tuotejono([
    Tarina("T-1", "asiakas", "hakea tuotteita nimellä",
           "löydän haluamani nopeasti",
           ("haku palauttaa osumat alle sekunnissa",
            "tyhjä haku näyttää ohjeen"), 3, (), "Etsi", 1),
    Tarina("T-2", "asiakas", "lisätä tuotteen ostoskoriin",
           "voin ostaa useita tuotteita kerralla",
           ("kori säilyy uudelleenkirjautumisen yli",), 2, ("T-1",),
           "Kerää", 1),
    Tarina("T-3", "asiakas", "maksaa verkkopankissa",
           "saan tilauksen heti käsittelyyn",
           ("epäonnistunut maksu ei luo tilausta",
            "maksusta tulee kuitti sähköpostiin"), 8, ("T-2",),
           "Maksa", 1),
    Tarina("T-4", "asiakas", "suodattaa hakua hinnan mukaan",
           "näen vain budjettiini sopivat", (), 2, ("T-1",), "Etsi", 2),
    Tarina("T-5", "ylläpitäjä", "tuoda tuotteet tiedostosta", "",
           ("virheellinen rivi raportoidaan rivinumerolla",), 13, (),
           "Ylläpidä", 2),
    Tarina("T-6", "asiakas", "tallentaa korin myöhemmäksi",
           "voin jatkaa ostoksia toisella laitteella",
           ("tallennettu kori näkyy kirjautumisen jälkeen",), None,
           ("T-7",), "Kerää", 2),
    Tarina("T-7", "asiakas", "kirjautua sähköpostilla",
           "en tarvitse uutta salasanaa",
           ("kirjautumislinkki vanhenee 15 minuutissa",), 3, ("T-6",),
           "Kerää", 2),
])
SUURIN_KOKO = 8     # sitä suurempi tarina pilkotaan


# @alku tarkistus
def keha(jono: Tuotejono, alku: Tarina) -> bool:
    """Onko tarinasta polku riippuvuuksia pitkin takaisin itseensä?"""
    tunnuksella = {t.tunnus: t for t in jono.tarinat}
    pino, nahty = list(alku.edellyttaa), set[str]()
    while pino:
        tunnus = pino.pop()
        if tunnus == alku.tunnus:
            return True
        if tunnus not in nahty and tunnus in tunnuksella:
            nahty.add(tunnus)
            pino.extend(tunnuksella[tunnus].edellyttaa)
    return False


def puutteet(jono: Tuotejono, t: Tarina) -> list[str]:
    loydokset = []
    if not t.hyoty:
        loydokset.append("hyöty puuttuu: miksi tämä tehdään?")
    if not t.kriteerit:
        loydokset.append("ei hyväksymiskriteerejä: ei voi testata")
    if t.koko is None:
        loydokset.append("ei arviota")
    elif t.koko > SUURIN_KOKO:
        loydokset.append(f"koko {t.koko} pv > {SUURIN_KOKO}: pilko")
    if keha(jono, t):
        loydokset.append("kehäriippuvuus")
    return loydokset
# @loppu tarkistus


for tarina in JONO.tarinat:
    for loydos in puutteet(JONO, tarina):
        print(f"{tarina.tunnus}: {loydos}")

# @alku kartta
print()
vaiheet = list(dict.fromkeys(t.vaihe for t in JONO.tarinat))
print("julkaisu  " + "".join(f"{v:<16}" for v in vaiheet))
for julkaisu in sorted({t.julkaisu for t in JONO.tarinat}):
    solut = [",".join(t.tunnus for t in JONO.tarinat
                      if t.vaihe == v and t.julkaisu == julkaisu)
             for v in vaiheet]
    print(f"{julkaisu:<10}" + "".join(f"{s or '-':<16}" for s in solut))
# @loppu kartta
