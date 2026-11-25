# Cortex-M-arkkitehtuuri

ARM jakaa prosessoriytimensä kolmeen profiiliin. A-profiili
(Cortex-A) on sovellusprosessori, jossa on muistinhallintayksikkö ja
joka ajaa Linuxia tai Androidia. R-profiili (Cortex-R) on
reaaliaikaprosessori esimerkiksi kiintolevyohjaimiin ja auton
jarruihin. M-profiili (Cortex-M) on mikrokontrolleriprofiili: pieni,
ennustettava ja helppo ohjelmoida ilman käyttöjärjestelmää. Ytimen
tekee ARM, mutta piirin tekee valmistaja (ST, NXP, Nordic,
Microchip, Raspberry Pi, Infineon ja monet muut), joka lisää ytimen
ympärille muistit ja oheislaitteet. Siksi kaikki Cortex-M-piirit
käynnistyvät ja käsittelevät keskeytykset samalla tavalla, mutta
UART-rekisterit ovat joka valmistajalla erilaiset.

| Ydin | Arkkitehtuuri | Tyypillinen käyttö ja erot |
|------|---------------|-----------------------------|
| Cortex-M0, M0+ | ARMv6-M | pienin ja halvin; ei jakokäskyä, ei LDREX/STREX |
| Cortex-M3 | ARMv7-M | täysi Thumb-2, jakokäsky, bit-band, MPU |
| Cortex-M4 | ARMv7E-M | M3 + DSP-käskyt ja valinnainen liukulukuyksikkö |
| Cortex-M7 | ARMv7E-M | nopea, välimuistit ja tiukasti kytketty muisti |
| Cortex-M23, M33 | ARMv8-M | TrustZone eli turvallinen ja tavallinen maailma |
| Cortex-M55, M85 | ARMv8.1-M | Helium-vektorikäskyt koneoppimiseen |

Tämän tutoriaalin esimerkit ajetaan Cortex-M3:lla. Kaikki opittu
siirtyy suoraan M4:lle, M7:lle ja M33:lle; M0+:lla poikkeukset
ovat erikseen mainitut käskyt ja rekisterit.

## Käskykanta ja Thumb-bitti

Cortex-M suorittaa vain *Thumb*-käskyjä: 16-bittisiä tiiviitä käskyjä
ja Thumb-2:n 32-bittisiä käskyjä sekaisin. Vanhemmissa ARM-ytimissä
oli myös 32-bittinen ARM-tila, ja tila valittiin hyppyosoitteen
alimmalla bitillä. Cortex-M on säilyttänyt käytännön: jokaisen
koodiosoitteen, joka ladataan PC:hen hypyllä, pitää olla pariton.
Linkkeri hoitaa tämän funktio-osoitteille itse, mutta käsin tehty
osoite, jonka alin bitti on nolla, aiheuttaa vian (luku 9).

## Rekisterit

| Rekisteri | Tehtävä |
|-----------|---------|
| `r0`–`r3` | argumentit ja paluuarvo; kutsuja tallentaa |
| `r4`–`r11` | kutsuttu funktio tallentaa, jos käyttää |
| `r12` | apurekisteri (IP); kutsuja tallentaa |
| `sp` (`r13`) | pino-osoitin: MSP tai PSP |
| `lr` (`r14`) | paluuosoite tai poikkeuksessa EXC_RETURN |
| `pc` (`r15`) | ohjelmalaskuri |
| `xPSR` | liput (APSR), poikkeuksen numero (IPSR), T-bitti (EPSR) |
| `PRIMASK` | 1 = kaikki säädettävät keskeytykset peitetty |
| `FAULTMASK` | 1 = myös vikapoikkeukset peitetty (ei M0+) |
| `BASEPRI` | peittää keskeytykset, joiden prioriteetti on heikompi (ei M0+) |
| `CONTROL` | bitti 0 nPRIV: ei-etuoikeutettu; bitti 1 SPSEL: PSP |

Jako kutsujan ja kutsutun tallentamiin rekistereihin tulee ARM:n
kutsukonventiosta AAPCS. Se on tärkeä myöhemmin: poikkeuksen alkaessa
prosessori tallentaa juuri kutsujan vastuulla olevat rekisterit, joten
keskeytyskäsittelijä voi olla tavallinen C-funktio.

Erikoisrekistereitä luetaan ja kirjoitetaan käskyillä `mrs` ja `msr`.
C:ssä niille ei ole vastinetta, joten käytetään pientä
inline-assemblyä. CMSIS-kirjastossa samat funktiot ovat nimillä
`__get_CONTROL`, `__get_IPSR` ja niin edelleen.

```{.c tiedosto="esimerkit/02-rekisterit/main.c" osa="erikoisrekisterit"}
```

## Tilat, etuoikeudet ja kaksi pinoa

Prosessori on aina jommassakummassa tilassa:

- **Thread-tila**: tavallinen ohjelma, alkaen resetistä. Voi olla
  etuoikeutettu tai ei-etuoikeutettu (CONTROL.nPRIV).
- **Handler-tila**: poikkeus- ja keskeytyskäsittelijät. Aina
  etuoikeutettu ja aina pääpinossa.

Pinoja on kaksi. *Pääpino* MSP (Main Stack Pointer) on käytössä
resetin jälkeen ja aina Handler-tilassa. *Prosessipino* PSP (Process
Stack Pointer) otetaan käyttöön Thread-tilassa asettamalla
CONTROL.SPSEL. Bare-metal-ohjelma käyttää yleensä pelkkää MSP:tä.
Reaaliaikakäyttöjärjestelmä antaa jokaiselle säikeelle oman PSP-pinon
ja vaihtaa säiettä vaihtamalla PSP:n arvon, kun taas ydin ja
keskeytykset käyttävät MSP:tä. Ei-etuoikeutettu koodi ei pääse
ytimen ohjausrekistereihin (alue `0xE000E000` alkaen) eikä voi
palauttaa itselleen etuoikeuksia: sen on pyydettävä niitä
järjestelmäkutsulla (luku 5).

## Muistikartta

Cortex-M:n 4 GiB:n osoiteavaruus on jaettu kiinteisiin alueisiin.
Alueen tyyppi määrää, saako sieltä suorittaa koodia ja voiko prosessori
järjestää tai yhdistää muistiviittauksia uudelleen.

| Alue | Osoitteet | Käyttö | mps2-an385 |
|----------|--------------|----------------------------------|----------------------------|
| Code | `0x00000000`– | flash, vektoritaulu | 4 MiB, esimerkeissä 256 KiB |
| SRAM | `0x20000000`– | RAM, bit-band-alias `0x22000000` | 4 MiB, esimerkeissä 64 KiB |
| Peripheral | `0x40000000`– | piirin oheislaitteet, alias `0x42000000` | UART, ajastimet, FPGA-I/O |
| External | `0x60000000`– | ulkoinen muisti ja laitteet | Ethernet, PSRAM |
| PPB | `0xE0000000`– | ytimen omat rekisterit | NVIC, SysTick, SCB, MPU |

Ytimen yksityisen väylän (Private Peripheral Bus) tärkein osa on
*System Control Space* (SCS) osoitteesta `0xE000E000`: siellä ovat
SysTick (`0xE000E010`), NVIC (`0xE000E100`), järjestelmän
ohjauslohko SCB (`0xE000ED00`) ja muistinsuojausyksikkö MPU
(`0xE000ED90`). Ne ovat samassa paikassa jokaisessa Cortex-M-piirissä.

```{.dot otsikko="Cortex-M:n osoiteavaruus (ei mittakaavassa). Oikealla esimerkkien käyttämät osat."}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.5;
  node [shape=plaintext, fontsize=10];
  kartta [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td align="right" border="0">0xE0000000</td><td bgcolor="#E4DCF0" port="ppb">PPB: ytimen rekisterit</td></tr>
    <tr><td align="right" border="0">0x60000000</td><td bgcolor="white">ulkoinen muisti ja laitteet</td></tr>
    <tr><td align="right" border="0">0x40000000</td><td bgcolor="#DCEBDD" port="per">oheislaitteet</td></tr>
    <tr><td align="right" border="0">0x20000000</td><td bgcolor="#F1E3CC" port="ram">SRAM</td></tr>
    <tr><td align="right" border="0">0x00000000</td><td bgcolor="#EEF1F2" port="code">Code: flash</td></tr>
  </table>>];
  scs [label="0xE000E000 SCS: SysTick, NVIC,\lSCB, MPU\l", shape=box, style=filled, fillcolor="#E4DCF0"];
  laitteet [label="0x40000000 ajastimet\l0x40004000 UART0\l0x40008000 vahtikoira\l0x40028000 LEDit, painikkeet\l", shape=box, style=filled, fillcolor="#DCEBDD"];
  ram [label="0x20000000 .data, .bss, .noinit, pino\l(64 KiB)\l", shape=box, style=filled, fillcolor="#F1E3CC"];
  flash [label="0x00000000 vektoritaulu, koodi, vakiot\l(256 KiB)\l", shape=box, style=filled, fillcolor="#EEF1F2"];
  kartta:ppb -> scs; kartta:per -> laitteet; kartta:ram -> ram; kartta:code -> flash;
}
```

## Poikkeukset

Kaikki, mikä keskeyttää ohjelman, on *poikkeus*: reset, viat,
järjestelmäkutsu ja oheislaitteiden keskeytykset. Jokaisella on numero
ja vektoritaulussa paikka, josta prosessori lukee käsittelijän
osoitteen.

| Numero | Poikkeus | Huomio |
|--------|----------|--------|
| 1 | Reset | ei paluuta |
| 2 | NMI | ei peitettävissä |
| 3 | HardFault | viat, joille ei ole omaa käsittelijää |
| 4–6 | MemManage, BusFault, UsageFault | sallittava erikseen (ei M0+) |
| 11 | SVCall | käsky `svc`: järjestelmäkutsu |
| 14 | PendSV | ohjelmallisesti laukaistava, RTOS:n säikeenvaihto |
| 15 | SysTick | ytimen ajastin |
| 16– | IRQ0, IRQ1, ... | piirin oheislaitteet |

Kun poikkeus alkaa, prosessori tekee laitteistolla seuraavan:

1. Tallentaa käytössä olevaan pinoon kahdeksan sanan *kehyksen*:
   `r0`–`r3`, `r12`, `lr`, `pc` ja `xPSR`.
2. Lukee käsittelijän osoitteen vektoritaulusta.
3. Siirtyy Handler-tilaan ja MSP:hen ja kirjoittaa IPSR:ään poikkeuksen
   numeron.
4. Kirjoittaa `lr`:ään erikoisarvon *EXC_RETURN*, joka kertoo, mihin
   tilaan ja pinoon palataan.

Käsittelijä päättyy tavallisella paluukäskyllä. Kun `pc`:hen
ladataan EXC_RETURN-arvo, prosessori tunnistaa sen ja purkaa kehyksen.

| EXC_RETURN | Paluu |
|------------|-------|
| `0xFFFFFFF1` | Handler-tilaan (sisäkkäinen poikkeus), MSP |
| `0xFFFFFFF9` | Thread-tilaan, MSP |
| `0xFFFFFFFD` | Thread-tilaan, PSP |

ARMv8-M:ssä ja liukulukuyksikön kanssa arvoja on enemmän, mutta bitti
2 kertoo aina, kummassa pinossa kehys on.

Kehys on aina samanmuotoinen, ja pino kasvaa alaspäin, joten
käsittelijä löytää keskeytetyn ohjelman rekisterit kiinteistä
siirtymistä pino-osoittimesta:

```{.dot otsikko="Poikkeuskehys: kahdeksan sanaa, jotka prosessori tallentaa keskeytetyn ohjelman pinoon"}
digraph {
  rankdir=LR; nodesep=0.3;
  node [shape=plaintext, fontsize=10];
  pino [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0" align="right">suuret osoitteet</td><td bgcolor="white">keskeytetyn ohjelman pino</td><td border="0" align="left" port="ennen">SP ennen poikkeusta</td></tr>
    <tr><td border="0" align="right">SP + 28</td><td bgcolor="#F1E3CC">xPSR</td><td border="0"></td></tr>
    <tr><td border="0" align="right">SP + 24</td><td bgcolor="#F1E3CC">pc: mihin palataan</td><td border="0"></td></tr>
    <tr><td border="0" align="right">SP + 20</td><td bgcolor="#F1E3CC">lr</td><td border="0"></td></tr>
    <tr><td border="0" align="right">SP + 16</td><td bgcolor="#F1E3CC">r12</td><td border="0"></td></tr>
    <tr><td border="0" align="right">SP + 12</td><td bgcolor="#F1E3CC">r3</td><td border="0"></td></tr>
    <tr><td border="0" align="right">SP + 8</td><td bgcolor="#F1E3CC">r2</td><td border="0"></td></tr>
    <tr><td border="0" align="right">SP + 4</td><td bgcolor="#F1E3CC">r1</td><td border="0"></td></tr>
    <tr><td border="0" align="right">SP + 0</td><td bgcolor="#F1E3CC">r0</td><td border="0" align="left">SP käsittelijän alussa</td></tr>
    <tr><td border="0" align="right">pienet osoitteet</td><td bgcolor="white" style="dashed">vapaata</td><td border="0"></td></tr>
  </table>>];
}
```

Poikkeuksista kaksi on tarkoitettu käyttöjärjestelmälle: SVCall on
järjestelmäkutsu ja PendSV säikeenvaihdon paikka. Niihin sekä
prosessipinoon ja etuoikeuksista luopumiseen palataan luvun 5 lopussa,
kun vektoritaulu, rekisterikirjoitukset ja tavallinen keskeytys ovat
tuttuja.

## Esimerkki: ydin, vektoritaulu ja tila

SCB:n ensimmäinen rekisteri CPUID kertoo, mikä ydin on kyseessä.
Ohjelma tulostaa sen, vektoritaulun kaksi ensimmäistä sanaa ja lopuksi
oman tilansa edellä näytetyllä funktiolla `tila`:

```{.c tiedosto="esimerkit/02-rekisterit/main.c" osa="cpuid"}
```

```{.tuloste tiedosto="esimerkit/testit/02-rekisterit.odotettu"}
```

Valmistajakoodi `0x41` on ARM, osanumero `0xc23` Cortex-M3. Oikeassa
piirissä CPUID on hyvä tarkistaa käynnistyksessä, jos sama ohjelma
on tarkoitettu usealle piirille. Vektoritaulun ensimmäinen sana on
pinon alkuarvo eikä käsittelijän osoite, ja toinen, Reset_Handlerin
osoite, on pariton. Pääohjelma on Thread-tilassa, etuoikeutettu ja
pääpinossa: IPSR on nolla ja CONTROL nolla. Luvussa 5 sama funktio
kutsutaan poikkeuskäsittelijästä ja prosessipinosta.

## Käytännössä

- **Selvitä ytimen versio ennen kuin kirjoitat koodia.** M0+:lta
  puuttuvat jakokäsky, LDREX/STREX, BASEPRI ja vikakohtaiset
  käsittelijät, ja niiden puute muuttaa ratkaisuja.
- **Käytä valmistajan CMSIS-otsakkeita** oikeassa projektissa.
  `core_cm3.h` ja muut ytimen otsakkeet ovat ARM:n, ja valmistajan
  laiteotsake (`stm32f4xx.h`, `nrf52.h` ja vastaavat) määrittelee
  oheislaitteet. Tämän tutoriaalin oma `mps2.h` on opetusta varten.
- **Pidä bare-metal-ohjelma etuoikeutettuna ja MSP:ssä**, ellei ole
  syytä muuhun. Erottelu kannattaa vasta, kun on ydin, joka valvoo
  muita, eli käytännössä RTOS ja MPU.
- **Lue piirin käyttöohje (Reference Manual) ja ytimen Generic User
  Guide rinnakkain.** Ensimmäinen kertoo oheislaitteet, jälkimmäinen
  kaiken, mikä on yhteistä kaikille Cortex-M-piireille.

## Itsearviointi

- Osaat nimetä Cortex-M:n rekisterit ja kertoa, mitkä niistä
  prosessori tallentaa poikkeuksen alussa ja miksi.
- Osaat selittää Thread- ja Handler-tilan, etuoikeudet sekä MSP:n ja
  PSP:n eron ja sen, mihin RTOS niitä käyttää.
- Osaat sijoittaa flashin, RAMin, oheislaitteet ja ytimen rekisterit
  Cortex-M:n muistikarttaan.
- Osaat kuvata poikkeuksen alun ja lopun vaiheet ja tulkita
  EXC_RETURN-arvon.
- Osaat lukea CPUID:n ja vektoritaulun alun ja kertoa, mitä kumpikin
  sana vektoritaulun alussa tarkoittaa.
