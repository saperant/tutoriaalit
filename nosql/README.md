# NoSQL-tietokannat

Avain-arvo-, dokumentti-, leveäsarake- ja graafitietokannat
käytännössä: Redis, MongoDB, Cassandra ja Neo4j oikeina palvelimina
Docker-konteissa, oma LSM-puu Pythonilla sekä vertailu PostgreSQLiin.
Lopuksi aikasarja- ja hakutietokannat ja valinnan perusteet. Valmis
dokumentti:
[nosql.pdf](https://saperant.github.io/tutoriaalit/materiaalit/nosql.pdf),
pikaopas:
[nosql-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/nosql-pikaopas.pdf).

Esitiedot: taidot *SQL ja relaatiotietokannat* ja *Kontit ja pilvi-infrastruktuuri*.

## Sisältö

1. Johdanto – ympäristö, testaus ja lisenssit
2. Milloin relaatiomalli ei riitä – normalisointi ja denormalisointi,
   kyselylähtöinen mallinnus, skeemattomuuden hinta
3. Redis: tietorakenteet muistissa – laskurit, hajautustaulut, listat,
   joukot, järjestetyt joukot, elinaika, putkitus
4. Redis: atomisuus, virrat ja pysyvyys – kadonnut päivitys, WATCH ja
   MULTI, Lua, virrat ja kuluttajaryhmät, RDB ja AOF
5. MongoDB: dokumenttimalli – haut ja päivitykset, upotus vai viittaus,
   indeksit ja explain
6. MongoDB: aggregaatio, skeema ja transaktiot – vertailu PostgreSQLin
   JSONB:hen
7. Cassandra – partitio- ja klusterointiavain, taulu kyselyä kohden,
   konsistenssitasot, hautakivet, kevyet transaktiot
8. LSM-puut – oma toteutus, Bloom-suodatin, kompaktointi,
   kirjoitusvahvistus
9. Graafitietokannat: Neo4j – Cypher, polut, suositukset, vertailu
   rekursiiviseen CTE:hen
10. Konsistenssi ja replikointi käytännössä – WAIT, write ja read
    concern, osiointi
11. Tietokannan valinta – aikasarja- ja hakutietokannat, vertailu
12. Lopuksi – nyrkkisäännöt ja lähteet

## Esimerkit

Hakemistossa `esimerkit/`. Tietokannat käynnistyvät Docker-konteissa
Testcontainersilla, joten Docker-palvelun on oltava käytettävissä:

```
make -C esimerkit                  # tarkistukset ja kaikki esimerkit
make -C esimerkit ESIMERKKI=luku07 # vain osa
cd esimerkit && python3 luku03/rakenteet.py
```

Kehityskontti: `.devcontainer/nosql` (käyttää isännän Dockeria).

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Vastuu ja lisenssit

Tutoriaali on lisensoitu CC BY-SA 4.0 -lisenssillä. Esimerkeissä
käytettävien tietokantojen lisenssit vaihtelevat (PostgreSQL License,
BSD-3, SSPL, Apache 2.0, GPLv3); ks. luku 1.
