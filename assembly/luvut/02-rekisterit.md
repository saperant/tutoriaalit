# Rekisterit, muisti ja osoitusmuodot

Suoritin laskee *rekistereissä*: pienissä, nopeissa muistipaikoissa
suorittimen sisällä. Muisti on suuri tavutaulukko, jota osoitetaan
64-bittisillä osoitteilla. Konekielinen ohjelma siirtää arvoja muistin
ja rekisterien välillä ja laskee rekistereillä.

## Rekisterit

| Asia | x86-64 | RISC-V (RV64) |
|--------------------|-------------------------------------|------------------------------|
| Yleisrekisterejä | 16: `rax`, `rbx`, `rcx`, `rdx`, `rsi`, `rdi`, `rbp`, `rsp`, `r8`–`r15` | 32: `x0`–`x31` |
| Nollarekisteri | ei | `x0` = `zero`, lukee aina 0 |
| Pino-osoitin | `rsp` | `x2` = `sp` |
| Paluuosoite | pinossa | `x1` = `ra` |
| Käskyosoitin | `rip` (ei yleisrekisteri) | `pc` (ei yleisrekisteri) |
| Liput | `rflags`: CF, ZF, SF, OF … | ei lippuja |
| Liukuluvut ja SIMD | `xmm0`–`xmm15` (128 b), `ymm` (256 b) | `f0`–`f31`, vektorilaajennus `v0`–`v31` |

RISC-V:n rekistereillä on *ABI-nimet*, jotka kertovat niiden käytön
kutsukonventiossa: `a0`–`a7` argumentit ja paluuarvot, `t0`–`t6`
väliaikaiset, `s0`–`s11` kutsun yli säilyvät. Kokoaja hyväksyy molemmat
nimet, ja koodissa käytetään ABI-nimiä. Kutsukonventio käsitellään
luvussa 5.

x86-64:n rekistereillä on historiallisia nimiä ja kapeampia osia,
jotka periytyvät 8- ja 16-bittisiltä edeltäjiltä:

| 64 bittiä | 32 bittiä | 16 bittiä | 8 bittiä |
|-----------|-----------|-----------|----------|
| `rax` | `eax` | `ax` | `al` |
| `rdi` | `edi` | `di` | `dil` |
| `r8` | `r8d` | `r8w` | `r8b` |

## Rekisterin leveys

Kun käsky kirjoittaa rekisterin osaan, mitä tapahtuu muille biteille?
Säännöt ovat arkkitehtuurikohtaisia ja aiheuttavat virheitä, jos niitä
ei tunne. Funktio `lisaa32` laskee kahden luvun 32-bittisen summan:

```{.gnuassembler tiedosto="esimerkit/02-rekisterit/x86.S" osa="lisaa32"}
```

```{.gnuassembler tiedosto="esimerkit/02-rekisterit/rv.S" osa="lisaa32"}
```

```{.c tiedosto="esimerkit/02-rekisterit/main.c"}
```

x86-64:llä:

```{.tuloste tiedosto="esimerkit/02-rekisterit/odotettu-x86"}
```

RISC-V:llä:

```{.tuloste tiedosto="esimerkit/02-rekisterit/odotettu-rv"}
```

Summa 4 000 000 000 ei mahdu etumerkilliseen 32-bittiseen lukuun.
x86-64:llä 32-bittiseen rekisteriin (`eax`) kirjoittava käsky
**nollaa** ylimmät 32 bittiä, joten 64-bittinen `rax` tulkitsee bitit
positiiviseksi luvuksi. RISC-V:n `W`-päätteiset käskyt (`addw`, `subw`,
`slliw`) laskevat 32 bitillä ja **laajentavat etumerkillä**, joten
bittiä 31 kopioidaan ylös ja tulos on negatiivinen. Molemmat ovat
johdonmukaisia sääntöjä, mutta eri sääntöjä: kun 32-bittinen arvo
palautetaan 64-bittisessä rekisterissä, kutsukonventio määrää, kumpaa
tulkintaa kutsuja saa olettaa (luku 10).

x86-64:n 8- ja 16-bittiset käskyt (`al`, `ax`) eivät koske muihin
bitteihin lainkaan. Siksi tavun lukemiseen käytetään `movzbl`
(laajenna nollilla) tai `movsbl` (laajenna etumerkillä) koko
rekisteriin. Muuten ylimpiin bitteihin jäisi vanhaa roskaa.

## Tavujärjestys

Muisti on tavutaulukko. Monitavuinen arvo, kuten 32-bittinen
`0x11223344`, tallennetaan neljään peräkkäiseen tavuun. Molemmat
käskykannat ovat **little-endian**: vähiten merkitsevä tavu on
pienimmässä osoitteessa. `tavu`-funktio lukee sanan tavun `i`:

```{.gnuassembler tiedosto="esimerkit/02-rekisterit/x86.S" osa="tavu"}
```

```{.gnuassembler tiedosto="esimerkit/02-rekisterit/rv.S" osa="tavu"}
```

Tulosteessa tavut ovat järjestyksessä `44 33 22 11`. Tavujärjestys
näkyy aina, kun data siirtyy koneiden välillä: verkkoprotokollat
käyttävät big-endian-järjestystä (*network byte order*), ja
tiedostomuodot määrittelevät oman järjestyksensä.

## Osoitusmuodot

*Osoitusmuoto* kertoo, miten käsky laskee muistiosoitteen. x86-64:n
yleinen muoto on

```text
siirtymä(kanta, indeksi, kerroin)  =  kanta + indeksi * kerroin + siirtymä
```

missä kerroin on 1, 2, 4 tai 8. Yhdellä käskyllä voi siis hakea
taulukon alkion, jonka koko on 1–8 tavua. RISC-V:n ainoa muoto on
`siirtymä(kanta)`: kanta-rekisteri plus 12-bittinen vakio. Indeksin
kertominen ja lisääminen tehdään erillisillä käskyillä:

```{.gnuassembler tiedosto="esimerkit/03-osoitus/x86.S" osa="hae"}
```

```{.gnuassembler tiedosto="esimerkit/03-osoitus/rv.S" osa="hae"}
```

Ero on tyypillinen: x86-64 tekee yhdellä pitkällä käskyllä sen, mihin
RISC-V tarvitsee kolme lyhyttä. Kumpikaan ei ole sellaisenaan nopeampi.
Nykyinen x86-64-suoritin pilkkoo käskyn sisäisesti mikro-operaatioiksi,
ja RISC-V-suoritin voi yhdistää peräkkäisiä käskyjä (*macro-op fusion*).

`lea` (*load effective address*) laskee osoitteen mutta ei lue muistia.
Kääntäjä käyttää sitä myös tavalliseen laskentaan: `lea (%rdi,%rdi,2),
%rax` laskee `3 * rdi` yhdellä käskyllä muuttamatta lippuja.

## Tietueet muistissa

Tietueen kenttä on vakiosiirtymä tietueen alusta. Kääntäjä sijoittaa
kentät järjestyksessä ja lisää täytettä, jotta jokainen kenttä on
kokonsa mukaisella rajalla (*alignment*). Assemblyssä siirtymät
kirjoitetaan käsin, joten C-puolen asettelu kannattaa lukita
`_Static_assert`-tarkistuksilla:

```{.c tiedosto="esimerkit/03-osoitus/main.c" osa="tuote"}
```

```{.gnuassembler tiedosto="esimerkit/03-osoitus/x86.S" osa="arvo"}
```

```{.gnuassembler tiedosto="esimerkit/03-osoitus/rv.S" osa="arvo"}
```

```{.tuloste tiedosto="esimerkit/03-osoitus/odotettu"}
```

Silmukka siirtää osoitinta tietueen koon (16 tavua) kerrallaan ja
lukee kentät vakiosiirtymillä 4 ja 8. x86-64:n `movslq` lukee
32-bittisen etumerkillisen luvun ja laajentaa sen 64-bittiseksi.
RISC-V:n `lw` laajentaa etumerkillä aina, ja `lwu` nollilla.

## Käytännössä

- **Lukitse rajapinnan asettelu.** Kun assembly käsittelee C:n
  tietueita, kirjoita siirtymät ja koko `_Static_assert`-tarkistuksiksi
  C-puolelle. Ilman tarkistuksia kentän lisääminen rikkoo
  assembly-koodin hiljaisesti.
- **Laajenna aina koko rekisteriin.** Lue tavut ja 16-bittiset arvot
  laajentavilla käskyillä (`movzbl`, `movsbl`, `lbu`, `lb`). Osittain
  kirjoitettu rekisteri on yleinen virheen lähde, ja x86-64:llä se voi
  lisäksi hidastaa riippuvuuksien takia.
- **Tunne W-käskyjen sääntö.** RISC-V:n 32-bittiset käskyt laajentavat
  etumerkillä, x86-64:n 32-bittiset käskyt nollaavat. Kun luet
  kääntäjän koodia, `sext.w`, `addw` ja `movl %eax, %eax` kertovat,
  mihin tulkintaan koodi luottaa.
- **Tavujärjestys rajapinnoissa.** Muunna data tunnettuun järjestykseen
  rajapinnassa (verkko, tiedosto), älä keskellä laskentaa.
- **`lea` ei ole muistikäsky.** Se laskee osoitteen kaavalla.
  Kääntäjän tuottamassa koodissa se on usein yhteen- ja kertolasku.

## Itsearviointi

- Osaat nimetä x86-64:n ja RISC-V:n yleisrekisterit ja niiden
  ABI-roolit.
- Osaat kertoa, mitä 32-bittinen kirjoitus tekee rekisterin ylimmille
  biteille kummallakin käskykannalla.
- Osaat lukea x86-64:n osoitusmuodon `siirtymä(kanta, indeksi,
  kerroin)` ja kirjoittaa saman RISC-V:llä.
- Osaat laskea tietueen kenttien siirtymät ja käyttää niitä
  assemblyssä.
- Osaat selittää little-endian-tavujärjestyksen ja sen, missä se
  näkyy.
