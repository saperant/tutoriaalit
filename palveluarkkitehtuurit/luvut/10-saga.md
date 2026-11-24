# Saga ja outbox

Monoliitissa tilaus, varaus ja veloitus tallentuvat yhdessä
transaktiossa tai eivät ollenkaan (luku 3). Kun ne ovat eri palveluissa
ja eri tietokannoissa, yhteistä transaktiota ei ole, eikä kahden vaiheen
vahvistus ole käyttökelpoinen (luku 7). *Saga* korvaa sen sarjalla
paikallisia transaktioita: jokainen palvelu tekee oman osansa ja
julkaisee tuloksen, ja jos jokin vaihe epäonnistuu, jo tehdyt vaiheet
perutaan *kompensoivilla* toiminnoilla.

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

```text
 myynti            varasto           maksut       toimitus, laskutus
   │ VARAA ──────────►│                 │                │
   │◄────────── VARATTU                 │                │
   │ VELOITA ───────────────────────────►│                │
   │◄──────────────────────────── MAKSETTU                │
   │ TilausVahvistettu (aihe) ───────────────────────────►│
   │                  │                 │                │
   │      kompensaatio, jos maksu hylätään:              │
   │◄─────────────────────────── MAKSU_HYLATTY            │
   │ VAPAUTA ────────►│                 │                │
   │◄──────── VAPAUTETTU                │                │
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

- Osaat selittää, miksi palvelujen välillä ei käytetä yhteistä
  transaktiota ja miten saga korvaa sen.
- Osaat verrata orkestrointia ja koreografiaa ja valita niistä.
- Osaat toteuttaa orkestroidun sagan tilakoneena, joka kestää toistot
  ja myöhästyneet viestit.
- Osaat järjestää sagan vaiheet kompensoitaviin, käännekohtaan ja
  uudelleenyritettäviin ja suunnitella kompensaatiot.
- Osaat toteuttaa outboxin ja välittäjän ja selittää muutostietojen
  kaappauksen vaihtoehtona.
