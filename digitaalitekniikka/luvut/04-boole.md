# Boolen algebra ja sieventäminen

Boolen algebra on porttipiirien laskusääntöjen järjestelmä. Sen avulla
totuustaulusta saadaan lauseke, lausekkeesta piiri, ja piiri voidaan
sieventää pienemmäksi muuttamatta sen toimintaa.

## Lait

Tärkeimmät lait ovat tuttuja tavallisesta algebrasta, mutta kaksi
poikkeaa: OR osittuu AND:n yli ($a + bc = (a+b)(a+c)$), ja
idempotenssi pätee ($a + a = a$, $aa = a$).

| Laki | AND-muoto | OR-muoto |
|------|-----------|----------|
| Identiteetti | $a \cdot 1 = a$ | $a + 0 = a$ |
| Nolla-alkio | $a \cdot 0 = 0$ | $a + 1 = 1$ |
| Komplementti | $a \bar{a} = 0$ | $a + \bar{a} = 1$ |
| Osittelu | $a(b + c) = ab + ac$ | $a + bc = (a+b)(a+c)$ |
| De Morgan | $\overline{ab} = \bar{a} + \bar{b}$ | $\overline{a+b} = \bar{a}\,\bar{b}$ |
| Absorptio | $a(a + b) = a$ | $a + ab = a$ |
| Konsensus | | $ab + \bar{a}c + bc = ab + \bar{a}c$ |

Laki on totta, jos se pätee kaikilla muuttujien arvoilla. Koska
muuttujia on vähän, sen voi tarkistaa käymällä kaikki rivit läpi.
Tämä on *tyhjentävä tarkistus*, ja se on digitaalisuunnittelun
yleisin todistusmenetelmä pienille lohkoille:

```{.python tiedosto="esimerkit/04-boole.py" osa="lait"}
```

Konsensuslaki on kiinnostavin. Termi $bc$ on looginen seuraus kahdesta
muusta, joten sen voi poistaa. Luvussa 7 nähdään, että juuri sitä
tarvitaan joskus takaisin: se poistaa hasardin.

## Kanoninen muoto

Mistä tahansa totuustaulusta saa lausekkeen suoraan: jokaista riviä,
jolla funktio on 1 (*mintermiä*), vastaa tulotermi, ja termit
yhdistetään OR-portilla. Tulos on *tulojen summa* (sum of products,
SOP), joka toteutetaan kaksitasoisena AND–OR-piirinä.

```{.python tiedosto="esimerkit/04-boole.py" osa="kanoninen"}
```

Kolmen syötteen enemmistöfunktio on 1, kun vähintään kaksi syötettä
on 1:

```{.python tiedosto="esimerkit/04-boole.py" osa="enemmisto"}
```

```{.tuloste tiedosto="esimerkit/04-boole.odotettu"}
```

Kanoninen muoto tarvitsee neljä kolmen tulon AND-porttia; sievennetty
kolme kahden tulon porttia. Enemmistöfunktio on muuten täyssummaimen
muistibitti (luku 6).

## Karnaugh-kartta

Karnaugh-kartta on totuustaulu ruudukkona, jonka rivit ja sarakkeet
ovat Gray-järjestyksessä. Vierekkäiset ruudut eroavat yhdessä
muuttujassa, myös reunojen yli, joten kaksi vierekkäistä ykköstä
voidaan yhdistää laista $xy + x\bar{y} = x$. Neljän, kahdeksan tai
kuudentoista ruudun suorakulmaiset ryhmät poistavat kaksi, kolme tai
neljä muuttujaa.

```{.python tiedosto="esimerkit/04-karnaugh.py" osa="kartta"}
```

Esimerkkinä on funktio, joka kertoo, onko BCD-numero alkuluku.
BCD-syötteessä koodit 10–15 eivät koskaan esiinny, joten niiden arvo
on *yhdentekevä* (don't care, x). Yhdentekevät ruudut saa ottaa
ryhmään, jos se suurentaa ryhmää:

```{.python tiedosto="esimerkit/04-karnaugh.py" osa="bcd"}
```

```{.tuloste tiedosto="esimerkit/04-karnaugh.odotettu"}
```

Tulos $\bar{b}c + bd$ on kaksi kahden tulon AND-porttia ja yksi OR.
Ilman yhdentekeviä rivejä tulos olisi $\bar{a}\bar{b}c + \bar{a}bd$:
kaksi kolmen tulon termiä, koska rivit 10–15 pitäisi pakottaa
nolliksi.

## Quine–McCluskey ohjelmana

Karnaugh-kartta toimii käsin enintään neljällä tai viidellä
muuttujalla. Sama ajatus algoritmina on Quine–McCluskeyn menetelmä:

1. Yhdistä termejä, jotka eroavat yhdessä bitissä, niin kauan kuin
   voi. Termejä, joita ei voi yhdistää, kutsutaan *alkutermeiksi*
   (prime implicants).
2. Valitse alkutermeistä mahdollisimman pieni joukko, joka kattaa
   kaikki ykköset.

Termi esitetään merkkijonona, jossa '-' tarkoittaa poistunutta
muuttujaa:

```{.python tiedosto="esimerkit/qm.py" osa="yhdista"}
```

```{.python tiedosto="esimerkit/qm.py" osa="alkutermit"}
```

Toinen vaihe on joukkopeitto-ongelma, joka on yleisesti NP-vaikea.
Ensin valitaan *välttämättömät alkutermit*, joita mikään muu termi ei
korvaa, ja loput ahneesti:

```{.python tiedosto="esimerkit/qm.py" osa="peitto"}
```

```{.python tiedosto="esimerkit/qm.py" osa="alkuluku"}
```

```{.tuloste tiedosto="esimerkit/qm.odotettu"}
```

Ahne valinta ei aina löydä pienintä ratkaisua, mutta käytännön
työkaluissa (esimerkiksi Espresso) käytetään heuristiikkoja juuri siksi,
että tarkka ratkaisu on liian kallis suurille funktioille. Samaa
`sievenna`-funktiota käytetään luvussa 10 tilakoneen logiikkaan.

## Käytännössä

- **Työkalu sieventää, ihminen jäsentää.** Synteesityökalu sieventää
  logiikan paremmin kuin kukaan käsin. Suunnittelijan tehtävä on kuvata
  funktio selkeästi ja kertoa työkalulle, mitä se saa olettaa:
  yhdentekevät arvot ovat sieventämisen tärkein lähde.
- **Kerro yhdentekevät tilanteet.** Jos jokin syöte ei koskaan esiinny,
  kuvaa se (SystemVerilogissa `default`-haara, jonka arvo on `'x`, tai
  `unique case`). Muuten työkalu toteuttaa turhaan arvon, jota ei
  tarvita.
- **Tyhjentävä tarkistus pienille lohkoille.** Alle noin 20 tulobitin
  kombinaatiologiikka testataan kaikilla syötteillä (2^20 on noin
  miljoona). Satunnaistestaus jättää aina aukkoja.
- **Kaksitasoinen ei ole aina paras.** Tulojen summa on nopea mutta
  voi olla suuri. XOR-funktiot (pariteetti, summa) ovat tulojen
  summana eksponentiaalisen suuria mutta pieniä XOR-puuna.

## Itsearviointi

- Osaat tarkistaa Boolen lain tai kahden lausekkeen yhtäpitävyyden
  tyhjentävästi.
- Osaat muodostaa totuustaulusta kanonisen tulojen summan.
- Osaat sieventää neljän muuttujan funktion Karnaugh-kartalla ja
  käyttää yhdentekeviä arvoja.
- Osaat selittää Quine–McCluskeyn menetelmän vaiheet ja sen, miksi
  peittovaihe on vaikea.
