<!-- Generoitu tiedostosta syscon.json (gen/rekisterit.py). Älä muokkaa. -->
# syscon

Järjestelmäohjain: tunniste, apurekisteri ja lopetus

## TUNNISTE (0x000)

Tyyppi vakio, 32 bittiä, nollausarvo 0x534F4331. SoC:n tunniste ASCII-
merkkeinä: "SOC1".

## APU (0x004)

Tyyppi rw, 32 bittiä, nollausarvo 0x0. Vapaasti käytettävä apurekisteri.

## LOPETA (0x008)

Tyyppi wo, 8 bittiä, nollausarvo 0x0. Simulaatio päättyy; arvo on
paluukoodi.
