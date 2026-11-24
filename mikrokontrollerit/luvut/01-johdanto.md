# Johdanto {.runko-johdanto}

Mikrokontrolleri on kokonainen tietokone yhdellä piirillä: prosessori,
flash-muisti ohjelmalle, RAM muuttujille ja joukko oheislaitteita,
kuten ajastimia, sarjaportteja ja yleiskäyttöisiä I/O-nastoja. Se
löytyy pesukoneesta, kuulokkeista, auton ovesta ja teollisuuden
antureista. Tyypillisessä piirissä on kymmeniä tai satoja kilotavuja
flashia, muutamia kymmeniä kilotavuja RAMia ja kello muutamasta
megahertsistä muutamaan sataan.

Tällaisessa laitteessa ei usein ole käyttöjärjestelmää. Ohjelma
käynnistyy suoraan virran kytkeytyessä, omistaa koko muistin ja ohjaa
oheislaitteita kirjoittamalla niiden rekistereihin. Tätä kutsutaan
*bare-metal*-ohjelmoinniksi: ohjelman ja raudan välissä ei ole mitään.
Sama tieto on pohjana myös silloin, kun laitteessa ajetaan
reaaliaikakäyttöjärjestelmää (RTOS): sen ytimen ja ajurien
kirjoittaja tekee juuri sitä, mitä tässä tutoriaalissa opetellaan.

Tutoriaali käsittelee

- **Cortex-M-arkkitehtuuria**: rekisterit, tilat, pinot,
  muistikartta ja poikkeusmalli
- **käynnistystä**: vektoritaulu, käynnistyskoodi ja linkkeriskripti,
  joka sijoittaa ohjelman flashiin ja muuttujat RAMiin
- **oheislaitteiden ohjausta**: muistiin kuvatut rekisterit,
  `volatile`, bittikentät ja GPIO
- **keskeytyksiä ja ajastimia**: NVIC, prioriteetit, SysTick ja
  laitteen ajastimet
- **jaettua dataa**: kilpailutilanteet keskeytyksen ja pääohjelman
  välillä, kriittiset osiot, LDREX/STREX ja rengaspuskuri
- **virransäästöä**: WFI, WFE ja oikea nukkumisen kaava
- **vikoja ja debuggausta**: HardFault ja sen syyt, MPU, SWD ja gdb
- **ohjelman rakennetta**: pääsilmukka, tapahtumajono ja tilakone,
  jonka logiikka testataan isäntäkoneella.

Esitiedoiksi oletetaan C-kieli, tietokoneen rakenteen perusteet
(rekisterit, muisti, pino, keskeytyksen idea, taito
*Tietokonearkkitehtuuri*) sekä käännöksen ja linkityksen vaiheet
(objektitiedostot, osiot, symbolit, taito *Binäärit ja linkitys*).
Konekieltä ei tarvitse osata kirjoittaa, mutta sitä täytyy pystyä
lukemaan, koska bare-metal-ohjelmassa muutama käsky on aina
kirjoitettava assemblynä. Taidot *Oheislaiteväylät* (UART, SPI, I2C,
DMA), *Reaaliaikakäyttöjärjestelmät* ja *Sulautettujen järjestelmien
tietoturva* jatkavat tästä.

## Laboratorio

Oikea kehityskortti on hyvä hankinta, mutta tutoriaalin esimerkit
ajetaan emulaattorissa, jotta jokainen tuloste voidaan testata. Kohde
on ARM:n MPS2-kehityskortin kokoonpano AN385, jossa on Cortex-M3 ja
ARM:n CMSDK-oheislaitteet (UART, ajastimet, LEDit). QEMU mallintaa sen
nimellä `mps2-an385`:

| Osa | Tässä | Tyypillinen oikea piiri |
|-----|-------|-------------------------|
| Prosessori | Cortex-M3, 25 MHz | Cortex-M0+, M3, M4 tai M33 |
| Ohjelmamuisti | 256 KiB flashina (`0x00000000`) | 32 KiB–2 MiB flash |
| RAM | 64 KiB (`0x20000000`) | 4–512 KiB SRAM |
| Konsoli | CMSDK UART0 | valmistajan UART tai USB |
| Lopetus | semihosting (`bkpt 0xab`) | ei: laite pyörii ikuisesti |

Kääntäjä on GNU-työkaluketjun ristikääntäjä `arm-none-eabi-gcc`:
`arm` kertoo arkkitehtuurin, `none` puuttuvan käyttöjärjestelmän ja
`eabi` kutsukonvention. Mukana tuleva C-kirjasto *newlib-nano* tarjoaa
funktiot kuten `memcpy` ja `strcmp`; esimerkit eivät käytä sen
syöte- ja tulostefunktioita.

Jokainen esimerkki on oma hakemistonsa `esimerkit/NN-nimi/`, jonka
`main.c` linkitetään yhteisen koodin kanssa (`esimerkit/yhteinen/`):
käynnistyskoodi, linkkeriskripti, rekisterimäärittelyt, UART-konsoli
ja semihosting-lopetus. Makefile kääntää, ajaa ja vertaa:

```{.make tiedosto="esimerkit/Makefile" osa="liput"}
```

Liput selitetään luvussa 3. QEMU:n valitsimista `-nographic` ja
`-serial stdio` ohjaavat sarjaportin päätteeseen ja
`-semihosting-config` sallii ohjelman lopettaa emulaattorin. Ohjelman
tuloste ja paluuarvo verrataan tiedostoon `testit/<esimerkki>.odotettu`:

```{.make tiedosto="esimerkit/Makefile" osa="ajo"}
```

Komennot esimerkkihakemistossa:

```text
make                  # kaikki esimerkit: käännös, ajo ja vertailu
make aja E=04-ledit   # yksi esimerkki päätteessä (keskeytys: Ctrl-c)
make gdb E=04-ledit   # pysäytettynä, odottaa gdb:tä portissa 1234
make siivoa
```

Tarvittavat paketit (Debian ja Ubuntu) ovat `gcc-arm-none-eabi`,
`libnewlib-arm-none-eabi`, `qemu-system-arm` ja `gdb-multiarch`.
Kehityskontissa `.devcontainer/mikrokontrollerit` ne ovat valmiina.

## Ensimmäinen ohjelma

```{.c tiedosto="esimerkit/01-hei/main.c" osa="main"}
```

```{.tuloste tiedosto="esimerkit/testit/01-hei.odotettu"}
```

Ohjelma näyttää tavalliselta C:ltä, mutta lähes kaikki tuttu puuttuu:
`main` ei saa argumentteja, `printf` ei ole käytössä (konsolin
`tulosta` on omatekoinen, noin sadan rivin funktio) ja paluuarvolla ei
normaalisti ole vastaanottajaa. Ennen `main`ia on kuitenkin
tapahtunut paljon: prosessori on lukenut pinon osoitteen ja
ensimmäisen käskyn osoitteen flashin alusta, käynnistyskoodi on
alustanut muuttujat, ja `konsoli_alusta` on kirjoittanut UART:n
rekistereihin jakajan ja käyttöönottobitit. Seuraavat luvut käyvät
nämä vaiheet läpi yksi kerrallaan.

QEMU on hyvä mutta ei täydellinen malli. Se suorittaa käskyt oikein ja
mallintaa NVIC:n, SysTickin ja oheislaitteet, mutta ei ajoitusta:
käskyt eivät kuluta kellojaksoja, odotustiloja tai väylän
kilpailua ei ole, eikä virrankulutusta voi mitata. Esimerkit on
rakennettu niin, että tulos ei riipu ajoituksesta; tekstissä kerrotaan,
missä oikea piiri käyttäytyy toisin.
