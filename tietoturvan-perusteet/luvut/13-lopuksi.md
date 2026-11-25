# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Kiellä oletuksena.** Pääsy, asetukset ja virhetilanteet johtavat
   kieltoon, ellei lupaa ole nimenomaisesti myönnetty.
2. **Kaikki luottamusrajan yli tuleva on hyökkääjän hallinnassa.**
   Jäsennä se reunalla tyypitetyksi arvoksi sallittujen arvojen
   perusteella.
3. **Erota data ja koodi.** Parametrisoidut kyselyt, argumenttilistat,
   automaattinen koodaus, ei koodia suorittavia sarjallistusmuotoja.
4. **Tarkista jokainen pääsy palvelimella**, myös objektin
   omistajuus.
5. **Vähimmät oikeudet** käyttäjille, palveluille, tunnuksille ja
   tiedostoille.
6. **Älä toteuta kryptografiaa itse.** Valitse työkalu sen takuiden
   mukaan: AEAD salaukseen, HMAC aitouteen, hidas suolattu tiiviste
   salasanoille, `secrets` satunnaisuuteen.
7. **Ei salaisuuksia koodiin, lokeihin eikä URL-osoitteisiin.**
   Vuotanut salaisuus vaihdetaan heti.
8. **Tee tarkistus ja toimenpide atomisesti.** Hyökkääjä lähettää
   pyynnöt samanaikaisesti.
9. **Mallinna uhat ennen toteutusta** ja ajattele hyökkääjän halvinta
   reittiä.
10. **Oleta, että jokin pettää.** Puolustus syvyyssuunnassa, lokit,
    hälytykset, testatut varmuuskopiot ja harjoiteltu toimintaohje.

## Jatkotaidot

| Kiinnostus | Seuraava taito |
|------------|----------------|
| salausmenetelmät ja protokollat | *Kryptografia* |
| web-sovellukset ja kirjautuminen | *Web-sovellusten tietoturva* |
| kehitysprosessi ja toimitusketju | *Tietoturva kehitystyössä* |
| laitteet ja laiteohjelmistot | *Sulautettujen järjestelmien tietoturva* |
| pilvi ja mikropalvelut | *Palveluarkkitehtuurin tietoturva* |
| konekielitason analyysi | *Takaisinmallinnus*, *Laiteohjelmiston takaisinmallinnus* |
| muistivirheiden löytäminen ja torjunta | *Haavoittuvuuksien analyysi ja torjunta* |
| verkot ja palomuurit | *Verkkoinfrastruktuuri* |

## Lähteet ja jatkolukeminen

### Kirjat ja artikkelit

- Ross Anderson: *Security Engineering*, 3. painos, Wiley 2020.
  Laaja ja käytännönläheinen; luvut luettavissa tekijän sivulla
  <https://www.cl.cam.ac.uk/~rja14/book.html>.
- Adam Shostack: *Threat Modeling: Designing for Security*, Wiley 2014.
- Jerome H. Saltzer ja Michael D. Schroeder: The Protection of
  Information in Computer Systems. *Proceedings of the IEEE* 63(9),
  1975.

### Ohjeet ja luokitukset

- OWASP Top 10 ja OWASP Cheat Sheet Series (CC BY-SA 4.0):
  <https://owasp.org/Top10/>,
  <https://cheatsheetseries.owasp.org/>.
- MITRE CWE (heikkousluokat) ja ATT&CK (hyökkäystekniikat):
  <https://cwe.mitre.org/>, <https://attack.mitre.org/>.
- FIRST: CVSS v4.0 ja v3.1, <https://www.first.org/cvss/>.
- NIST SP 800-63B, *Digital Identity Guidelines: Authentication and
  Lifecycle Management*, versio 4 (2025).
- NIST SP 800-61, *Incident Response Recommendations and
  Considerations for Cybersecurity Risk Management*, versio 3 (2025).
- NIST *Cybersecurity Framework* 2.0 (2024).
- RFC 4226 (HOTP), RFC 6238 (TOTP), RFC 7914 (scrypt), RFC 9116
  (security.txt).

### Säädökset ja viranomaiset

- Tietosuoja-asetus (EU) 2016/679, NIS2-direktiivi (EU) 2022/2555 ja
  kyberkestävyyssäädös (EU) 2024/2847: <https://eur-lex.europa.eu/>.
- Kyberturvallisuuslaki (124/2025) ja rikoslaki (39/1889) 38 luku:
  <https://www.finlex.fi/>.
- Traficomin Kyberturvallisuuskeskus: ohjeet, haavoittuvuuksien
  koordinointi ja poikkeamailmoitukset,
  <https://www.kyberturvallisuuskeskus.fi/>.
- Tietosuojavaltuutetun toimisto: <https://tietosuoja.fi/>.

### Työkalut

- ruff ja sen flake8-bandit-säännöt: <https://docs.astral.sh/ruff/>.
- Bandit, Semgrep ja CodeQL: staattinen analyysi.
- gitleaks ja trufflehog: salaisuuksien skannaus.
- Pythonin `secrets`-, `hmac`- ja `hashlib`-modulien dokumentaatio.

## Lisenssi

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0). Esimerkkiohjelmat saa
vapaasti käyttää omissa ohjelmissa.
