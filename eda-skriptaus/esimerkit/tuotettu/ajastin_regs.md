<!--
   Tuotettu tiedostosta asetukset/rekisterit.toml (vuo/rekisterit.py).
   Älä muokkaa käsin: muutokset tehdään kuvaukseen.
-->

# Lohko ajastin

Perusosoite 0x40001000, rekisterit 32-bittisiä.

## CTRL (+0x00): Ohjaus

| Bitit | Kenttä | Pääsy | Nollaus | Kuvaus |
|-------|--------|-------|---------|--------|
| 0 | EN | rw | 0x0 | Ajastin käy |
| 1 | IE | rw | 0x0 | Keskeytys sallittu |
| 15:8 | JAKAJA | rw | 0x1 | Kellon jakaja |

## STATUS (+0x04): Tila

| Bitit | Kenttä | Pääsy | Nollaus | Kuvaus |
|-------|--------|-------|---------|--------|
| 0 | VALMIS | w1c | 0x0 | Vertailuarvo saavutettu |

## LASKURI (+0x08): Laskurin arvo

| Bitit | Kenttä | Pääsy | Nollaus | Kuvaus |
|-------|--------|-------|---------|--------|
| 15:0 | ARVO | ro | 0x0 | Nykyinen arvo |

## VERTAA (+0x0C): Vertailuarvo

| Bitit | Kenttä | Pääsy | Nollaus | Kuvaus |
|-------|--------|-------|---------|--------|
| 15:0 | ARVO | rw | 0xFFFF | Arvo, jolla VALMIS asettuu |
