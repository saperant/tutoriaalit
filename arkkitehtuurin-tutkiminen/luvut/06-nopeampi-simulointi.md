# Intervallimalli ja näytteistys

Yksityiskohtainen suoritinsimulaattori on hidas: gem5:n
epäjärjestyssuoritusmalli simuloi suuruusluokkaa satojatuhansia käskyjä
sekunnissa, ja yksi SPEC-kuorma on biljoonia käskyjä. Täysi ajo
kestäisi viikkoja. Tähän on kaksi vastausta, jotka tämä luku esittelee:

- **Abstraktimpi malli.** Intervallimalli ei simuloi jaksoja vaan
  laskee suoritusajan tapahtumista, jotka katkaisevat käskyvirran:
  välimuistihudeista ja väärin ennustetuista haaroista.
- **Vähemmän simuloitavaa.** Näytteistys simuloi yksityiskohtaisesti vain
  edustavat osat ajosta ja yleistää ne koko ajoon.

Kumpaakin verrataan yksityiskohtaiseen malliin, joka toimii viitteenä.

## Yksityiskohtainen ydinmalli

Viitemalli on epäjärjestyksessä suorittava ydin, jolla on uudelleenjärjestyspuskuri
(ROB) $W$ käskylle ja leveys $D = 4$ käskyä jaksossa. Käsky tulee
ikkunaan järjestyksessä, kun ikkunassa on tilaa, alkaa, kun sen operandi
on valmis, ja poistuu järjestyksessä. Väärin ennustettu haara
pysäyttää käskyjen haun, kunnes haara on ratkaistu ja liukuhihna
täytetty uudelleen (8 jaksoa).

Ohjelma on synteettinen, ja sen vaiheet toistuvat satunnaisessa
järjestyksessä: laskentaa pienellä taulukolla ja vaikeasti
ennustettavilla haaroilla, virtaavaa muistiliikennettä, jossa hudit ovat
toisistaan riippumattomia, ja osoitinjahtia, jossa jokainen lataus
riippuu edellisestä. Jokaisella vaiheella on kaksi peruslohkoa, ja
latausten osumat ja hudit ratkaisee 8 KiB:n 4-tie-LRU-välimuisti.
Ohjelman käskyt ovat tällaisia:

```{.cpp tiedosto="esimerkit/06-ydin/main.cpp" osa="kasky"}
```

Koska suoritusyksiköitä on rajattomasti, jokaisen käskyn ajoitus seuraa
suoraan säännöistä: ikkunaan tulo, operandin valmistuminen, viive ja
järjestyksessä poistuminen. Säännöt voi laskea käsky kerrallaan ilman
jaksoittaista silmukkaa, ja tulos on sama. Tätä tekniikkaa käyttävät
myös oikeat nopeat simulaattorit aina, kun mallin rakenne sallii.

```{.cpp tiedosto="esimerkit/06-ydin/main.cpp" osa="ajoitus"}
```

```{.cpp tiedosto="esimerkit/06-ydin/main.cpp" osa="tulokset"}
```

```{.tuloste tiedosto="esimerkit/06-ydin/odotettu"}
```

Ihanteellinen CPI on ajo ilman hutia ja väärää ennustusta. Leveyden 4
raja on 0,25, ja pienimmällä ikkunalla riippuvuusketjut nostavat sen
0,30:een. Hudit ja haarat nostavat CPI:n 1,8–4,3:een, ja ikkunan koko
vaikuttaa siihen voimakkaasti: suurempi ikkuna pitää useampia
riippumattomia huteja yhtä aikaa kesken.

## Intervallimalli

Intervallimalli (Karkhanis ja Smith 2004, Eyerman ym. 2009) kuvaa
epäjärjestyssuoritusta näin: ydin suorittaa käskyjä tasaisella
nopeudella, kunnes jokin *tapahtuma* katkaisee virran. Suoritusaika on
perusaika ja tapahtumien hintojen summa. Mallin taito on tietää, mitä
kukin tapahtuma maksaa:

- **Väärä ennustus** maksaa haun uudelleenaloituksen ja haaran
  ratkaisuajan.
- **Pitkä huti** pysäyttää poistumisen, kun ikkuna täyttyy sen takana.
  Huti, joka on enintään ikkunan päässä edeltävästä hudista, on kesken
  samaan aikaan ja limittyy sen kanssa, eli se ei maksa lisää. Tämä on
  *muistitason rinnakkaisuutta* (*memory-level parallelism*, MLP).
- **Riippuva huti** ei voi alkaa ennen kuin edellinen on valmis, joten
  se maksaa aina koko viiveen.

```{.python tiedosto="esimerkit/arkki/intervalli.py" osa="intervalli"}
```

Malli saa yksityiskohtaiselta mallilta vain käskyvirran tyypit (osuma,
huti, riippuva huti, haara, väärä haara) ja ihanteellisen CPI:n. Kolme
versiota: ilman limitystä (luvun 3 CPI-pino), limityksellä ja
limityksellä, joka tuntee riippuvuudet:

```{.python tiedosto="esimerkit/06-intervalli.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/06-intervalli.odotettu"}
```

Versioiden erot opettavat, mitä mallinnettava ilmiö merkitsee:

- **Ilman limitystä** malli on oikeassa pienellä ikkunalla, jossa hudit
  eivät mahdu limittymään. Suurilla ikkunoilla se yliarvioi ajan
  kaksin- tai kaksi ja puolikertaiseksi: CPI-pino ei näe MLP:tä.
- **Limitys ilman riippuvuuksia** heilahtaa toiseen suuntaan ja
  aliarvioi ajan suurilla ikkunoilla 37–51 %. Se olettaa, että osoitinjahdin hudit
  limittyvät, vaikka jokainen odottaa edellistä.
- **Riippuvuudet mukana** virhe on 2–9 %. Jäljelle jäävä ero tulee
  siitä, että malli ei näe ikkunan täyttymisen ja tyhjenemisen
  yksityiskohtia eikä haarojen todellista ratkaisuaikaa.

Intervallimalli on laskennallisesti kevyt: yksi läpikäynti
käskyvirrasta, ei jaksoja. Sniper-simulaattori käyttää sitä
moniydinsimulointiin, ja se on kertaluokkia nopeampi kuin syklitarkka
simulointi muutaman prosentin tarkkuudella. Hinta on se, että
käskyvirran tapahtumat (osuiko lataus, ennustettiinko haara oikein)
tarvitaan edelleen: ne tulevat funktionaalisesta simulaattorista ja
välimuisti- ja ennustinmalleista.

## Näytteistys

Toinen tapa nopeuttaa on simuloida vähemmän. Satunnaiset tai
tasavälein otetut näytteet toimivat, jos ohjelma on tasainen, mutta
vaiheittaisessa ohjelmassa ne voivat osua epätasaisesti vaiheisiin.
*SimPoint* (Sherwood ym. 2002) valitsee näytteet ohjelman rakenteen
perusteella:

1. Ajo jaetaan intervalleihin (tässä 1000 käskyä, oikeissa kuormissa
   10–100 miljoonaa).
2. Jokaiselle intervallille lasketaan *peruslohkovektori*: kuinka monta
   käskyä kustakin peruslohkosta suoritettiin. Vektori kertoo, mitä
   koodia intervalli ajoi, ja se saadaan nopealla funktionaalisella
   simulaatiolla.
3. Vektorit ryhmitellään k-means-algoritmilla. Samankaltaista koodia
   ajavat intervallit kuuluvat samaan vaiheeseen.
4. Kustakin ryhmästä simuloidaan yksityiskohtaisesti vain keskusta
   lähin intervalli, ja sen tulos painotetaan ryhmän koolla.

```{.python tiedosto="esimerkit/arkki/intervalli.py" osa="kmeans"}
```

```{.python tiedosto="esimerkit/arkki/intervalli.py" osa="simpoint"}
```

Ydinmalli kirjoittaa jokaisen intervallin jaksot ja peruslohkovektorin.
Arviota verrataan koko ajon CPI:hin ja kahteen yksinkertaiseen
näytteistykseen:

```{.python tiedosto="esimerkit/06-simpoint.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/06-simpoint.odotettu"}
```

Ajon alku on huono näyte: siinä sattui olemaan virtaavaa vaihetta, jonka
hudit limittyvät, ja arvio on 37 % liian pieni. Tasavälinen näytteistys ei ole paljon
parempi, koska vaiheet ovat eri pituisia ja viisi näytettä osuu niihin
sattumanvaraisesti. SimPoint kolmella ryhmällä, eli kolmella
simuloidulla intervallilla sadasta, osuu 4 %:n päähän, koska ohjelmassa
on kolme vaihetta ja jokainen saa painon, joka vastaa sen todellista
osuutta. Yksi ryhmä ei riitä: koko ajoa edustaa silloin yksi intervalli, joka on
lähimpänä kaikkien keskiarvoa.

Näytteistyksellä on omat sudenkuoppansa. Intervallin mikroarkkitehtuurinen
tila (välimuistien ja ennustimien sisältö) on lämmitettävä ennen
mittausta, tai tulos on liian huono. Ryhmien määrä valitaan
tyypillisesti BIC-kriteerillä tai kasvattamalla, kunnes arvio vakiintuu.
SMARTS (Wunderlich ym. 2003) käyttää sen sijaan tilastollista otantaa
lyhyistä intervalleista ja antaa luottamusvälin.

## Käytännössä

- **Valitse abstraktio sen mukaan, mitä ilmiötä tutkit.** Intervallimalli
  riittää, kun kysymys on välimuistin tai ennustimen vaikutus
  suoritusaikaan. Kun kysymys on liukuhihnan yksityiskohdista, tarvitaan
  syklitarkka malli.
- **Validoi abstrakti malli yksityiskohtaista vastaan** useilla
  parametriarvoilla, ei vain yhdellä. Tässä riippumattomuusoletuksen
  virhe näkyi vasta suurilla ikkunoilla.
- **Näytteistä rakenteen mukaan.** Ajon alku on lähes aina huono näyte:
  se on alustusta. Tasavälinen otanta toimii vain tasaiselle
  ohjelmalle.
- **Lämmitä tila.** Näytteen välimuisti- ja ennustintila on tuotava
  oikeaksi ennen mittausta joko funktionaalisella esiajolla tai
  tallennetulla tilalla (*checkpoint*).

## Itsearviointi

- Osaat selittää intervallimallin periaatteen ja kertoa, mitä väärä
  ennustus, riippumaton huti ja riippuva huti maksavat.
- Osaat selittää muistitason rinnakkaisuuden ja sen, miksi CPI-pino
  yliarvioi suoritusajan suurella ikkunalla.
- Osaat valita edustavat intervallit peruslohkovektoreiden ja
  k-meansin avulla ja laskea painotetun arvion.
- Osaat kertoa, miksi ajon alku ja tasavälinen otanta ovat
  vaiheittaisessa ohjelmassa huonoja näytteitä.
