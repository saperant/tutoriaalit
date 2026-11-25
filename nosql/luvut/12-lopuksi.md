# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. Relaatiotietokanta on oletus. Muu tietokanta valitaan nimetyn ja
   mitatun tarpeen perusteella.
2. NoSQL-malli suunnitellaan kyselyjen mukaan. Kirjoita kyselyt ja
   niiden määrät ylös ennen tietomallia.
3. Denormalisointi on normaalia, mutta jokainen kopio on päivitettävä.
   Päätä, kuka pitää kopiot samassa tahdissa.
4. Skeemattomuus siirtää skeeman sovellukseen. Validoi rakenne, mieluiten
   tietokannassa.
5. Älä lue, laske ja kirjoita takaisin. Käytä tietokannan atomisia
   operaatioita, ehdollisia kirjoituksia tai transaktioita.
6. Selvitä, mitä kuittaus tarkoittaa: yksi palvelin muistissa,
   enemmistö levyllä vai jotain siltä väliltä.
7. Lukeminen replikalta voi palauttaa vanhan arvon. Käyttäjän oma
   kirjoitus luetaan ensisijaiselta tai kausaalisessa istunnossa.
8. Osioavain on vaikea muuttaa. Sen on jaettava kuorma tasaisesti, ja
   tavallisimman kyselyn on osuttava yhteen osioon.
9. LSM-puu tekee kirjoituksista halpoja ja poistoista kalliita.
   Suunnittele, miten vanha data poistetaan.
10. Testaa oikeaa tietokantaa vastaan. Muistissa toimiva jäljitelmä ei
    paljasta konsistenssin, transaktioiden tai kyselysuunnitelman
    eroja.

## Jatkotaidot

- *Integraatiotestaus ja Testcontainers* näyttää, miten tämän
  tutoriaalin tapaan oikeita tietokantoja käytetään sovelluksen
  testeissä.
- *Hajautetut järjestelmät* käsittelee replikoinnin ja konsistenssin
  teorian: kvoorumit, konsistenssimallit, CRDT:t ja konsensuksen.
- *Skaalautuvien järjestelmien suunnittelu* kokoaa tietokannat osaksi
  arkkitehtuuria: välimuistit, osioinnin, jonot ja havaittavuuden.
- *SQL ja relaatiotietokannat* syventää relaatiotietokantojen
  vertailua, aikasarjoja ja sovelluksen tietokantarajapintoja.

## Lähteet

Kirjat:

- Martin Kleppmann: *Designing Data-Intensive Applications*.
  O'Reilly 2017. Tietomallit, tallennusmoottorit (B-puu ja LSM-puu),
  replikointi ja osiointi.
- Pramod J. Sadalage ja Martin Fowler: *NoSQL Distilled*.
  Addison-Wesley 2012. Tietomallit ja polyglot persistence.
- Alex Petrov: *Database Internals*. O'Reilly 2019. Tallennusrakenteet
  ja hajautetut tietokannat.

Artikkelit:

- Patrick O'Neil, Edward Cheng, Dieter Gawlick ja Elizabeth O'Neil: The
  Log-Structured Merge-Tree (LSM-Tree). *Acta Informatica* 33, 1996.
- Fay Chang ym.: Bigtable: A Distributed Storage System for
  Structured Data. *OSDI* 2006.
- Giuseppe DeCandia ym.: Dynamo: Amazon's Highly Available Key-value
  Store. *SOSP* 2007.
- Avinash Lakshman ja Prashant Malik: Cassandra – A Decentralized
  Structured Storage System. *ACM SIGOPS Operating Systems Review* 44(2),
  2010.
- Burton H. Bloom: Space/Time Trade-offs in Hash Coding with Allowable
  Errors. *Communications of the ACM* 13(7), 1970.

Dokumentaatio:

- Redis-dokumentaatio: *Data types*, *Transactions*, *Scripting with
  Lua*, *Streams* ja *Persistence*, redis.io/docs. Valkey-dokumentaatio,
  valkey.io.
- MongoDB-käsikirja: *Data Modeling*, *Aggregation*, *Indexes*,
  *Schema Validation*, *Transactions*, *Read Concern* ja *Write
  Concern*, mongodb.com/docs/manual.
- Apache Cassandra -dokumentaatio: *Data Modeling*, *Dynamo* ja
  *Compaction*, cassandra.apache.org/doc.
- Neo4j: *Cypher Manual*, neo4j.com/docs. ISO/IEC 39075:2024 *GQL*.
- PostgreSQL 16 -dokumentaatio: *JSON Types* ja *WITH Queries*,
  postgresql.org/docs/16.
- Testcontainers for Python, testcontainers-python.readthedocs.io.
- Python-asiakkaat: redis-py, PyMongo, DataStax Python Driver for
  Apache Cassandra, Neo4j Python Driver ja psycopg 3.

Lisenssit:

- Server Side Public License (SSPL) v1, mongodb.com/legal/licensing.
- Redis-lisenssit: redis.io/legal.
