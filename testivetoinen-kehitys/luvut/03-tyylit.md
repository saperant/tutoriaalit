# TDD suunnittelun välineenä

Edellisen luvun kori ei tarvinnut mitään itsensä ulkopuolelta. Oikea
koodi tarvitsee: kassa käyttää varastoa ja maksupalvelua. Silloin on
päätettävä, mistä työ aloitetaan ja mitä testissä käytetään
yhteistyökumppaneiden paikalla. Vastauksia on kaksi koulukuntaa, ja
niiden ero näkyy vasta, kun koodia muutetaan.

## Sisältä ulos ja ulkoa sisään

**Sisältä ulos** (klassinen eli Chicagon koulukunta) aloittaa
riippumattomista osista: ensin hinnoittelu ja varasto, sitten kassa,
joka käyttää niitä. Testeissä käytetään oikeita olioita aina kun ne
ovat nopeita, ja testi tarkistaa **lopputilan**: paljonko varastossa on,
mitä kuitissa lukee.

**Ulkoa sisään** (mockistinen eli Lontoon koulukunta) aloittaa
käyttötapauksesta: ensin kassan testi, jossa varastoa ja maksupalvelua
ei vielä ole. Niiden paikalla on mock-olioita, ja testi tarkistaa
**vuorovaikutuksen**: mitä kassa pyysi keneltäkin. Yhteistyökumppanien
rajapinnat syntyvät sen mukaan, mitä kassa niiltä tarvitsee.

Esimerkin kassa varaa ostokset varastosta ja veloittaa summan. Jos maksu
epäonnistuu, varaukset vapautetaan:

```{.python tiedosto="esimerkit/03-tyylit/1-alku/kassa.py" osa="kassa"}
```

Klassinen testi tarvitsee toimivan varaston ja maksupalvelun. Oikeat ovat
tietokannan ja verkon takana, joten niiden tilalle kirjoitetaan
väärennökset, joissa on oikea logiikka mutta tila on muistissa:

```{.python tiedosto="esimerkit/03-tyylit/1-alku/muisti.py" osa="varasto"}
```

Testi ajaa oston ja katsoo, mihin tilaan maailma päätyi:

```{.python tiedosto="esimerkit/03-tyylit/1-alku/test_tila.py" osa="tila"}
```

Mockistinen testi ei tarvitse väärennöksiä. `Mock(spec=Varasto)` luo
olion, joka hyväksyy rajapinnan metodikutsut ja muistaa ne:

```{.python tiedosto="esimerkit/03-tyylit/1-alku/test_vuorovaikutus.py" osa="vuorovaikutus"}
```

Molemmat testisarjat menevät läpi:

```{.tuloste tiedosto="esimerkit/03-tyylit/1-alku/odotettu"}
```

## Ero näkyy muutoksessa

Varastoon lisätään metodi `varaa_kaikki`, joka varaa koko ostoksen
kerralla tai ei mitään. Se korjaa todellisen puutteen: aiemmin toisen
tuotteen loppuminen jätti ensimmäisen varatuksi.

```{.python tiedosto="esimerkit/03-tyylit/2-refaktoroitu/muisti.py" osa="kaikki"}
```

Kassa käyttää uutta metodia. Sen käytös ulospäin ei muutu: onnistunut
osto vähentää saldoa ja epäonnistunut maksu palauttaa tuotteet.

```{.python tiedosto="esimerkit/03-tyylit/2-refaktoroitu/kassa.py" osa="osta"}
```

Testeihin ei kosketa. Tulos:

```{.tuloste tiedosto="esimerkit/03-tyylit/2-refaktoroitu/odotettu"}
```

Tilaa tarkistavat testit menevät läpi, koska lopputila on sama.
Vuorovaikutusta tarkistavat testit hajoavat, vaikka koodi toimii: ne
väittivät, että kassa kutsuu metodia `varaa` kerran tuotetta kohden, ja
se oli toteutuksen yksityiskohta eikä vaatimus.

Tämä on mockien tunnetuin hinta. Testi, joka kuvaa *miten* koodi tekee
työnsä, hajoaa aina kun tapa muuttuu, ja silloin se jarruttaa
refaktorointia sen sijaan, että suojaisi sitä.

## Kumpaa käyttää

Kumpikin tyyli on työkalu, ja useimmat tiimit käyttävät molempia.

| Kysymys | Tilan tarkistus | Vuorovaikutuksen tarkistus |
|------------------------|---------------------------|---------------------------|
| Mitä testi väittää | lopputuloksen | kutsut ja niiden argumentit |
| Kestää refaktoroinnin | hyvin | huonosti |
| Virheen paikantaminen | vika voi olla kumppanissa | osoittaa testattavaan luokkaan |
| Vaatii | toimivat kumppanit tai väärennökset | vain rajapinnan |
| Sopii, kun | kumppani on nopea ja deterministinen | kutsu itse on vaatimus |

Vuorovaikutuksen tarkistus on oikea valinta, kun kutsu *on* se, mitä
vaaditaan: sähköposti lähtee tasan kerran, maksua ei veloiteta kahdesti,
lokiin kirjataan epäonnistunut kirjautuminen. Näillä ei ole lopputilaa,
jonka voisi kysyä jälkikäteen.

Kolmas vaihtoehto on usein paras: väärennös, joka kerää tapahtumat
tilaksi. Luvun `MuistiMaksut` muistaa veloitetun summan, joten testi voi
tarkistaa sen ilman mockia.

Väärennöksessä on oma riskinsä: se voi käyttäytyä eri tavalla kuin
oikea toteutus. Siksi sama testisarja kannattaa ajaa myös oikeaa
varastoa vasten (taito *Integraatiotestaus ja Testcontainers*).

## Milloin TDD kannattaa

TDD toimii parhaiten, kun tiedät, mitä koodin pitää tehdä, mutta et
vielä, miten:

- laskentasäännöt, jäsentimet, tilakoneet ja muu logiikka, jolla on
  selvä syöte ja tulos
- virheen korjaus: kirjoita ensin testi, joka toistaa virheen
- rajapinnan suunnittelu, kun käyttäjän näkökulma on tärkeä.

TDD sopii huonosti tai ei lainkaan seuraaviin:

- **Tutkiva koodi.** Kun et tiedä, mitä rakennat (prototyyppi,
  kirjastokokeilu, data-analyysi), testit lukitsevat rajapinnan, joka
  heitetään kuitenkin pois. Kokeile ensin, heitä kokeilu pois ja
  kirjoita sitten toteutus testien kanssa.
- **Ulkoasu ja käyttökokemus.** Testi ei kerro, onko sivu selkeä.
  Logiikka kannattaa erottaa näkymästä ja testata erikseen (luku 9).
- **Ohut liima.** Koodi, joka vain välittää kutsun kirjastolle, saa
  enemmän turvaa integraatiotestistä kuin yksikkötestistä.
- **Algoritmi, jonka keksiminen on varsinainen ongelma.** Testit eivät
  johda lajittelualgoritmiin tai jäsentimen arkkitehtuuriin pienin
  askelin; ne kertovat, milloin olet valmis.

## Mitä tutkimus sanoo

TDD:n hyödyistä on tutkimusta kahden vuosikymmenen ajalta, ja tulokset
ovat varovaisempia kuin menetelmän puolestapuhujat tai arvostelijat
antavat ymmärtää.

- Nagappan ym. (2008) vertasivat neljää teollista tiimiä IBM:llä ja
  Microsoftilla vastaaviin tiimeihin ilman TDD:tä. Julkaisua edeltävä
  vikatiheys oli 40–90 % pienempi, ja kehitysaika kasvoi tiimien
  arvion mukaan 15–35 %. Tutkimus on tapaustutkimus, ei kontrolloitu
  koe.
- Rafiquen ja Mišićin meta-analyysi (2013) 27 tutkimuksesta löysi
  pienen myönteisen vaikutuksen laatuun eikä selvää vaikutusta
  tuottavuuteen. Teollisissa tutkimuksissa laatuhyöty oli suurempi ja
  tuottavuuden lasku selvempi kuin opiskelijakokeissa.
- Fucci ym. (2017) erittelivät, mikä TDD:ssä vaikuttaa. Heidän
  aineistossaan ratkaisevaa oli työskentely pienin, tasaisin askelin;
  sillä, kirjoitettiinko testi ennen koodia vai heti sen jälkeen, oli
  vähemmän merkitystä.

Varma johtopäätös on vaatimaton: lyhyt palautesilmukka ja testit, jotka
kirjoitetaan koodin kanssa samaan aikaan, parantavat laatua. Järjestys
"testi ensin" on keino pitää silmukka lyhyenä ja varmistaa, että testi
todella syntyy.

## Käytännössä

- **Korvaa vain se, mikä on pakko.** Verkko, kello, satunnaisuus,
  tiedostojärjestelmä ja hitaat palvelut korvataan. Omat nopeat luokat
  käytetään sellaisinaan.
- **Suosi väärennöstä mockin sijaan,** kun samaa kumppania tarvitaan
  monessa testissä. Väärennös kirjoitetaan kerran, ja se kestää
  refaktoroinnin.
- **`Mock(spec=...)` aina.** Ilman `spec`-argumenttia mock hyväksyy
  minkä tahansa metodin, myös kirjoitusvirheen, ja testi menee läpi
  vaikka kutsuttua metodia ei olisi olemassa.
- **Älä mockaa sitä, mitä et omista.** Kolmannen osapuolen kirjaston
  mock kuvaa oletuksesi kirjastosta, ei kirjastoa. Kääri kirjasto omaan
  rajapintaan ja testaa kääre oikeaa kirjastoa vasten.
- **Vian korjaus alkaa testistä.** Testi, joka toistaa virheen, todistaa
  korjauksen ja estää virheen paluun.
- **Jos testi on vaikea kirjoittaa, vika on yleensä suunnittelussa.**
  Pitkä alustus tai monta mockia kertoo, että luokka tekee liikaa tai
  tietää liikaa naapureistaan.

## Itsearviointi

- Osaat kirjoittaa samasta käytöksestä sekä tilaa että vuorovaikutusta
  tarkistavan testin ja kertoa, kumpi kestää refaktoroinnin.
- Osaat valita yhteistyökumppanin tilalle oikean olion, väärennöksen
  tai mockin ja perustella valinnan.
- Osaat nimetä tilanteita, joissa TDD ei kannata, ja kertoa, mitä
  niissä tehdään sen sijaan.
- Osaat kuvata, mitä tutkimus TDD:n vaikutuksista sanoo ja mitä se ei
  sano.
