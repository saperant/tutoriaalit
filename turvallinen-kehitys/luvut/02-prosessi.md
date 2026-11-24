# Turvallinen kehitysprosessi

Turvallinen kehitysprosessi (*secure software development life cycle*,
SSDLC) tarkoittaa, että tietoturva on mukana jokaisessa vaiheessa:
vaatimuksissa, suunnittelussa, toteutuksessa, testauksessa, julkaisussa
ja ylläpidossa. Ajatus ei ole uusi, mutta sen toteutus on muuttunut:
raskaan dokumentaation sijaan tarkistukset ovat koodia ja ajetaan
jokaisen muutoksen yhteydessä.

## Viitekehykset periaatteina

Kaksi laajasti käytettyä viitekehystä jäsentää, mitä kypsä prosessi
sisältää. Niitä ei tarvitse ottaa käyttöön kokonaan; ne toimivat
tarkistuslistana sille, mitä tiimiltä puuttuu.

| Viitekehys | Mitä se on | Hyöty tiimille |
|------------|-----------|----------------|
| OWASP SAMM | kypsyysmalli: 15 käytäntöä viidessä toiminnossa, kullakin kolme tasoa | nykytilan arvio ja seuraavan askeleen valinta |
| NIST SSDF (SP 800-218) | luettelo tehtävistä: valmistele organisaatio, suojaa ohjelmisto, tuota turvallista koodia, reagoi haavoittuvuuksiin | yhteinen kieli asiakkaiden ja sääntelyn kanssa |

SSDF on erityisen käyttökelpoinen, koska EU:n kyberkestävyyssäädös
(CRA) ja monet hankintavaatimukset viittaavat samoihin asioihin:
haavoittuvuuksien käsittelyprosessi, ohjelmiston osaluettelo (luku
*SBOM ja haavoittuvuustiedot*), turvalliset oletusasetukset ja
tietoturvapäivitykset koko tuen ajan.

## Uhkamallinnus tiimin rutiinina

Uhkamallinnuksen menetelmät (STRIDE, tietovuokaaviot, hyökkäyspuut)
opetetaan taidossa *Tietoturvan perusteet*. Prosessin kannalta
olennaista on, **milloin** malli tehdään ja päivitetään:

- Uuden ominaisuuden suunnittelussa, kun muutos ylittää luottamusrajan:
  uusi ulkoinen rajapinta, uusi tietovarasto, uusi kolmas osapuoli.
- Kun todennusta, valtuutusta, salausta tai henkilötietojen käsittelyä
  muutetaan.
- Tietoturvapoikkeaman jälkeen: miksi mallissa ei ollut tätä uhkaa?

Kevyt käytäntö toimii parhaiten: tietovuokaavio ja uhkalista ovat
repositoriossa tekstinä (esimerkiksi `docs/uhkamalli.md`), ja niitä
muokataan pull requestissa samaan tapaan kuin koodia. Näin malli pysyy
ajan tasalla ja muutoshistoria on näkyvissä.

## Tietoturvavaatimukset ja valmiin määritelmä

Vaatimus "järjestelmän on oltava turvallinen" ei ohjaa työtä. Toimiva
vaatimus on tarkistettava. OWASP ASVS (*Application Security
Verification Standard*) on hyvä lähde valmiille vaatimuksille, kuten
"salasanat tallennetaan hitaalla tiivistefunktiolla" tai "jokainen
rajapinta tarkistaa valtuutuksen palvelimella".

Tiimin **valmiin määritelmään** (*definition of done*) kirjataan
tietoturvaehdot, jotka koskevat jokaista muutosta. Kun ehdot ovat
koodia, niiden noudattaminen ei riipu katselmoijan muistista:

```{.python tiedosto="esimerkit/02-valmis.py" osa="muutos"}
```

```{.python tiedosto="esimerkit/02-valmis.py" osa="saannot"}
```

```{.tuloste tiedosto="esimerkit/02-valmis.odotettu"}
```

Oikeassa projektissa samat säännöt toteutetaan CI:n tarkistuksina ja
haarasuojauksina: koodinomistajat vaativat tietoturvatiimin
hyväksynnän todennuskoodiin (luku *Katselmointi ja julkaisu*), CI estää
yhdistämisen ilman testejä, ja riippuvuustiedoston muutos käynnistää
riippuvuusarvion. Pull requestin pohja (`.github/pull_request_template.md`)
muistuttaa asioista, joita ei voi tarkistaa koneellisesti, kuten
uhkamallin päivityksestä.

## Tietoturva ylläpidossa

Prosessi ei pääty julkaisuun. Ylläpidon tietoturvatehtäviä ovat:

- **Haavoittuvuuksien vastaanotto.** Julkinen yhteystieto
  (`SECURITY.md`, `security.txt`) ja sovittu käsittelyaika. Taito
  *Tietoturvan perusteet* käsittelee koordinoidun julkistamisen.
- **Riippuvuuksien päivitys.** Automaattiset päivityspyynnöt
  (Dependabot, Renovate) ja testit, jotka tekevät päivityksestä
  turvallisen (luku *Riippuvuudet ja toimitusketju*).
- **Tunnusten ja avainten kierto** (luku *Salaisuuksien hallinta*).
- **Poikkeamista oppiminen.** Syyllistämätön jälkikatsaus (*blameless
  postmortem*): mikä prosessissa salli virheen, ja mikä koneellinen
  tarkistus estää sen ensi kerralla.

## Käytännössä

- **Aloita kypsyysarviosta, älä työkaluista.** SAMM:n nopea arvio
  kertoo, onko suurin puute vaatimuksissa, katselmoinnissa vai
  julkaisussa. Työkalu oikeaan kohtaan tuottaa enemmän kuin kymmenen
  väärään.
- **Siirrä tarkistukset vasemmalle, mutta älä vain vasemmalle.**
  Commit-koukku antaa nopeimman palautteen, CI on varmin portti, ja
  tuotannon valvonta huomaa sen, mikä pääsi läpi. Tarvitaan kaikki
  kolme.
- **Kirjoita säännöt koodiksi.** Valmiin määritelmän ehdot, jotka
  voidaan tarkistaa koneellisesti, tarkistetaan koneellisesti. Muistilista
  jää ihmisille vain siihen, mikä vaatii harkintaa.
- **Uhkamalli on elävä tiedosto.** Repositoriossa, pull requesteissa,
  päivitetään muutosten yhteydessä. Kerran tehty ja kansioon unohdettu
  malli ei suojaa mitään.
- **Mittaa prosessia, älä löydösten määrää.** Hyviä mittareita ovat
  aika haavoittuvuuden ilmoituksesta korjaukseen ja kriittisten
  riippuvuuspäivitysten viive. Löydösten määrä kasvaa, kun työkalut
  paranevat, eikä se kerro turvallisuudesta.

## Itsearviointi

- Osaat selittää, mitä SSDLC tarkoittaa ja miten OWASP SAMM ja NIST
  SSDF jäsentävät sitä.
- Osaat kertoa, milloin uhkamalli tehdään tai päivitetään, ja pitää sen
  repositoriossa koodin rinnalla.
- Osaat muuttaa tietoturvavaatimukset tarkistettaviksi valmiin
  määritelmän säännöiksi.
- Osaat luetella ylläpidon tietoturvatehtävät julkaisun jälkeen.
