# Tietokanta

Palvelun tila on tietokannassa. Tämä luku käy läpi, miten skeemaa
muutetaan hallitusti (Flyway), miten aggregaatit tallennetaan (Spring
Data JDBC), miten kyselyt kirjoitetaan (JdbcClient) ja missä
transaktioraja on.

## Migraatiot

Skeema on koodia: se muuttuu versioittain, ja jokainen ympäristö –
kehittäjän kone, testit, tuotanto – on samassa tilassa. Flyway ajaa
käynnistyksessä hakemiston `db/migration` tiedostot
`V<versio>__<kuvaus>.sql` järjestyksessä ja kirjaa ajetut tauluun
`flyway_schema_history`. Ajettua tiedostoa ei koskaan muuteta, koska
sen tarkistussumma tallennettiin; korjaus on uusi migraatio.

```{.sql tiedosto="esimerkit/kauppa/src/main/resources/db/migration/V1__tuotteet.sql" osa="v1"}
```

Tietokanta valvoo, mitä se pystyy valvomaan: `NOT NULL`, `UNIQUE`,
`CHECK` ja viiteavaimet. Sovelluksen validointi antaa käyttäjälle
hyvän virheviestin, mutta tietokannan rajoite on se, joka pitää myös
eräajot, käsin tehdyt korjaukset ja sovelluksen bugit kurissa.

Tuotannossa migraatio ajetaan, kun vanha versio palvelusta on vielä
käynnissä. Siksi muutokset tehdään vaiheittain (*expand–contract*):

1. Lisää uusi sarake sallien `NULL`, julkaise sovellus, joka kirjoittaa
   molempiin.
2. Täytä vanhat rivit eräajona.
3. Kun vanha versio on poissa, lisää `NOT NULL` ja poista vanha
   sarake.

Sarakkeen uudelleennimeäminen tai `NOT NULL` -sarakkeen lisääminen
yhdellä migraatiolla rikkoo käynnissä olevan version. Suuren taulun
indeksi luodaan PostgreSQL:ssä `CREATE INDEX CONCURRENTLY`, jotta
kirjoitukset eivät pysähdy.

## Aggregaatit: Spring Data JDBC

*Aggregaatti* on joukko olioita, joka tallennetaan ja ladataan
kokonaisuutena ja jonka säännöt pätevät yhdessä. Tuote on oma
aggregaattinsa:

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/tuote/Tuote.java" osa="tuote"}
```

Tilaus on aggregaatti, johon rivit kuuluvat: rivejä ei tallenneta eikä
haeta erikseen, eikä niillä ole omaa repositoryä. Viittaus tuotteeseen
on pelkkä tunniste (`tuoteId`), ei olioviittaus: toinen aggregaatti
ladataan tarvittaessa omalla repositoryllään.

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/tilaus/Tilaus.java" osa="tilaus"}
```

Repository on rajapinta, jonka Spring Data toteuttaa. Perustoiminnot
(`save`, `findById`, `findAll`, `delete`) ja sivutus tulevat
perittyinä, ja hakumetodit johdetaan nimestä:

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/tuote/TuoteRepository.java" osa="repository"}
```

Spring Data JDBC on tarkoituksella yksinkertainen. `save` kirjoittaa
koko aggregaatin heti: tilauksen tallennus poistaa vanhat rivit ja
lisää nykyiset. Laiskaa latausta, istunnon välimuistia ja
automaattista muutosten seurantaa ei ole, joten kaikki SQL syntyy
näkyvistä kutsuista. Hinta on, että suuri aggregaatti ladataan aina
kokonaan: aggregaatit pidetään pieninä.

## Kyselyt: JdbcClient

Raportit ja näkymät eivät ole aggregaatteja vaan kyselyitä. Niihin
käytetään SQL:ää suoraan. `JdbcClient` sitoo nimetyt parametrit ja
muuntaa rivit tietueiksi (sarake `myynti_sentteina` → kenttä
`myyntiSentteina`):

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/raportti/MyyntiRaportti.java" osa="raportti"}
```

Parametrit sidotaan aina (`:montako`), eikä arvoja koskaan liitetä
merkkijonoon. Tämä estää SQL-injektion ja antaa tietokannan käyttää
valmisteltua suunnitelmaa uudelleen. Tämä *CQRS-tyyli* – kirjoitukset
aggregaattien kautta, luku suoraan kyselyinä – on yleinen ja hyvä
oletus, vaikka koko CQRS-arkkitehtuuria erillisine lukumalleineen ei
tarvittaisi.

## N+1-ongelma

Kun lista ladataan ja jokaiselle alkiolle tehdään oma kysely, syntyy
1 + N kyselyä. Ongelma ei näy kehityksessä kymmenellä rivillä mutta
tuotannossa kymmenellätuhannella. Testi laskee valmistellut
SQL-lauseet käärimällä `DataSource`-pavun:

```{.java tiedosto="esimerkit/kauppa/src/test/java/fi/tutoriaalit/kauppa/raportti/NPlusYksiTest.java" osa="nplus1"}
```

20 tilauksen lataus aggregaatteina tekee 21 kyselyä: yksi tilauksille
ja yksi kunkin tilauksen riveille. Sama summa lasketaan
`GROUP BY` -kyselyllä yhdellä. Korjauksia on kolme: kysely, joka
palauttaa vain tarvittavan (kuten tässä), liitos, joka hakee juuret ja
lapset kerralla, tai erähaku (`WHERE tilaus IN (...)`).

JPA:ssa (Hibernate) sama ongelma on yleisempi ja piilotetumpi: laiskasti
ladattu kokoelma tekee kyselyn vasta, kun sitä käytetään, esimerkiksi
JSON-muunnoksessa ohjaimessa. Siksi JPA-projekteissa tarvitaan
`JOIN FETCH`-kyselyitä tai `@EntityGraph`-määrityksiä ja kyselyjen
määrän valvontaa testeissä. Hibernaten SQL-loki
(`spring.jpa.show-sql`) on ensimmäinen työkalu.

## Transaktiot

`@Transactional` palvelun metodissa aloittaa transaktion ennen metodia
ja sitoo sen lopuksi. Ajonaikainen poikkeus peruu kaiken. Tilauksen
luonti varaa saldot ja tallentaa tilauksen samassa transaktiossa, joten
puolikasta tilausta ei synny:

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/tilaus/TilausPalvelu.java" osa="luo"}
```

Integraatiotesti varmistaa sen: kahden rivin tilaus, jonka jälkimmäinen
rivi ei mahdu varastoon, ei vähennä ensimmäisenkään rivin saldoa.

```{.java tiedosto="esimerkit/kauppa/src/test/java/fi/tutoriaalit/kauppa/tilaus/TilausIntegraatioTest.java" osa="atomisuus"}
```

Spring toteuttaa `@Transactional`-merkinnän välityspalvelinoliolla
(*proxy*), joka kietoo pavun. Siitä seuraa kolme sudenkuoppaa:

- **Kutsu saman luokan sisältä** (`this.toinenMetodi()`) ohittaa
  välityspalvelimen, eikä toisen metodin merkintä vaikuta.
- **Tarkistettu poikkeus** (`IOException`) ei oletuksena peru
  transaktiota; vain `RuntimeException` ja `Error` perivät. Tarvittaessa
  `@Transactional(rollbackFor = Exception.class)`.
- **Yksityinen metodi** ei saa transaktiota lainkaan.

`readOnly = true` kertoo, ettei metodi kirjoita. Spring ja ajuri
voivat optimoida (PostgreSQL-ajuri voi ohjata lukijan replikaan), ja se
dokumentoi aikeen. Eristystaso jätetään yleensä tietokannan oletukseksi
(PostgreSQL: *Read Committed*) ja samanaikaisuus ratkaistaan
ehdollisilla päivityksillä tai versioilla (luku 6). SQL-tutoriaalin
transaktioluku selittää tasojen erot.

## Yhteysallas

Tietokantayhteyden avaaminen kestää millisekunteja ja vie palvelimelta
muistia, joten yhteydet ovat altaassa (HikariCP). Altaan koko on
yksi tärkeimmistä suorituskykyasetuksista, ja suurempi ei ole parempi:
tietokantapalvelin suorittaa kerrallaan vain prosessoriytimiensä ja
levyjensä verran työtä, ja ylimääräiset yhteydet vain jonottavat sen
sisällä. Lähtökohta on muutama yhteys tietokannan ydintä kohden
*kaikkien* sovellusinstanssien yhteensä: kymmenen instanssia kymmenen
yhteyden altailla on jo sata yhteyttä.

Kun allas on tyhjä, pyyntö odottaa (`connection-timeout`, oletus 30 s)
ja epäonnistuu sitten. Siksi transaktiot pidetään lyhyinä: transaktion
sisällä ei kutsuta toista palvelua eikä odoteta käyttäjää. Hidas
ulkoinen kutsu transaktion sisällä varaa yhteyden koko ajaksi ja
tyhjentää altaan kuormassa.

## Käytännössä

- **Skeema migraatioina**, joita ei muuteta jälkikäteen. Tuotannossa
  laajenna–supista-järjestys, jotta vanha ja uusi versio toimivat
  rinnakkain.
- **Pienet aggregaatit, viittaukset tunnisteina.** Iso olioverkko, joka
  ladataan kerralla, on hidas ja lukitsee paljon.
- **Kirjoitukset aggregaatteina, raportit kyselyinä.** Älä lataa sataa
  aggregaattia laskeaksesi summan.
- **Laske kyselyt.** Testi, joka valvoo kyselyjen määrää, löytää
  N+1-ongelman ennen tuotantoa.
- **Transaktio palvelun julkisessa metodissa**, lyhyt ja ilman
  verkkokutsuja.
- **Hinta:** jokainen kysely on verkon edestakainen matka (0,1–1 ms
  samassa konesalissa) ja yhteyden varaus altaasta. JPA:n laiska lataus
  voi muuttaa yhden näkymän sadoiksi kyselyiksi; Spring Data JDBC:n
  hinta on suurten aggregaattien kokonainen lataus ja kirjoitus.

## Itsearviointi

- Osaat kirjoittaa Flyway-migraation ja tehdä rikkovan skeemamuutoksen
  vaiheittain.
- Osaat mallintaa aggregaatin Spring Data JDBC:llä ja kirjoittaa
  kyselyn JdbcClientillä sidotuin parametrein.
- Osaat tunnistaa N+1-ongelman ja korjata sen.
- Osaat kertoa, missä `@Transactional` ei toimi, ja mitoittaa
  yhteysaltaan.
