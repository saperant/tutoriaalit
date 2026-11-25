# Funktiot

Funktio on nimetty koodin osa, joka saa syötteenä *parametreja* ja
palauttaa *paluuarvon*. Funktiot ovat ohjelmoinnin tärkein työkalu
monimutkaisuuden hallintaan: iso ongelma jaetaan pieniin osiin, joista
jokainen on helppo ymmärtää, testata ja käyttää uudelleen.

## Määrittely ja kutsu

```{.python tiedosto="esimerkit/04-kuitti.py"}
```

```{.tuloste tiedosto="esimerkit/04-kuitti.odotettu"}
```

Funktion osat:

- `def rivin_hinta(maara: int, a_hinta_snt: int) -> int:` määrittelee
  funktion nimen ja parametrit. Merkinnät `: int` ja `-> int` ovat
  *tyyppivihjeitä*: parametrit ja paluuarvo ovat kokonaislukuja.
  Python ei käytä niitä ajon aikana, mutta mypy tarkistaa niiden
  avulla, että funktiota kutsutaan oikein.
- Ensimmäinen rivi `"""..."""` on dokumentaatiomerkkijono. Se kertoo,
  *mitä* funktio tekee, ei *miten*.
- `return` lopettaa funktion ja palauttaa arvon kutsujalle. Funktio
  ilman `return`-lausetta palauttaa `None`.

Kutsu `rivin_hinta(2, 189)` sijoittaa argumentit parametreihin
järjestyksessä, suorittaa rungon ja korvautuu paluuarvolla.

Pääohjelma on nyt lyhyt ja luettava: se kertoo *mitä* tehdään, ja
funktiot kertovat *miten*. Jos ALV-laskenta muuttuu, muutos tehdään
yhteen paikkaan.

## Paluuarvo vai tulostus

Funktio, joka palauttaa tuloksen, on hyödyllisempi kuin funktio, joka
tulostaa sen. Palautettua arvoa voi käyttää laskennassa, tallentaa,
näyttää eri muodoissa ja testata. Tulostettu arvo on vain tekstiä
ruudulla.

```{.python tiedosto="esimerkit/04-salasana.py"}
```

```{.tuloste tiedosto="esimerkit/04-salasana.odotettu"}
```

`salasanan_ongelmat` ei päätä, miten ongelmat esitetään: sama funktio
sopisi verkkolomakkeeseen ja komentoriviohjelmaan. Paluuarvona on lista
ongelmista, joten tyhjä lista tarkoittaa hyväksyttyä salasanaa ja
kutsuja voi kertoa käyttäjälle kaikki puutteet kerralla.

Esimerkki käyttää listaa jo ennen lukua *Kokoelmat*: `ongelmat = []`
luo tyhjän listan, `append` lisää sen loppuun alkion ja
`", ".join(ongelmat)` yhdistää listan merkkijonot pilkuin erotelluksi
tekstiksi. `for merkki in salasana` käy läpi merkkijonon merkit yksi
kerrallaan.

## Oletusarvot ja nimetyt argumentit

Parametrilla voi olla oletusarvo (`min_pituus: int = 12`), jolloin
argumentin voi jättää kutsusta pois. Argumentin voi antaa myös nimellä:
`salasanan_ongelmat("Kissa123", min_pituus=8)`. Nimetty argumentti tekee
kutsusta itsedokumentoivan: pelkkä `8` ei kertoisi lukijalle mitään.

## Näkyvyys: paikalliset ja globaalit nimet

Funktion sisällä sijoitetut nimet ovat *paikallisia*: ne ovat olemassa
vain funktion suorituksen ajan, eivätkä ne näy funktion ulkopuolelle.
Tämä on hyvä asia, koska funktion sisäiset nimet eivät voi sotkea
muuta ohjelmaa. Seurauksena funktio ei kuitenkaan voi muuttaa
ulkopuolista muuttujaa sijoituksella:

```{.python tiedosto="esimerkit/04-kavijat.ei-kaanny.py"}
```

Funktiossa `kirjaa_kavija_vaarin` sijoitus tekee nimestä `kavijoita`
paikallisen, joten oikean puolen `kavijoita` viittaa paikalliseen
muuttujaan, jolla ei vielä ole arvoa. Ohjelma kaatuisi virheeseen
`UnboundLocalError`, mutta ruff huomaa sen jo ennen ajoa:

```text
F823 Local variable `kavijoita` referenced before assignment
```

Oikea ratkaisu on `kirjaa_kavija`: arvo tuodaan funktioon parametrina
ja uusi arvo palautetaan. Avainsanalla `global` funktio voisi muuttaa
globaalia muuttujaa, mutta sitä ei käytetä, koska silloin funktion
toiminta riippuu piilotetusta tilasta, jota on vaikea seurata ja
testata.

## Rekursio: funktio kutsuu itseään

Funktio voi kutsua myös itseään. Tällainen *rekursiivinen* funktio
ratkaisee tehtävän palauttamalla sen samaan tehtävään pienemmällä
syötteellä. Kertoma 4! on 4 · 3 · 2 · 1, eli 4 kertaa kertoma 3!:

```{.python tiedosto="esimerkit/04-rekursio.py"}
```

```{.tuloste tiedosto="esimerkit/04-rekursio.odotettu"}
```

Rekursiivisessa funktiossa on aina kaksi osaa:

- *Päättymisehto* (`n <= 1`) palauttaa tuloksen suoraan ilman uutta
  kutsua. Ilman sitä kutsut jatkuisivat loputtomiin.
- *Rekursioaskel* (`n * kertoma(n - 1)`) kutsuu funktiota syötteellä,
  joka on lähempänä päättymisehtoa.

```{.dot otsikko="Kutsun `kertoma(4)` kutsupino. Jokaisella kutsulla on oma paikallinen `n`. Paluuarvot (katkoviivat) lasketaan alhaalta ylös, kun sisin kutsu on palannut."}
digraph {
  nodesep=0.9; ranksep=0.28;
  p [label="pääohjelma: print(kertoma(4))"];
  k4 [label="kertoma(4):  n = 4"];
  k3 [label="kertoma(3):  n = 3"];
  k2 [label="kertoma(2):  n = 2"];
  k1 [label="kertoma(1):  n = 1"];
  p:sw -> k4:nw [label="kutsu  "];
  k4:sw -> k3:nw [label="kutsu  "];
  k3:sw -> k2:nw [label="kutsu  "];
  k2:sw -> k1:nw [label="kutsu  "];
  k1:ne -> k2:se [label="  palauttaa 1", style=dashed];
  k2:ne -> k3:se [label="  palauttaa 2 · 1 = 2", style=dashed];
  k3:ne -> k4:se [label="  palauttaa 3 · 2 = 6", style=dashed];
  k4:ne -> p:se [label="  palauttaa 4 · 6 = 24", style=dashed];
}
```

Python pitää keskeneräiset kutsut muistissa *kutsupinossa*: kun
`kertoma(4)` kutsuu funktiota `kertoma(3)`, se jää odottamaan tulosta,
ja sen paikalliset nimet säilyvät. Uusi kutsu saa omat paikalliset
nimensä, joten eri kutsujen `n` eivät sekoitu. Pino purkautuu
käänteisessä järjestyksessä. Sama pino näkyy virheilmoituksessa, kun
ohjelma kaatuu (luku *Virheet ja poikkeukset*).

Pinon koko on rajattu: Python keskeyttää ohjelman poikkeukseen
`RecursionError`, kun sisäkkäisiä kutsuja on noin tuhat. Näin käy
myös, jos päättymisehto puuttuu tai sitä ei koskaan saavuteta.

Pelkkään toistoon silmukka on Pythonissa yleensä selkeämpi, kuten
esimerkin `kertoma_silmukalla`. Rekursio on luonteva, kun data itse
on sisäkkäistä: hakemistossa on hakemistoja, listassa listoja ja
lausekkeessa osalausekkeita. Silloin funktio käsittelee yhden tason
ja kutsuu itseään jokaiselle sisemmälle osalle (taidot
*Tietorakenteet* ja *Algoritmit*).

## Kokeile itse

Tästä luvusta alkaen useimmissa tehtävissä kirjoitetaan funktio.
Tarkistin kutsuu funktiota suoraan ja vertaa paluuarvoa odotettuun,
joten funktion pitää palauttaa tulos eikä tulostaa sitä.

1. **Celsiuksesta fahrenheitiksi** (`04-1`). Funktio
   `celsius_fahrenheitiksi` muuntaa lämpötilan kaavalla
   F = C · 9 / 5 + 32.
2. **Karkausvuosi** (`04-2`). Funktio `on_karkausvuosi` palauttaa
   totuusarvon: neljällä jaolliset vuodet ovat karkausvuosia, sadalla
   jaolliset eivät, paitsi 400:lla jaolliset.
3. **Postimaksu** (`04-3`). Funktio `postimaksu` palauttaa hinnan
   painoluokan mukaan. Pikalähetys on parametri, jolla on oletusarvo.
4. **Numeroiden summa rekursiolla** (`04-4`). Luvun *Ehdot ja toisto*
   numerosumma ilman silmukkaa: funktio kutsuu itseään luvulla, josta
   viimeinen numero on pudotettu pois.

## Käytännössä

- **Yksi funktio, yksi tehtävä.** Jos funktion tehtävän kuvaamiseen
  tarvitaan sana "ja", se kannattaa todennäköisesti jakaa kahdeksi.
  Hyvä funktio mahtuu ruudulle, tyypillisesti alle 20 riviä.
- **Nimeä funktio teon mukaan** (`laske_tarkiste`, `tulosta_rivi`) tai
  tuloksen mukaan (`rivin_hinta`, `salasanan_ongelmat`).
- **Palauta, älä tulosta.** Erota laskenta ja esittäminen: laskevat
  funktiot palauttavat arvon, ja vain ohjelman reunalla oleva koodi
  lukee syötteen ja tulostaa.
- **Puhtaat funktiot ensin.** Funktio, jonka tulos riippuu vain
  parametreista eikä se muuta mitään muuta, on helppo ymmärtää ja
  testata. Vältä globaaleja muuttujia; vakiot (`ALV_PROSENTTI`) ovat
  sallittuja, koska ne eivät muutu.
- **Tyyppivihjeet ja dokumentaatiomerkkijono jokaiseen funktioon.**
  Ne ovat funktion käyttöohje, jonka myös mypy ymmärtää.
- **DRY (*don't repeat yourself*).** Kun sama laskenta toistuu, siitä
  tehdään funktio. Kopioitu koodi korjataan helposti vain yhdestä
  kohdasta.
- **Silmukka toistoon, rekursio sisäkkäiseen dataan.** Rekursiivisesta
  funktiosta tarkistetaan ensin päättymisehto ja se, että jokainen
  kutsu lähestyy sitä.

## Itsearviointi

- Osaat määritellä funktion parametreineen, tyyppivihjeineen,
  dokumentaatiomerkkijonoineen ja paluuarvoineen.
- Osaat pilkkoa ohjelman pieniksi funktioiksi ja perustella jaon.
- Osaat selittää, miksi palauttava funktio on parempi kuin tulostava.
- Osaat käyttää oletusarvoja ja nimettyjä argumentteja.
- Osaat selittää paikallisen ja globaalin nimen eron ja välttää
  globaalia tilaa.
- Osaat kirjoittaa rekursiivisen funktion, nimetä sen päättymisehdon
  ja selittää, mitä kutsupinossa tapahtuu.
