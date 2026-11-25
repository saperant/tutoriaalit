# Toimintaohje: lukemien levy täynnä

- Hälytys: `saa_levy_vapaana_prosenttia < 10`
- Vaikutus: uudet lukemat hylätään, kun levy on täynnä. Asemat
  puskuroivat lukemia 24 tuntia, joten tietoa ei katoa heti.
- Omistaja: mittaustiimi

## Tarkista

1. Kirjaudu palvelimelle `saa-1`.
2. Katso levyn tila: `df -h /var/lib/saa`.
3. Katso suurimmat hakemistot: `du -sh /var/lib/saa/*`.

## Korjaa

1. Jos `arkisto` on suurin, siirrä yli vuoden vanhat tiedostot
   arkistopalvelimelle: `saa-arkistoi --vanhemmat 365`.
2. Jos `loki` on suurin, palvelu kirjoittaa virhettä toistuvasti.
   Katso viimeiset rivit ja avaa tiketti.

## Varmista

Hälytys poistuu, kun vapaata tilaa on yli 20 prosenttia. Tarkista
puolen tunnin kuluttua, että uusia lukemia tallentuu.

## Jos tämä ei auta

Soita päivystäjälle. Älä poista tiedostoja hakemistosta `lukemat`:
ne ovat ainoa kopio viimeisen vuorokauden mittauksista.

Katso myös projektin [yleiskuvaus](../README.md).
