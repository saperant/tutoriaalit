# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **HTTP:n semantiikka on sopimus.** Oikea metodi, tilakoodi ja
   otsakkeet; GET ei muuta tilaa; 4xx asiakkaalle, 5xx palvelulle.
2. **DTO rajalla, validointi rajalla.** Sisäinen koodi käsittelee vain
   kelvollisia, tyypitettyjä arvoja.
3. **Yksi virhemuoto** (RFC 9457) vakaalla `type`-tunnisteella.
4. **Säännöt ja transaktioraja palveluun.** Transaktio on lyhyt eikä
   sisällä verkkokutsuja.
5. **Tarkistus ja muutos samaan lauseeseen**, muuten versio ja
   `If-Match`. Yksilöivä rajoite on paras lukko.
6. **Idempotenssiavain** jokaiseen POST-pyyntöön, jonka toistaminen
   olisi vahingollista.
7. **Oletus kieltää**, ja olion tason valtuutus jokaisessa haussa ja
   listauksessa.
8. **Salaisuudet ympäristöstä**, asetukset tyypitettyinä ja
   validoituina.
9. **Korrelaatiotunnus, RED-mittarit ja erilliset liveness- ja
   readiness-tarkistukset** ennen ensimmäistä tuotantojulkaisua.
10. **Testaa rajat** pienimmällä luotettavalla kontekstilla ja oikealla
    tietokannalla.

## Mallit

| Malli | Ongelma | Luku |
|-------|---------|------|
| DTO | tietomalli vuotaisi rajapintaan | 3 |
| Problem Details | virheet eri muodoissa | 3, 7 |
| Kerrokset (ohjain, palvelu, repository) | HTTP ja säännöt sekaisin | 4 |
| Aggregaatti | mitkä oliot muuttuvat yhdessä | 5 |
| Repository | tallennuksen yksityiskohdat logiikassa | 5 |
| Unit of work (transaktio) | puolikkaat muutokset | 5 |
| CQRS-tyylinen lukumalli | raportit aggregaattien kautta | 5 |
| Ehdollinen päivitys | lue–tarkista–kirjoita-kilpatilanne | 6 |
| Optimistinen lukitus, ETag | kadonnut päivitys | 2, 6 |
| Idempotenssiavain | toistettu POST | 6 |
| Outbox | viesti ja tietokantamuutos eri aikaan | 6 |
| Jäsennä, älä vain tarkista | toistuvat tai unohtuneet tarkistukset | 7 |
| Korrelaatiotunnus | hajallaan olevat lokirivit | 9 |
| Aikaraja, uudelleenyritys, varavastaus | hidas tai kaatunut riippuvuus | 6 |

## Jatkotaidot

- *Palveluarkkitehtuurit*: usean palvelun rajat, viestinvälitys,
  katkaisija, saga ja outbox toteutettuina. Tämän tutoriaalin
  idempotenssi ja lähtevien kutsujen aikarajat ovat sen perustaa.
- *Skaalautuvien järjestelmien suunnittelu*: välimuistit, jonot,
  replikointi ja kapasiteetti.
- *Kontit ja pilvi-infrastruktuuri*: palvelu konttiin (Spring Bootin
  `spring-boot:build-image` tai Dockerfile), Kubernetesin terveystarkistukset,
  salaisuuksien hallinta ja julkaisuputki.
- *Integraatiotestaus ja Testcontainers*: testit tuotannon
  tietokantaa vasten.
- *Web-sovellukset*: selainsovellus, joka käyttää tätä rajapintaa.
- *Palveluarkkitehtuurin tietoturva*: palvelujen väliset
  identiteetit, mTLS ja tokenit.
- *Tekninen dokumentaatio*: rajapinnan kuvaus (OpenAPI) ja sen
  pitäminen ajan tasalla.
- *Kotlin* ja *Go*: samat periaatteet toisella kielellä. Kotlin
  toimii Spring Bootissa sellaisenaan.

## Lähteet ja dokumentaatio

- **Spring Boot -dokumentaatio** (<https://docs.spring.io/spring-boot/>)
  ja **Spring Framework -dokumentaatio** (Web MVC, transaktiot,
  testaus). Spring Data JDBC:n ja Spring Securityn
  referenssidokumentaatio samassa osoitteessa.
- **RFC 9110 HTTP Semantics** (<https://www.rfc-editor.org/rfc/rfc9110>):
  metodit, tilakoodit, ehdolliset pyynnöt ja sisältöneuvottelu.
  **RFC 9457 Problem Details for HTTP APIs**.
- **Zalando RESTful API Guidelines**
  (<https://opensource.zalando.com/restful-api-guidelines/>, CC BY 4.0)
  ja **Microsoft REST API Guidelines** (GitHub): kattavat ja
  perustellut suunnitteluohjeet, myös versioinnista ja sivutuksesta.
- **OWASP API Security Top 10** (<https://owasp.org/API-Security/>) ja
  **OWASP Cheat Sheet Series**: todennus, salasanojen tallennus,
  JWT, lokitus.
- **The Twelve-Factor App** (<https://12factor.net>): konfiguraatio
  ympäristöstä, tilattomat prosessit, lokit tapahtumavirtana.
- **HikariCP: About Pool Sizing** (projektin wiki GitHubissa):
  miksi pieni yhteysallas on nopeampi.
- **Flyway-dokumentaatio** (<https://documentation.red-gate.com/fd>).
- **Kirjat:** Martin Kleppmann, *Designing Data-Intensive
  Applications* (transaktiot, replikointi, idempotenssi). Michael
  Nygard, *Release It!* (katkaisija, aikakatkaisut, vakausmallit).
  Vaughn Vernon, *Implementing Domain-Driven Design* (aggregaatit).
  Vlad Mihalcea, *High-Performance Java Persistence* (JDBC, JPA ja
  yhteysaltaat syvällisesti).

### Työkalut

- **Spring Initializr** (<https://start.spring.io>) luo uuden projektin
  valituilla startereilla.
- **HTTPie**, **Bruno** ja IDE:n `.http`-tiedostot rajapinnan
  kokeiluun; **k6** ja **Gatling** kuormitustestaukseen.
- **springdoc-openapi** ja **openapi-generator** rajapintakuvauksiin;
  **oasdiff** rikkovien muutosten tunnistamiseen.
- **Testcontainers** (<https://testcontainers.com>) oikeat tietokannat
  ja palvelut testeihin.

## Lisenssi

Tämä tutoriaali ja sen esimerkkikoodit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0,
<https://creativecommons.org/licenses/by-sa/4.0/deed.fi>). Teosta saa
kopioida, levittää ja muokata, kunhan alkuperäinen lähde mainitaan ja
muokatut versiot jaetaan samalla lisenssillä.
