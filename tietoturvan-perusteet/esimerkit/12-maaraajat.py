"""Ilmoitusten määräajat tietoturvapoikkeamassa (GDPR, NIS2, CRA).

Määräajat ovat yksinkertaistuksia: ne lasketaan siitä, kun organisaatio
sai tiedon poikkeamasta. Tarkat ehdot ovat säädöksissä (luku 12).
"""

from datetime import datetime, timedelta

# @alku maaraajat
MAARAAJAT = [
    ("NIS2/kyberturvallisuuslaki", "varhainen varoitus", timedelta(hours=24)),
    ("NIS2/kyberturvallisuuslaki", "poikkeamailmoitus", timedelta(hours=72)),
    ("NIS2/kyberturvallisuuslaki", "loppuraportti",
     timedelta(hours=72) + timedelta(days=30)),
    ("GDPR art. 33", "ilmoitus tietosuojavaltuutetulle",
     timedelta(hours=72)),
    ("CRA art. 14", "varhainen varoitus (hyödynnetty haavoittuvuus)",
     timedelta(hours=24)),
    ("CRA art. 14", "haavoittuvuusilmoitus", timedelta(hours=72)),
]
# @loppu maaraajat

havaittu = datetime(2026, 11, 20, 9, 15)
print(f"tieto poikkeamasta perjantaina {havaittu:%d.%m. %H:%M}")
print("määräajat kulkevat myös viikonloppuna:")
for saados, ilmoitus, aika in sorted(MAARAAJAT, key=lambda m: m[2]):
    print(f"{havaittu + aika:%d.%m. %H:%M}  {saados}: {ilmoitus}")
