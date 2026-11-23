# Synteesikelpoisuus ja koodaustyyli

Simulaattori hyväksyy koko SystemVerilogin, synteesityökalu vain
osajoukon. Pahinta ei ole se, että synteesi hylkää koodin, vaan se, että
se hyväksyy koodin ja tuottaa piirin, joka toimii toisin kuin
simulaatio. Tämä luku kokoaa synteesikelpoisuuden säännöt ja
koodaustyylin, joka pitää simulaation ja piirin yhtäpitävinä.

## Mikä syntetisoituu

| Rakenne | Synteesissä |
|---------|-------------|
| `always_comb`, `always_ff`, `assign` | kyllä |
| `if`, `case`, `for` vakiorajoin, funktiot | kyllä, puretaan logiikaksi |
| parametrit, `generate`, `$clog2`, `$bits` | kyllä, käännösaikana |
| `enum`, `struct packed`, `typedef`, `package` | kyllä |
| `initial`, alkuarvot | FPGA: alkuarvo konfiguraatioon; ASIC: ei |
| viiveet `#5` | jätetään huomiotta |
| `$display`, `$fatal`, väittämät | jätetään huomiotta |
| `while` ja `repeat` muuttuvalla rajalla | ei |
| jonot, merkkijonot, luokat, dynaamiset taulukot | ei |
| `fork`, `wait`, `@` muualla kuin herkkyyslistassa | ei |

Viiveen huomiotta jättäminen on vaarallisin rivi: `assign #2 y = a;`
näyttää simuloinnissa viiveeltä, mutta synteesi tekee siitä suoran
johtimen. RTL:ssä ei käytetä viiveitä lainkaan. Ajoitus on
ajoitusanalyysin asia.

## Täydellinen case

Luvussa 4 puuttuva sijoitus tuotti salvan. Sama tapahtuu, kun
`case`-lause ei kata kaikkia valitsimen arvoja eikä siinä ole
oletussijoitusta. Verilator varoittaa jo kattamattomasta `case`-lauseesta
(`CASEINCOMPLETE`), vaikka salpaa ei vielä olisikaan:

```{.systemverilog tiedosto="esimerkit/11-segmentti.ei-kaanny.sv"}
```

```{.tuloste tiedosto="esimerkit/11-segmentti.odotettu"}
```

Korjattu dekooderi kertoo `default`-haarassa, mitä virheellinen syöte
tuottaa. Näyttö näyttää viivan, mikä on parempi kuin satunnainen
merkki:

```{.systemverilog tiedosto="esimerkit/11-segmentti.ei-kaanny.sv" osa="oikein"}
```

Verilogin aikana yleiset synteesidirektiivit `// synopsys full_case
parallel_case` kertoivat synteesille saman asian kuin `unique`, mutta
simulaattori ei nähnyt niitä. Tuloksena oli piirejä, jotka toimivat
toisin kuin simulaatio. `unique` ja `priority` korvaavat ne, koska
simulaattori tarkistaa lupauksen. Verilatorissa ajonaikainen tarkistus
on käytössä valitsimella `--assert`.

## Kombinatorinen silmukka

Kombinatorinen silmukka syntyy, kun signaali riippuu itsestään ilman
kiikkua välissä. Piirissä se voi värähdellä tai lukittua, eikä
ajoitusanalyysi osaa käsitellä sitä. Tyypillinen syy on kättely, jossa
molemmat osapuolet tekevät päätöksensä toistensa signaalien perusteella:

```{.systemverilog tiedosto="esimerkit/11-silmukka.ei-kaanny.sv"}
```

```{.tuloste tiedosto="esimerkit/11-silmukka.odotettu"}
```

Verilator ilmoittaa silmukasta varoituksella `UNOPTFLAT`. Korjaus on
protokollan sääntö: `kelvollinen` ei saa riippua `valmis`-signaalista.
Moduulirajojen yli kulkevaa silmukkaa ei näe yhdestä tiedostosta,
joten sääntö kirjataan rajapinnan dokumentaatioon.

## Monta ajajaa

Jokaisella signaalilla on yksi ajaja: yksi `assign`, yksi `always`-lohko
tai yksi instanssin ulostulo. SystemVerilog-standardin mukaan saman
muuttujan sijoittaminen kahdessa `always_ff`-lohkossa on virhe, ja
synteesityökalut hylkäävät sen. Verilator 5.020 ei kuitenkaan aina
huomaa sitä, kun molemmat lohkot käyttävät samaa kelloa. Sääntö on siis
pidettävä mielessä, vaikka lint ei valittaisi.

## Lint ja varoitukset

Verilatorin `-Wall` on tiukka, ja juuri siksi se on hyödyllinen.
Tämän tutoriaalin esimerkkien kääntämisessä esiintyneet varoitukset:

| Varoitus | Merkitys |
|----------|----------|
| `WIDTHEXPAND`, `WIDTHTRUNC` | leveydet eroavat lausekkeessa tai kytkennässä |
| `UNUSEDSIGNAL`, `UNDRIVEN` | signaalia ei käytetä tai sitä ei ajeta |
| `LATCH` | `always_comb`-lohkosta syntyy salpa |
| `CASEINCOMPLETE` | `case` ei kata kaikkia arvoja |
| `BLKSEQ` | estävä sijoitus kellotetussa lohkossa |
| `UNOPTFLAT` | kombinatorinen silmukka |
| `IMPLICIT` | implisiittinen johto (luku 12) |
| `SYNCASYNCNET` | sama signaali on sekä asynkroninen että synkroninen nollaus |
| `USERERROR` | elaboraatioaikainen `$error` |

Aiheellinen poikkeus vaiennetaan paikallisesti kommenttiparilla
`/* verilator lint_off VAROITUS */` ja `/* verilator lint_on VAROITUS */`,
ja viereen kirjoitetaan syy. Esimerkki on luvun 8 rekisteripankin
porttilistassa, jossa 32-bittisen väylän kaikkia bittejä ei käytetä.

Varoituksia ei vaienneta koko tiedostolle eikä komentorivillä, koska
silloin vaimennus peittää myös tulevat aidot virheet.

## Kaksitilainen ja nelitilainen simulointi

Nelitilainen simulaattori näyttää alustamattoman rekisterin `X`:nä, ja
`X` leviää laskennassa. Se paljastaa puuttuvat nollaukset, mutta
`X`-semantiikka on myös optimistinen: `if (x)` valitsee `else`-haaran,
kun `x` on `X`, ja peittää ongelman (X-optimismi). Verilator on
kaksitilainen. Se alustaa muuttujat oletuksena nollaksi. Valitsin
`--x-initial unique` yhdessä ajonaikaisen valitsimen
`+verilator+rand+reset+2` kanssa alustaa ne satunnaisiksi, mikä
paljastaa nollauksesta riippuvat virheet toisella tavalla. Hyvä käytäntö on
ajaa regressiotestit useammalla siemenluvulla ja nelitilaisella
simulaattorilla ennen tapeoutia tai julkaisua.

## Käytännössä

- **Kirjoita kuvioita, älä algoritmeja.** Synteesi tunnistaa
  vakiintuneet kuviot: rekisteri, multiplekseri, laskuri,
  siirtorekisteri, muisti, tilakone. Mitä lähempänä koodi on
  kuviota, sitä ennustettavampi tulos. Laitteistoa kuvaava koodi on
  usein pidempää kuin ohjelmisto, mutta yksinkertaisempaa.
- **Tyylioppaan säännöt.** Laajasti käytetty pohja on lowRISCin
  *Verilog Coding Style Guide*: `logic` kaikkialle, `always_comb` ja
  `always_ff`, ei viiveitä, nimetyt kytkennät, `_q`- ja `_d`-
  jälkiliitteet, yksi moduuli tiedostossa ja `default_nettype none`.
  Kun projektilla on tyyliopas, sitä noudatetaan.
- **Lint ennen simulointia.** `verilator --lint-only -Wall` on nopein
  palaute. Projektit ajavat lintin jatkuvassa integraatiossa ja
  vaativat, että varoituksia ei ole.
- **Lue synteesiraportti.** Raportissa näkyvät päätellyt salvat,
  muistit, DSP-lohkot, poistetut rekisterit ja ajoitus. Odottamaton
  salpa tai poistettu rekisteri on lähes aina virhe RTL:ssä.
- **Muotoilu työkalulla.** Verible (`verible-verilog-format`) muotoilee
  koodin yhtenäisesti, jolloin katselmoinnit keskittyvät
  sisältöön.

## Itsearviointi

- Osaat kertoa, mitkä SystemVerilogin rakenteet syntetisoituvat ja mitkä
  jätetään synteesissä huomiotta.
- Osaat kirjoittaa täydellisen `case`-lauseen ja perustella
  `default`-haaran sisällön.
- Osaat tunnistaa kombinatorisen silmukan ja korjata sen kättelyn
  säännöllä.
- Osaat tulkita Verilatorin tavallisimmat lint-varoitukset ja vaientaa
  aiheellisen poikkeuksen perusteltuna.
- Osaat selittää kaksi- ja nelitilaisen simuloinnin erot ja
  X-optimismin.
