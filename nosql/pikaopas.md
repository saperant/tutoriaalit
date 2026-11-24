---
title: NoSQL-tietokannat
subtitle: Pikaopas · Redis · MongoDB · Cassandra · Neo4j · LSM-puut
---

# Valinta

| Tarve | Valinta |
|-------|---------|
| moninaiset kyselyt, eheys, transaktiot | relaatio (PostgreSQL) |
| avaimella, muistin nopeus, laskurit, jonot | avain-arvo (Redis, Valkey) |
| vaihteleva rakenne, luetaan kokonaisuutena | dokumentti (MongoDB, JSONB) |
| valtava kirjoitusmäärä, monta palvelinta | leveäsarake (Cassandra) |
| monen askeleen polut, suositukset | graafi (Neo4j) |
| mittaukset aikaleimoineen | aikasarja (InfluxDB, TimescaleDB) |
| tekstihaku, relevanssi | haku (OpenSearch, Elasticsearch) |

# Redis

| Tarve | Komennot |
|-------|----------|
| laskuri | `INCR`, `INCRBY`, `DECR` |
| olio | `HSET`, `HGETALL`, `HINCRBY` |
| uusimmat N | `LPUSH` + `LTRIM` |
| joukot | `SADD`, `SINTER`, `SUNION` |
| tulostaulu | `ZADD`, `ZINCRBY`, `ZREVRANGE`, `ZREVRANK` |
| elinaika | `EXPIRE`, `SET ... PX`, `TTL` (-1 ei, -2 puuttuu) |
| optimistinen lukko | `WATCH` + `MULTI`/`EXEC` (hylätty: `None`) |
| atominen logiikka | Lua `EVAL`, `register_script` |
| jono | `XADD`, `XREADGROUP`, `XACK`, `XAUTOCLAIM` |
| replika | `WAIT n ms` |

Pysyvyys: ei mitään (välimuisti) · RDB tilannekuva · AOF `everysec`
(≤ 1 s) · AOF `always` (hidas). `maxmemory-policy`: välimuistille
`allkeys-lru`, datalle `noeviction`.

# MongoDB

```{.python tiedosto="esimerkit/luku05/dokumentit.py" osa="haku"}
```

| Operaattori | Merkitys |
|-------------|----------|
| `$eq $lt $gte $in` | vertailut |
| `"a.b"` | sisäkkäinen kenttä |
| `$set $inc $push` | päivitys paikallaan |
| `upsert=True` | lisää, jos puuttuu |
| `$match $unwind $group $sort $project $lookup` | aggregaatio |

- Upota pientä ja yhdessä luettua, viittaa suureen ja jaettuun.
- ESR: indeksiin yhtäsuuruus, järjestys, väli.
- `explain()`: `COLLSCAN` = ei indeksiä; luettu paljon yli palautetun = huono.
- Transaktiot vain replikajoukossa; `with_transaction` yrittää uudelleen.
- `w="majority"` ei katoa; `WriteConcernError` ≠ peruttu.

# Cassandra

```{.python tiedosto="esimerkit/luku07/taulut.py" osa="taulu"}
```

- `((partitio), klusterointi...)`: partitio jakaa, klusterointi järjestää.
- Yksi taulu kyselyä kohden; ei `ALLOW FILTERING`.
- Rajaa partitio: `((anturi, kuukausi), aika)`.
- Taso `QUORUM` + `QUORUM` = uusin arvo; `ONE` nopea, voi olla vanha.
- Poisto ja TTL = hautakivi, `gc_grace_seconds` 10 vrk.
- `IF NOT EXISTS` = LWT (Paxos), harvoin.

# Neo4j ja Cypher

```{.python tiedosto="esimerkit/luku09/graafi.py" osa="suositus"}
```

| Cypher | Merkitys |
|--------|----------|
| `(k:Kayttaja {nimi: $n})` | solmu, nimiö, ominaisuus |
| `-[:SEURAA]->` | suhde ja suunta |
| `-[:SEURAA*1..3]->` | 1–3 askelta |
| `shortestPath(...)` | lyhin polku |
| `MERGE` | luo, jos puuttuu |

# LSM-puu

| Vaihe | Toiminta |
|-------|----------|
| kirjoitus | loki + memtable; täynnä → SSTable |
| luku | memtable, sitten SSTablet uusimmasta |
| Bloom | "ei varmasti" ohittaa tiedoston |
| poisto | hautakivi |
| kompaktointi | yhdistää, pudottaa vanhat ja hautakivet |

Kirjoitusvahvistus = levylle kirjoitettu / sovelluksen kirjoittama.
