# Sopimustestaus

Integraatiotesti hintapalvelun väärennöstä vasten todistaa, että
varastopalvelu toimii väärennöksen kanssa. Se ei todista, että väärennös
vastaa oikeaa hintapalvelua. Jos hintapalvelun tiimi nimeää kentän
uudelleen, varastopalvelun testit menevät yhä läpi, ja tuotanto hajoaa.
Kahden palvelun yhteensopivuus on oma testattava asiansa.

Yksi vaihtoehto on päästä päähän -testi: käynnistetään molemmat oikeat
palvelut ja niiden tietokannat. Se on hidas ja hauras, ja kun palveluja
on kymmeniä, kokonaisuutta ei saa ylös luotettavasti. *Sopimustestaus*
jakaa saman tarkistuksen kahteen nopeaan testiin.

## Kuluttajavetoinen sopimus

Sopimuksen kirjoittaa *kuluttaja* (varastopalvelu): se kuvaa, mitä se
tarvitsee tuottajan vastauksesta. Ei koko rajapintaa, vaan juuri ne
kentät ja tyypit, joita sen koodi käyttää. Sopimus on tiedosto, joka
jaetaan tuottajalle.

```{.dot otsikko="Kuluttajavetoinen sopimustestaus"}
digraph {
  rankdir=LR;
  kuluttaja [label="kuluttaja\nvarastopalvelu"];
  sopimus [label="sopimus\nhinta-v1", shape=note];
  tuottaja [label="tuottaja\nhintapalvelu"];
  kuluttaja -> sopimus [label="kirjoittaa ja\ntestaa väärennöstä vasten"];
  sopimus -> tuottaja [label="tuottajan CI\ntarkistaa vastaukset"];
}
```

1. Kuluttaja kirjoittaa sopimuksen ja testaa oman koodinsa väärennöstä
   vasten, joka noudattaa sopimusta.
2. Tuottaja ajaa sopimuksen omaa oikeaa palveluaan vasten jokaisessa
   muutoksessa. Jos muutos rikkoo sopimuksen, tuottajan CI pysähtyy
   ennen kuin kuluttaja ehtii hajota.

Tunnetuin työkalu on Pact. Siinä kuluttajan testi kirjaa odotetut
pyynnöt ja vastaukset sopimustiedostoon, sopimukset jaetaan
välityspalvelimen (Pact Broker) kautta, ja tuottajan testi toistaa
pyynnöt oikeaa palvelua vasten. Välityspalvelin kertoo myös, mitkä
versiot ovat yhteensopivia, jolloin julkaisun voi estää, jos jokin
tuotannossa oleva kuluttaja hajoaisi (`can-i-deploy`).

## Kevyt sopimus JSON Schemalla

Pienempi versio samasta ajatuksesta on JSON Schema: kuluttaja kuvaa
vastauksen muodon, ja molemmat osapuolet tarkistavat sitä vasten.
Varastopalvelu tarvitsee hintavastauksesta kolme kenttää:

```{.json tiedosto="esimerkit/sopimukset/hinta-v1.schema.json"}
```

Skeema ei kiellä ylimääräisiä kenttiä. Tämä on tarkoituksellista:
tuottaja saa lisätä kenttiä rikkomatta kuluttajaa (*tolerant reader*).
Rikkovia muutoksia ovat kentän poisto, uudelleennimeäminen ja tyypin
vaihto.

Sopimus tarkistetaan tuottajan kahta versiota vasten. Versio 2 ilmoittaa
hinnan euroina kentässä `hinta`:

```{.python tiedosto="esimerkit/luku09/sopimus.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/luku09/sopimus.odotettu"}
```

Testinä sama on kaksi tarkistusta: nykyinen tuottaja täyttää sopimuksen
kaikilla tunnetuilla tuotteilla, ja rikkova muutos havaitaan.

```{.python tiedosto="esimerkit/testit/test_sopimus.py" osa="sopimustesti"}
```

Oikeassa järjestelyssä ensimmäinen testi ajetaan *tuottajan*
CI:ssä oikeaa hintapalvelua vasten, ja sopimustiedosto haetaan
kuluttajan repositoriosta tai yhteisestä paikasta. Tässä molemmat ovat
samassa repositoriossa, jotta esimerkki on ajettavissa.

## Sopimus ja väärennös

Sopimus sitoo myös väärennöksen. Kun kuluttajan integraatiotestit
käyttävät hintapalvelun väärennöstä, väärennöksen vastausten on
täytettävä sama sopimus. Muuten kuluttaja testaa itseään palvelua
vasten, jota ei ole olemassa. Testi `test_tuottaja_tayttaa_sopimuksen`
ajetaan tässä väärennöstä vasten, ja tuottajan CI:ssä sama testi ajetaan
oikeaa palvelua vasten: näin väärennös ja oikea palvelu pysyvät samana
sopimuksen kattamilta osin.

## Rajapinnan kehittäminen

Sopimukset tekevät rajapinnan muutoksista näkyviä, mutta eivät poista
tarvetta muuttaa rajapintoja hallitusti:

| Muutos | Rikkova? | Tapa |
|-------------------------|---------|---------------------------------|
| uusi valinnainen kenttä | ei | lisää suoraan |
| uusi pakollinen pyynnön kenttä | kyllä | oletusarvo tai uusi versio |
| kentän uudelleennimeäminen | kyllä | lisää uusi, poista vanha, kun kuluttajat ovat siirtyneet |
| tyypin muutos (snt → euroa) | kyllä | uusi kenttä tai versio |
| virhekoodin muutos | usein | sopimukseen myös virhetilanteet |

Taito *Palveluarkkitehtuurit* käsittelee rajapintojen versiointia ja
viestien kehittämistä laajemmin; sopimustesti on työkalu, joka kertoo,
milloin versiointia tarvitaan.

## Käytännössä

- Kirjoita sopimukseen vain se, mitä kuluttaja käyttää. Liian tarkka
  sopimus estää tuottajaa kehittämästä rajapintaa.
- Aja sopimustesti tuottajan CI:ssä jokaisessa muutoksessa. Kuluttajan
  CI:ssä ajettuna se löytää vian vasta, kun tuottaja on jo julkaissut.
- Tarkista väärennöksen vastaukset samaa sopimusta vasten.
- Ota sopimukseen mukaan myös virhevastaukset, joita kuluttaja käsittelee
  (404, 503), eikä vain onnistunutta tapausta.

## Itsearviointi

- Osaat selittää kuluttajavetoisen sopimustestauksen kulun ja sen,
  miksi se korvaa osan päästä päähän -testeistä.
- Osaat kirjoittaa vastauksen sopimuksen JSON Schemana ja tarkistaa
  palvelun vastaukset sitä vasten.
- Osaat erottaa rikkovan ja rikkomattoman rajapinnan muutoksen.
- Osaat kertoa, miten sopimus sitoo myös kuluttajan käyttämän
  väärennöksen.
