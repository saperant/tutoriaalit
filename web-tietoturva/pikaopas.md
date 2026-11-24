---
title: Web-sovellusten tietoturva
subtitle: Pikaopas · hyökkäykset, torjunta, tunnistus ja valtuutus
---

# Hyökkäys ja torjunta

| Hyökkäys | Torjunta |
|----------|----------|
| SQL-injektio | parametrit; tunnisteet sallittujen luettelosta |
| NoSQL-operaattori | tyyppitarkistus reunalla (skeema) |
| Komentoinjektio | `execFile` ilman komentotulkkia, `--`, nimen muoto |
| SSRF | tarkista IP (ei teksti), estä yksityiset verkot, ei uudelleenohjauksia |
| XSS | koodaus kontekstin mukaan, `textContent`, tiukka CSP, Trusted Types |
| CSRF | `SameSite=Lax`, CSRF-tunniste, `Origin`/`Sec-Fetch-Site` |
| Clickjacking | `frame-ancestors 'none'`, `X-Frame-Options: DENY` |
| Istunnon kiinnitys | uusi tunniste kirjautuessa, ei tunnistetta osoitteessa |
| Tunnusten arvailu | sama viesti ja sama työ, nopeusrajoitus |
| Kirjautumis-CSRF (OIDC) | `state` |
| Kaapattu koodi | PKCE (S256) |
| JWT `alg: none`, avainsekaannus | kiinteä algoritmi ja avainjoukko |
| BOLA/IDOR | omistajuus kyselyssä, 404 |
| Massamääritys | syöteolio, sallitut kentät |
| Ladattu HTML | tyyppi sisällöstä, `attachment`, `sandbox`, oma verkkotunnus |
| Avoin uudelleenohjaus | vain suhteelliset polut, ei `//` eikä `/\` |

# Tiukka CSP

```{.typescript tiedosto="esimerkit/src/03-xss/xss.ts" osa="csp"}
```

# Istuntoeväste

```{.typescript tiedosto="esimerkit/src/05-istunnot/istunnot.ts" osa="eväste"}
```

| Attribuutti | Miksi |
|-------------|-------|
| `__Host-` | ei aliverkkotunnuksen asettama |
| `Secure` | vain HTTPS |
| `HttpOnly` | ei skriptin luettavissa |
| `SameSite=Lax` | ei toisen sivuston pyynnöissä |

# Salasanat (NIST SP 800-63B-4)

- Argon2id tai scrypt, suola ja parametrit tiivisteessä.
- Vähintään 15 merkkiä (8 MFA:n kanssa), vähintään 64 sallittava.
- Ei merkkiluokkia, ei määräaikaista vaihtoa, ei vihjeitä.
- Vuotaneet estetään (k-anonymiteetti).
- Rajoitus tiliä ja lähdettä kohden, ei pysyvää lukitusta.

# MFA

| Menetelmä | Kalastelu |
|-----------|-----------|
| Pääsyavain (WebAuthn) | kestää |
| TOTP, push, tekstiviesti | ei kestä |

WebAuthn-palvelin tarkistaa: tyyppi, haaste, alkuperä, rpId-tiiviste,
UV-lippu, allekirjoitus, laskuri.

# OAuth 2.0 / OIDC

1. `state`, `nonce`, `code_verifier` → `authorize` + `code_challenge`.
2. Paluu: `state` täsmää → `token` + `code_verifier`.
3. ID-token: allekirjoitus, `iss`, `aud`, `exp`, `nonce`.

Selainsovellus: BFF, tokenit palvelimella, `HttpOnly`-istunto.

# JWT-tarkistus

```{.typescript tiedosto="esimerkit/src/09-jwt/jwt.ts" osa="korjattu"}
```

# Valtuutus

| Taso | Tarkistus |
|------|-----------|
| Objekti | `WHERE id = ? AND omistaja = ?` |
| Toiminto | rooli reitillä, oletuksena kielletty |
| Ominaisuus | syöte- ja vastausoliot |

# Turvaotsakkeet

```{.typescript tiedosto="esimerkit/src/11-tiedostot/ohjaus.ts" osa="otsakkeet"}
```

# Testaus

| Taso | Työkalu |
|------|---------|
| Hyökkäystestit | `node:test`, Playwright |
| SAST | Semgrep, CodeQL |
| Riippuvuudet | `npm audit`, Dependabot |
| DAST | OWASP ZAP |
| Tarkistuslista | OWASP ASVS |
