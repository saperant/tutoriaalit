# Verkko ja offline first

Mobiiliyhteys katkeaa hississä, junassa ja kellarikaupassa. Sovellus,
joka näyttää latausilmaisinta aina verkon puuttuessa, on käyttäjälle
rikki. **Offline first** -sovellus toimii ensin paikallisen datan
varassa ja synkronoi verkon kanssa, kun yhteys on.

## HTTP-asiakas

Esimerkki käyttää **Ktor**-asiakasta ja **kotlinx.serialization**-
kirjastoa. Ktorin moottori vaihdetaan: sovelluksessa OkHttp, testeissä
`MockEngine`. Retrofit (OkHttpin päälle rakennettu, rajapinta
merkinnöillä) on yhtä yleinen valinta; periaatteet ovat samat.

Palvelimen esitys on oma tyyppinsä:

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/verkko/OstosApi.kt" osa="dto"}
```

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/verkko/OstosApi.kt" osa="asiakas"}
```

- **`ignoreUnknownKeys`**: palvelin voi lisätä kenttiä rikkomatta
  vanhoja sovellusversioita. Mobiilisovelluksen vanhoja versioita on
  käytössä vuosia, joten rajapinnan on kestettävä se.
- **Aikakatkaisu** on aina asetettu. Oletuksena pyyntö voi odottaa
  kauan, ja käyttäjä näkee jumittuneen ruudun.
- **Virhevastaus on virhe.** `expectSuccess = false` ja tarkistus
  tekevät tilakoodin käsittelystä näkyvää. `VerkkoVirhe` periytyy
  `IOException`ista, joten yhteysvirhe ja palvelinvirhe käsitellään
  samoin.
- **Verkko ei pääsäikeessä.** Android kaataa sovelluksen
  (`NetworkOnMainThreadException`), jos pääsäikeessä tehdään
  verkkopyyntö. Suspend-funktiot ja Ktorin moottori hoitavat säikeet.

Rajapinnan testi antaa vastaukset `MockEngine`llä ilman verkkoa:

```{.kotlin tiedosto="esimerkit/app/src/test/java/fi/esimerkki/ostokset/verkko/OstosApiTest.kt" osa="testi"}
```

Ensimmäinen testi varmistaa, että tuntematon kenttä ei kaada
jäsennystä; toinen tarkistaa lähetetyn JSONin tarkasti.

## Offline first -repository

Repository yhdistää tietokannan ja verkon. Käyttöliittymä lukee aina
tietokantaa; verkko vain päivittää sitä.

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/data/OstosRepository.kt" osa="toteutus"}
```

1. **Kirjoitus menee ensin paikallisesti.** `lisaa` ja `merkitse`
   tallentavat tietokantaan ja merkitsevät rivin synkronoimattomaksi.
   Käyttäjä näkee muutoksen heti, verkosta riippumatta.
2. **Synkronointi lähettää muutokset ja hakee palvelimen tilan.**
   Onnistuneet merkitään synkronoiduiksi, palvelimen rivit tallennetaan
   tietokantaan, ja Flow päivittää käyttöliittymän.
3. **Virhe ei ole poikkeus vaan tulos.** `Result` kertoo kutsujalle,
   että synkronointi epäonnistui; data on silti tallessa.

`try`–`catch (e: IOException)` on tarkoituksella kapea. Yleinen
`runCatching` tai `catch (e: Exception)` sieppaisi myös
korutiinin peruutuksen (`CancellationException`), jolloin peruutettu
työ jatkuisi ja rakenteellinen rinnakkaisuus (tutoriaali *Kotlin*)
rikkoutuisi.

Testi käyttää oikeaa muistitietokantaa ja `MockEngine`ä, jonka verkon
voi katkaista:

```{.kotlin tiedosto="esimerkit/app/src/test/java/fi/esimerkki/ostokset/data/OstosRepositoryTest.kt" osa="testi"}
```

## Ristiriidat

Esimerkin synkronointi on yksinkertainen: paikalliset muutokset
lähetetään, ja palvelimen versio korvaa paikallisen. Oikeassa
sovelluksessa sama rivi voi muuttua kahdella laitteella, ja
ristiriidalle tarvitaan sääntö:

- **Viimeinen voittaa** aikaleiman tai versionumeron perusteella.
  Yksinkertainen, mutta toisen muutos katoaa.
- **Kenttäkohtainen yhdistäminen**: eri kenttien muutokset yhdistetään.
- **Operaatiot tapahtumina**: lähetetään "merkitse ostetuksi", ei koko
  riviä. Palvelin soveltaa operaatiot järjestyksessä.
- **CRDT-tietorakenteet** yhdistyvät automaattisesti, mutta ovat
  monimutkaisia.

Valinta on tuotepäätös yhtä paljon kuin tekninen päätös. Kerran
lähetetyn operaation uudelleenlähetys ei saa tehdä muutosta kahdesti,
joten pyynnöissä käytetään **idempotenssiavainta** (tutoriaali
*Taustapalvelut*).

## Käytännössä

- **Offline first.** Tietokanta on totuuden lähde, verkko
  synkronointikanava. Käyttöliittymä ei koskaan odota verkkoa
  näyttääkseen jotain.
- **DTO erillään entiteetistä ja mallista.** Kolme tyyppiä näyttää
  toistolta, mutta rajapinnan, skeeman ja käyttöliittymän muutokset
  pysyvät omilla alueillaan.
- **Kapea virheenkäsittely.** Siepataan odotetut virheet
  (`IOException`), ei peruutusta eikä ohjelmointivirheitä.
- **Rajapinta kestää vanhoja asiakkaita.** Tuntemattomat kentät
  ohitetaan, uudet kentät ovat valinnaisia, ja poistettavat kentät
  vanhennetaan hitaasti.
- **Hinnat:** radion herättäminen kuluttaa akkua enemmän kuin
  siirrettävä data. Yksi iso synkronointi on halvempi kuin monta pientä
  pyyntöä, ja synkronointi kannattaa ajoittaa WorkManagerilla (luku 9)
  eikä tehdä jokaisen muutoksen jälkeen. Mittaa myös vastausten koko:
  pakkaus (`gzip`) ja sivutus ovat mobiilissa erityisen tärkeitä.

## Itsearviointi

- Osaat tehdä HTTP-asiakkaan, joka jäsentää JSONin, sietää
  tuntemattomat kentät ja käsittelee virhevastaukset.
- Osaat testata verkkokerroksen `MockEngine`llä ilman verkkoa.
- Osaat toteuttaa offline first -repositoryn, jossa tietokanta on
  totuuden lähde ja synkronoinnin virhe ei menetä dataa.
- Osaat selittää, miksi `runCatching` on vaarallinen korutiineissa, ja
  valita ristiriitojen ratkaisustrategian.
