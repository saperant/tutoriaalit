---
title: Skaalautuvien järjestelmien suunnittelu
subtitle: Pikaopas · arviot · välimuistit · replikointi · jonot · saatavuus
---

# Suunnittelun vaiheet

| Vaihe | Tulos |
|-------|-------|
| vaatimukset | toiminnot, SLO:t persentiileinä, rajaukset |
| arviot | pyyntöä/s huipussa, tallennus, kaista, muisti |
| rajapinta ja tietomalli | API, taulut, avaimet, osioavain |
| arkkitehtuuri | osat ja tietovuot, kopiot ja vikaantumisalueet |
| pullonkaulat | mikä loppuu ensin 10-kertaisella kuormalla |

# Mittaluokat

| Suure | Kokoluokka |
|-------|------------|
| päivä | 86 400 s, noin 10^5^ |
| vuosi | noin 3 · 10^7^ s |
| kiertoviive konesalissa | 0,1–0,5 ms |
| Redis-haku | 0,2–1 ms |
| indeksoitu kantahaku | 1–5 ms |
| Eurooppa–USA | 80–100 ms |
| Redis, komentoja | 100 000+/s |
| PostgreSQL, lukuja | 10^4^–10^5^/s |

# Suorituskyky

- Littlen laki: kesken = saapumisnopeus · viipymä, $L = \lambda W$.
- Jonotus kasvaa kuin $1/(1-\rho)$; mitoita 60–70 % käyttöasteelle
  yhden palvelimen puuttuessa (N + 1).
- Hajautettu pyyntö: $P(\text{hidas}) = 1 - (1-p)^n$.
- Varmistettu pyyntö p95:n kohdalla leikkaa hännän, jos hitaus on
  satunnaista.

```{.python tiedosto="esimerkit/luku03/kapasiteetti.py" osa="erlang"}
```

# Kuormantasaus

| Algoritmi | Milloin |
|-----------|---------|
| kierto | samanlaiset palvelimet ja pyynnöt |
| painotettu kierto | tunnetut kapasiteettierot |
| vähiten kesken | eri nopeudet, eri raskaat pyynnöt |
| kaksi satunnaista | monta tasaajaa, ei jaettua tilaa |
| tiiviste, konsistentti | avainkohtainen tila palvelimella |

```{.text tiedosto="esimerkit/luku04/haproxy.cfg" osa="palvelu"}
```

# Hajautus ja osiointi

- Modulo: n → n + 1 siirtää noin n/(n+1) avaimista.
- Rengas tai rendezvous: siirtyy vain 1/(n+1).
- Virtuaalisolmuja 100+ solmua kohden.
- Kasvava avain + avainalueet = kuuma viimeinen osio.
- Kuuma avain: suolaus kirjoituksiin, välimuisti lukuihin.

# Välimuistit

| Strategia | Kirjoitus |
|-----------|-----------|
| cache-aside | kantaan, välimuistista poisto |
| write-through | molempiin samalla kertaa |
| write-back | välimuistiin, kantaan myöhemmin |

- Aina TTL; invalidointi päivityksessä.
- Vuokra estää vanhan arvon tallennuksen ja ryntäyksen.
- Negatiivinen välimuisti olemattomille avaimille.
- `allkeys-lru` välimuistille, `noeviction` tallennukselle.

```{.python tiedosto="esimerkit/jarjestelma/valimuisti.py" osa="rinnalla"}
```

# Replikointi

- Asynkroninen replika on jäljessä: lue omat kirjoituksesi.
- WAL-sijainti: `pg_current_wal_lsn()` ensisijaisella,
  `pg_last_wal_replay_lsn() >= sijainti` replikalla.
- `synchronous_commit = remote_apply`: tuore luku, hitaampi kirjoitus.
- Viive: `pg_stat_replication`, `pg_last_xact_replay_timestamp()`.
- Yhteysallas Littlen lailla; PgBouncer, kun palvelimia on paljon.

# Jonot

- Purkuaika = jono / (kapasiteetti − kuorma).
- Seuraa jonon pituutta ja vanhimman viestin ikää.
- Vähintään kerran + idempotentti kuluttaja; avain samaan atomiseen
  operaatioon kuin työ.
- Redis Streams: `XGROUP CREATE`, `XREADGROUP`, `XACK`, `XPENDING`,
  `XAUTOCLAIM`; kuolleet kolmannen yrityksen jälkeen.
- Järjestys säilyy vain osion sisällä.

# Ylikuorma

- Token bucket: nopeus + purske; jaettu raja Redisissä Lualla.
- Uudelleenyritys: budjetti (esim. 10 %), eksponentiaalinen viive,
  hajonta, yksi kerros.
- Määräaika pyynnön mukana; vanhentuneet pudotetaan käsittelemättä.
- Hylkää aikaisin, priorisoi, siisti heikentyminen, laipiot.

# Saatavuus

| SLO | katko / 30 pv |
|-----|---------------|
| 99 % | 7,2 h |
| 99,9 % | 43 min |
| 99,99 % | 4,3 min |

- Sarja: $A = \prod A_i$; rinnan: $1 - A = \prod (1 - A_i)$.
- Yhteiset viat kumoavat kahdennuksen: vyöhykkeet, versiot, asetukset.
- Kulumisnopeus 14,4: 2 % budjetista tunnissa.

# Havaittavuus

- RED palveluille, USE resursseille.
- Histogrammit, ei persentiilejä; lokeroraja SLO:n rajalle.
- Nimiöiden arvojoukko pieni; tunnukset lokeihin ja jälkiin.
- `traceparent: 00-<jälki>-<väli>-01` kaikkiin kutsuihin.
- Hälytä virhebudjetin kulumisesta, tutki resurssit.
