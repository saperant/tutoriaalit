# Saga ja outbox

Monoliitissa tilaus, varaus ja veloitus tallentuvat yhdessä
transaktiossa tai eivät ollenkaan (luku 3). Kun ne ovat eri palveluissa
ja eri tietokannoissa, yhteistä transaktiota ei ole. *Saga* korvaa sen
sarjalla paikallisia transaktioita: jokainen palvelu tekee oman osansa
ja julkaisee tuloksen, ja jos jokin vaihe epäonnistuu, jo tehdyt vaiheet
perutaan *kompensoivilla* toiminnoilla. Luku perustelee ensin, miksi
hajautettu transaktio ei kelpaa, rakentaa sitten sagan tilakoneena ja
ratkaisee lopuksi, miten tilan muutos ja viestin lähetys saadaan
tapahtumaan yhdessä.

## Miksi ei kahden vaiheen vahvistusta

Hajautettu transaktio *kahden vaiheen vahvistuksella* (*two-phase
commit*, 2PC, XA) lupaa, että usean tietokannan muutokset tallentuvat
yhdessä. Koordinaattori kysyy ensin kaikilta, voivatko ne vahvistaa
(ja nämä lukitsevat resurssinsa), ja käskee sitten vahvistamaan. Jos
koordinaattori kaatuu vaiheiden välissä, osallistujat odottavat
lukot päällä. Saatavuus on osallistujien saatavuuksien tulo, kuten
luvun 7 kutsuketjussa, ja jokaisen palvelun on luotettava toisten
lukkoihin. Siksi palvelujen välillä ei käytetä 2PC:tä, vaan saga, joka
hyväksyy hetkellisen epäjohdonmukaisuuden. Protokollan toteutus ja sen
vikatilanteet ovat taidossa *Hajautetut järjestelmät*.

## Orkestrointi ja koreografia

Sagan voi ohjata kahdella tavalla:

- **Orkestrointi**: yksi palvelu (*orkestroija*) tuntee prosessin ja
  lähettää komennot vuorollaan: varaa, veloita, vahvista tai peru.
  Prosessi on yhdessä paikassa luettavissa ja testattavissa.
- **Koreografia**: ei keskusohjausta. Jokainen palvelu reagoi muiden
  tapahtumiin: varasto kuulee "tilaus tehty" ja julkaisee "tuotteet
  varattu", jonka maksut kuulee. Palvelut ovat löyhemmin kytkettyjä,
  mutta prosessin kulku on hajallaan, ja syklit ovat helppoja tehdä
  vahingossa.

Esimerkki käyttää molempia. Tilauksen kriittinen polku (varaus,
veloitus, kompensaatio) on orkestroitu, koska sen virheet ovat kalliita
ja sen on oltava luettavissa yhdestä paikasta. Vahvistetun tilauksen
jälkeinen toimitus ja laskutus ovat koreografiaa: myynti julkaisee
tapahtuman eikä tiedä, kuka sen tilaa.

```{.dot otsikko="Tilaussagan viestit. Aika kulkee ylhäältä alas. Yhtenäiset nuolet ovat komentoja ja niiden vastauksia jonoissa, katkoviiva aiheeseen julkaistu tapahtuma. Alaosa näyttää kompensaation, kun maksu hylätään varauksen jälkeen."}
digraph {
  layout=neato; splines=false;
  node [shape=point, width=0.01, height=0.01, style=invis];
  edge [arrowsize=0.7];
  m0 [label="myynti", shape=box, style="rounded,filled", width=0, height=0.3, pos="0.00,0!"];
  mL [pos="0.00,-3.64!"];
  m0 -> mL [arrowhead=none, style=dotted];
  v0 [label="varasto", shape=box, style="rounded,filled", width=0, height=0.3, pos="1.50,0!"];
  vL [pos="1.50,-3.64!"];
  v0 -> vL [arrowhead=none, style=dotted];
  x0 [label="maksut", shape=box, style="rounded,filled", width=0, height=0.3, pos="3.00,0!"];
  xL [pos="3.00,-3.64!"];
  x0 -> xL [arrowhead=none, style=dotted];
  t0 [label="toimitus, laskutus", shape=box, style="rounded,filled", width=0, height=0.3, pos="4.50,0!"];
  tL [pos="4.50,-3.64!"];
  t0 -> tL [arrowhead=none, style=dotted];
  m1 [pos="0.00,-0.51!"]; v1_ [pos="1.50,-0.51!"];
  m1 -> v1_ [];
  t1 [shape=plain, style="", fontsize=9, label="VARAA", pos="0.75,-0.41!"];
  v2 [pos="1.50,-0.87!"]; m2_ [pos="0.00,-0.87!"];
  v2 -> m2_ [];
  t2 [shape=plain, style="", fontsize=9, label="VARATTU", pos="0.75,-0.77!"];
  m3 [pos="0.00,-1.23!"]; x3_ [pos="3.00,-1.23!"];
  m3 -> x3_ [];
  t3 [shape=plain, style="", fontsize=9, label="VELOITA", pos="0.75,-1.13!"];
  x4 [pos="3.00,-1.59!"]; m4_ [pos="0.00,-1.59!"];
  x4 -> m4_ [];
  t4 [shape=plain, style="", fontsize=9, label="MAKSETTU", pos="2.25,-1.49!"];
  m5 [pos="0.00,-1.95!"]; t5_ [pos="4.50,-1.95!"];
  m5 -> t5_ [style=dashed];
  t5 [shape=plain, style="", fontsize=9, label="TilausVahvistettu (aihe)", pos="0.75,-1.85!"];
  o6 [shape=plain, style="", fontsize=8, label="kompensaatio, jos maksu hylätään", pos="2.25,-2.31!"];
  x7 [pos="3.00,-2.67!"]; m7_ [pos="0.00,-2.67!"];
  x7 -> m7_ [];
  t7 [shape=plain, style="", fontsize=9, label="MAKSU_HYLATTY", pos="2.25,-2.57!"];
  m8 [pos="0.00,-3.03!"]; v8_ [pos="1.50,-3.03!"];
  m8 -> v8_ [];
  t8 [shape=plain, style="", fontsize=9, label="VAPAUTA", pos="0.75,-2.93!"];
  v9 [pos="1.50,-3.39!"]; m9_ [pos="0.00,-3.39!"];
  v9 -> m9_ [];
  t9 [shape=plain, style="", fontsize=9, label="VAPAUTETTU", pos="0.75,-3.29!"];
}
```

## Orkestroija tilakoneena

Tilaus alkaa paikallisella transaktiolla, joka tallentaa tilauksen ja
ensimmäisen komennon:

```{.java tiedosto="esimerkit/viestit/src/main/java/fi/tutoriaalit/palvelut/viestit/myynti/Tilaukset.java" osa="aloita"}
```

Orkestroija on tilakone. Jokainen vastaus siirtää tilausta yhden
askeleen, ja siirtymä on yksi transaktio, jossa tila muuttuu ja seuraava
komento kirjoitetaan lähteviin:

```{.java tiedosto="esimerkit/viestit/src/main/java/fi/tutoriaalit/palvelut/viestit/myynti/TilausSaga.java" osa="saga"}
```

Sama tilakone kuvana. Kaavio on tuotettu yllä olevasta
`switch`-lauseesta (`esimerkit/kaaviot/saga_tilat.py`), ja esimerkkien
testi tarkistaa, että se vastaa koodia:

```{.dot tiedosto="esimerkit/kaaviot/saga-tilat.dot" otsikko="Tilaussagan tilat. Nuolessa on vastaus, joka laukaisee siirtymän, ja sen alla viesti, jonka siirtymä kirjoittaa lähteviin. Kaksoiskehys merkitsee lopputilaa. Vastaus, jolle tilassa ei ole nuolta, ohitetaan."}
```

Tilakone tekee sagasta kestävän toistoille ja myöhästyneille viesteille:
vastaus, joka ei sovi nykyiseen tilaan, ohitetaan. `FOR UPDATE` lukitsee
tilauksen rivin siirtymän ajaksi, jotta kaksi samanaikaista vastausta ei
siirrä samaa tilausta kahdesti.

Testit kulkevat sagan kaikki polut läpi:

```{.java tiedosto="esimerkit/viestit/src/test/java/fi/tutoriaalit/palvelut/viestit/SagaTest.java" osa="onnistuu"}
```

```{.java tiedosto="esimerkit/viestit/src/test/java/fi/tutoriaalit/palvelut/viestit/SagaTest.java" osa="kompensaatio"}
```

## Kompensaatio ei ole peruutus

Kompensoiva toiminto ei pyyhi historiaa, vaan tekee uuden muutoksen,
joka kumoaa aiemman vaikutuksen: varaus vapautetaan, veloitus
hyvitetään, ja lähetetty vahvistusviesti korjataan uudella viestillä.
Sagan suunnittelussa vaiheet jaetaan kolmeen lajiin:

1. **Kompensoitavat** vaiheet, jotka voi kumota (varaus).
2. **Käännekohta** (*pivot*), jonka jälkeen saga etenee loppuun
   (veloitus onnistui).
3. **Uudelleenyritettävät** vaiheet käännekohdan jälkeen, joiden on
   lopulta onnistuttava (toimitus, laskutus).

Kompensoitavat vaiheet tehdään ensin ja vaikeasti kumottavat
viimeisinä. Siksi esimerkki varaa ennen kuin veloittaa: varauksen
vapautus on helppoa, rahan palautus ei.

## Eristyksen puute

Sagalta puuttuu tietokantatransaktion eristys. Muut näkevät
välitilat: tuotteet ovat varattuja, vaikka tilaus voi vielä peruuntua.
Tavalliset vastakeinot ovat:

- **Semanttinen lukko**: tila kertoo, että tilaus on kesken
  (`ALOITETTU`, `PERUUTETAAN`), ja käyttöliittymä ja muut toiminnot
  ottavat sen huomioon.
- **Vaihdannaiset päivitykset**: saldoa vähennetään ja lisätään
  suhteellisesti (`saldo = saldo - :maara`), jolloin järjestyksellä ei
  ole väliä.
- **Uudelleenluku**: ennen käännekohtaa tarkistetaan, ettei tieto ole
  muuttunut.

## Outbox: tila ja viesti yhdessä

Jokainen sagan siirtymä muuttaa tietokantaa ja lähettää viestin. Ne
ovat kaksi eri järjestelmää, ja jos lähetys tehdään suoraan, jompikumpi
voi jäädä tekemättä: tietokanta vahvistettiin mutta viesti katosi, tai
viesti lähti mutta transaktio peruttiin. Taustapalveluissa esitelty
*outbox* ratkaisee ongelman kirjoittamalla viestin tauluun samassa
transaktiossa:

```{.java tiedosto="esimerkit/viestit/src/main/java/fi/tutoriaalit/palvelut/viestit/myynti/Lahtevat.java" osa="lahtevat"}
```

```{.sql tiedosto="esimerkit/viestit/src/main/resources/schema.sql" osa="myynti"}
```

Erillinen *välittäjä* (*message relay*) lukee lähettämättömät rivit ja
lähettää ne:

```{.dot otsikko="Outbox. Tilan muutos ja lähtevä viesti tallentuvat samassa tietokantatransaktiossa, joten ne joko syntyvät molemmat tai eivät kumpikaan. Välittäjä siirtää rivit viestinvälittäjään erikseen ja voi toistaa lähetyksen."}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.4;
  saga [label="saga:\nsiirtymä"];
  subgraph cluster_tk {
    label="myynnin tietokanta:\nyksi transaktio"; style="rounded"; margin=10;
    tilaus [label="tilaus\n(tila)", shape=cylinder, height=0.5];
    lahtevat [label="lähtevät\n(viesti)", shape=cylinder, height=0.5];
  }
  valittaja [label="välittäjä"];
  jono [label="viestin-\nvälittäjä", shape=cylinder, height=0.5];
  saga -> tilaus [label="UPDATE"]; saga -> lahtevat [label="INSERT"];
  lahtevat -> valittaja [label="kysely"];
  valittaja -> jono [label="lähetys"];
}
```

```{.java tiedosto="esimerkit/viestit/src/main/java/fi/tutoriaalit/palvelut/viestit/myynti/Valittaja.java" osa="valittaja"}
```

Jos transaktio perutaan, viestiä ei ole koskaan olemassa:

```{.java tiedosto="esimerkit/viestit/src/test/java/fi/tutoriaalit/palvelut/viestit/ViestitTest.java" osa="outbox"}
```

Lähetys on vähintään kerran, joten vastaanottajat ovat idempotentteja
(luku 8). Tauluun kertyvät lähetetyt rivit poistetaan ajoittain.
Kyselyyn perustuvan välittäjän sijaan voidaan käyttää *muutostietojen
kaappausta* (*change data capture*, CDC): esimerkiksi Debezium lukee
tietokannan transaktiolokia ja julkaisee outbox-taulun rivit Kafkaan
ilman kyselyjä ja viivettä.

## Käytännössä

- **Orkestroi kriittinen polku, koreografioi reaktiot.** Rahan ja
  varaston liikkeet yhdessä luettavassa tilakoneessa; ilmoitukset muille
  tapahtumina.
- **Tilakone ohittaa odottamattomat viestit.** Toisto ja myöhästyminen
  ovat normaaleja, joten jokaisen siirtymän on oltava idempotentti.
- **Järjestä vaiheet:** kompensoitavat ensin, käännekohta, sitten
  uudelleenyritettävät. Kompensaatio on liiketoimintatoiminto, ja sen
  sisältö sovitaan liiketoiminnan kanssa.
- **Outbox jokaiseen palveluun, joka muuttaa tilaa ja lähettää
  viestin.** Suora lähetys transaktion sisältä tai jälkeen on
  vikaherkkä.
- **Hinnat:** saga on monta kertaa monimutkaisempi kuin yksi transaktio:
  välitilat näkyvät, kompensaatiot on suunniteltava ja testattava, ja
  vianetsintä vaatii jäljityksen. Siksi rajat kannattaa vetää niin, että
  sagoja tarvitaan vähän (luku 4).

## Itsearviointi

- Osaat selittää, miksi palvelujen välillä ei käytetä kahden vaiheen
  vahvistusta ja miten saga korvaa yhteisen transaktion.
- Osaat verrata orkestrointia ja koreografiaa ja valita niistä.
- Osaat toteuttaa orkestroidun sagan tilakoneena, joka kestää toistot
  ja myöhästyneet viestit.
- Osaat järjestää sagan vaiheet kompensoitaviin, käännekohtaan ja
  uudelleenyritettäviin ja suunnitella kompensaatiot.
- Osaat toteuttaa outboxin ja välittäjän ja selittää muutostietojen
  kaappauksen vaihtoehtona.
