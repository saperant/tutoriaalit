# Ajastin (ajastin)

Tuotettu tiedostosta rdl/ajastin.rdl. Ala muokkaa kasin.

## CTRL (0x000): Ohjaus

| Bitit | Kentta | Paasy | Nollaus | Kuvaus |
|-------|--------|-------|---------|--------|
| 15:8 | JAKAJA | RW | 0x1 | Kellon jakaja. |
| 1 | IE | RW | 0x0 | Keskeytys sallittu. |
| 0 | EN | RW | 0x0 | Ajastin kay. |

## STATUS (0x004): Tila

| Bitit | Kentta | Paasy | Nollaus | Kuvaus |
|-------|--------|-------|---------|--------|
| 0 | VALMIS | W1C | 0x0 | Vertailuarvo saavutettu. 1 nollaa. (hwset, intr) |

## LASKURI (0x008): Laskurin arvo

| Bitit | Kentta | Paasy | Nollaus | Kuvaus |
|-------|--------|-------|---------|--------|
| 15:0 | ARVO | RO | - | Nykyinen arvo. |

## VERTAA (0x00C): Vertailuarvo

| Bitit | Kentta | Paasy | Nollaus | Kuvaus |
|-------|--------|-------|---------|--------|
| 15:0 | ARVO | RW | 0xFFFF | Arvo, jolla VALMIS asettuu. |
