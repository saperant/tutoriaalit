# Testaus

Taustapalvelun virheet ovat usein rajoilla: väärä tilakoodi, puuttuva
valtuutus, SQL joka toimii H2:ssa mutta ei PostgreSQL:ssä, transaktio
joka ei peru. Siksi testit kohdistetaan rajoihin, ja jokaiselle tasolle
valitaan pienin konteksti, joka sen testaa luotettavasti.

## Testipyramidi

| Taso | Mitä | Työkalu | Kesto | Määrä |
|------|------|---------|-------|-------|
| Yksikkö | laskenta, säännöt ilman kehystä | JUnit, AssertJ | ms | paljon |
| Viipale | yksi kerros kehyksen kanssa | `@WebMvcTest`, `@DataJdbcTest` | 1–2 s | kohtalaisesti |
| Integraatio | koko sovellus, oikea HTTP ja kanta | `@SpringBootTest` | 3–5 s | tärkeimmät polut |
| Päästä päähän | useampi palvelu, oikea ympäristö | Playwright, k6 | minuutteja | vähän |

Pyramidin muoto tulee hinnasta: yksikkötesti on nopea ja kertoo
tarkasti, mikä meni rikki, mutta ei näe kerrosten välisiä virheitä.
Integraatiotesti näkee ne, mutta on hidas ja epäonnistuessaan
epätarkka. Tämän projektin koko sarja kestää alle minuutin, koska
kontekstit käynnistetään vain kolme kertaa.

## Yksikkötestit

Laskenta ja säännöt, jotka eivät tarvitse kehystä, testataan ilman sitä:

```{.java tiedosto="esimerkit/kauppa/src/test/java/fi/tutoriaalit/kauppa/tilaus/TilausTest.java" osa="yksikko"}
```

Konstruktori-injektion ansiosta myös palvelun voi luoda testissä
valeolioilla (`new TuotePalvelu(vale)`). Valeolioita (Mockito)
käytetään säästeliäästi: testi, joka tarkistaa, että palvelu kutsui
repositoryä tietyillä parametreilla, toistaa toteutuksen eikä huomaa,
jos SQL on väärin. Tietokantaa käyttävä logiikka testataan mieluummin
oikeaa kantaa vasten.

## Web-viipale

`@WebMvcTest` käynnistää vain web-kerroksen: ohjaimen, JSON-muunnoksen,
validoinnin, ohjainneuvojat ja (tuotuna) turvaketjun. Palvelu korvataan
`@MockitoBean`-valeoliolla.

```{.java tiedosto="esimerkit/kauppa/src/test/java/fi/tutoriaalit/kauppa/tuote/TuoteOhjainTest.java" osa="viipale"}
```

`MockMvcTester` lähettää pyynnön suoraan Springin
`DispatcherServlet`-olioon ilman verkkoa, ja AssertJ-tyyliset
väitteet tarkistavat tilan, otsakkeet ja JSONin:

```{.java tiedosto="esimerkit/kauppa/src/test/java/fi/tutoriaalit/kauppa/tuote/TuoteOhjainTest.java" osa="etag"}
```

Viipaletesti on oikea paikka HTTP-sopimuksen yksityiskohdille:
tilakoodit, otsakkeet, virhemuoto ja valtuutussäännöt. Ne ovat
nopeita kirjoittaa kattavasti, koska palvelun käytöksen voi asettaa
valeoliolla.

## Tietokantaviipale

`@DataJdbcTest` käynnistää vain tietokantakerroksen: yhteyden,
Flyway-migraatiot ja repositoryt. Jokainen testi ajetaan
transaktiossa, joka perutaan lopuksi, joten testit eivät näe
toistensa muutoksia.

```{.java tiedosto="esimerkit/kauppa/src/test/java/fi/tutoriaalit/kauppa/tuote/TuoteRepositoryTest.java" osa="viipale"}
```

Testiaineisto on Flyway-migraatio, jonka vain testiprofiili ottaa
mukaan. Näin aineisto kulkee samaa reittiä kuin skeema ja pysyy sen
kanssa yhteensopivana:

```{.sql tiedosto="esimerkit/kauppa/src/test/resources/db/testidata/V1000__testidata.sql"}
```

## Integraatiotesti

`@SpringBootTest(webEnvironment = RANDOM_PORT)` käynnistää koko
sovelluksen satunnaiseen porttiin, ja `RestTestClient` tekee oikeita
HTTP-pyyntöjä. Pyyntö kulkee Tomcatin, turvaketjun, ohjaimen,
palvelun, transaktion ja tietokannan läpi. Tällä tasolla testataan
asiat, jotka syntyvät kerrosten yhteistyöstä: transaktion peruminen,
samanaikaisuus, idempotenssi ja olion tason valtuutus (luvut 5, 6 ja 8).

```{.java tiedosto="esimerkit/kauppa/src/test/java/fi/tutoriaalit/kauppa/tilaus/TilausIntegraatioTest.java" osa="asetelma"}
```

Integraatiotestien tietokanta on jaettu saman kontekstin testien
kesken, eikä HTTP-pyyntöjen muutoksia peruta. Siksi testi asettaa itse
tarvitsemansa tilan (`tuote(nimi, saldo)`) eikä oleta toisten testien
jättämää tilaa tai suoritusjärjestystä.

## Kontekstien välimuisti

Spring käynnistää kontekstin kerran ja käyttää sitä uudelleen kaikissa
testiluokissa, joilla on sama kokoonpano. Jokainen eri
`@MockitoBean`-yhdistelmä, `@ActiveProfiles`-arvo tai
`@TestPropertySource` luo uuden kontekstin, ja kymmenen hieman erilaista
integraatiotestiluokkaa käynnistää sovelluksen kymmenen kertaa.
Yhteinen kantaluokka tai yhteinen merkintä pitää kokoonpanot samoina.

## Oikea tietokanta: Testcontainers

H2 PostgreSQL-tilassa kattaa tavallisen SQL:n, mutta ei kaikkea:
PostgreSQL:n `jsonb`, osittaiset indeksit, `FOR UPDATE SKIP LOCKED`,
eristystasojen käytös ja virheilmoitukset ovat erilaisia. Tuotannossa
integraatiotestit ajetaan samaa tietokantaa vasten kuin tuotanto.
Testcontainers käynnistää PostgreSQL:n Docker-konttiin testin ajaksi,
ja Spring Boot liittää sen sovellukseen merkinnällä `@ServiceConnection`:

```text
@Container
@ServiceConnection
static PostgreSQLContainer<?> kanta =
        new PostgreSQLContainer<>("postgres:17");
```

Tämän tutoriaalin testit eivät käytä Testcontainersia, koska ne ajetaan
ympäristöissä, joissa Dockeria ei ole. Oikeassa projektissa
Testcontainers on suositeltu oletus heti alusta.

## Testien ajo

Maven ajaa testit vaiheessa `test` ja koko tarkistuksen vaiheessa
`verify`. Esimerkkien Makefile ajaa saman kuin CI:

```{.makefile tiedosto="esimerkit/Makefile"}
```

Testiriippuvuudet ovat startereita kuten muutkin:

```{.xml tiedosto="esimerkit/kauppa/pom.xml" osa="testiriippuvuudet"}
```

## Käytännössä

- **Pienin konteksti, joka testaa asian luotettavasti.** Laskenta
  yksikkötestillä, HTTP-sopimus web-viipaleella, SQL tietokantaviipaleella,
  transaktiot ja samanaikaisuus integraatiotestillä.
- **Testaa tilakoodit, virhemuodot ja valtuutus kattavasti**: ne ovat
  rajapinnan sopimus, ja asiakkaat rikkoutuvat niiden muuttuessa.
- **Oikea tietokanta tuotannon versiona** (Testcontainers), kun
  käytetään tietokannan omia ominaisuuksia.
- **Testi asettaa oman tilansa.** Testit, jotka riippuvat
  suoritusjärjestyksestä, rikkoutuvat satunnaisesti rinnakkaisajossa.
- **Vähän valeolioita.** Vale palvelukerroksen rajalla (web-viipale)
  on hyödyllinen; vale jokaiselle luokalle tekee testeistä
  toteutuksen kopioita.
- **Hinta:** kontekstin käynnistys on 1–5 sekuntia, ja se on suurin
  testisarjan kesto. Kymmenen kontekstia on minuutti; yksi jaettu
  konteksti muutama sekunti.

## Itsearviointi

- Osaat valita testille tason (yksikkö, viipale, integraatio) ja
  perustella valinnan.
- Osaat kirjoittaa `@WebMvcTest`-testin MockMvcTesterillä ja
  `@DataJdbcTest`-testin testiaineistoineen.
- Osaat kirjoittaa integraatiotestin, joka on riippumaton muista
  testeistä.
- Osaat selittää kontekstien välimuistin ja Testcontainersin hyödyt.
