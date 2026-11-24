# Binäärihaku

Järjestetystä taulukosta haku onnistuu logaritmisessa ajassa:
verrataan keskimmäiseen alkioon ja jatketaan siitä puoliskosta, jossa
haettava voi olla. Miljoonan alkion taulukosta haku vie 20 vertailua.
*Binäärihaku* eli puolitushaku on yksinkertainen idea, jonka
toteutuksessa on silti kolme tavallista virhettä: väärä silmukan
ehto, ikuinen silmukka ja keskikohdan ylivuoto. Tämä luku kirjoittaa
haun muotoon, jossa niitä ei voi tehdä, ja yleistää sen hauksi
vastauksen arvoalueelta.

## Alaraja ja yläraja

Pelkkä "löytyikö" ei yleensä riitä. Hyödyllisempi kysymys on *missä
kohdassa* haettava olisi: ensimmäinen alkio, joka on vähintään $x$
(*alaraja*, engl. lower bound), ja ensimmäinen alkio, joka on
suurempi kuin $x$ (*yläraja*). Ne kertovat, onko $x$ mukana, montako
kertaa se esiintyy ja mihin kohtaan se lisättäisiin järjestyksen
säilyttäen. C++:n `std::lower_bound` ja `std::upper_bound` ovat juuri
nämä. C:n `bsearch` palauttaa vain jonkin osuman, ei ensimmäistä.

```{.c tiedosto="esimerkit/06-haku.c" osa="alaraja"}
```

Haku pitää yllä puoliavointa väliä `[lo, hi)`, jossa vastaus on.
Invariantti on, että kaikki välin vasemmalla puolella ovat pienempiä
kuin $x$ ja kaikki välin kohdassa `hi` ja sen oikealla puolella
vähintään $x$. Alussa väli on koko taulukko `[0, n)`, joten invariantti
pätee tyhjästi. Jokainen kierros säilyttää sen ja lyhentää väliä
ainakin yhdellä, koska `keski` on aina välin sisällä. Kun väli on
tyhjä, `lo == hi`, ja invariantin mukaan se on ensimmäinen kohta, jossa
alkio on vähintään $x$. Vastaus voi olla myös $n$: kaikki alkiot ovat
pienempiä.

Yläraja eroaa vain ehdon osalta: `<=` siirtää yhtä suuret vasemmalle
puolelle. Kahden rajan erotus on esiintymien määrä:

```{.c tiedosto="esimerkit/06-haku.c" osa="esimerkki"}
```

```{.tuloste tiedosto="esimerkit/06-haku.odotettu"}
```

Puuttuvalla arvolla, kuten 5, molemmat rajat osoittavat samaan kohtaan,
johon 5 lisättäisiin. Viimeinen rivi on vertailutesti: 1000
satunnaista kasvavaa taulukkoa, joissa on paljon toistoja, ja jokaisella
arvolla taulukon arvoalueen kummaltakin puolelta lineaarinen haku
antaa saman tuloksen. Testiin kuuluvat myös tyhjä taulukko ja arvot,
jotka ovat pienempiä tai suurempia kuin kaikki alkiot, koska juuri
niissä silmukan rajat menevät tavallisesti väärin.

Puoliavoin väli ja kaksi haaraa (`lo = keski + 1` ja `hi = keski`)
ovat tämän muodon ydin. Muoto, jossa väli on suljettu `[lo, hi]` ja
haara `hi = keski - 1`, toimii myös, mutta silloin päättymisehto, alku-
ja loppuarvot sekä paluuarvo on sovitettava toisiinsa erikseen.
Ikuinen silmukka syntyy, kun haara `lo = keski` yhdistetään
keskikohtaan, joka pyöristyy alaspäin: kahden alkion välillä `keski`
on `lo`, eikä väli lyhene.

## Keskikohdan ylivuoto

Keskikohta lasketaan muodossa `lo + (hi - lo) / 2`. Tutumpi
`(lo + hi) / 2` on matemaattisesti sama, mutta summa voi ylivuotaa.
Taulukon indekseillä se vaatii yli miljardin alkion taulukon, ja
virhe olikin Javan standardikirjaston binäärihaussa lähes kymmenen
vuotta, ennen kuin taulukot kasvoivat niin suuriksi. Kun haetaan
kokonaislukujen arvoalueelta, ylivuoto tapahtuu heti. Esimerkki hakee
neliöjuurta koko `int`-alueelta. Koska haara on `lo = keski`,
keskikohta pyöristetään ylöspäin lisäämällä summaan yksi, jotta väli
lyhenee:

```{.c tiedosto="esimerkit/06-keskikohta.kaatuu.c" osa="vaarin"}
```

```text
runtime error: signed integer overflow: 2147483647 + 1 cannot be
represented in type 'int'
```

Ilman sanitoijaa ohjelma jatkaisi negatiivisella keskikohdalla ja
palauttaisi väärän vastauksen. Muoto `lo + (hi - lo) / 2` ei voi
ylivuotaa, kun `0 <= lo <= hi`, koska `hi - lo` on enintään `hi`.
Ylöspäin pyöristävä versio on `hi - (hi - lo) / 2`. Jos välin
alaraja voi olla negatiivinen, myös erotus voi ylivuotaa, ja laskenta
tehdään leveämmällä tyypillä. Etumerkittömillä tyypeillä ylivuoto ei ole
määrittelemätöntä, mutta kiertynyt summa antaa yhtä lailla väärän
keskikohdan.

## Haku vastauksen arvoalueelta

Binäärihaku ei tarvitse taulukkoa. Se tarvitsee vain *monotonisen
ehdon*: kysymyksen, johon vastaus on "ei" jollekin alkuosalle
mahdollisista arvoista ja "kyllä" lopuille. Silloin ensimmäinen
"kyllä" löytyy samalla alarajan haulla.

Kuljetusyritys ajaa paketteja annetussa järjestyksessä yhdellä
autolla, ja paketit on ajettava $D$ päivässä. Mikä on pienin auton
kapasiteetti, jolla se onnistuu? Suoraan optimia on vaikea laskea,
mutta annetun kapasiteetin riittävyyden voi tarkistaa ahneesti
lineaarisessa ajassa: kuormataan paketteja niin kauan kuin mahtuu ja
aloitetaan uusi päivä, kun ei mahdu.

```{.c tiedosto="esimerkit/06-kapasiteetti.c" osa="ehtii"}
```

Ehto on monotoninen: jos kapasiteetti $c$ riittää, myös $c + 1$
riittää. Vastaus on välillä suurimmasta paketista kaikkien summaan,
ja haku on tavallinen alarajan haku tällä välillä:

```{.c tiedosto="esimerkit/06-kapasiteetti.c" osa="pienin"}
```

```{.tuloste tiedosto="esimerkit/06-kapasiteetti.odotettu"}
```

Arvoalueella 42–139 on 98 vaihtoehtoa, ja seitsemän kokeilua riittää,
koska $2^7 = 128$. Kokonaistyö on $O(n \log S)$, missä $S$ on painojen
summa. Raaka vertailu kokeilee kapasiteetit nollasta ylöspäin, kunnes
ehto on tosi, ja antaa 300 satunnaisella syötteellä saman vastauksen.

Sama malli ratkaisee yllättävän monta tehtävää: pienin nopeus, jolla
tiedosto siirtyy määräajassa; suurin puskurikoko, joka mahtuu
muistiin; versionhallinnan `git bisect`, joka etsii ensimmäisen
rikkovan muutoksen. Kaikissa on kaksi osaa: ehto, jonka tarkistaminen
on helppoa, ja todiste siitä, että ehto on monotoninen. Ilman
monotonisuutta binäärihaku palauttaa jonkin vastauksen, mutta ei
välttämättä oikeaa.

## Käytännössä

- **Kirjoita aina alarajan haku.** Puoliavoin väli `[lo, hi)`, ehto
  `lo < hi` ja haarat `lo = keski + 1` ja `hi = keski`. Kaikki muut
  haut (osuma, yläraja, lisäyskohta, esiintymät) saadaan siitä.
- **Keskikohta on `lo + (hi - lo) / 2`.** Summa `lo + hi` ylivuotaa
  arvoalueen hauissa heti ja suurilla taulukoilla myöhemmin.
- **Testaa reunat.** Tyhjä taulukko, yksi alkio, kaikki samat ja arvot
  alueen kummaltakin puolelta; vertaa lineaariseen hakuun.
- **Etsi monotoninen ehto.** Jos optimin laskeminen on vaikeaa mutta
  ehdokkaan tarkistaminen helppoa, hae vastausta arvoalueelta.
- **Kirjasto, kun mahdollista.** C++:n `std::lower_bound` ja
  `std::partition_point` ovat valmiita; C:n `bsearch` ei kerro
  ensimmäistä osumaa.

## Itsearviointi

- Osaat kirjoittaa alarajan ja ylärajan haun puoliavoimella välillä ja
  perustella ne invariantilla.
- Osaat selittää, miksi `(lo + hi) / 2` voi ylivuotaa ja miten
  ylivuoto vältetään.
- Osaat tunnistaa tehtävän, jossa vastausta voi hakea arvoalueelta, ja
  perustella ehdon monotonisuuden.
- Osaat testata binäärihaun reunatapaukset lineaarista hakua vastaan.
