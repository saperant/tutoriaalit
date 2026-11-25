# Ohjeet

## Aseman valinta

Valitsin `--asema` on pakollinen. Jos asemalta ei ole lukemia, ohjelma
kertoo sen ja palauttaa arvon 1:

<!-- komento: python3 -m saa lukemat.csv --asema oulu -->
```text
virhe: asemalta oulu ei ole lukemia
```

## Virheilmoitukset

Ohjelma pysähtyy ensimmäiseen virheelliseen riviin. Ilmoitus alkaa
kentän nimellä:

| Ilmoitus alkaa | Syy | Korjaus |
|---|---|---|
| `aika:` | aika ei ole ISO 8601 -muodossa tai aikavyöhyke puuttuu | lisää aikavyöhyke, esimerkiksi `+02:00` |
| `lampotila_c:` | arvo ei ole luku tai se on alle -60 tai yli 60 | tarkista anturin kytkentä |
| `kosteus:` | arvo ei ole välillä 0-100 | jätä kenttä tyhjäksi, jos anturia ei ole |
