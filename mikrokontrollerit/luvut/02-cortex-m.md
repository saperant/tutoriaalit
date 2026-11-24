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
järjestelmäkutsulla.

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
SCB:n ensimmäinen rekisteri CPUID kertoo, mikä ydin on kyseessä:

```{.c tiedosto="esimerkit/02-rekisterit/main.c" osa="cpuid"}
```

Valmistajakoodi `0x41` on ARM, osanumero `0xc23` Cortex-M3. Oikeassa
piirissä CPUID on hyvä tarkistaa käynnistyksessä, jos sama ohjelma
on tarkoitettu usealle piirille.

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

## Järjestelmäkutsu SVC

Käsky `svc #n` aiheuttaa poikkeuksen 11. Sitä käytetään
järjestelmäkutsuna: ei-etuoikeutettu koodi pyytää ydintä tekemään
jotain, mihin sillä itsellään ei ole oikeutta. Argumentit kulkevat
rekistereissä, ja koska prosessori tallentaa ne kehykseen,
käsittelijä löytää ne pinosta ja voi myös kirjoittaa paluuarvon
kehyksen `r0`:aan.

```{.c tiedosto="esimerkit/02-rekisterit/main.c" osa="kutsu"}
```

Käsittelijän alku on kirjoitettava assemblynä, koska C-funktion
prologi tallentaisi rekistereitä ja siirtäisi pino-osoitinta ennen
kuin ehdimme lukea niitä. Kolme käskyä valitsee EXC_RETURNin bitin 2
perusteella oikean pinon ja siirtyy C-funktioon, jolle kehys ja
EXC_RETURN annetaan argumentteina. SVC-numero ei ole rekisterissä:
se luetaan käskystä itsestään, joka on kaksi tavua ennen
tallennettua paluuosoitetta.

```{.c tiedosto="esimerkit/02-rekisterit/main.c" osa="svc"}
```

Pinon vaihtaminen kesken C-funktion ei onnistu, koska kääntäjä
tallentaa paluuosoitteen funktion alussa yhteen pinoon ja hakisi sen
lopussa toisesta. Siksi siirtymä prosessipinoon tehdään pienessä
assembly-funktiossa, joka kutsuu C-funktiota uudessa pinossa ja palaa
vanhaan:

```{.c tiedosto="esimerkit/02-rekisterit/main.c" osa="psp"}
```

Prosessipinossa ajettava funktio luopuu lopuksi etuoikeuksistaan ja
yrittää palauttaa ne itse. Kirjoitus CONTROL-rekisteriin ei-
etuoikeutetusta tilasta jää vaikutuksetta ilman virhettä, joten
etuoikeudet palautetaan järjestelmäkutsulla `svc #2`:

```{.c tiedosto="esimerkit/02-rekisterit/main.c" osa="prosessi"}
```

```{.c tiedosto="esimerkit/02-rekisterit/main.c" osa="main"}
```

```{.tuloste tiedosto="esimerkit/testit/02-rekisterit.odotettu"}
```

Tulosteesta näkyy koko malli: Handler-tilassa IPSR on 11 ja pino
aina MSP, vaikka kehys tallennettiin PSP:hen. Handler-tilassa
CONTROL.SPSEL luetaan aina nollana, ja nPRIV ei vaikuta, koska
Handler-tila on aina etuoikeutettu. Vektoritaulun ensimmäinen sana on
pinon alkuarvo eikä osoite, ja toinen, Reset_Handlerin osoite, on
pariton.

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
- Osaat toteuttaa järjestelmäkutsun SVC:llä niin, että argumentit ja
  paluuarvo kulkevat kehyksen kautta.
