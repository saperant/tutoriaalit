# Koodingenerointi RISC-V:lle

Takaosa muuntaa välikielen kohdekoneen assemblyksi. Siinä on kolme
tehtävää: **käskyjen valinta** (mikä käsky tai käskyjono toteuttaa
kunkin välikielen operaation), **rekisterien varaus** (missä kukin
virtuaalirekisteri on, luku 14) ja **kutsukonvention noudattaminen**
(miten argumentit, paluuarvo ja tallennettavat rekisterit kulkevat
funktioiden välillä). Kide tuottaa RV64IM-koodia: RISC-V:n 64-bittinen
peruskäskykanta ja kerto- ja jakolaskulaajennus.

## Kutsukonventio

RISC-V:n kutsukonventio (*psABI*, LP64) jakaa 32 kokonaislukurekisteriä
näin (taito *Assembly* käsitteli tämän tarkemmin):

| Rekisterit | ABI-nimi | Tehtävä | Säilyykö kutsun yli |
|------------|----------|---------|---------------------|
| x1 | `ra` | paluuosoite | ei |
| x2 | `sp` | pino-osoitin, 16:lla jaollinen | kyllä |
| x8 | `s0`/`fp` | kehysosoitin | kyllä |
| x9, x18–x27 | `s1`–`s11` | tallennettavat | kyllä |
| x10–x17 | `a0`–`a7` | argumentit, `a0` paluuarvo | ei |
| x5–x7, x28–x31 | `t0`–`t6` | väliaikaiset | ei |

"Säilyy kutsun yli" tarkoittaa, että kutsuttu funktio (*callee*) lupaa
palauttaa rekisterin ennalleen: jos se käyttää `s1`:tä, sen on
tallennettava vanha arvo ja palautettava se. Rekisterit `t0`–`t6`
ja `a0`–`a7` taas saavat muuttua, joten kutsuja (*caller*) tallentaa ne
itse, jos niiden arvoja tarvitaan kutsun jälkeen.

Kide käyttää yksinkertaista jakoa. Virtuaalirekistereille varataan vain
`s1`–`s11`, joten arvot säilyvät kutsujen yli ilman ylimääräistä työtä.
`t0`–`t2` ovat apurekistereitä pinosta ladatuille arvoille ja `t6`
suurten pinosiirtymien laskemiseen. `a`-rekistereitä käytetään vain
argumenttien välitykseen juuri ennen kutsua.

## Pinokehys

Jokainen funktio varaa pinosta **kehyksen**. Kehyksen yläreunaan
osoittaa `s0`, joten kaikki paikat ovat vakiosiirtymän päässä siitä,
vaikka `sp` muuttuisi:

```{.cpp tiedosto="esimerkit/kide/koodigen.cpp" osa="kehys"}
```

RISC-V:n lataus- ja tallennuskäskyjen siirtymä on 12-bittinen
etumerkillinen luku. Suurempi siirtymä lasketaan ensin rekisteriin;
tämä on tyypillinen RISC-arkkitehtuurin rajoitus, jonka kääntäjä
piilottaa.

**Prologi** tallentaa paluuosoitteen ja kutsujan kehysosoittimen,
varaa kehyksen, tallentaa käytetyt `s`-rekisterit ja siirtää
parametrit `a`-rekistereistä paikoilleen. **Epilogi** palauttaa
`s`-rekisterit, `sp`:n, `s0`:n ja `ra`:n ja palaa `ret`-käskyllä:

```{.cpp tiedosto="esimerkit/kide/koodigen.cpp" osa="prologi"}
```

Pinon 16 tavun tasaus on psABI:n vaatimus, ja sen rikkominen on
klassinen vaikeasti löydettävä virhe: ohjelma toimii, kunnes jokin
kirjastofunktio käyttää tasausta vaativia käskyjä (taito *Assembly*
näytti tämän x86-64:llä).

## Operandit ja tulokset

Rekisterien varaus (luku 14) kertoo kunkin virtuaalirekisterin
paikan: `s`-rekisteri tai pinopaikka. Koodingeneraattori kysyy
operandin rekisteriä; pinossa oleva arvo ladataan apurekisteriin, ja
pinoon menevä tulos lasketaan `t0`:aan ja tallennetaan:

```{.cpp tiedosto="esimerkit/kide/koodigen.cpp" osa="operandit"}
```

## Käskyjen valinta

Useimmat välikielen operaatiot vastaavat yhtä käskyä. Vertailuista
RISC-V:ssä on vain `slt` (*set if less than*), joten muut johdetaan
siitä: `a > b` on `b < a`, ja `a <= b` on `!(b < a)`. Yhtäsuuruus
lasketaan erotuksen nollatestinä:

```{.cpp tiedosto="esimerkit/kide/koodigen.cpp" osa="vertailut"}
```

Makro `KIDE_VIKA` rakentaa kääntäjästä tarkoituksella rikotun version,
jossa `<=` käännetään kuten `<`. Testisarja käyttää sitä mittaamaan,
löytävätkö testit tällaisen vian (luku 15).

Ehdollinen haara tuottaa `bnez`- tai `beqz`-käskyn ja jättää hypyn
pois, kun kohde on heti seuraava lohko:

```{.cpp tiedosto="esimerkit/kide/koodigen.cpp" osa="haara"}
```

Kutsu siirtää argumentit `a`-rekistereihin, tekee `call`-käskyn ja
siirtää tuloksen `a0`:sta kohteeseen. Paluu siirtää arvon `a0`:aan ja
hyppää epilogiin.

Tämä on **makrolaajennusta**: jokainen välikielen käsky käännetään
erikseen kiinteäksi käskyjonoksi. Se on yksinkertainen ja oikea mutta
jättää käyttämättä kohdekoneen vahvuudet. RISC-V:llä on esimerkiksi
`addi` (välitön vakio käskyssä), ja vertailu ja haara yhdistyvät
yhdeksi käskyksi (`ble a, b, L`). Tuotantokääntäjät tekevät käskyjen
valinnan **puiden peittämisenä** (*tree pattern matching*): välikielen
lausekepuu peitetään kohdekoneen käskyjä vastaavilla malleilla, ja
dynaaminen ohjelmointi valitsee halvimman peitteen. LLVM:n
SelectionDAG ja GCC:n konekuvaukset (`.md`-tiedostot) ovat tällaisia
mallikokoelmia.

## Kaikki pinoon

Yksinkertaisin rekisterien varaus on olla varaamatta: jokainen
virtuaalirekisteri saa pinopaikan, ja jokainen käsky lataa operandinsa
ja tallentaa tuloksensa. Funktio, joka laskee `a * a + b * b`, näyttää
silloin tältä (`-O0 --varaus=pino`):

```{.rust tiedosto="esimerkit/naytteet/nelio.kide"}
```

```{.gnuassembler tiedosto="esimerkit/naytteet/asm-pino.txt"}
```

Koodi on pitkää ja muistiliikenteen kuormittamaa, mutta se on helppo
saada oikeaksi, ja sitä käytetään testeissä vertailukohtana
varaajalle. GCC:n `-O0` tekee lähes saman (luku 16): jokainen muuttuja
asuu pinossa, jotta debuggeri voi lukea ja muuttaa sitä milloin tahansa.

## Käytännössä

- **Noudata kutsukonventiota tarkasti.** Se on ainoa rajapinta, jonka
  kautta käännetty koodi toimii yhdessä C-kirjaston, käyttöjärjestelmän
  ja muiden kääntäjien koodin kanssa.
- **Aloita kaikki pinoon -varauksella.** Se on oikea, ja paremman
  varaajan tuloksia voi verrata siihen.
- **Kehysosoitin selkeyttää.** Vakiosiirtymät `s0`:sta helpottavat
  debuggausta ja pinojäljen kulkua; optimoivat kääntäjät jättävät sen
  usein pois (`-fomit-frame-pointer`) ja vapauttavat rekisterin.
- **Hyödynnä kohdekoneen käskyjä.** Välittömät vakiot, osoitusmuodot ja
  yhdistetty vertailu ja haara ovat ilmaista nopeutta, jonka
  makrolaajennus jättää käyttämättä.

## Itsearviointi

- Osaat selittää RISC-V:n kutsukonvention rekisteriluokat ja sen,
  kumpi osapuoli tallentaa minkäkin rekisterin.
- Osaat suunnitella pinokehyksen ja kirjoittaa sen prologin ja
  epilogin niin, että pino pysyy tasattuna.
- Osaat kääntää välikielen käskyt RISC-V-käskyiksi ja johtaa puuttuvat
  vertailut `slt`-käskystä.
- Osaat kertoa, mitä makrolaajennuksesta puuttuu verrattuna puiden
  peittämiseen.
