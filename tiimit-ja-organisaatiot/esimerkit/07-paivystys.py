"""Päivystysringin mitoitus: osuus ajasta ja häiriöiden kuorma."""

PAIVYSTAJIA_KERRALLA = 2       # ensisijainen ja varalla oleva
ENIMMAISOSUUS = 0.25           # päivystystä enintään neljännes ajasta
TUNTIA_HAIRIOSTA = 6           # selvitys, korjaus ja jälkiselvitys
TYOTUNNIT_VIIKOSSA = 37.5


# @alku rinki
def paivystysosuus(tiimin_koko: int) -> float:
    """Osuus viikoista, jolloin yksi henkilö on päivystysvuorossa."""
    return PAIVYSTAJIA_KERRALLA / tiimin_koko


print("tiimin koko  päivystysosuus  kestävä")
for koko in (3, 4, 6, 8, 10):
    osuus = paivystysosuus(koko)
    kestava = "kyllä" if osuus <= ENIMMAISOSUUS else "ei"
    print(f"{koko:>11}{osuus:>15.0%}  {kestava}")
# @loppu rinki

# @alku kuorma
print("häiriöitä/vk  tunteja  osuus ensisijaisen työviikosta")
for hairioita in (1, 2, 4, 7):
    tunnit = hairioita * TUNTIA_HAIRIOSTA
    print(f"{hairioita:>12}{tunnit:>9}  "
          f"{tunnit / TYOTUNNIT_VIIKOSSA:.0%}")
# @loppu kuorma
