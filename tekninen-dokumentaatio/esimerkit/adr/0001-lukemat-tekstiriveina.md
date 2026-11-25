# 0001. Asemat lähettävät lukemat tekstiriveinä

- Tila: hyväksytty
- Päivä: 2026-04-02

## Tausta

Asemien laiteohjelmisto ajetaan mikrokontrollerissa, jossa on 32
kilotavua muistia. Kenttähuollossa lukemia pitää voida lukea
sarjaportista ilman työkaluja.

## Päätös

Asema lähettää jokaisen lukeman yhtenä tekstirivinä, jonka kentät
erotetaan puolipisteellä: asema, aika, lämpötila ja kosteus.

## Seuraukset

Rivin voi lukea ja kirjoittaa käsin, ja jäsennin on kymmeniä rivejä.
Uuden kentän lisääminen muuttaa muotoa kaikille asemille yhtä aikaa,
koska rivissä ei ole versiota. JSON hylättiin, koska sen jäsennin ei
mahdu laitteen muistiin muun ohjelman rinnalle.
