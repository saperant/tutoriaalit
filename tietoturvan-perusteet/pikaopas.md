---
title: Tietoturvan perusteet
subtitle: Pikaopas kehittäjälle · uhat, virheluokat ja korjaukset · Python 3.12
---

# Käsitteet

| Termi | Merkitys |
|-------|----------|
| CIA | luottamuksellisuus, eheys, saatavuus (+ aitous, kiistämättömyys) |
| uhka | mahdollinen haitallinen tapahtuma ja sen aiheuttaja |
| haavoittuvuus | heikkous, jonka kautta uhka toteutuu |
| riski | todennäköisyys × vaikutus |
| hyökkäyspinta | kaikki kohdat, joista hyökkääjä voi vaikuttaa |
| luottamusraja | eri luottamustasojen raja; ylittävä data on syötettä |

Periaatteet: vähimmät oikeudet, turvallinen oletus, täydellinen
välitys, yksinkertaisuus, avoin suunnittelu, oikeuksien erottelu,
puolustus syvyyssuunnassa.

# Uhkamallinnus

Neljä kysymystä: mitä rakennamme, mikä voi mennä pieleen, mitä
teemme, riittikö se. Tietovuokaavio → luottamusrajat → STRIDE.

| STRIDE | Rikkoo | Torjunta |
|--------|--------|----------|
| Spoofing | aitous | todennus |
| Tampering | eheys | MAC, allekirjoitus, pääsynhallinta |
| Repudiation | kiistämättömyys | lokit, allekirjoitus |
| Information disclosure | luottamuksellisuus | salaus, pääsynhallinta |
| Denial of service | saatavuus | rajat, kapasiteetti |
| Elevation of privilege | valtuutus | vähimmät oikeudet |

Riskin käsittely: pienennä, vältä, siirrä tai hyväksy (omistaja
päättää). Hyökkääjä valitsee halvimman reitin.

# Kryptografian työkalut

| Tarve | Työkalu | Ei |
|-------|---------|-----|
| eheys (luotettu tiiviste) | SHA-256 | MD5, SHA-1 |
| aitous jaetulla avaimella | HMAC-SHA-256 | pelkkä tiiviste |
| salassapito | AEAD: AES-GCM, ChaCha20-Poly1305 | salaus ilman todennusta |
| kiistämättömyys | allekirjoitus (Ed25519, ECDSA) | MAC |
| salasanat | Argon2id, scrypt, bcrypt + suola | SHA-256, salaus |
| satunnaisuus | `secrets` | `random` |

```{.python tiedosto="esimerkit/pikaopas.py" osa="satunnaisuus"}
```

```{.python tiedosto="esimerkit/pikaopas.py" osa="vertailu"}
```

```{.python tiedosto="esimerkit/pikaopas.py" osa="salasana"}
```

# Todennus ja istunnot

- MFA: pääsyavain/FIDO2 > TOTP > push numerotäsmäytyksellä > tekstiviesti.
- Salasana: yksin ≥ 15 merkkiä, MFA:n osana ≥ 8; ei merkkiluokkavaatimuksia,
  ei määräaikaista vaihtoa, vuotaneiden esto (NIST SP 800-63B).
- Rajoita: kasvava viive tilikohtaisesti + osoitekohtainen raja; ei
  pysyvää lukitusta.
- Istuntotunniste: `secrets.token_urlsafe(32)`, vanhenee (tyhjäkäynti ja
  enimmäisaika), vaihtuu kirjautuessa, mitätöidään palvelimella.
- Samat virheilmoitukset: "väärä tunnus tai salasana".

# Pääsynhallinta

| Malli | Päättää |
|-------|---------|
| DAC | omistaja (Unix-oikeudet) |
| MAC | järjestelmän politiikka |
| RBAC | roolit → oikeudet (toimenpiteinä: `lasku:hyvita`) |
| ABAC | sääntö subjektin, objektin ja ympäristön ominaisuuksista |

Jokainen pyyntö palvelimella; oletus kielto; omistajuus kyselyyn:
`WHERE id = ? AND asiakas = ?`; sama vastaus olemattomalle ja
kielletylle (IDOR). Tiedostot `0o600`, palvelu omalla käyttäjällä.

# Virheluokat ja korjaukset

| Luokka | Korjaus |
|--------|---------|
| SQL-injektio | parametrisoitu kysely |
| komentoinjektio | argumenttilista, ei `shell=True` |
| polkujen ohitus | `resolve()` ja sitten `is_relative_to()` |
| turvaton deserialisointi | JSON + rakenteen tarkistus, ei `pickle` |
| vahvistamaton syöte | jäsennä reunalla: koko, tyyppi, alue, sallitut kentät |
| TOCTOU | atominen operaatio: `O_EXCL`, ehdollinen `UPDATE` |
| oletusasetukset | turvalliset oletukset + käynnistystarkastus |
| tunnistetietojen vuodot | ei koodiin/lokeihin/URL:iin, vaihda vuotanut |

```{.python tiedosto="esimerkit/pikaopas.py" osa="sql"}
```

```{.python tiedosto="esimerkit/pikaopas.py" osa="komento"}
```

```{.python tiedosto="esimerkit/pikaopas.py" osa="polku"}
```

# Staattinen analyysi (ruff, säännöt S)

| Sääntö | Löytää |
|--------|--------|
| S602/S603 | `shell=True` / aliprosessi |
| S608 | SQL merkkijonoista |
| S301 | `pickle`-lataus |
| S105–S107 | salasana koodissa |
| S324 | MD5, SHA-1 |
| S104 | kuuntelu kaikissa verkoissa |

Tarkoituksellinen poikkeus rivikohtaisesti ja perusteltuna:
`# noqa: S603 – argumenttilista, ei syötettä komentotulkille`.

# Havaitseminen ja poikkeamat

- Lokita: kirjautumiset, kiellot, oikeusmuutokset, viennit, asetukset.
  UTC, rakenteisesti, ei salaisuuksia, keskitetysti.
- Hälytä: onnistuminen virheiden jälkeen, salasanaruiskutus (monta tiliä
  yhdestä osoitteesta), poikkeava vienti.
- Poikkeama: valmistautuminen → havaitseminen → rajaaminen (eristä, älä
  sammuta) → poisto ja palautus → jälkitarkastelu.

| Ilmoitus | Määräaika tiedosta |
|----------|--------------------|
| NIS2 varhainen varoitus | 24 h |
| NIS2 poikkeamailmoitus | 72 h |
| GDPR tietosuojavaltuutetulle | 72 h |
| CRA hyödynnetty haavoittuvuus | 24 h / 72 h |
| NIS2 loppuraportti | kuukausi ilmoituksesta |

Löysitkö haavoittuvuuden? `security.txt` → valmistaja → sovittu
julkistus; tarvittaessa Kyberturvallisuuskeskus. Lupa ensin.
