# Determinismi

Simulaatio on *deterministinen*, jos sama alkutila ja samat syötteet
tuottavat joka kerta saman lopputilan, bitilleen. Ominaisuus kuulostaa
itsestään selvältä, koska tietokone tekee, mitä käsketään. Silti se
menetetään helposti, ja moni pelin ominaisuus nojaa siihen:

- **Toistot.** Uusinta tallennetaan pelaajan syötteinä, ja peli
  simuloidaan uudelleen. Tallenne on pieni, mutta yksikin poikkeava
  bitti kasvaa lopulta eri lopputulokseksi.
- **Moninpeli.** Monet verkkomallit lähettävät vain syötteet tai
  ennustavat paikallisesti ja korjaavat palvelimen tilan mukaan
  (taito *Reaaliaikaiset moninpelit*). Molemmat vaativat, että sama
  askel antaa saman tuloksen.
- **Virheiden etsintä.** Virhe, joka toistuu samalla syötteellä, on
  löydettävissä. Fysiikkavirhe, joka ilmenee joka kymmenennellä
  kerralla, ei juuri ole.

Fysiikkasimulaatio on tässä erityisen herkkä. Pino laatikoita on
kaoottinen järjestelmä: viimeisen bitin ero kosketuspisteessä muuttaa
impulssia, impulssi muuttaa seuraavaa kosketusta, ja muutaman sekunnin
kuluttua pallo on eri paikassa.

## Tilan tiiviste

Bitintarkka vertailu tehdään *tiivisteellä*: kappaleiden tilan tavut
syötetään tiivistefunktioon, ja kahta ajoa verrataan yhdellä luvulla.
Liukulukuja ei verrata toleranssilla, koska kysymys ei ole "onko
tulos lähellä" vaan "onko tulos sama".

```{.cpp tiedosto="esimerkit/13-determinismi.cpp" osa="tiiviste"}
```

Koekohtaus on kuuden laatikon pino, johon pallo osuu:

```{.cpp tiedosto="esimerkit/13-determinismi.cpp" osa="kohtaus"}
```

```{.cpp tiedosto="esimerkit/13-determinismi.cpp" osa="toisto"}
```

```{.tuloste tiedosto="esimerkit/13-determinismi.odotettu" rivit="1-1"}
```

Kaksi ajoa samassa ohjelmassa antavat saman tiivisteen. Tämä on
vähimmäisvaatimus, ja se pätee, koska moottorissa ei ole mitään, mikä
vaihtelisi ajosta toiseen: ei kellonaikaa, ei osoittimien arvoihin
perustuvaa järjestystä, ei säikeitä eikä alustamatonta muistia.

## Tila on enemmän kuin kappaleet

Tilannevedos (*snapshot*) on kopio simulaation tilasta. Siitä jatkettu
ajo päätyy samaan tulokseen kuin keskeytymätön vain, jos vedoksessa on
*koko* tila.

```{.cpp tiedosto="esimerkit/13-determinismi.cpp" osa="vedos"}
```

```{.tuloste tiedosto="esimerkit/13-determinismi.odotettu" rivit="2-3"}
```

Toinen vedos sisältää kaikkien kappaleiden paikat ja nopeudet, mutta
ei kosketusten kertyneitä impulsseja. Jatko alkaa kylmällä
käynnistyksellä, ratkaisija päätyy hieman eri impulsseihin, ja tulos
eroaa. Ero on tässä millimetri, mutta se on ero, ja verkkopelissä se
kasvaa joka askeleella.

Vedokseen kuuluu kaikki, mistä seuraava askel riippuu: kappaleet,
lämpimän käynnistyksen impulssit, nivelten kertymät, lepolaskurit ja
satunnaislukugeneraattorin tila. Luvun 12 pisara-allas pitää siksi
oman generaattorinsa tilassaan eikä käytä ohjelman yhteistä.

## Järjestys

```{.cpp tiedosto="esimerkit/13-determinismi.cpp" osa="jarjestys"}
```

```{.tuloste tiedosto="esimerkit/13-determinismi.odotettu" rivit="4-4"}
```

Kohtaus on fysikaalisesti sama, mutta laatikot on lisätty maailmaan
käänteisessä järjestyksessä. Peräkkäisten impulssien menetelmässä
rajoitteiden järjestys vaikuttaa tulokseen (luku 7), joten pallo päätyy
kolmenkymmenen sentin päähän vertailuajosta.

Kumpikaan tulos ei ole väärä. Determinismi ei tarkoita, että tulos
olisi tarkka, vaan että se on toistettava. Siksi järjestyksen on
oltava osa määrittelyä:

- Laaja vaihe palauttaa parit aina samassa järjestyksessä. Luvun 9
  toteutus lajittelee ne ja ratkaisee tasatilanteet indeksillä.
- Säiliön läpikäynti ei saa riippua muistiosoitteista. Osoittimilla
  avainnettu hajautustaulu käy alkionsa läpi eri järjestyksessä eri
  ajoilla.
- Kappaleen lisääminen ja poistaminen tapahtuu samassa kohdassa
  askelta kaikilla koneilla.
- Rinnakkainen ratkaisija jakaa työn tavalla, joka ei riipu säikeiden
  määrästä eikä ajoituksesta. Saaret voi ratkaista rinnakkain, koska
  ne eivät vaikuta toisiinsa, kunhan tulokset kootaan kiinteässä
  järjestyksessä.

## Kiinteä askel

```{.cpp tiedosto="esimerkit/13-determinismi.cpp" osa="askel"}
```

```{.tuloste tiedosto="esimerkit/13-determinismi.odotettu" rivit="5-7"}
```

Sama viisi sekuntia eri askelpituudella antaa eri lopputuloksen, eikä
ero pienene askelta lyhentämällä. Jos askel seuraa ruudunpäivitystä,
jokainen kone simuloi eri pelin. Kiinteä askel ja kerryttäjä (taito
*Peliohjelmointi*) ovat siksi determinismin ensimmäinen ehto: fysiikka
etenee aina saman mittaisin askelin, ja renderöinti interpoloi
kahden viimeisen tilan välillä.

## Liukuluvut

Viimeinen ja hankalin kerros on laskutoimitusten itsensä
toistettavuus. IEEE 754 -standardi määrää yhteen-, vähennys-, kerto- ja
jakolaskun sekä neliöjuuren tuloksen bitilleen. Moottorin
simulaatiopolku käyttää vain näitä, joten periaatteessa tulos on sama
kaikkialla. Käytännössä kääntäjä saa muuttaa laskua kolmella tavalla:

- **Yhdistetty kerto- ja yhteenlasku.** Lausekkeen `a * b + c` voi
  laskea yhdellä FMA-käskyllä, joka pyöristää vain kerran. Tulos on
  tarkempi mutta eri kuin kahdella käskyllä. Se, yhdistääkö kääntäjä,
  riippuu kääntäjästä, optimointitasosta ja kohdesuorittimesta.
- **Laskujärjestyksen muuttaminen.** Valitsimet kuten `-ffast-math`
  antavat kääntäjälle luvan järjestää lausekkeet uudelleen.
  Liukulukujen yhteenlasku ei ole liitännäinen, joten tulos muuttuu.
- **Kirjastofunktiot.** Sinin, kosinin ja eksponenttifunktion
  tarkkuutta standardi ei määrää, ja toteutukset eroavat
  viimeisessä bitissä.

Tämän paketin koodi kieltää ensimmäisen otsakkeessa, jonka kaikki
muut sisällyttävät:

```{.cpp tiedosto="esimerkit/yhteinen/liukuluvut.hpp" osa="fma"}
```

Vaikutuksen voi mitata. Esimerkki tulostaa tiivisteen, kun sille
annetaan argumentti `tiiviste`, ja komento `make tiivisteet` kääntää
sen molemmilla kääntäjillä kiellon kanssa ja ilman. Tulos tämän
tutoriaalin rakennuskoneella (x86-64):

| Käännös | GCC 14 | Clang 20 |
|---------|--------|----------|
| kielto päällä, `-O0` | `58bc7770d4c971d4` | `58bc7770d4c971d4` |
| kielto päällä, `-O2 -mfma` | `58bc7770d4c971d4` | `58bc7770d4c971d4` |
| FMA sallittu, `-O2 -mfma` | `252bdcf2228ffcc6` | `708ffc7f4e7469a5` |

: Vertailuajon tiiviste 300 askeleen jälkeen.

Kiellon kanssa kääntäjä ja optimointitaso eivät vaikuta tulokseen.
Ilman kieltoa kääntäjät yhdistävät eri kohdat, ja jokainen käännös on
oma simulaationsa. Toista suoritinarkkitehtuuria tässä ei ole
mitattu: ARM-käännöksen pitäisi samoilla perusteilla antaa sama
tiiviste, mutta väite on todennettava ajamalla, ei päättelemällä.

Kirjastofunktioita simulaatiopolulla ei ole. Kohtausten rakentaminen
käyttää siniä ja kosinia kiertojen luomiseen, joten alkutila kannattaa
tallentaa lukuina eikä laskea uudelleen joka koneella.

## Käytännössä

- **Päätä, missä laajuudessa determinismiä tarvitaan.** Sama ohjelma
  samalla koneella on helppo, eri suorittimet vaativat kurinalaisuutta
  ja eri kääntäjät lisäksi jatkuvaa testausta.
- **Testaa tiivisteellä jatkuvassa integraatiossa.** Tallennettu
  syötesarja ajetaan joka alustalla, ja tiivisteitä verrataan.
  Ensimmäinen eroava askel paljastaa virheen heti, kun se syntyy.
- **Kiinteän pilkun luvut ovat vaihtoehto.** Kokonaislukulaskenta on
  sama kaikkialla. Osa strategia- ja taistelupeleistä tekee koko
  simulaation niillä, ja hinta on kapeampi lukualue ja työläämpi
  matematiikka.
- **Erota pelitila koristeesta.** Hiukkaset, kangas ja äänet voivat
  olla epädeterministisiä, jos ne eivät vaikuta pelin kulkuun. Näin
  ne voi myös laskea näytönohjaimella.
- **Moottorit lupaavat eri asioita.** Osa lupaa saman tuloksen eri
  alustoilla tietyin käännösasetuksin, osa vain samalla koneella ja
  käännöksellä. Lupaus luetaan ennen verkkomallin valintaa.
- **Tilaa korjaava verkkomalli sietää eroja.** Jos palvelin lähettää
  säännöllisesti oikean tilan, pienet erot korjautuvat, eikä
  bitintarkkuutta tarvita. Vaatimus riippuu siis verkkomallista
  (taito *Reaaliaikaiset moninpelit*).

## Itsearviointi

- Osaat selittää, mitä determinismi tarkoittaa ja miksi se on eri
  asia kuin tarkkuus.
- Osaat luetella, mitä simulaation tilannevedokseen kuuluu
  kappaleiden paikkojen ja nopeuksien lisäksi.
- Osaat nimetä, mistä käsittelyjärjestyksen vaihtelu voi tulla, ja
  perustella, miksi fysiikka-askeleen on oltava kiinteä.
- Osaat kertoa, miten FMA ja `-ffast-math` rikkovat toistettavuuden.
- Osaat rakentaa testin, joka toteaa kahden ajon olevan bitilleen
  samat.
