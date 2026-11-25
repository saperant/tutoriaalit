# Tallennus: Room ja DataStore

Androidissa on kolme tavallista tapaa tallentaa tietoa pysyvästi:

| Tarve | Väline |
|-------|--------|
| rakenteinen data, kyselyt, suhteet | **Room** (SQLite) |
| pienet asetukset ja liput | **DataStore** (Preferences tai Proto) |
| tiedostot, kuvat, välimuisti | `filesDir`, `cacheDir`, MediaStore |

Kaikki tallennus on I/O:ta, joka ei saa tapahtua pääsäikeessä. Room ja
DataStore tarjoavat siksi suspend-funktiot ja Flow't, ja ne vaihtavat
säiettä itse. SQL:n perusteet ovat taidossa *SQL ja
relaatiotietokannat*.

## Room: entiteetti, DAO ja tietokanta

Room on SQLiten päälle rakennettu kirjasto, joka tarkistaa SQL-kyselyt
käännösaikana ja generoi niiden toteutuksen (KSP-koodigeneraattori,
luku 1). Taulu kuvataan entiteettinä:

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/data/Tietokanta.kt" osa="entiteetti"}
```

Entiteetti on erillinen tyyppi sovelluksen mallista (`Tuote`, luku 4).
Taulussa on synkronointiin liittyvä sarake, jota käyttöliittymän ei
tarvitse tietää, ja malli voi tarkistaa sääntöjä, joita tietokanta ei
tunne. Muunnosfunktio `malliksi` on ainoa paikka, jossa kerrokset
kohtaavat.

Kyselyt kirjoitetaan **DAO**-rajapintaan (*data access object*):

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/data/Tietokanta.kt" osa="dao"}
```

- **`Flow`-paluuarvo** tekee kyselystä havaittavan: Room lähettää uuden
  tuloksen aina, kun tauluun kirjoitetaan. Käyttöliittymä päivittyy
  ilman erillistä "lataa uudelleen" -logiikkaa.
- **`suspend`-funktiot** suoritetaan Roomin omassa säiepoolissa.
- **`@Upsert`** lisää rivin tai päivittää olemassa olevan pääavaimen
  perusteella.
- **Kyselyn virhe on käännösvirhe.** Väärä sarakkeen nimi tai tyyppi
  pysäyttää käännöksen eikä kaada sovellusta käyttäjällä.

Tietokantaluokka kokoaa entiteetit ja DAOt:

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/data/Tietokanta.kt" osa="tietokanta"}
```

Tietokanta avataan kerran sovelluksessa (säiliö, luku 5), koska
avaaminen on kallista ja useampi yhteys samaan tiedostoon aiheuttaa
lukitusongelmia.

## Migraatiot

Kun skeema muuttuu, `version` kasvaa ja vanha tietokanta muunnetaan
**migraatiolla**. Room tukee automaattisia migraatioita
(`@AutoMigration(from = 1, to = 2)`) yksinkertaisille muutoksille ja
käsin kirjoitettuja (`Migration(1, 2) { db -> db.execSQL(...) }`)
monimutkaisemmille. Migraatioita varten `exportSchema = true` ja
skeemahakemisto (`room { schemaDirectory(...) }`) tallentavat jokaisen
version skeeman versionhallintaan, ja `MigrationTestHelper` testaa
siirtymän. Esimerkin tietokanta on ensimmäisessä versiossaan, joten
skeemaa ei viedä.

`fallbackToDestructiveMigration` poistaa vanhan datan, kun migraatio
puuttuu. Se sopii vain välimuistiksi tarkoitettuun tietokantaan, ei
käyttäjän omaan tietoon.

## DAOn testaus

Robolectric tarjoaa Androidin SQLiten JVM:llä, joten testi ajaa oikeat
kyselyt muistissa olevaa tietokantaa vasten:

```{.kotlin tiedosto="esimerkit/app/src/test/java/fi/esimerkki/ostokset/data/TuoteDaoTest.kt" osa="testi"}
```

Testi näkee Flow'n jokaisen päivityksen ja tarkistaa järjestyksen
(`ORDER BY ostettu, id`) ja poiston. Muistissa oleva tietokanta on
nopea ja tyhjä jokaisessa testissä.

## DataStore

**DataStore** tallentaa pienet asetukset. Se korvaa
`SharedPreferences`in, joka luki tiedoston pääsäikeessä, ei
ilmoittanut virheistä ja saattoi menettää kirjoituksia.

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/Sailio.kt" osa="datastore"}
```

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/data/Asetukset.kt" osa="asetukset"}
```

`preferencesDataStore`-delegaatti takaa, että tiedostolla on yksi
DataStore koko prosessissa; kaksi samaa tiedostoa käsittelevää oliota
on virhe. `edit` on transaktio: muutos joko tallentuu kokonaan tai ei
lainkaan. **Proto DataStore** tallentaa tyypitetyn olion
(Protocol Buffers tai kotlinx.serialization), mikä sopii
monimutkaisempiin asetuksiin.

DataStore on puhdasta Kotlinia, joten testi ei tarvitse edes
Robolectricia:

```{.kotlin tiedosto="esimerkit/app/src/test/java/fi/esimerkki/ostokset/data/AsetuksetTest.kt" osa="testi"}
```

Sovelluksen omat tiedostot ovat muiden sovellusten ulottumattomissa,
mutta eivät salattuja sovelluksen itsensä tai juurioikeuksin
varustetun laitteen kannalta. Salaisuudet (kirjautumistoken,
salausavain) suojataan **Android Keystorella**: avain luodaan
laitteen suojattuun ympäristöön (TEE tai erillinen turvapiiri), eikä
sitä voi lukea ulos; sovellus pyytää Keystorea salaamaan ja
purkamaan. Tallennettava token salataan
Keystoren avaimella ja kirjoitetaan DataStoreen. Salasanoja ei
tallenneta laitteelle lainkaan.

## Käytännössä

- **Tietokanta on totuuden lähde.** Käyttöliittymä lukee Roomin
  Flow'ta, ja kaikki muutokset kirjoitetaan tietokantaan. Näytettävä
  tieto päivittyy itsestään, ja sovellus toimii ilman verkkoa (luku 8).
- **Entiteetti erillään mallista.** Skeema muuttuu eri tahdissa kuin
  käyttöliittymä. Erillinen tyyppi ja muunnos estävät muutosta
  leviämästä koko sovellukseen.
- **Skeema versionhallintaan ja migraatiot testattuina.** Puuttuva tai
  virheellinen migraatio kaataa sovelluksen päivityksen jälkeen kaikilla
  käyttäjillä.
- **Salaisuudet Keystoren avaimella salattuina**, ei selväkielisinä
  asetuksiin eikä koodiin. APK:n voi purkaa kuka tahansa, joten
  koodissa oleva avain on julkinen.
- **DataStore asetuksille, Room datalle.** Lista tai haettava tieto ei
  kuulu DataStoreen, koska DataStore lukee ja kirjoittaa koko tiedoston
  kerralla.
- **Hinnat:** tietokannan avaaminen ja ensimmäinen kysely maksavat
  kymmeniä millisekunteja. Avaa yhteys kerran. Flow-kysely suoritetaan
  uudelleen jokaisen taulun muutoksen jälkeen, joten laaja kysely
  usein muuttuvaan tauluun kannattaa rajata (`WHERE`, `LIMIT`, Paging).

## Itsearviointi

- Osaat määritellä Room-entiteetin, DAOn ja tietokannan sekä erottaa
  entiteetin sovelluksen mallista.
- Osaat palauttaa kyselyn tuloksen Flow'na ja selittää, milloin se
  päivittyy.
- Osaat kuvata migraatioiden tekemisen ja testaamisen.
- Osaat tallentaa asetukset DataStoreen ja testata sekä DAOn että
  DataStoren ilman laitetta.
