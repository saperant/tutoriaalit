---
title: Integraatiotestaus ja Testcontainers
subtitle: Pikaopas · kontit · fixturet · eristys · kaksoiset · viat · CI
---

# Testcontainers

```{.python tiedosto="esimerkit/testiapu/kontit.py" osa="postgres"}
```

| Odotusstrategia | Valmis, kun |
|-----------------|-------------|
| `LogMessageWaitStrategy` | kontti kirjoittaa rivin |
| `PortWaitStrategy` | portti hyväksyy yhteyden |
| `HttpWaitStrategy` | polku vastaa tilakoodilla |
| `HealthcheckWaitStrategy` | HEALTHCHECK on terve |
| `ExecWaitStrategy` | komento kontissa onnistuu |

- Isäntä ja portti kontilta: `get_container_host_ip()`,
  `get_exposed_port(5432)`. Älä oleta portteja.
- Ei koskaan `sleep(5)`: odota valmiutta.
- Lukitse kuvat (`postgres:16-alpine`), hae peilistä.

# Fixturet

```{.python tiedosto="esimerkit/testit/conftest.py" osa="istunto"}
```

```{.python tiedosto="esimerkit/testit/conftest.py" osa="yhteys"}
```

| Laajuus | Käyttö |
|---------|--------|
| `session` | kontit, kuvan rakennus, migraatiot |
| `module` | tiedoston Docker-verkko |
| `function` | transaktio, tyhjä Redis |

`pytest --setup-show` näyttää alustukset ja purut.

# Eristys

| Tapa | Milloin |
|------|---------|
| transaktion peruutus | oletus; testi käyttää fixturen yhteyttä |
| `TRUNCATE` | koodi tekee omat transaktionsa |
| `CREATE DATABASE … TEMPLATE` | täysi eristys testille |
| satunnainen tunnus | pysyvät kirjoitukset, rinnakkaiset ajot |

Skeema samoilla migraatioilla kuin tuotannossa.

# Kaksoiset

| Nimi | Tekee |
|------|-------|
| tynkä | palauttaa annetun vastauksen |
| vakoilija | kirjaa kutsut |
| mock | tarkistaa odotetut kutsut |
| väärennös | toimiva kevyt toteutus |

Väärennös + sama sopimustestisarja kuin oikealle toteutukselle:
parametroitu fixture `params=["muisti", "postgres"]` ajaa jokaisen
testin kummallekin.

# Viat ja sopimukset

- Vikaproxy (Toxiproxy) riippuvuuden eteen samaan Docker-verkkoon.
- Testaa viive yli aikarajan ja katkos; palauta `finally`-lohkossa.
- `pool_pre_ping=True`: allas toipuu katkoksesta.
- Kuluttajan sopimus (JSON Schema, Pact) ajetaan tuottajan CI:ssä.
- Lisätty kenttä ei riko; poisto, nimen ja tyypin muutos rikkovat.

# CI

- GitHub Actions `ubuntu-24.04`: Docker valmiina.
- Esihae kuvat omassa vaiheessa; peili rajoituksia (429) vastaan.
- Ryuk siivoaa kontit, jos prosessi kaatuu.
- Isännän soketti = isännän pääkäyttäjän oikeudet.
- Epävakaa testi: odota ehtoa, eristä data, marginaali aikarajoihin.
