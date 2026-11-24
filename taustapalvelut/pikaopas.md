---
title: Taustapalvelut
subtitle: Pikaopas · Java 21 · Spring Boot 4.2 · Spring Data JDBC · Flyway
---

# HTTP

| Metodi | Turvallinen | Idempotentti | Käyttö |
|--------|-------------|--------------|--------|
| GET | kyllä | kyllä | haku |
| POST | ei | ei (avaimella kyllä) | luonti, toiminto |
| PUT | ei | kyllä | korvaus |
| PATCH | ei | ei | osittainen muutos |
| DELETE | ei | kyllä | poisto |

| Koodi | Kun |
|-------|-----|
| 200 / 201 + `Location` / 204 | ok / luotu / ei runkoa |
| 304 | `If-None-Match` täsmää |
| 400 / 422 | muoto / sisältö ei kelpaa |
| 401 / 403 | kuka olet? / et saa |
| 404 / 405 + `Allow` | ei ole / väärä metodi |
| 409 | ristiriita tilan kanssa |
| 412 / 428 | `If-Match` ei täsmää / puuttuu |
| 415 / 406 | `Content-Type` / `Accept` |
| 429 / 503 + `Retry-After` | rajoitus / tilapäisesti poissa |

# Rakenne

| Kerros | Merkintä | Vastuu |
|--------|----------|--------|
| Ohjain | `@RestController` | HTTP, DTO, `@Valid` |
| Palvelu | `@Service`, `@Transactional` | säännöt, transaktio |
| Repository | `ListCrudRepository` | aggregaatit |
| Kysely | `JdbcClient` | raportit, näkymät |
| Virheet | `@RestControllerAdvice` | `ProblemDetail` |
| Asetukset | `@ConfigurationProperties` + record | tyypitetty, `@Validated` |

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/tuote/TuoteOhjain.java" osa="haku"}
```

# Tietokanta

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/tilaus/Varasto.java" osa="varasto"}
```

- Migraatio `V<n>__kuvaus.sql`, ajettua ei muuteta. Laajenna →
  täytä → supista.
- Aggregaatti kokonaan `save`-kutsulla; viittaus toiseen tunnisteena.
- `@Version` + `ETag`/`If-Match` → optimistinen lukitus.
- N+1: lataa lista kyselyllä tai liitoksella, laske kyselyt testissä.
- `@Transactional` ei toimi: saman luokan sisäinen kutsu, yksityinen
  metodi; tarkistettu poikkeus ei peru.
- Yhteysallas pieni: muutama yhteys tietokannan ydintä kohden kaikki
  instanssit yhteensä.

# Turva

| Asia | Ratkaisu |
|------|----------|
| Salasana | `{bcrypt}`/Argon2, delegoiva kooderi |
| Käyttäjille | OIDC-tunnistuspalvelu, JWT-resurssipalvelin |
| JWT | allekirjoitus, `exp` lyhyt, `iss`, `aud` |
| Olio | `@PostAuthorize`, omistaja hakuehtoon |
| Evästeet | CSRF päälle; tilaton token: pois |
| CORS | tarkka lista alkuperiä, ei `*` |

# Havainnointi

- MDC-korrelaatiotunnus suodattimessa, palautetaan otsakkeessa.
- Rakenteiset lokit: `logging.structured.format.console: ecs`.
- RED: pyynnöt, virheet, kesto (p95, p99). Ei rajattomia tageja.
- `/actuator/health/liveness` ilman ulkoisia riippuvuuksia,
  `/readiness` niiden kanssa.

# Testit

| Merkintä | Konteksti |
|----------|-----------|
| (ei mitään) | yksikkö, ms |
| `@WebMvcTest(X.class)` + `@MockitoBean` | web-kerros |
| `@DataJdbcTest` | kanta, Flyway, peruttava transaktio |
| `@SpringBootTest(RANDOM_PORT)` + `RestTestClient` | koko sovellus |
| `ApplicationContextRunner` | konfiguraatio |
| `@WithMockUser(roles = "X")` | todennettu käyttäjä |

```{.java tiedosto="esimerkit/kauppa/src/test/java/fi/tutoriaalit/kauppa/tuote/TuoteOhjainTest.java" osa="etag"}
```

# Komennot

| Tarkoitus | Komento |
|-----------|---------|
| Testit | `./mvnw verify` |
| Yksi testi | `./mvnw -pl kauppa test -Dtest=Luokka` |
| Käynnistys | `./mvnw -pl kauppa spring-boot:run` |
| Riippuvuudet | `./mvnw dependency:tree` |
| Kokeilu | `curl -i -u aino:… localhost:8080/api/v1/tuotteet` |
