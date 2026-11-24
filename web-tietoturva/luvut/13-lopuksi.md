# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Kaikki syöte on hyökkääjän.** Osoite, runko, otsakkeet,
   evästeet, tiedostot ja toisen palvelun vastaukset.
2. **Erota koodi ja data rakenteellisesti:** parametrit, koodaus
   kontekstin mukaan, ohjelmakutsu ilman komentotulkkia.
3. **Jäsennä reunalla.** Tarkistettu tyyppi kerran, sitten luottamus
   sisällä.
4. **Syvyyspuolustus:** koodaus + CSP, SameSite + tunniste + Origin,
   valtuutus kyselyssä + politiikassa.
5. **Istunto palvelimella**, satunnainen tunniste `__Host-`-evästeessä,
   kierto kirjautuessa.
6. **Salasanat hitaalla tiivisteellä**, pituus ennen monimutkaisuutta,
   vuotaneet estettynä, arvailu rajoitettuna.
7. **Pääsyavaimet** ensisijaiseksi toiseksi tekijäksi; palautus yhtä
   vahvaksi kuin kirjautuminen.
8. **OAuth: koodivirta + PKCE + `state` + `nonce`**, paluuosoitteet
   täsmälleen, tokenit palvelimelle (BFF).
9. **JWT:n tarkistus kiinteillä odotuksilla** kirjastolla; lyhyt elinaika.
10. **Valtuutus oletuksena kielteinen**, objektin, toiminnon ja kentän
    tasolla, politiikka yhdessä paikassa.
11. **Turvaotsakkeet keskitetysti**, myös virhesivuille.
12. **Jokainen haavoittuvuus testiksi.**

## Mallit

| Malli | Ongelma | Luku |
|-------|---------|------|
| Parametrisoitu kysely | injektio | 2 |
| Sallittujen luettelo | tunnisteet, tyypit, uudelleenohjaukset | 2, 11 |
| Jäsennys reunalla | tyypitön syöte | 2 |
| Tiukka CSP (nonce + strict-dynamic) | XSS | 3 |
| Synchronizer token, Origin-tarkistus | CSRF | 4 |
| Istunnon kierto | kiinnitys | 5 |
| Merkkiämpäri | arvailu | 6 |
| k-anonymiteetti | vuotaneiden salasanojen tarkistus | 6 |
| Haaste–vastaus julkisella avaimella | kalastelu | 7 |
| PKCE | kaapattu koodi | 8 |
| BFF | tokenit selaimessa | 8 |
| Kiinteät tarkistusodotukset | JWT-väärennökset | 9 |
| Keskitetty politiikka | valtuutusvirheet | 10 |
| Erillinen sisältöverkkotunnus | ladatut tiedostot | 11 |
| Hyökkäystesti | regressiot | 12 |

## Mihin seuraavaksi

- **Tietoturva kehitystyössä:** salaisuudet, toimitusketju ja
  tietoturva osana kehitysprosessia ja CI:tä.
- **Palveluarkkitehtuurin tietoturva:** palvelujen välinen
  tunnistus (mTLS), salaisuudet tuotannossa ja nollaluottamus.
- **Kryptografia:** algoritmit, joiden päälle salasanatiivisteet,
  TLS ja allekirjoitukset rakentuvat.
- **Taustapalvelut:** Spring Securityn toteutus samoille periaatteille.

## Lähteet ja jatkolukeminen

- OWASP Top 10 ja OWASP API Security Top 10. <https://owasp.org/Top10/>,
  <https://owasp.org/API-Security/>
- OWASP Cheat Sheet Series: XSS, CSRF, Session Management, Password
  Storage, Authentication, File Upload, OAuth 2.0.
  <https://cheatsheetseries.owasp.org/>
- OWASP Application Security Verification Standard (ASVS) 5.0.
  Tarkistuslista vaatimuksiksi ja testaukseen.
- NIST SP 800-63B-4: *Digital Identity Guidelines, Authentication and
  Authenticator Management* (2025).
- RFC 6238 (TOTP), RFC 7519 (JWT), RFC 7636 (PKCE), RFC 9700 (*OAuth
  2.0 Security Best Current Practice*), RFC 6265bis (evästeet).
- W3C: *Web Authentication Level 3*, *Content Security Policy Level 3*,
  *Trusted Types*.
- OpenID Foundation: *OpenID Connect Core 1.0*.
- IETF OAuth WG: *OAuth 2.0 for Browser-Based Applications* (BFF-malli).
- MDN Web Docs: HTTP-otsakkeet ja evästeet.
  <https://developer.mozilla.org/>
- web.dev: *Mitigate cross-site scripting with a strict CSP*.
- PortSwigger Web Security Academy: maksuttomat harjoitukset
  jokaisesta tämän tutoriaalin hyökkäyksestä.
  <https://portswigger.net/web-security>

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0).
