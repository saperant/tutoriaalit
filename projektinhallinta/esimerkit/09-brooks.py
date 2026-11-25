"""Brooksin laki: lisäväki myöhästyttää myöhässä olevaa projektia.

Malli: uusi tekijä pääsee täyteen tehoon vasta perehdytyksen jälkeen,
perehdytys vie kokeneiden aikaa, ja jokainen tiimiläinen käyttää osan
ajastaan yhteydenpitoon jokaisen muun kanssa.
"""

TYOTA = 80.0           # henkilötyöviikkoa jäljellä
TIIMI = 5
PEREHDYTYS = 8         # viikkoa täyteen tehoon
OHJAUS = 0.5           # kokeneen aikaa uutta kohden perehdytyksen ajan
YHTEYDENPITO = 0.01    # osuus ajasta jokaista muuta tiimiläistä kohden


# @alku polut
def viestintapolut(henkiloita: int) -> int:
    """Parien määrä: jokainen voi joutua sopimaan jokaisen kanssa."""
    return henkiloita * (henkiloita - 1) // 2
# @loppu polut


# @alku malli
def valmistumisviikko(lisays: int, lisaysviikko: int) -> float:
    """Viikko, jolla työ valmistuu, kun tiimiin tuodaan lisää väkeä."""
    jaljella, viikko = TYOTA, 0
    while True:
        uusia = lisays if viikko >= lisaysviikko else 0
        ollut = viikko - lisaysviikko          # viikkoja talossa
        osaaminen = min(1.0, ollut / PEREHDYTYS) if uusia else 0.0
        ohjaus = OHJAUS * uusia if 0 <= ollut < PEREHDYTYS else 0.0
        teho = (TIIMI - ohjaus) + uusia * osaaminen
        teho *= 1 - YHTEYDENPITO * (TIIMI + uusia - 1)
        if teho >= jaljella:
            return viikko + jaljella / teho
        jaljella -= teho
        viikko += 1
# @loppu malli


print("henkilöitä  viestintäpolkuja")
for n in (3, 5, 8, 12, 20):
    print(f"{n:10d}  {viestintapolut(n):16d}")

perus = valmistumisviikko(0, 0)
print(f"viiden hengen tiimi valmistuu viikolla {perus:.1f}")
print("kolme lisää viikolla   valmistuu   muutos")
for lisaysviikko in (0, 4, 8, 10, 12, 14):
    valmis = valmistumisviikko(3, lisaysviikko)
    print(f"{lisaysviikko:20d}   {valmis:9.1f}   {valmis - perus:+6.1f} vk")
