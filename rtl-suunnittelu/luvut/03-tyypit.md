# Tyypit ja lausekkeet

Laitteistossa on vain johtimia ja bittejä. Tyypit kertovat, miten
bittejä tulkitaan, ja auttavat työkaluja löytämään virheet. Tässä
luvussa käydään läpi synteesikelpoiset tyypit, literaalit, operaattorit
ja ne leveys- ja etumerkkisäännöt, joihin kokenutkin suunnittelija
kompastuu.

## logic, wire ja reg

Verilogissa oli kaksi perustyyppiä: `wire` on johdin, jota ajaa
`assign` tai instanssin ulostulo, ja `reg` on muuttuja, johon
sijoitetaan `always`-lohkossa. Nimi `reg` johtaa harhaan, sillä se ei
tarkoita rekisteriä: `always @*`-lohkossa sijoitettu `reg` on
kombinaatiologiikkaa.

SystemVerilogin `logic` korvaa molemmat. Sitä voi ajaa joko
jatkuvalla sijoituksella tai yhdestä `always`-lohkosta. Jos samaa
signaalia yritetään ajaa kahdesta paikasta, työkalu ilmoittaa virheestä.
`wire` tarvitaan enää signaaleille, joilla on oikeasti useita ajajia,
kuten kaksisuuntaisille nastoille.

| Tyyppi | Tilat | Etumerkki | Käyttö |
|--------|-------|-----------|--------|
| `logic` | 4 (0, 1, X, Z) | ei | kaikki suunnitelman signaalit |
| `bit` | 2 (0, 1) | ei | testipenkin apumuuttujat |
| `int` | 2, 32 bittiä | kyllä | silmukkamuuttujat, parametrit |
| `byte`, `shortint`, `longint` | 2; 8, 16, 64 bittiä | kyllä | testipenkki |
| `integer` | 4, 32 bittiä | kyllä | vanha Verilog-tyyppi |

Suunnitelmassa käytetään `logic`-tyyppiä, koska nelitilainen
simulaattori näyttää silloin alustamattoman tai ristiriitaisesti ajetun
signaalin `X`:nä. Kaksitilainen tyyppi peittäisi saman virheen nollana.

## Vektorit ja literaalit

`logic [7:0] tavu` on 8-bittinen *pakattu* vektori: bitit ovat yksi
luku, jolla voi laskea. `logic [7:0] muisti [256]` on 256 alkion
*pakkaamaton* taulukko, jonka alkiot ovat 8-bittisiä (luku 8).
Vektorista otetaan bitti `tavu[7]`, osa `tavu[3:0]` tai osa annetusta
kohdasta annetulla leveydellä `tavu[i*4 +: 4]`.

Literaali kirjoitetaan muodossa *leveys*`'`*kanta* *arvo*: `8'hA5`,
`4'b1010`, `12'd100`, `-8'sd20` (etumerkillinen). Alaviiva erottaa
numeroita: `16'b1011_0000_1111_0000`. Ilman leveyttä luku, kuten `5`,
on 32-bittinen. Erityisliteraalit `'0`, `'1`, `'x` ja `'z` täyttävät
kohteen koko leveyden: `q <= '0;` nollaa minkä levyisen rekisterin
tahansa.

## enum, struct ja typedef

Luettelotyyppi `enum` antaa arvoille nimet. Tilakoneet kirjoitetaan
lähes aina sillä (luku 6). Pakattu rakenne `struct packed` on
bittivektori, jonka kentillä on nimet: se sopii väylän sanoihin,
otsikkokenttiin ja rekisterikarttoihin. `typedef` nimeää tyypin
uudelleenkäyttöä varten.

```{.systemverilog tiedosto="esimerkit/03-pakattu.sv" osa="tyypit"}
```

Pakatun rakenteen ensimmäinen kenttä on merkitsevin. Rakenne
muunnetaan bittivektoriksi pelkällä sijoituksella ja takaisin
tyyppimuunnoksella `tyyppi'(lauseke)`:

```{.systemverilog tiedosto="esimerkit/03-pakattu.sv" osa="kaytto"}
```

Synteesissä rakenteella ei ole hintaa: kentät ovat vain nimiä
bittiväleille. Pakkaamaton rakenne (`struct` ilman `packed`-sanaa) on
sallittu, mutta sitä ei voi käsitellä bittivektorina.

## Operaattorit

Aritmeettiset (`+ - * / % **`), vertailu- (`== != < <= > >=`),
loogiset (`&& || !`), bittioperaattorit (`& | ^ ~`) ja siirrot
(`<< >> <<< >>>`) toimivat kuten C:ssä. Laitteistolle ominaisia ovat
seuraavat:

- **Redusointi.** Yksiargumenttinen `&`, `|` tai `^` yhdistää vektorin
  kaikki bitit yhdeksi: `^tavu` on pariteetti, `|tavu` kertoo,
  onko yksikään bitti ykkönen.
- **Liitos ja toisto.** `{a, b}` liittää vektorit peräkkäin,
  `{4{2'b10}}` toistaa neljästi.
- **Ehto-operaattori.** `s ? a : b` on multiplekseri.

```{.systemverilog tiedosto="esimerkit/03-pakattu.sv" osa="operaattorit"}
```

```{.tuloste tiedosto="esimerkit/03-pakattu.odotettu"}
```

Operaattorien hinnat poikkeavat toisistaan paljon. Bittioperaatiot ja
vakiosiirrot ovat lähes ilmaisia, ja vakiosiirto on pelkkää
johdotusta. Yhteen- ja vähennyslasku ovat halpoja. Kertolasku on
kallis, mutta FPGA:ssa sille on valmiit DSP-lohkot. Jakolasku ja
jakojäännös muulla kuin kahden potenssilla tuottavat valtavan ja
hitaan piirin: niitä ei kirjoiteta RTL:ään, vaan käytetään
monijaksoista jakajaa tai kerrotaan käänteisluvulla.

## Leveys- ja etumerkkisäännöt

Lausekkeen leveys määräytyy *kontekstista*: operandit laajennetaan
ensin lausekkeen leveimmän operandin ja sijoituskohteen levyisiksi, ja
vasta sitten lasketaan. Siksi `summa9 = a8 + b8` laskee yhdeksällä
bitillä eikä menetä muistibittiä, kun `summa9` on yhdeksän bittiä
leveä. Liitoksen osat ovat kuitenkin *itsemääräytyviä*:
`{a8 + b8}` lasketaan kahdeksalla bitillä.

Etumerkkisääntö on vielä ankarampi: jos yksikin operandi on
etumerkitön, koko lauseke lasketaan etumerkittömänä. Etumerkillinen
operandi ei silloin laajennu etumerkillä, ja negatiivinen luku muuttuu
suureksi positiiviseksi:

```{.systemverilog tiedosto="esimerkit/03-etumerkki.sv" osa="sudenkuoppa"}
```

Siirroissa `>>` on aina looginen (täyttää nollilla), `>>>` aritmeettinen
etumerkillisellä operandilla (kopioi etumerkkibittiä):

```{.systemverilog tiedosto="esimerkit/03-etumerkki.sv" osa="siirrot"}
```

```{.tuloste tiedosto="esimerkit/03-etumerkki.odotettu"}
```

Tyyppimuunnokset kirjoitetaan muodossa `N'(x)` (leveys), `signed'(x)`
tai `$signed(x)` (etumerkki) ja `tyyppi'(x)`. Verilator varoittaa
lausekkeista, joissa leveydet eroavat (`WIDTHEXPAND`, `WIDTHTRUNC`).
Varoitus poistetaan muunnoksella, joka kertoo lukijalle, että
katkaisu tai laajennus on tarkoituksellinen.

## Käytännössä

- **`logic` kaikkialle.** Uudessa koodissa `wire` ja `reg` ovat
  tarpeettomia. Poikkeuksena ovat useaa ajajaa tarvitsevat signaalit ja
  Verilog-2005-yhteensopivuus (luku 12).
- **Leveydet näkyviin.** Literaali kirjoitetaan aina leveyden kanssa
  (`4'd9`, ei `9`), ja leveyden muutos tehdään muunnoksella
  (`LW'(JAKSO - 1)`). Lint-varoitus leveyserosta on lähes aina aito
  virhe tai puuttuva dokumentaatio.
- **Etumerkki eksplisiittisesti.** Aritmetiikka on joko kokonaan
  etumerkillistä tai kokonaan etumerkitöntä. Sekalausekkeissa
  molemmat operandit muunnetaan ensin samaan tyyppiin. Laitteistossa
  etumerkki ei maksa mitään, mutta väärä tulkinta voi tuottaa väärän
  vertailun.
- **Pakattu rakenne rajapinnoille.** Väylän sana, käsky tai otsikko on
  luettavampi kenttien nimillä kuin bittiväleillä (`m.arvo` eikä
  `vayla[11:0]`). Kenttien järjestys on osa rajapintaa.
- **Ei jakolaskua datapolkuun.** `/` ja `%` sallitaan vain
  käännösaikaisissa vakioissa (`KELLO_HZ / BAUD`) ja kahden
  potenssilla, joka on pelkkä siirto.
- **`'0` nollaukseen.** Kirjoitus `q <= '0;` toimii, vaikka `q`:n
  leveyttä muutettaisiin.

## Itsearviointi

- Osaat valita `logic`-, `bit`- ja `int`-tyyppien välillä ja perustella
  valinnan.
- Osaat kirjoittaa literaalit leveyksineen ja käyttää osavalintaa
  `[i*4 +: 4]`.
- Osaat määritellä `enum`- ja `struct packed` -tyypit ja muuntaa
  rakenteen bittivektoriksi ja takaisin.
- Osaat ennustaa lausekkeen leveyden ja etumerkillisyyden sekä korjata
  etumerkillisen ja etumerkittömän vertailun.
- Osaat arvioida operaattorien laitteistohinnan.
