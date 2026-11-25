# Avoin osoitteistus

Ketjutettu hajautustaulu varaa jokaiselle avaimelle oman solmun ja
seuraa haussa osoittimia ympäri muistia. *Avoimessa osoitteistuksessa*
(engl. open addressing) avaimet ovat itse taulukossa. Jos avaimen
paikka on varattu, kokeillaan seuraavaa paikkaa ennalta määrätyssä
järjestyksessä, kunnes löytyy avain tai tyhjä paikka. Solmuja ja
osoittimia ei ole, ja peräkkäiset kokeilut osuvat samaan
välimuistiriviin. Siksi useimmat nopeat hajautustaulut – esimerkiksi
Rustin ja Abseilin taulut sekä Pythonin `dict` – käyttävät avointa
osoitteistusta.

## Kokeilujärjestys

Yksinkertaisin järjestys on *lineaarinen kokeilu* (engl. linear
probing): paikka $h$, sitten $h + 1$, $h + 2$ ja niin edelleen,
taulukon lopusta takaisin alkuun. Vaihtoehtoja ovat *neliöllinen
kokeilu* ($h + 1$, $h + 3$, $h + 6$, …) ja *kaksoishajautus*, jossa
askeleen pituus lasketaan toisella hajautusfunktiolla. Ne hajottavat
paremmin, mutta lineaarinen kokeilu käyttää välimuistia parhaiten, ja
hyvällä hajautusfunktiolla se on käytännössä nopein.

Esimerkin taulussa on 32-bittisiä avaimia. Jokaisella paikalla on tila:
tyhjä, käytössä tai hautakivi (selitetään alla). Paikka lasketaan
Fibonacci-hajautuksella, joka kertoo avaimen luvulla
$\lfloor 2^{32}/\varphi \rfloor$ ja ottaa tuloksen ylimmät bitit:

```{.c tiedosto="esimerkit/07-avoin.c" osa="rakenne"}
```

Kertolasku sekoittaa avaimen kaikki bitit ylimpiin bitteihin, joten
peräkkäisetkin avaimet (1, 2, 3, …) hajaantuvat ympäri taulua. Ilman
sekoitusta peräkkäiset avaimet täyttäisivät peräkkäiset paikat ja
muodostaisivat pitkän yhtenäisen jakson.

## Haku ja hautakivet

Haku etenee avaimen paikasta, kunnes löytyy avain tai tyhjä paikka.
Tyhjä paikka todistaa, ettei avainta ole: jos se olisi lisätty, se
olisi sijoitettu viimeistään tähän paikkaan.

```{.c tiedosto="esimerkit/07-avoin.c" osa="haku"}
```

Tämä päättely tekee poistosta hankalan. Jos poistettu paikka
merkittäisiin tyhjäksi, haku pysähtyisi siihen eikä löytäisi avaimia,
jotka on lisätty sen *ohi* törmäyksen vuoksi. Siksi poistettu paikka
merkitään *hautakiveksi* (engl. tombstone): haku jatkaa sen yli, mutta
lisäys saa käyttää sen uudelleen.

Esimerkin funktio `jakso` näyttää tilanteen kahdeksan paikan
taulussa. Avaimilla 1, 9 ja 17 on sama kotipaikka, joten ne asettuvat
peräkkäin. Keskimmäinen poistetaan (hautakivi on tulosteessa `+`), ja
viimeisen haku kulkee hautakiven yli:

```{.tuloste tiedosto="esimerkit/07-avoin.odotettu" rivit="1-6"}
```

```{.dot tiedosto="kaaviot/avoin-jakso.dot" otsikko="Kokeilujakso: hautakivi (†) pitää jakson yhtenäisenä, tyhjäksi merkitty paikka katkaisee sen"}
```

Viimeisellä rivillä poisto on tehty väärin merkitsemällä paikka
tyhjäksi. Avain 17 on yhä taulussa, mutta haku pysähtyy paikkaan 5
eikä löydä sitä.

Hautakivillä on hintansa. Ne eivät sisällä avaimia, mutta pidentävät
hakuja kuin käytössä olevat paikat. Jos taulussa lisätään ja poistetaan
jatkuvasti, hautakivet voivat täyttää sen, ja epäonnistunut haku käy
koko taulun läpi. Siksi uudelleenrakennuksen raja lasketaan käytössä
olevista paikoista *ja* hautakivistä. Uudelleenrakennus lisää vain
elävät avaimet, joten hautakivet katoavat; taulua suurennetaan vain,
jos eläviä avaimia on paljon:

```{.c tiedosto="esimerkit/07-avoin.c" osa="kasvu"}
```

Lineaarisessa kokeilussa hautakivet voi välttää kokonaan siirtämällä
poiston jälkeen saman jakson myöhempiä avaimia taaksepäin (engl.
backward shift deletion). Algoritmi on hieman monimutkaisempi, mutta
taulu pysyy puhtaana.

## Vertailutesti

Avoimen osoitteistuksen virheet ovat salakavalia: väärin käsitelty
hautakivi rikkoo vain ne haut, joiden ketju sattuu kulkemaan sen yli.
Tällaiset virheet löytää parhaiten *satunnaistettu vertailutesti*.
Satunnainen lisäysten, poistojen ja hakujen sarja ajetaan sekä taululle
että referenssille, jonka oikeellisuus on ilmeinen – tässä
totuusarvotaulukolle, joka kertoo suoraan, onko avain mukana:

```{.c tiedosto="esimerkit/07-avoin.c" osa="vertailu"}
```

Avainalue on pieni (4096), jotta samat avaimet toistuvat usein ja
poistot osuvat olemassa oleviin avaimiin. Kun siemen on kiinteä, sama
sarja toistuu joka ajossa; jos testi löytää eron, sen voi ajaa
uudelleen debuggerissa. Silmukan voi helposti laajentaa tulostamaan
ensimmäisen eroavan operaation numeron, jolloin virheen paikantaminen
on suoraviivaista.

```{.tuloste tiedosto="esimerkit/07-avoin.odotettu" rivit="8-8"}
```

## Kuormituskerroin

Avoimessa osoitteistuksessa kuormituskerroin $\alpha$ on enintään 1,
ja hakujen hinta kasvaa jyrkästi, kun taulu täyttyy. Knuthin
analyysin mukaan lineaarisessa kokeilussa tarvitaan keskimäärin

$$\frac{1}{2}\left(1 + \frac{1}{1 - \alpha}\right) \quad\text{ja}\quad
\frac{1}{2}\left(1 + \frac{1}{(1 - \alpha)^2}\right)$$

kokeilua onnistuneessa ja epäonnistuneessa haussa. Mittaus täyttää
65 536 paikan taulun satunnaisilla avaimilla eri asteisiin ja hakee
ensin jokaisen lisätyn avaimen, sitten yhtä monta puuttuvaa:

```{.c tiedosto="esimerkit/07-avoin.c" osa="kuormitus"}
```

```{.tuloste tiedosto="esimerkit/07-avoin.odotettu" rivit="9-"}
```

![Kokeilujen määrä kuormituskertoimen funktiona: Knuthin kaavat
käyrinä ja yllä olevan tulosteen mittaukset pisteinä](kuvat/kuormitus.png){width=85%}

Mittaus osuu teoriaan. Kun kerroin kasvaa puolesta 0,9:ään,
onnistuneen haun hinta lähes nelinkertaistuu, mutta epäonnistuneen
kaksikymmenkertaistuu. Varatut paikat kasautuvat yhtenäisiksi
jaksoiksi (engl. primary clustering), ja puuttuvan avaimen haku joutuu
käymään jakson loppuun. Siksi lineaarisen kokeilun taulu kasvatetaan
tavallisesti, kun kerroin ylittää 0,5–0,875; esimerkki käyttää rajaa
0,75.

## Ketjutus vai avoin osoitteistus?

| Ominaisuus | Ketjutus | Avoin osoitteistus |
|------------|----------|--------------------|
| Muistinvaraus | solmu avainta kohti | yksi taulukko |
| Kuormituskerroin | voi ylittää 1 | oltava selvästi alle 1 |
| Välimuisti | osoittimien seuraaminen | peräkkäiset kokeilut |
| Poisto | listan poisto | hautakivi tai siirto |
| Osoitin alkioon | pysyy voimassa | mitätöityy kasvatuksessa |
| Suuret alkiot | halpa siirtää (vain linkit) | kallis siirtää |

Ketjutus on yksinkertaisempi ja sietää huonoa hajautusfunktiota ja
suurta kuormaa paremmin. Avoin osoitteistus on nopeampi pienillä
avaimilla, kunhan hajautusfunktio on hyvä ja kerroin pidetään
kohtuullisena. Suurten alkioiden kanssa taulukkoon kannattaa
tallentaa avain ja indeksi erilliseen alkiotaulukkoon, kuten Pythonin
`dict` tekee.

## Käytännössä

- **Lineaarinen kokeilu ja hyvä sekoitus.** Fibonacci-hajautus tai
  vastaava sekoitus ennen indeksointia on välttämätön, jos avaimet ovat
  peräkkäisiä lukuja.
- **Hautakivet lasketaan kuormaan.** Uudelleenrakennuksen raja
  lasketaan käytössä olevista paikoista ja hautakivistä yhteensä.
- **Kuormituskerroin 0,75 tai alle.** Epäonnistuneen haun hinta kasvaa
  kertoimen $1/(1 - \alpha)^2$ mukaan.
- **Satunnaistettu vertailutesti kiinteällä siemenellä.** Pieni
  avainalue saa poistot ja hautakivet osumaan toisiinsa.
- **Erota tila avaimesta.** Erillinen tilataulukko välttää varatun
  "tyhjä"-avainarvon, jota käyttäjä ei saisi tallentaa.

## Itsearviointi

- Osaat toteuttaa avoimen osoitteistuksen hajautustaulun lineaarisella
  kokeilulla.
- Osaat selittää, miksi poistettua paikkaa ei voi merkitä tyhjäksi ja
  miten hautakivet vaikuttavat kuormaan.
- Osaat kirjoittaa satunnaistetun vertailutestin, joka vertaa rakennetta
  yksinkertaiseen referenssiin kiinteällä siemenellä.
- Osaat kertoa, miksi epäonnistuneen haun hinta kasvaa jyrkästi
  kuormituskertoimen lähestyessä yhtä.
