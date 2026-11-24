# Testikaksoiset vai oikea riippuvuus

*Testikaksoinen* (*test double*) on olio, joka esittää testissä oikeaa
riippuvuutta. Gerard Meszarosin jaottelu on vakiintunut, ja sanat
kannattaa käyttää tarkasti, koska ne kertovat, mitä testi oikeastaan
tarkistaa:

| Nimi | Mitä tekee | Esimerkki varastopalvelussa |
|-------------------|-------------------------------------|----------------------------|
| täyte (*dummy*) | täyttää parametrin, ei käytetä | tyhjä tapahtumakirjuri |
| tynkä (*stub*) | palauttaa ennalta annetun vastauksen | `KiinteaHinta` |
| vakoilija (*spy*) | kirjaa kutsut tarkistettaviksi | `Kirjuri` |
| mock | odottaa tiettyjä kutsuja ja tarkistaa ne | `create_autospec` |
| väärennös (*fake*) | toimiva mutta kevyt toteutus | `MuistiVarasto` |

Yksikkötestit käyttävät kaksoisia, jotta testattava koodi saadaan
eristettyä (luku 2). Kysymys on, milloin kaksoinen on liian suuri
yksinkertaistus.

## Mock tarkistaa vuorovaikutusta

Mock-kirjastolla testi voi määrätä, mitä riippuvuus palauttaa, ja
tarkistaa, miten sitä kutsuttiin. `create_autospec` tekee mockin
rajapinnan mukaan, joten olemattoman metodin kutsu tai väärä
parametrimäärä on virhe:

```{.python tiedosto="esimerkit/testit/test_mock.py" osa="mock"}
```

Testi menee läpi, ja se on hyödyllinen: palvelu kutsuu riippuvuuksiaan
oikeassa järjestyksessä oikeilla arvoilla. Mutta paluuarvot ovat testin
kirjoittajan oletuksia. Oikea tietokanta palauttaisi SKU:n muodossa
`ABC-1`, ja oikea hintapalvelu ehkä virheen. Mock toistaa sen, mitä
kirjoittaja luuli riippuvuuden tekevän, eikä voi koskaan yllättää.

## Kun väärennös valehtelee

Väärennös on parempi kuin mock, koska se toimii: tallennettu tuote
löytyy haulla, ja saldo pienenee varauksessa. Vaara on, että väärennös
toimii *eri tavalla* kuin oikea riippuvuus. Tässä on ensimmäinen,
"nopeasti testejä varten" kirjoitettu versio:

```{.python tiedosto="esimerkit/luku06/valehteleva.py" osa="naiivi"}
```

Sama koe sille ja oikealle PostgreSQLille:

```{.tuloste tiedosto="esimerkit/luku06/valehteleva.odotettu"}
```

Väärennös tekee kolme oletusta, joita tietokanta ei tee. Sanakirjan avain
on kirjainkoon mukainen, joten haku pienillä kirjaimilla ei löydä
tuotetta, ja sama SKU eri kirjainkoolla hyväksytään toiseen kertaan;
tietokannan uniikki indeksi `lower(sku)` hylkää sen. Aikaleima on
`datetime.now()` ilman aikavyöhykettä, tietokannan `timestamptz` palauttaa
vyöhykkeellisen. Kaikki yksikkötestit, jotka käyttävät tätä väärennöstä,
menevät läpi, ja tuotannossa sama koodi käyttäytyy toisin.

## Sopimustestit varmistavat väärennöksen

Ratkaisu ei ole luopua väärennöksistä vaan *todentaa* ne: sama
testisarja ajetaan väärennökselle ja oikealle toteutukselle. Pytestissä
tämä on parametroitu fixture:

```{.python tiedosto="esimerkit/testit/conftest.py" osa="sopimus"}
```

```{.python tiedosto="esimerkit/testit/test_varasto.py" osa="sopimustestit"}
```

Jokainen testi ajetaan kahdesti (`[muisti]` ja `[postgres]`). Naiivi
väärennös ei läpäisisi sarjaa, joten korjattu `MuistiVarasto` vertaa
SKU:t pienillä kirjaimilla ja antaa vyöhykkeellisen aikaleiman:

```{.python tiedosto="esimerkit/varasto/varasto.py" osa="muisti"}
```

Nyt väärennöksen käyttö yksikkötesteissä on perusteltua: se on todistetusti
samanlainen kuin oikea tallennus niiltä osin, joita sopimus kattaa. Kun
oikea toteutus muuttuu, sopimustesti kertoo, että myös väärennös on
päivitettävä. Rajapinta, jota testi käyttää, on pieni:

```{.python tiedosto="esimerkit/varasto/varasto.py" osa="rajapinta"}
```

## HTTP-riippuvuus kontissa

Toisen palvelun kohdalla vaihtoehtoja on kolme: mockata HTTP-asiakas,
ajaa toisen tiimin oikeaa palvelua tai ajaa *palvelun väärennöstä*
kontissa. Kolmas on yleensä paras integraatiotestiin: oma HTTP-asiakas
(aikarajat, uudelleenyritykset, JSON:n jäsennys, virhekoodit) testataan
oikealla HTTP-liikenteellä, mutta testi ei riipu toisen palvelun
tietokannasta tai saatavuudesta.

```{.python tiedosto="esimerkit/varasto/hinnat.py" osa="asiakas"}
```

```{.python tiedosto="esimerkit/testit/test_hinnat.py" osa="hintatestit"}
```

Väärennöksen hallintarajapinta (`/hallinta/virheet`) antaa testin
pyytää tilapäisiä 503-vastauksia. Näin uudelleenyritysten logiikka
testataan oikeaa HTTP-pinoa vasten: tilapäinen virhe yritetään uudelleen,
pysyvä päättyy virheeseen, eikä 404:ää yritetä lainkaan uudelleen.

Valmiita työkaluja samaan ovat WireMock (Java, myös konttikuvana) ja
MockServer. Niissä vastaukset kuvataan asetustiedostoissa tai
rajapinnan kautta, ja ne osaavat tallentaa oikean palvelun liikennettä
toistettavaksi. Pieni oma väärennös on perusteltu, kun rajapinta on
pieni ja väärennöksen pitää käyttäytyä (esimerkiksi tuottaa virheitä
pyynnöstä).

## Milloin mitäkin

| Tilanne | Valinta |
|--------------------------------------------|-------------------------|
| puhdas logiikka, riippuvuus vain välittää dataa | tynkä tai vakoilija |
| tärkeää on, että kutsu tehdään (esim. tapahtuma julkaistaan) | vakoilija tai mock |
| paljon testejä, jotka tarvitsevat toimivan tallennuksen | väärennös + sopimustestit |
| SQL, rajoitteet, transaktiot, samanaikaisuus | oikea tietokanta kontissa |
| oma HTTP-asiakas | palvelun väärennös kontissa |
| toisen palvelun käyttäytyminen | sopimustesti (luku 9) |

## Käytännössä

- Nimeä kaksoiset sen mukaan, mitä ne ovat. "Mock" kaikesta tekee
  testeistä vaikeita lukea.
- Älä mockaa sitä, mitä et omista: tietokannan ajuria, HTTP-kirjastoa tai
  toisen palvelun asiakasta. Kääri ne omaan rajapintaan ja testaa kääre
  integraatiotestillä.
- Aja väärennökselle sama sopimustestisarja kuin oikealle toteutukselle.
  Väärennös ilman sopimustestejä on ajan myötä valehteleva väärennös.
- Käytä mockia vuorovaikutuksen tarkistamiseen, ei käyttäytymisen
  todistamiseen.

## Itsearviointi

- Osaat erottaa tyngän, vakoilijan, mockin ja väärennöksen ja valita
  niistä tilanteeseen sopivan.
- Osaat näyttää, miten mock tai naiivi väärennös voi hyväksyä koodin,
  joka ei toimi oikean riippuvuuden kanssa.
- Osaat kirjoittaa parametroidun sopimustestisarjan, joka todentaa
  väärennöksen oikeaa toteutusta vasten.
- Osaat testata HTTP-asiakkaan virheenkäsittelyn kontissa ajettavaa
  palvelun väärennöstä vasten.
