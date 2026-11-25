# Muutosloki

Tiedosto noudattaa Keep a Changelog -rakennetta, ja versiot ovat
semanttisia.

## [Julkaisematon]

### Lisätty

- Yhteenvedon voi hakea HTTP-rajapinnasta.

## [1.2.0] - 2026-11-20

### Lisätty

- Kosteus on valinnainen: asema ilman kosteusanturia jättää kentän
  tyhjäksi.

### Korjattu

- Aika ilman aikavyöhykettä hylätään. Aiemmin se tulkittiin palvelimen
  paikalliseksi ajaksi.

## [1.1.0] - 2026-09-02

### Lisätty

- Liukuva keskiarvo.

### Vanhentunut

- Funktio `keskiarvo` poistuu versiossa 2.0.0. Käytä funktiota
  `yhteenveto`.

## [1.0.0] - 2026-05-14

### Lisätty

- Lukemarivien jäsennys ja aseman yhteenveto.
