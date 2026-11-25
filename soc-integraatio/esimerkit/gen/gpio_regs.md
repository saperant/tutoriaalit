<!-- Generoitu tiedostosta gpio.toml (gen/rekisterit.py). Älä muokkaa. -->
# gpio

Yleiskäyttöiset 8-bittiset tulot ja lähdöt

## ULOS (0x000)

Pääsy rw, 8 bittiä, nollausarvo 0x0. Lähtöjen tila.

## SISAAN (0x004)

Pääsy ro, 8 bittiä, nollausarvo 0x0. Tulojen tila (tahdistettu).

## SALLI (0x008)

Pääsy rw, 8 bittiä, nollausarvo 0x0. Keskeytykset sallittu tulon
nousevalla reunalla.

## REUNAT (0x00C)

Pääsy w1c, 8 bittiä, nollausarvo 0x0. Havaitut nousevat reunat; ykkösen
kirjoitus nollaa.
