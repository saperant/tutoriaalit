# Spring Boot: rakenne ja konfiguraatio

Spring on *riippuvuuksien injektoinnin* säiliö: sovelluksen oliot
(*papu*, *bean*) luodaan säiliössä, ja kukin saa riippuvuutensa
konstruktorin parametreina. Spring Boot lisää tähän *automaattisen
konfiguraation*: kun luokkapolulla on esimerkiksi H2 ja Flyway, Boot
luo yhteysaltaan, ajaa migraatiot ja tekee `JdbcClient`-olion ilman
riviäkään omaa koodia.

## Käynnistys ja komponenttihaku

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/KauppaSovellus.java" osa="sovellus"}
```

`@SpringBootApplication` tekee kolme asiaa: merkitsee luokan
konfiguraatioksi, käynnistää automaattisen konfiguraation ja etsii
paketista `fi.tutoriaalit.kauppa` ja sen alapaketeista luokat, joilla
on stereotyyppimerkintä (`@Component`, `@Service`, `@Repository`,
`@RestController`, `@Configuration`). `@Bean`-metodit luovat papuja,
joiden luokkaa ei voi merkitä, kuten tässä JDK:n `Clock`.

Automaattinen konfiguraatio on ehdollinen: se luo pavun vain, jos
sovellus ei ole luonut omaa. Siksi oma `PasswordEncoder` tai
`CorsConfigurationSource` (luku 8) korvaa oletuksen. Käynnistyksen
raportti näyttää, mitkä konfiguraatiot otettiin käyttöön ja miksi:

```text
./mvnw -pl kauppa spring-boot:run -Dspring-boot.run.arguments=--debug
```

## Riippuvuuksien injektointi

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/tuote/TuotePalvelu.java" osa="palvelu"}
```

Konstruktori-injektio on suositeltu tapa:

- Riippuvuudet ovat `final`-kenttiä, ja olio on valmis heti
  luonnin jälkeen.
- Luokan voi luoda testissä ilman Springiä: `new TuotePalvelu(vale)`.
- Liian pitkä konstruktori on näkyvä varoitus: luokalla on liian monta
  vastuuta. (`TilausPalvelu` on rajalla seitsemällä riippuvuudella.)

Kenttäinjektio (`@Autowired` kentässä) piilottaa riippuvuudet ja vaatii
säiliön myös testissä; sitä käytetään vain testiluokissa.
Jos luokalla on yksi konstruktori, `@Autowired`-merkintää ei tarvita.

Papujen oletuselinkaari on *singleton*: säiliössä on yksi
`TuotePalvelu`, jota kaikki pyynnöt käyttävät yhtä aikaa. Siksi
palveluluokissa ei säilytetä pyyntökohtaista tilaa kentissä. Tila on
tietokannassa, pyynnön parametreissa tai tarvittaessa
pyyntökohtaisessa papussa.

## Kerrokset ja niiden rajat

Pyyntö kulkee palvelussa aina saman reitin. Jokaisella kerroksella on
yksi vastuu, ja transaktio alkaa ja päättyy palvelukerroksen rajalla:

```{.dot otsikko="Pyynnön kulku kerrosten läpi; transaktioraja on palvelun metodi"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.3;
  alku [shape=point, width=0.05];
  suodattimet [label="suodattimet\nturva,\nkorrelaatio"];
  ohjain [label="ohjain\nHTTP,\nDTO:t"];
  subgraph cluster_tx {
    label="transaktio"; style="rounded,dashed";
    color="#B4532A"; fontcolor="#B4532A";
    palvelu [label="palvelu\nsäännöt"];
    repo [label="repository\nSQL"];
  }
  kanta [label="tieto-\nkanta", shape=cylinder];
  alku -> suodattimet [label="HTTP"];
  suodattimet -> ohjain -> palvelu -> repo -> kanta;
}
```

| Kerros | Vastuu | Ei saa |
|--------|--------|--------|
| Ohjain (`@RestController`) | HTTP: polut, otsakkeet, DTO-muunnos, validointi | sisältää liiketoimintasääntöjä |
| Palvelu (`@Service`) | käyttötapaukset, säännöt, transaktioraja | tietää HTTP:stä (ei `HttpServletRequest`) |
| Repository | tallennus ja kyselyt | päättää säännöistä |
| Aggregaatti, arvot | invariantit, laskenta | riippua kehyksestä enempää kuin merkinnöin |

Raja on käytännöllinen, ei uskonnollinen: pieni lukukysely voi kulkea
ohjaimesta suoraan raporttiluokkaan (`RaporttiOhjain`), koska siinä ei
ole sääntöjä. Tärkeää on, että transaktioraja ja säännöt ovat yhdessä
paikassa, jotta sama käyttötapaus toimii samoin rajapinnasta,
eräajosta ja viestijonosta kutsuttuna.

Ohjain on ohut: se kääntää HTTP:n palvelukutsuksi ja tuloksen
vastaukseksi.

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/tuote/TuoteOhjain.java" osa="haku"}
```

## Konfiguraatio

Asetukset luetaan monesta lähteestä, ja myöhempi voittaa:
`application.yaml`, profiilin tiedosto `application-<profiili>.yaml`,
ympäristömuuttujat ja komentorivi. Ympäristömuuttujan nimi saadaan
asetuksen nimestä isoilla kirjaimilla ja alaviivoin:
`kauppa.maksimirivit` → `KAUPPA_MAKSIMIRIVIT`. Näin sama konttikuva
toimii kaikissa ympäristöissä (*twelve-factor*-periaate), ja salaisuudet
tulevat ympäristöstä eivätkä koskaan versionhallintaan.

```{.yaml tiedosto="esimerkit/kauppa/src/main/resources/application.yaml" osa="asetukset"}
```

Sovelluksen omat asetukset sidotaan tyypitettyyn tietueeseen. Merkintä
`@Validated` tarkistaa arvot käynnistyksessä, joten virheellinen
asetus kaataa sovelluksen heti eikä vasta ensimmäisessä pyynnössä
kolmen viikon kuluttua.

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/KauppaAsetukset.java" osa="asetukset"}
```

`ApplicationContextRunner` testaa konfiguraation ilman koko sovellusta:

```{.java tiedosto="esimerkit/kauppa/src/test/java/fi/tutoriaalit/kauppa/AsetuksetTest.java" osa="asetukset"}
```

## Profiilit

Profiili on nimetty joukko asetuksia ja papuja. Testit käyttävät
profiilia `test`, joka lisää tuotannon migraatioiden päälle
testiaineiston:

```{.yaml tiedosto="esimerkit/kauppa/src/test/resources/application-test.yaml" osa="testiprofiili"}
```

Profiileja käytetään säästeliäästi. Kun profiileja on monta
(`dev`, `test`, `staging`, `prod`) ja niissä on eri papuja, tuotannossa
ajettava kokoonpano on se, jota on testattu vähiten. Parempi on yksi
kokoonpano, jonka *arvot* tulevat ympäristöstä, ja profiilit vain
testiaineistolle ja paikalliselle kehitykselle.

## Virtuaalisäikeet

Spring MVC käsittelee jokaisen pyynnön omassa säikeessään, ja säie
odottaa tietokannan ja muiden palvelujen vastauksia. Asetus
`spring.threads.virtual.enabled` ajaa pyynnöt Java 21:n
virtuaalisäikeissä, joten odottavia pyyntöjä voi olla tuhansia ilman
suurta säiealtaata. Kaksi asiaa ei muutu: tietokantayhteyksiä on
silti vain altaan verran (luku 5), ja `synchronized`-lohkossa odottava
virtuaalisäie voi Java 21:ssä sitoa kantasäikeensä (Java 24 korjasi
tämän). Reaktiivinen WebFlux on vaihtoehto, kun tarvitaan
virtausmaista käsittelyä, mutta tavalliseen rajapintaan
virtuaalisäikeet antavat saman skaalautuvuuden yksinkertaisemmalla
koodilla.

## Käytännössä

- **Konstruktori-injektio ja muuttumattomat palvelut.** Singleton-papu
  on jaettu kaikille pyynnöille; pyyntökohtainen tila kentässä on
  kilpatilanne.
- **Transaktio ja säännöt palveluun**, HTTP ohjaimeen. Testaa sääntö
  palvelun tasolla, HTTP-käytös ohjaimen viipaletestillä.
- **Tyypitetyt ja validoidut asetukset** (`@ConfigurationProperties` ja
  record) merkkijonoavainten (`@Value("${...}")`) sijaan. Virheellinen
  arvo pysäyttää käynnistyksen.
- **Salaisuudet ympäristöstä** tai salaisuuksien hallinnasta (Vault,
  pilven secret manager), ei koskaan `application.yaml`-tiedostoon.
- **Kello ja satunnaisuus ovat riippuvuuksia.** `Clock`-papu tekee
  ajasta testattavan; `Instant.now()` keskellä logiikkaa ei ole.
- **Hinta:** automaattinen konfiguraatio ja komponenttihaku maksavat
  käynnistysajassa (tämä palvelu noin 2–3 s) ja muistissa (noin 150 Mt).
  Pitkään ajettavassa palvelussa sillä ei ole väliä; lyhytikäisissä
  funktioissa (*serverless*) käytetään GraalVM:n natiivikäännöstä,
  CRaC-tilannevedosta tai kevyempää kehystä.

## Itsearviointi

- Osaat selittää, miten komponenttihaku, `@Bean`-metodit ja
  automaattinen konfiguraatio luovat sovelluksen papuja.
- Osaat jakaa käyttötapauksen ohjaimeen, palveluun ja repositoryyn ja
  perustella rajat.
- Osaat sitoa asetukset tyypitettyyn tietueeseen, validoida ne ja
  ylikirjoittaa ne ympäristömuuttujalla.
- Osaat kertoa, mitä virtuaalisäikeet muuttavat ja mitä eivät.
