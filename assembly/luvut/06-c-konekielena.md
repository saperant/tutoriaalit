# C:n rakenteet konekielenä

Useimmiten assemblyä luetaan, ei kirjoiteta, ja luettava koodi on
kääntäjän tuottamaa. Tässä luvussa käännetään tavallisia C-rakenteita
ja luetaan tulos. Kun tunnistaa toistuvat mallit, kuten silmukan,
taulukon indeksoinnin, kenttäsiirtymät ja hyppytaulun, kääntäjän
tuottamaa koodia voi lukea nopeasti ilman lähdekoodia.

## Kääntäjän assembly-tuloste

`gcc -S` pysäyttää käännöksen assemblyyn. Luettavuutta varten
näytteissä käytetään lisävalitsimia:

```text
gcc-14 -O2 -S -fno-asynchronous-unwind-tables -fcf-protection=none \
    -fno-stack-protector -fno-tree-vectorize taulukko.c -o -
```

Valitsimet poistavat purkutiedot (`.cfi`-direktiivit), Ubuntun
oletuksena lisäämät `endbr64`-hyppykohdemerkinnät ja pinosuojan sekä
automaattisen vektoroinnin, joka käsitellään luvussa 9. Lisäksi
direktiivejä on karsittu. Esimerkkihakemiston `testaa.sh` tuottaa
näytteet uudelleen ja vertaa niitä alla näytettyihin, joten näytteet
vastaavat kehityskontin kääntäjää. Toinen kätevä väline on *Compiler
Explorer* (godbolt.org), joka näyttää lähdekoodin ja assemblyn
vierekkäin monilla kääntäjillä.

Kääntäjän tuloste käyttää AT&T-syntaksissa kokopäätteitä (`movq`,
`addq`) myös silloin, kun koon voisi päätellä rekistereistä, ja
nimiöitä muotoa `.L3`. RISC-V-tuloste käyttää ABI-rekisterinimiä ja
pseudokäskyjä.

## Optimointi muuttaa kaiken

Taulukon summa C:llä:

```{.c tiedosto="esimerkit/07-c-rakenteet/taulukko.c"}
```

Ilman optimointia (`-O0`) kääntäjä pitää jokaisen muuttujan pinossa ja
lataa sen jokaisessa käytössä. Koodi vastaa lähdekoodia rivi riviltä,
mikä helpottaa debuggausta mutta on hidasta:

```{.gnuassembler tiedosto="esimerkit/07-c-rakenteet/taulukko-x86-O0.s"}
```

`-O2`:lla muuttujat ovat rekistereissä, indeksi on korvattu
osoittimella ja silmukassa on vain neljä käskyä:

```{.gnuassembler tiedosto="esimerkit/07-c-rakenteet/taulukko-x86.s"}
```

```{.gnuassembler tiedosto="esimerkit/07-c-rakenteet/taulukko-rv.s"}
```

Tunnistettavat mallit:

- **Tyhjän tapauksen tarkistus ensin** (`testq`/`jle`, `ble a1,zero`)
  ja ehto silmukan lopussa (*loop rotation*): kierrosta kohden yksi
  hyppy.
- **Indeksi muutettu osoittimeksi.** `t[i]` ja `i++` ovat muuttuneet
  osoittimeksi, jota kasvatetaan 8:lla ja verrataan loppuosoitteeseen.
  Loppuosoite lasketaan ennen silmukkaa (`leaq (%rdi,%rsi,8)`,
  `slli`+`add`).
- **x86-64 laskee muistista suoraan** (`addq (%rdi), %rax`),
  RISC-V lataa ensin (`ld`) ja laskee sitten.

Debugattaessa optimoitua koodia muuttuja voi puuttua kokonaan tai
elää eri rekistereissä eri kohdissa. Debuggerin `<optimized out>`
tarkoittaa juuri tätä.

## Tietueen kentät

```{.c tiedosto="esimerkit/07-c-rakenteet/kentat.c"}
```

```{.gnuassembler tiedosto="esimerkit/07-c-rakenteet/kentat-x86.s"}
```

```{.gnuassembler tiedosto="esimerkit/07-c-rakenteet/kentat-rv.s"}
```

Kentät näkyvät vakiosiirtyminä: `maara` on siirtymässä 4, `hinta` 8 ja
`asiakas` 16. `tila`-kentän perässä on kolme tavua täytettä, jotta
`int` on neljän tavun rajalla. Kun luet tuntematonta koodia, toistuvat
siirtymät samasta kantarekisteristä paljastavat tietueen rakenteen.
Takaisinmallinnuksessa tietueet rekonstruoidaan juuri näin.

Liukuluvut kulkevat omissa rekistereissään: x86-64:llä `xmm0`
(SSE2-käskyt `cvtsi2sdl` ja `mulsd`), RISC-V:llä `fa0` (D-laajennus,
`fcvt.d.w` ja `fmul.d`). Paluuarvo on `xmm0`:ssa tai `fa0`:ssa.

## switch ja hyppytaulu

Tiheä `switch` käännetään *hyppytauluksi*. Tapauksen numerolla
haetaan taulukosta hypyn kohde, jolloin kaikki tapaukset ovat yhtä
nopeita:

```{.c tiedosto="esimerkit/07-c-rakenteet/valinta.c"}
```

```{.gnuassembler tiedosto="esimerkit/07-c-rakenteet/valinta-x86.s"}
```

```{.gnuassembler tiedosto="esimerkit/07-c-rakenteet/valinta-rv.s"}
```

Rakenne on molemmilla sama:

1. **Rajatarkistus yhdellä etumerkittömällä vertailulla** (`ja`,
   `bgtu`): negatiivinen `op` muuttuu suureksi etumerkittömäksi
   luvuksi ja päätyy `default`-haaraan (luku 4).
2. **Taulukko `.rodata`-osiossa**: 32-bittiset erotukset taulukon
   alusta (`.L10-.L4`). Suhteelliset siirtymät toimivat, vaikka ohjelma
   ladataan mihin osoitteeseen tahansa (PIE).
3. **Epäsuora hyppy** (`jmp *%rax`, `jr a5`) laskettuun osoitteeseen.

Harva `switch` (esimerkiksi tapaukset 1, 1000 ja 1 000 000)
käännetään vertailuketjuksi tai binäärihauksi. Jos kaikki tapaukset
vain palauttavat vakion, kääntäjä tekee hyppytaulun sijaan
arvotaulukon (`CSWTCH`), jolloin hyppyä ei ole lainkaan.

Epäsuorat hypyt ovat myös tietoturvakysymys: Spectre-hyökkäykset
käyttävät niiden ennustusta hyväksi, ja `endbr64`-merkinnät
(`-fcf-protection`) rajaavat sallitut kohteet. Siksi tuotantokoodin
hyppytauluissa on usein lisäkäskyjä, jotka näytteistä on poistettu.

## Osoittimen seuraaminen

```{.c tiedosto="esimerkit/07-c-rakenteet/lista.c"}
```

```{.gnuassembler tiedosto="esimerkit/07-c-rakenteet/lista-x86.s"}
```

```{.gnuassembler tiedosto="esimerkit/07-c-rakenteet/lista-rv.s"}
```

Linkitetyn listan silmukassa seuraava osoite ladataan siirtymästä 8
(`movq 8(%rdi), %rdi`, `ld a5,8(a5)`). Jokainen kierros odottaa
edellisen latauksen valmistumista. Ketjua ei voi rinnakkaistaa, ja jos
solmut ovat hajallaan muistissa, jokainen lataus voi olla
välimuistiohitus. Siksi linkitetty lista on käytännössä hitaampi kuin
taulukko, vaikka algoritmi olisi sama. Konekielestä tämän näkee
suoraan: latauksen tulos on seuraavan latauksen osoite.

Näytteiden toiminta testataan ajamalla ne C-pääohjelmalla molemmilla
arkkitehtuureilla:

```{.tuloste tiedosto="esimerkit/07-c-rakenteet/odotettu"}
```

## Käytännössä

- **Lue optimoitua koodia.** `-O0`-koodi on helppoa mutta
  harhaanjohtavaa. Suorituskyvyn arviointi ja tuotannon kaatumisten
  tutkiminen tehdään sillä koodilla, joka oikeasti ajetaan.
- **Etsi silmukan runko.** Takaisinpäin hyppäävä ehdollinen hyppy
  merkitsee silmukan loppua. Lue sen ja kohteen välinen koodi ensin:
  siellä kuluu aika.
- **Tunnista mallit.** Toistuvat siirtymät samasta rekisteristä ovat
  tietueen kenttiä, `jmp *` ja taulukko `.rodata`:ssa on `switch`,
  `xor eax, eax` on nolla ja `lea` on usein laskutoimitus.
- **Vertaa kääntäjiä ja valitsimia.** Pienikin muutos lähdekoodiin
  (`int` vai `long`, `restrict`, etumerkillinen vai etumerkitön
  indeksi) voi muuttaa konekieltä paljon. Compiler Explorer näyttää
  erot välittömästi.
- **Älä optimoi käsin ennen kuin olet lukenut kääntäjän tuloksen.**
  Kääntäjä tekee yleensä yhtä hyvää tai parempaa koodia kuin käsin
  kirjoitettu assembly. Poikkeukset (vektorointi, erikoiskäskyt) näkyvät
  vasta, kun tuloksen lukee.

## Itsearviointi

- Osaat tuottaa kääntäjän assembly-tulosteen (`gcc -S`, Compiler
  Explorer) ja poistaa siitä lukemista haittaavat direktiivit.
- Osaat tunnistaa kääntäjän koodista silmukan, taulukon indeksoinnin,
  tietueen kentät, hyppytaulun ja osoittimen seuraamisen.
- Osaat selittää, miksi `-O0`- ja `-O2`-koodi eroavat ja miten
  optimointi vaikuttaa debuggaukseen.
- Osaat perustella konekielen perusteella, miksi linkitetyn listan
  läpikäynti on hitaampaa kuin taulukon.
