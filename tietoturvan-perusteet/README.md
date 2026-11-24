# Tietoturvan perusteet

Tiivis suomenkielinen johdatus tietoturvaan ohjelmistokehittäjälle:
käsitteet, uhkamallinnus, kryptografian oikea käyttö, todennus,
pääsynhallinta ja yleisimmät haavoittuvuusluokat haavoittuvana ja
korjattuna koodina. Esimerkit ovat Pythonia (vain standardikirjasto).
Valmiit dokumentit: [tietoturvan-perusteet.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tietoturvan-perusteet.pdf)
ja pikaopas
[tietoturvan-perusteet-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tietoturvan-perusteet-pikaopas.pdf).

## Sisältö

1. Johdanto – mitä tietoturva on, taitopuun jatkotaidot, laki ja etiikka
2. Käsitteet ja periaatteet – CIA, uhka, haavoittuvuus, riski,
   suunnitteluperiaatteet, turvallinen oletus, puolustus syvyyssuunnassa
3. Uhkamallinnus ja riskit – tietovuokaavio, luottamusrajat, STRIDE,
   hyökkäyspuut, riskimatriisi, CVSS
4. Kryptografia käyttäjän näkökulmasta – tiivisteet, HMAC, salaus ilman
   eheyttä, allekirjoitukset ja varmenteet, salasanojen tallennus
5. Todennus – tekijät ja MFA, salasanakäytännöt, arvausten
   rajoittaminen, TOTP, istunnot
6. Pääsynhallinta – DAC, MAC, RBAC, ABAC, tiedosto-oikeudet, IDOR
7. Injektiot – SQL- ja komentoinjektio, staattinen analyysi (ruff S)
8. Syöte, polut ja sarjallistus – polkujen ohitus, pickle,
   jäsentäminen reunalla
9. Kilpailutilanteet ja asetukset – TOCTOU, rinnakkaiset pyynnöt,
   turvalliset oletukset
10. Salaisuudet ja tunnistetietojen vuodot – skannaus, ajoympäristö,
    lokien peittäminen
11. Lokitus, havaitseminen ja poikkeamat – turvallisuuslokit,
    tiivisteketju, hyökkäysten tunnistus, poikkeaman käsittely
12. Lainsäädäntö ja etiikka – GDPR, NIS2 ja kyberturvallisuuslaki, CRA,
    ilmoitusten määräajat, vastuullinen ilmoittaminen
13. Lopuksi – nyrkkisäännöt, jatkotaidot, lähteet

## Rakentaminen

```text
make testaa   # rakenne, ruff (myös S-säännöt), mypy --strict ja ajot
make pdf      # tietoturvan-perusteet.pdf ja pikaopas
```

Esimerkit toimivat Python 3.12:lla ja uudemmilla ilman lisäpaketteja.
Tarkistukseen tarvitaan ruff ja mypy (kehityskontissa valmiina).

Lisenssi: CC BY-SA 4.0.
