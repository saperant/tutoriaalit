# Paikkariippumaton koodi, GOT ja PLT

Jaettu kirjasto ladataan eri prosesseissa eri osoitteisiin, mutta sen
koodisivut halutaan jakaa: sama fyysinen muisti kaikille prosesseille.
Koodiin ei siis voi kirjoittaa latausosoitteesta riippuvia arvoja.
*Paikkariippumaton koodi* (*position-independent code*, PIC) ratkaisee
tämän kahdella periaatteella:

1. Saman tiedoston sisällä viitataan `rip`-suhteellisesti: etäisyys
   koodista dataan on vakio, latausosoitteesta riippumatta.
2. Muihin tiedostoihin viitataan taulukon kautta, joka on
   kirjoitettavassa datassa. Lataaja täyttää taulukon, ja koodi pysyy
   muuttumattomana.

Taulukoita on kaksi. **GOT** (*global offset table*) sisältää
muuttujien ja funktioiden osoitteet. **PLT** (*procedure linkage
table*) on joukko pieniä hyppykoodeja, yksi kutakin ulkoista funktiota
kohti; jokainen hyppää GOT:ssa olevaan osoitteeseen.

## Kirjasto, jonka symbolit voi korvata

Esimerkin mittauskirjasto laskee kutsunsa ja pyöristää tuloksen
apufunktiolla:

```{.c tiedosto="esimerkit/08-got-plt/mittari.c" osa="mittari"}
```

Kun tiedosto käännetään valitsimella `-fPIC`, relokaatiot näyttävät,
miten kääntäjä viittaa omaan muuttujaansa ja funktioonsa:

```{.bash tiedosto="esimerkit/08-got-plt/aja.sh" osa="pic"}
```

```{.tuloste tiedosto="esimerkit/08-got-plt/odotettu" alkaen="== relokaatiot -fPIC-objektissa" asti="pyorista"}
```

Sama näkyy konekielestä. Skripti rakentaa kirjaston kahdesti, ensin
oletusnäkyvyydellä ja sitten piilotetuilla symboleilla (seuraava
osio), ja tulostaa funktion `mittaa` kummastakin:

```{.bash tiedosto="esimerkit/08-got-plt/aja.sh" osa="nakyvyys"}
```

```{.tuloste tiedosto="esimerkit/08-got-plt/odotettu" alkaen="== mittaa kirjastossa" asti="ret"}
```

Tulos voi yllättää: `kutsuja` ja `pyorista` ovat *samassa
tiedostossa*, mutta `mittaa` hakee muuttujan osoitteen GOT:sta
(`mov ...(%rip),%rax` ja sitten `addl $0x1,(%rax)`) ja kutsuu
apufunktiota PLT:n kautta (`jmp <pyorista@plt>`, häntäkutsuna). Kääntäjä
ei myöskään upottanut lyhyttä `pyorista`-funktiota.

Syy on *symbolien korvattavuus* (*symbol interposition*). ELF:n
sääntöjen mukaan globaali symboli jaetussa kirjastossa voidaan korvata:
jos ohjelma tai aiemmin ladattu kirjasto määrittelee saman nimen,
dynaaminen linkkeri sitoo *kaikki* viittaukset siihen, myös kirjaston
omat (luku 10). Kääntäjän on varauduttava siihen, että `kutsuja` ja
`pyorista` eivät ole ne, jotka se näkee.

## Näkyvyys: mikä on rajapintaa

Valitsin `-fvisibility=hidden` tekee kaikista symboleista oletuksena
*piilotettuja*: ne ovat globaaleja kirjaston sisällä mutta eivät näy
sen ulkopuolelle. Makro `VIENTI` merkitsee julkisen rajapinnan
näkyväksi (`visibility("default")`). Toisessa käännöksessä kääntäjä
tietää, ettei kukaan voi korvata symboleita `kutsuja` ja `pyorista`,
joten muuttujaa kasvatetaan suoraan `rip`-suhteellisesti ja
`pyorista` upotetaan kokonaan (kertolasku `0x66666667`:llä on
jakolasku kymmenellä).

Piilottamisella on neljä hyötyä:

- **Nopeampi koodi**: suorat viittaukset, upotus ja muut
  optimoinnit kirjaston sisällä.
- **Nopeampi käynnistys**: dynaamisessa symbolitaulussa on vähemmän
  symboleita, ja lataaja tekee vähemmän relokaatioita.
- **Hallittu ABI**: vain merkityt symbolit ovat rajapintaa, joten
  sisäisiä funktioita voi muuttaa vapaasti (luku 9).
- **Ei törmäyksiä**: sisäinen apufunktio ei voi sekoittua toisen
  kirjaston samannimiseen funktioon (luku 10).

| Keino | Vaikutus | Käyttö |
|-------|----------|--------|
| `-fvisibility=hidden` ja vientimakro | vain merkityt symbolit näkyvät | uudet kirjastot |
| versioskripti `local: *;` | piilottaa linkityksessä | olemassa oleva koodi |
| `-fno-semantic-interposition` | kääntäjä saa olettaa, ettei korvata | GCC 5+, Python käyttää |
| `-Wl,-Bsymbolic` | linkkeri sitoo sisäiset viittaukset itseensä | rikkoo `LD_PRELOAD`-kääreet |
| `static` | paikallinen, ei rajapintaa | aina, kun mahdollista |

Sama makro kirjoitetaan yleensä niin, että se toimii myös Windowsilla,
jossa vienti merkitään `__declspec(dllexport)`. CMake tuottaa
tällaisen otsakkeen komennolla `generate_export_header`, ja
`CXX_VISIBILITY_PRESET hidden` asettaa valitsimen.

## Miten PLT toimii

Ohjelman kutsu `mittaa(14)` kääntyy kutsuksi `call mittaa@plt`. PLT:n
merkintä on hyppy GOT:n paikkaan (`objdump -d oletus`, osoitteet
poistettu):

```text
<mittaa@plt>:
    endbr64
    jmp    *SIIRTYMA(%rip)    # osoite GOT:n paikasta
    nopw   0x0(%rax,%rax,1)
```

`endbr64` on epäsuoran hypyn kohdemerkintä (Intel CET, `-fcf-protection`),
ja `nopw` täyttää merkinnän 16 tavuun.

Kun ohjelma käynnistyy, lataaja kirjoittaa funktion `mittaa`
todellisen osoitteen GOT:n paikkaan. Sen jälkeen jokainen kutsu on
epäsuora hyppy: yksi lisämuistiviittaus kutsua kohti, jonka
haarautumisennustin oppii nopeasti.

```{.dot otsikko="Kutsu jaettuun kirjastoon, kun GOT on täytetty (välitön sidonta tai toinen kutsu). Koodisivut ovat muuttumattomia; vain GOT on dataa."}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.5;
  node [shape=box, style="filled", fontsize=10];
  subgraph cluster_ohjelma {
    label="ohjelma"; color="#B8C4C8"; fontsize=10;
    kutsu [label="main:\ncall mittaa@plt", fillcolor="#E4DCF0"];
    plt [label="PLT: mittaa@plt\njmp *GOT[mittaa]", fillcolor="#E4DCF0"];
    got [label="GOT[mittaa]\n= funktion osoite", fillcolor="#F1E3CC"];
  }
  subgraph cluster_kirjasto {
    label="libmittari.so"; color="#B8C4C8"; fontsize=10;
    f [label="mittaa:\n…\nret", fillcolor="#E4DCF0"];
  }
  kutsu -> plt [label="1"];
  plt -> got [label="2: lue", style=dashed];
  plt -> f [label="3: hyppy"];
}
```

*Laiska sidonta* (*lazy binding*) lykkää osoitteen ratkaisemista
ensimmäiseen kutsuun. GOT:n paikassa on aluksi osoite takaisin
PLT:hen, josta hypätään lataajan ratkaisijaan (`_dl_runtime_resolve`).
Ratkaisija etsii symbolin, kirjoittaa osoitteen GOT:iin ja hyppää
funktioon. Seuraavat kutsut menevät suoraan.

```{.dot otsikko="Laiskan sidonnan ensimmäinen kutsu: GOT:n paikka osoittaa aluksi takaisin PLT:hen, ja lataajan ratkaisija korjaa sen"}
digraph {
  nodesep=0.5; ranksep=0.35;
  node [shape=box, style="filled", fontsize=10];
  kutsu [label="main: call mittaa@plt", fillcolor="#E4DCF0"];
  plt [label="PLT: mittaa@plt\njmp *GOT[mittaa]", fillcolor="#E4DCF0"];
  got [label="GOT[mittaa]\naluksi: PLT:n ratkaisukoodi", fillcolor="#F1E3CC"];
  plt0 [label="PLT:n ratkaisukoodi\npush symbolin numero, jmp ratkaisijaan", fillcolor="#E4DCF0"];
  ratk [label="ld.so: _dl_runtime_resolve", fillcolor="#EEF1F2"];
  f [label="libmittari.so: mittaa", fillcolor="#E4DCF0"];
  kutsu -> plt [label=" 1"];
  plt -> plt0 [label=" 3"];
  plt0 -> ratk [label=" 4"];
  ratk -> f [label=" 6: hyppy"];
  { rank=same; plt; got; }
  plt -> got [label="2: lue", style=dashed];
  ratk -> got [label=" 5: kirjoita osoite", style=dashed, constraint=false];
}
```
 Esimerkin ohjelma
kirjoittaa merkkirivit ennen ja jälkeen ensimmäisen kutsun, ja
`LD_DEBUG=bindings` näyttää, milloin `mittaa` sidottiin:

```{.c tiedosto="esimerkit/08-got-plt/main.c"}
```

```{.bash tiedosto="esimerkit/08-got-plt/aja.sh" osa="oletus"}
```

```{.tuloste tiedosto="esimerkit/08-got-plt/odotettu" alkaen="== oletus: sidonta käynnistyksessä" asti="ensimmäisen kutsun jälkeen"}
```

```{.bash tiedosto="esimerkit/08-got-plt/aja.sh" osa="laiska"}
```

```{.tuloste tiedosto="esimerkit/08-got-plt/odotettu" alkaen="== laiska sidonta"}
```

Ubuntun GCC linkittää oletuksena valitsimella `-z now`: lippu
`BIND_NOW` käskee lataajaa sitomaan kaikki symbolit käynnistyksessä,
ja sidonta tapahtuu ennen ensimmäistä merkkiriviä. Valitsimella
`-z lazy` sidonta tapahtuu vasta ensimmäisessä kutsussa.

Välitön sidonta yhdessä RELRO:n kanssa (*full RELRO*: `-z relro -z
now`) on turvallisempi. Kun kaikki osoitteet on kirjoitettu, lataaja
suojaa GOT:n kirjoitukselta, eikä muistivirhettä voi käyttää
funktio-osoitteiden ylikirjoittamiseen. Laiskassa sidonnassa GOT:n
funktiopaikkojen on pysyttävä kirjoitettavina koko ajon ajan.
Lisäksi puuttuva symboli paljastuu heti käynnistyksessä eikä vasta,
kun harvinainen koodipolku ajetaan. Laiska sidonta nopeuttaa
käynnistystä vain ohjelmilla, joilla on tuhansia tuontisymboleita ja
joista käytetään pientä osaa.

Valitsin `-fno-plt` poistaa PLT:n kokonaan: kääntäjä tuottaa
kutsukohtaan `call *mittaa@GOTPCREL(%rip)`. Tämä säästää yhden
hypyn mutta vaatii välittömän sidonnan.

GOT:n kautta kulkee myös *epäsuora funktio* (IFUNC, `nm`:n kirjain
`i`). Sen symboli ei osoita funktioon vaan valitsijaan, jonka lataaja
ajaa sidonnan yhteydessä ja joka palauttaa toteutuksen osoitteen.
glibc valitsee näin funktioille `memcpy` ja `strlen` suorittimen
tukeman SIMD-version, eikä kutsuja huomaa eroa.

## Säiekohtaiset muuttujat

Säiekohtainen muuttuja (`_Thread_local`, C++:n `thread_local`) on
olemassa kerran jokaista säiettä kohti. `errno` on tällainen, samoin
monen kirjaston sisäinen tila. Se ei voi olla osiossa `.data`, koska
`.data`:sta on prosessissa yksi kopio, joten sille on omat osionsa ja
oma tapansa laskea osoite:

```{.c tiedosto="esimerkit/08-tls/laskuri.c" osa="laskuri"}
```

```{.bash tiedosto="esimerkit/08-tls/aja.sh" osa="osiot"}
```

```{.tuloste tiedosto="esimerkit/08-tls/odotettu" alkaen="== osiot ja segmentti" asti="TLS FileSiz"}
```

Osiot `.tdata` ja `.tbss` vastaavat osioita `.data` ja `.bss`, ja
lippu `T` merkitsee ne säiekohtaisiksi. Linkkeri kokoaa ne
ohjelmaotsakkeeseen `TLS`. Se on *malli*: kun säie luodaan, lataaja
tai säiekirjasto varaa säikeelle `MemSiz` tavua ja kopioi alkuun
`FileSiz` tavua alkuarvoja. x86-64:llä rekisteri `fs` osoittaa
säikeen omaan alueeseen.

Miten koodi löytää muuttujan, riippuu siitä, mitä kääntäjä tietää.
Ohjelman omassa koodissa muuttujan etäisyys säikeen osoittimesta on
linkitysaikainen vakio (*local-exec*-malli), ja luku on yksi käsky:

```{.bash tiedosto="esimerkit/08-tls/aja.sh" osa="ohjelma"}
```

```{.tuloste tiedosto="esimerkit/08-tls/odotettu" alkaen="== ohjelmassa" asti="ret"}
```

Jaetun kirjaston koodi ei tiedä, mihin kohtaan säikeen aluetta
kirjaston muuttujat sijoittuvat, eikä edes, onko kirjasto ladattu
`dlopen`:lla kesken ajon. Yleisessä tapauksessa (*general-dynamic*)
se kysyy osoitteen funktiolta `__tls_get_addr`:

```{.bash tiedosto="esimerkit/08-tls/aja.sh" osa="kirjasto"}
```

```{.tuloste tiedosto="esimerkit/08-tls/odotettu" alkaen="== jaetussa kirjastossa" asti="TLSGD kutsuja"}
```

Jos kirjasto ladataan aina ohjelman käynnistyksessä, etäisyys on
lataajan tiedossa ja se voidaan lukea GOT:sta (*initial-exec*).
Kääntäjälle tämä luvataan valitsimella tai attribuutilla
`tls_model`:

```{.bash tiedosto="esimerkit/08-tls/aja.sh" osa="initial"}
```

```{.tuloste tiedosto="esimerkit/08-tls/odotettu" alkaen="== kirjastossa, joka ladataan" asti="GOTTPOFF kutsuja"}
```

| Malli | Relokaatio | Hinta | Käyttö |
|-------|------------|-------|--------|
| local-exec | `TPOFF32` | yksi käsky | ohjelman oma muuttuja |
| initial-exec | `GOTTPOFF` | lataus GOT:sta | kirjasto, jota ei ladata `dlopen`:lla |
| general-dynamic | `TLSGD` + `__tls_get_addr` | funktiokutsu | mikä tahansa jaettu kirjasto |

Linkkeri osaa keventää mallia, kun se näkee lopputuloksen: ohjelmaan
linkitetty general-dynamic-koodi muutetaan local-exec-muotoon.
Ohjelma, jossa kaksi säiettä ja pääsäie kasvattavat laskuria,
tulostaa kolme toisistaan riippumatonta arvoa:

```{.c tiedosto="esimerkit/08-tls/main.c" osa="saie"}
```

```{.tuloste tiedosto="esimerkit/08-tls/odotettu" alkaen="== ajo"}
```

Kun `objdump -dr` näyttää relokaation, jonka nimessä on `TLS` tai
`TPOFF`, tai käskyn, joka osoittaa `%fs`:n kautta, kyse on
säiekohtaisesta muuttujasta. Luvun 12 aputaulukon satunnaisluvuista
tehty pinosuojan vertailuarvo luetaan samalla tavalla (`%fs:0x28`).

## Käytännössä

- **Käännä kirjastot `-fvisibility=hidden`:llä** ja merkitse rajapinta
  vientimakrolla. Se on suurin yksittäinen parannus jaetun kirjaston
  nopeuteen, kokoon ja ABI:n hallintaan.
- **Pidä oletuksena välitön sidonta ja täysi RELRO.**
  `readelf -d ohjelma | grep FLAGS` näyttää `BIND_NOW`, ja
  `readelf -lW` näyttää `GNU_RELRO`-segmentin.
- **Älä käytä `-Bsymbolic`:ia sokeasti.** Se nopeuttaa kirjastoa
  mutta estää symbolien korvaamisen, jota muistinhallintakirjastot ja
  kääreet tarvitsevat. Näkyvyys on tarkempi keino.
- **Säiekohtainen muuttuja kirjastossa maksaa funktiokutsun.** Jos
  kirjastoa ei ladata `dlopen`:lla, `-ftls-model=initial-exec`
  poistaa kutsun. Kuumassa silmukassa osoite kannattaa hakea kerran
  paikalliseen osoittimeen.
- **Mittaa ennen kuin poistat PLT:n.** `-fno-plt` ja
  linkitysaikainen optimointi auttavat vain kuumissa kutsupoluissa.

## Itsearviointi

- Osaat selittää, miksi jaetun kirjaston koodi viittaa omiin
  globaaleihin muuttujiinsa GOT:n kautta.
- Osaat kuvata PLT:n ja GOT:n yhteistyön sekä laiskan ja välittömän
  sidonnan eron.
- Osaat käyttää näkyvyysattribuutteja ja `-fvisibility=hidden`:ia ja
  tunnistaa niiden vaikutuksen konekielestä.
- Osaat kertoa, miksi täysi RELRO edellyttää välitöntä sidontaa ja
  miten sen tarkistaa.
- Osaat selittää, mihin säiekohtainen muuttuja sijoitetaan
  (`.tdata`, `.tbss`, `TLS`-otsake) ja miksi jaettu kirjasto hakee sen
  osoitteen eri tavalla kuin ohjelma.
