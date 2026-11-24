# Taustapalvelut

HTTP-rajapintojen ja taustajärjestelmien toteutus Javalla ja Spring
Bootilla: REST-rajapinnan suunnittelu, tietokanta ja migraatiot,
samanaikaisuus ja idempotenssi, validointi ja virheet, todennus ja
valtuutus, havainnointi ja testaus. Valmis dokumentti:
[taustapalvelut.pdf](https://saperant.github.io/tutoriaalit/materiaalit/taustapalvelut.pdf), pikaopas:
[taustapalvelut-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/taustapalvelut-pikaopas.pdf).

Esitiedot: taidot *Java*, *SQL ja relaatiotietokannat* ja *Tietoverkot*.

## Sisältö

1. Johdanto – pino ja valinnat, esimerkkiprojekti
2. HTTP ja REST ilman kehystä – metodit, tilakoodit, sisältöneuvottelu,
   ETag
3. Rajapinnan suunnittelu – resurssit, DTO:t, sivutus, RFC 9457,
   versiointi, OpenAPI
4. Spring Boot – riippuvuuksien injektointi, kerrokset, konfiguraatio,
   profiilit, virtuaalisäikeet
5. Tietokanta – Flyway, Spring Data JDBC, JdbcClient, N+1,
   transaktiot, yhteysallas
6. Samanaikaiset pyynnöt ja idempotenssi – ehdollinen päivitys,
   optimistinen lukitus, idempotenssiavain, outbox
7. Validointi ja virheiden käsittely
8. Todennus ja valtuutus – suodatinketju, salasanat, tokenit, olion
   tason valtuutus, CORS
9. Havainnointi – korrelaatiotunnus, metriikat, terveystarkistukset
10. Testaus – yksikkö-, viipale- ja integraatiotestit
11. Lopuksi – nyrkkisäännöt, mallit, lähteet

## Esimerkit

`esimerkit/` on Maven-projekti (Java 21, Spring Boot 4.2), jossa on
kaksi modulia: `http-perusteet` (HTTP pelkällä JDK:lla) ja `kauppa`
(verkkokaupan tuote- ja tilausrajapinta). Kaikki tekstissä näytetty
koodi on näistä tiedostoista, ja testit varmistavat sen toiminnan.

```text
make -C esimerkit          # ./mvnw verify: kääntää ja ajaa testit
make -C esimerkit aja      # palvelu porttiin 8080
make testaa                # rakenne, viittaukset ja esimerkkien testit
make pdf                   # PDF:t
```

Kehityskontti: `.devcontainer/taustapalvelut/`.

Lisenssi: CC BY-SA 4.0.
