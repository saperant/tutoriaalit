"""Muodostaa käyttäjätunnuksen henkilön nimestä."""

KORVAUKSET = str.maketrans({"ä": "a", "ö": "o", "å": "a", "-": ""})


def kayttajatunnus(koko_nimi: str) -> str:
    """'  Väinö  ÅKERMAN-Öhrn ' -> 'vaino.akermanohrn'"""
    osat = koko_nimi.lower().split()          # pilkkoo välilyönneistä
    etunimi, sukunimi = osat[0], osat[-1]     # keskimmäiset ohitetaan
    return f"{etunimi}.{sukunimi}".translate(KORVAUKSET)


def siisti_nimi(koko_nimi: str) -> str:
    """Poistaa ylimääräiset välit ja korjaa kirjainkoon."""
    return " ".join(koko_nimi.split()).title()


for nimi in ["  Väinö  ÅKERMAN-Öhrn ", "anna maria virtanen", "Li Wu"]:
    print(f"{siisti_nimi(nimi):<20} -> {kayttajatunnus(nimi)}")

sahkoposti = "aino.virtanen@example.org"
kayttaja, _, verkkotunnus = sahkoposti.partition("@")
print(kayttaja, verkkotunnus, sahkoposti.endswith(".org"))
print(sahkoposti[:4], sahkoposti.find("@"), len(sahkoposti))
