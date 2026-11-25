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

Nimet ovat saman rekisterin osia, eivät eri rekistereitä:

```{.dot otsikko="Rekisterin rax osat. Sama kuvio toistuu muissa yleisrekistereissä."}
digraph {
  node [shape=plaintext, style=""];
  r [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td colspan="4" bgcolor="#E4DCF0">rax: 64 bittiä</td></tr>
    <tr><td border="0" width="170"></td>
        <td colspan="3" bgcolor="#E4DCF0">eax: 32 bittiä</td></tr>
    <tr><td border="0"></td><td border="0" width="90"></td>
        <td colspan="2" bgcolor="#E4DCF0">ax: 16 bittiä</td></tr>
    <tr><td border="0"></td><td border="0"></td>
        <td bgcolor="#F1E3CC" width="48">ah</td>
        <td bgcolor="#E4DCF0" width="48">al</td></tr>
    <tr><td border="0"><font point-size="9" color="#5B6B70">bitit 63–32</font></td>
        <td border="0"><font point-size="9" color="#5B6B70">31–16</font></td>
        <td border="0"><font point-size="9" color="#5B6B70">15–8</font></td>
        <td border="0"><font point-size="9" color="#5B6B70">7–0</font></td></tr>
  </table>>];
}
```

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

| Kirjoitus | Rekisterin ylemmät bitit |
|-----------|--------------------------|
| x86-64, 32 bittiä (`eax`) | nollataan |
| x86-64, 8 tai 16 bittiä (`al`, `ax`) | säilyvät ennallaan |
| RISC-V, W-käsky (`addw`) | bitin 31 kopioita (etumerkin laajennus) |

## Tavujärjestys

Muisti on tavutaulukko. Monitavuinen arvo, kuten 32-bittinen
`0x11223344`, tallennetaan neljään peräkkäiseen tavuun. Molemmat
käskykannat ovat **little-endian**: vähiten merkitsevä tavu on
pienimmässä osoitteessa. `tavu`-funktio lukee sanan tavun `i`:

```{.gnuassembler tiedosto="esimerkit/02-rekisterit/x86.S" osa="tavu"}
```

```{.gnuassembler tiedosto="esimerkit/02-rekisterit/rv.S" osa="tavu"}
```

```{.dot otsikko="Luku 0x11223344 muistissa osoitteessa p: vähiten merkitsevä tavu ensin"}
digraph {
  node [shape=plaintext, style=""];
  m [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6">
    <tr><td border="0"><font point-size="9" color="#5B6B70">p</font></td>
        <td border="0"><font point-size="9" color="#5B6B70">p+1</font></td>
        <td border="0"><font point-size="9" color="#5B6B70">p+2</font></td>
        <td border="0"><font point-size="9" color="#5B6B70">p+3</font></td></tr>
    <tr><td bgcolor="#E4DCF0" width="44"><font face="DejaVu Sans Mono">44</font></td>
        <td bgcolor="#E4DCF0" width="44"><font face="DejaVu Sans Mono">33</font></td>
        <td bgcolor="#E4DCF0" width="44"><font face="DejaVu Sans Mono">22</font></td>
        <td bgcolor="#E4DCF0" width="44"><font face="DejaVu Sans Mono">11</font></td></tr>
  </table>>];
}
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

```{.gnuassembler tiedosto="esimerkit/02-osoitus/x86.S" osa="hae"}
```

```{.gnuassembler tiedosto="esimerkit/02-osoitus/rv.S" osa="hae"}
```

Ero on tyypillinen: x86-64 tekee yhdellä pitkällä käskyllä sen, mihin
RISC-V tarvitsee kolme lyhyttä. Kumpikaan ei ole sellaisenaan nopeampi.
Nykyinen x86-64-suoritin pilkkoo käskyn sisäisesti mikro-operaatioiksi,
ja RISC-V-suoritin voi yhdistää peräkkäisiä käskyjä (*macro-op fusion*).

`lea` (*load effective address*) laskee osoitteen mutta ei lue muistia.
Kääntäjä käyttää sitä myös tavalliseen laskentaan: `lea (%rdi,%rdi,2),
%rax` laskee `3 * rdi` yhdellä käskyllä muuttamatta lippuja.

## Globaali data ja vakiot

Tähän asti data on tullut funktion argumentteina. Ohjelman omat
muuttujat ja taulukot sijoitetaan *osioihin*, jotka kokoaja valitsee
direktiivillä:

| Osio | Sisältö | Direktiivejä |
|------|---------|--------------|
| `.text` | käskyt | |
| `.rodata` | vakiot ja taulukot, vain luku | `.quad`, `.long`, `.byte`, `.ascii`, `.asciz` |
| `.data` | alustetut muuttujat | samat |
| `.bss` | nollilla alustetut muuttujat | `.zero N` (ei vie tilaa tiedostossa) |

```{.gnuassembler tiedosto="esimerkit/02-data/x86.S" osa="osiot"}
```

Käsky ei voi sisältää datan 64-bittistä osoitetta sellaisenaan, koska
ohjelma ladataan joka ajolla eri osoitteeseen (taito
*Objektitiedostot, linkitys ja ABI*). x86-64 osoittaa globaalia dataa
*käskyosoittimen suhteen*: `laskuri(%rip)` tarkoittaa "tämän käskyn
lopusta niin ja niin monta tavua eteenpäin". Etäisyys käskystä dataan
on sama, ladattiinpa ohjelma mihin tahansa, ja linkkeri kirjoittaa sen
käskyyn:

```{.gnuassembler tiedosto="esimerkit/02-data/x86.S" osa="seuraava"}
```

```{.gnuassembler tiedosto="esimerkit/02-data/x86.S" osa="alkuluku"}
```

RISC-V:n käskyyn mahtuu vain 12-bittinen vakio, joten osoite haetaan
ensin rekisteriin pseudokäskyllä `la` (*load address*) ja muistia
käsitellään sen kautta:

```{.gnuassembler tiedosto="esimerkit/02-data/rv.S" osa="seuraava"}
```

```{.gnuassembler tiedosto="esimerkit/02-data/rv.S" osa="alkuluku"}
```

Sama rajoitus koskee vakioita. x86-64:n `movabs` kantaa 64-bittisen
vakion käskyn sisällä (kymmenen tavua). RISC-V:n `li` (*load
immediate*) on pseudokäsky, jonka kokoaja purkaa niin moneksi käskyksi
kuin vakio vaatii:

```{.gnuassembler tiedosto="esimerkit/02-data/x86.S" osa="vakio"}
```

```{.gnuassembler tiedosto="esimerkit/02-data/rv.S" osa="vakio"}
```

```{.c tiedosto="esimerkit/02-data/main.c"}
```

```{.tuloste tiedosto="esimerkit/02-data/odotettu"}
```

Disassembly näyttää, miksi nämä pseudokäskyt ja osoitusmuodot on hyvä
tunnistaa. x86-64:llä siirtymä on käskyn neljässä viimeisessä tavussa
(objektitiedostossa vielä nollina):

```{.gnuassembler tiedosto="esimerkit/02-data-tavut/x86.S"}
```

```{.tuloste tiedosto="esimerkit/02-data-tavut/odotettu-x86"}
```

RISC-V:llä sama näkyy käskypareina:

```{.gnuassembler tiedosto="esimerkit/02-data-tavut/rv.S"}
```

```{.tuloste tiedosto="esimerkit/02-data-tavut/odotettu-rv"}
```

- `lla` on kaksi käskyä: `auipc` laskee osoitteen ylimmät bitit
  käskyosoittimesta ja `addi` lisää alimmat 12 bittiä. Objektitiedostossa
  siirtymät ovat vielä nollia, joten disassembleri näyttää `addi`:n
  nimellä `mv`.
- `la` tekee saman, mutta paikkariippumattomassa koodissa (Ubuntun
  kääntäjän oletus) se lukee osoitteen taulukosta (`auipc` + `ld`).
  Tämä GOT-taulu käsitellään taidossa *Objektitiedostot, linkitys ja
  ABI*.
- `li` on yksi käsky, kun vakio mahtuu 12 bittiin, `lui` + `addiw`,
  kun se mahtuu 32 bittiin, ja 64-bittiselle vakiolle siirtojen ja
  lisäysten ketju. Kääntäjä sijoittaa suuret vakiot siksi usein
  `.rodata`-osioon ja lataa ne muistista.

## Tietueet muistissa

Tietueen kenttä on vakiosiirtymä tietueen alusta. Kääntäjä sijoittaa
kentät järjestyksessä ja lisää täytettä, jotta jokainen kenttä on
kokonsa mukaisella rajalla (*alignment*). Assemblyssä siirtymät
kirjoitetaan käsin, joten C-puolen asettelu kannattaa lukita
`_Static_assert`-tarkistuksilla:

```{.c tiedosto="esimerkit/02-osoitus/main.c" osa="tuote"}
```

```{.dot otsikko="Tietueen tuote asettelu: kentän siirtymä on sen etäisyys tietueen alusta tavuina"}
digraph {
  node [shape=plaintext, style=""];
  t [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6">
    <tr><td border="0" align="left"><font point-size="9" color="#5B6B70">0</font></td>
        <td border="0" align="left"><font point-size="9" color="#5B6B70">4</font></td>
        <td border="0" align="left"><font point-size="9" color="#5B6B70">8</font></td>
        <td border="0" align="right"><font point-size="9" color="#5B6B70">16</font></td></tr>
    <tr><td bgcolor="#E4DCF0" width="90">koodi<br/>4 tavua</td>
        <td bgcolor="#F1E3CC" width="90">maara<br/>4 tavua</td>
        <td bgcolor="#E4DCF0" width="180" colspan="2">hinta_snt<br/>8 tavua</td></tr>
  </table>>];
}
```

```{.gnuassembler tiedosto="esimerkit/02-osoitus/x86.S" osa="arvo"}
```

```{.gnuassembler tiedosto="esimerkit/02-osoitus/rv.S" osa="arvo"}
```

```{.tuloste tiedosto="esimerkit/02-osoitus/odotettu"}
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
- **Vakiot `.rodata`-osioon, nollat `.bss`-osioon.** Vain luettava
  data on suojattu kirjoituksilta ja jaetaan prosessien kesken, ja
  `.bss` ei kasvata ohjelmatiedostoa. Kirjoitettavaa globaalia tilaa
  kannattaa välttää assemblyssä samasta syystä kuin C:ssä.
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
- Osaat sijoittaa datan osioihin `.rodata`, `.data` ja `.bss` ja
  osoittaa sitä käskyosoittimen suhteen (x86-64) tai `la`-käskyllä
  (RISC-V).
- Osaat kertoa, miksi RISC-V:n `li` ja `la` purkautuvat useaksi
  käskyksi.
