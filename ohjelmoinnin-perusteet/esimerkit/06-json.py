"""JSON: sisäkkäinen rakenne tiedostoon ja takaisin."""

import json

kurssi = {
    "nimi": "Ohjelmoinnin perusteet",
    "opintopisteet": 5,
    "avoin": True,
    "osallistujat": ["Aino", "Ville"],
}

with open("kurssi.json", "w", encoding="utf-8") as tiedosto:
    json.dump(kurssi, tiedosto, ensure_ascii=False, indent=2)

with open("kurssi.json", encoding="utf-8") as tiedosto:
    print(tiedosto.read())

with open("kurssi.json", encoding="utf-8") as tiedosto:
    luettu = json.load(tiedosto)
print(luettu == kurssi, luettu["osallistujat"][0])
