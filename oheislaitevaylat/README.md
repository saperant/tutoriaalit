# Oheislaiteväylät

Tiivis suomenkielinen tutoriaali sulautettujen järjestelmien
sarjaväylistä ja niiden ajureista: väylien sähköiset perusteet, UART,
SPI, I2C, CAN, DMA ja ajurikerrosten suunnittelu ja testaus. Valmiit
dokumentit:
[oheislaitevaylat.pdf](https://saperant.github.io/tutoriaalit/materiaalit/oheislaitevaylat.pdf)
ja pikaopas
[oheislaitevaylat-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/oheislaitevaylat-pikaopas.pdf).

## Sisältö

1. Johdanto – laboratorio: QEMU:n emuloidut väylälaitteet ja
   Python-mallit, oheislaitteiden tunnistus
2. Väylien perusteet – synkroninen ja asynkroninen siirto, topologia,
   avokollektori ja vetovastuksen mitoitus, jännitetasot, väylien
   vertailu (myös LIN, 1-Wire, I2S ja USB)
3. UART – kehys, vastaanotin, nopeuden virhe ja sieto,
   keskeytysohjattu lähetys, vuonohjaus, COBS ja CRC, RS-485
4. SPI – moodit, PL022-ajuri, A/D-muunnin, ketjutus, SPI-flash
5. I2C – ehdot ja kuittaukset, rekisterien luku, kellonvenytys,
   arbitraatio, jumiutuneen väylän vapautus, ohjelmallinen isäntä
6. CAN – fyysinen kerros, kehys ja bittitäyttö, virheet, arbitraatio,
   virhelaskurit, bitin ajoitus, ISO-TP, CAN FD
7. DMA – kanavat, kuvaajaketjut, muistiaidat, välimuisti
8. Ajurikerrokset – rajapinnat, EEPROM-ajuri, testaus isäntäkoneella,
   pollaus, keskeytys ja DMA, aikarajat
9. Lopuksi – nyrkkisäännöt, oikeaan laitteeseen, jatkotaidot, lähteet

## Esimerkit

- `esimerkit/NN-nimi/` ovat Cortex-M-ohjelmia QEMU:n
  `mps2-an385`-kortille (DMA: `mps2-an505`). QEMU kytkee väyliin
  lämpötila-anturin, EEPROMin ja A/D-muuntimen, ja UART1 lukee ja
  kirjoittaa tiedostoja. Tuloste ja paluuarvo verrataan tiedostoon
  `esimerkit/testit/<nimi>.odotettu`.
- `esimerkit/ajurit/` sisältää väyläohjaimet (PL022, SBCon-I2C),
  I2C-rajapinnan ja EEPROM-ajurin; `esimerkit/isanta/` testaa ne
  isäntäkoneella sanitoijien kanssa laitemallia ja rekisterisivua
  vastaan.
- `esimerkit/python/` sisältää UARTin, SPI:n, I2C:n ja CANin
  bittitason mallit, niiden yksikkötestit (pytest) ja esimerkit;
  tarkistukset tekevät ruff ja `mypy --strict`.
- `esimerkit/kaaviot/` sisältää kirjan ajoituskaaviot, jotka
  `python/aaltokaaviot.py` tuottaa malleista; testi tarkistaa, että ne
  ovat ajan tasalla. Luvun 2 kuva (`kuvat/nousuaika.png`) tuotetaan
  komennolla `make kuvat` (Matplotlib).

## Rakentaminen

```text
make testaa   # rakenne ja esimerkit (esimerkit/Makefile)
make pdf      # tutoriaali ja pikaopas
```

Tarvitaan `gcc-arm-none-eabi`, `libnewlib-arm-none-eabi`,
`qemu-system-arm`, isäntäkoneen C-kääntäjä sekä Pythonin `ruff`, `mypy`
ja `pytest`; kehityskontissa (`.devcontainer/oheislaitevaylat`) ne
ovat valmiina.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.
