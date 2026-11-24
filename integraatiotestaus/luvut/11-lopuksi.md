# Lopuksi {.runko-lahteet}

Integraatiotestin tehtävä on näyttää, toimiiko oma koodi niiden
ohjelmien kanssa, joiden kanssa se ajetaan tuotannossa. Kontit tekevät
tästä halpaa: oikea tietokanta, välimuisti, jono tai palvelun väärennös
käynnistyy testin alussa ja katoaa lopuksi.

## Nyrkkisäännöt

1. **Testaa saumat oikeaa riippuvuutta vasten.** SQL-murre, rajoitteet,
   transaktiot, serialisointi ja verkko eivät näy väärennöksissä.
2. **Älä korvaa tuotannon tietokantaa toisella.** Muistikanta testaa eri
   ohjelmaa.
3. **Käynnistä kontit kerran, eristä testit halvalla.** Istuntolaajuinen
   kontti ja testikohtainen transaktio.
4. **Odota valmiutta, älä nuku.** Lokirivi, portti, HTTP-vastaus.
5. **Lukitse versiot.** Kuvat, kirjastot ja työkalut.
6. **Todenna väärennökset.** Sama sopimustestisarja väärennökselle ja
   oikealle toteutukselle.
7. **Simuloi viat.** Jokaisesta ulkoisesta kutsusta viive yli aikarajan
   ja katkos.
8. **Sovi rajapinnoista testeillä.** Kuluttajan sopimus ajetaan tuottajan
   CI:ssä.
9. **Pidä CI vihreänä.** Epävakaa testi korjataan heti.

## Mitä jäi pois

- **Päästä päähän -testit** selaimella (Playwright, Selenium) ja koko
  järjestelmän testiympäristöt.
- **Suorituskykytestit.** Kontit sopivat niihinkin, mutta mittaaminen
  vaatii vakaan ympäristön (taito *Suorituskyky*).
- **Kubernetes-testit** (k3s-moduuli, kind), joissa testataan
  käyttöönottoa eikä sovellusta.
- **Mutaatiotestaus,** joka mittaa, löytävätkö testit tarkoituksella
  tehdyt virheet.

## Lähteet

- Testcontainers. *Testcontainers for Python* -dokumentaatio ja
  *Testcontainers for Java* -dokumentaatio. <https://testcontainers.com/>
- Meszaros, G. *xUnit Test Patterns: Refactoring Test Code.*
  Addison-Wesley, 2007. (Testikaksoisten nimet.)
- Fowler, M. *Mocks Aren't Stubs.* martinfowler.com, 2007.
- Vocke, H. *The Practical Test Pyramid.* martinfowler.com, 2018.
- Cohn, M. *Succeeding with Agile.* Addison-Wesley, 2009. (Testipyramidi.)
- Pact Foundation. *Pact*-dokumentaatio. <https://docs.pact.io/>
- JSON Schema. *JSON Schema Draft 2020-12.* <https://json-schema.org/>
- Shopify. *Toxiproxy*. <https://github.com/Shopify/toxiproxy>
- PostgreSQL Global Development Group. *PostgreSQL 16 Documentation:*
  luvut CREATE DATABASE (template), Transactions ja SAVEPOINT.
  <https://www.postgresql.org/docs/16/>
- SQLite. *Datatypes In SQLite* (type affinity).
  <https://www.sqlite.org/datatype3.html>
- SQLAlchemy. *Joining a Session into an External Transaction*
  (testien transaktiot). <https://docs.sqlalchemy.org/>
- Redis. *Redis Streams* -dokumentaatio (kuluttajaryhmät, XAUTOCLAIM).
  <https://redis.io/docs/>
- pytest. *How to use fixtures* (laajuudet, `--setup-show`).
  <https://docs.pytest.org/>
- GitHub. *Workflow syntax for GitHub Actions.*
  <https://docs.github.com/actions>
- Docker. *Docker Hub usage and rate limits.* <https://docs.docker.com/>
- Google Cloud. *Pulling cached Docker Hub images* (mirror.gcr.io).
  <https://cloud.google.com/>

Esimerkkien kirjastot: testcontainers (Apache-2.0), SQLAlchemy (MIT),
psycopg (LGPL-3.0), redis-py (MIT), jsonschema (MIT) ja pytest (MIT).
Konttikuvat: PostgreSQL (PostgreSQL License), Redis 7.2 (BSD-3-Clause;
versiosta 7.4 alkaen Redisin lisenssi muuttui, siksi 7.2) ja Python
(PSF License).
