<!-- Generoitu tiedostosta gpio.json (gen/rekisterit.py). Älä muokkaa. -->
# gpio

Yleiskäyttöiset 8-bittiset tulot ja lähdöt

## ULOS (0x000)

Tyyppi rw, 8 bittiä, nollausarvo 0x0. Lähtöjen tila.

## SISAAN (0x004)

Tyyppi ro, 8 bittiä, nollausarvo 0x0. Tulojen tila (tahdistettu).

## SALLI (0x008)

Tyyppi rw, 8 bittiä, nollausarvo 0x0. Keskeytykset sallittu tulon
nousevalla reunalla.

## REUNAT (0x00C)

Tyyppi w1c, 8 bittiä, nollausarvo 0x0. Havaitut nousevat reunat; ykkösen
kirjoitus nollaa.
