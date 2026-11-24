---
title: Palveluarkkitehtuurin tietoturva
subtitle: Pikaopas · nollaluottamus · mTLS · tokenit · salaisuudet · IAM
---

# Nollaluottamus

- Verkon sijainti, IP ja otsake **eivät todista** mitään.
- Jokainen pyyntö: **todennus → valtuutus → kirjaus**.
- PDP päättää, PEP (palvelu, sivuvaunu, yhdyskäytävä) toteuttaa.
- Kysy jokaisesta palvelusta: *jos tämä murretaan, mihin pääsee?*

# Identiteetit ja mTLS

| Asia | Oikein |
|------|--------|
| identiteetti | `spiffe://alue/palvelu` SAN-kentässä |
| elinikä | tunteja, uusiminen automaattisesti |
| avain | syntyy työkuormassa, ei liiku |
| luottamus | vain oma nippu, ei julkiset CA:t |
| asiakas | `need`, ei `want` |
| valtuutus | sallitut identiteetit nimeltä |

```{.java tiedosto="esimerkit/luottamus/src/main/java/fi/tutoriaalit/palveluturva/luottamus/Identiteetti.java" osa="tunniste"}
```

**Varmentajan kierto:** 1. uusi juuri kaikkien nippuun → 2. uudet
varmenteet → 3. vanha juuri pois. Odota välissä yksi elinikä.

**Kumoaminen:** lyhyt elinikä + varmenteiden myönnön esto; välitön
eristys valtuutuksessa.

# Tokenit

Tarkista aina: **alg kiinnitetty · iss tunnettu · allekirjoitus · exp
· aud = minä**. Käyttäjän tokenia ei välitetä: **vaihda** (RFC 8693)
→ uusi `aud`, oikeuksien leikkaus, `act` = välittäjä, elinikä
minuutteja. Sido avaimeen: mTLS-sidottu (RFC 8705) tai DPoP.

# Salaisuudet

| Tilanne | Ratkaisu |
|---------|----------|
| palvelun salaisuudet | varastosta ajon aikana identiteetillä |
| arkaluonteinen data | kirjekuorisalaus + konteksti (AAD) |
| pääavaimen kierto | uusi versio, uudelleenkääre taustalla |
| poisto kaikkialta | kryptografinen tuhoaminen |
| tietokanta | dynaamiset tunnukset, vuokra ~1 h |
| jaettu API-avain | kaksoisavain siirtymäajalla |

```{.java tiedosto="esimerkit/salaisuudet/src/main/java/fi/tutoriaalit/palveluturva/salaisuudet/Kirjekuori.java" osa="kirjekuori"}
```

# Pääsynhallinta

1. Oletuksena estetty. 2. Nimenomainen esto voittaa. 3. Ehdot
rajaavat. Ei `*` toimintoihin eikä resursseihin. Organisaation
suojakaiteet: lokien ja avainten poisto, auditoinnin pysäytys.
Kavenna **käytön perusteella** (auditointiloki). Käytännöt
versionhallintaan, katselmointiin ja CI:hin (OPA/Rego, Cedar).

# Reuna ja segmentointi

Yhdyskäytävä: **siivoa sisäiset otsakkeet** → todenna → rajoita
identiteettiä kohti → validoi skeema. Palvelu todentaa silti itse.
NetworkPolicy: oletuksena esto, sallitut yhteydet nimeltä, myös
lähtevä liikenne.

# Auditointi ja poikkeamat

| Kirjaa | Älä kirjaa |
|--------|------------|
| todennus, estot, muutokset | tokenit, salasanat, avaimet |
| kenen tietoja luettiin | täydet korttinumerot |
| välittäjäketju (`act`) | pyyntöjen rungot sellaisenaan |
| korrelaatiotunniste | |

Loki: peitetty, rakenteinen, ketjutettu ja **allekirjoitetut
tarkistuspisteet muualle**.

**Rajaa järjestyksessä:** valtuutus (kumoamislista, esto) →
salaisuudet (kumoa, kierrä) → identiteetti (ei uusia varmenteita) →
verkko → työkuorma talteen ja puhtaasta kuvasta.
