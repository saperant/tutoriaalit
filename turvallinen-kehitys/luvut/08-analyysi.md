# Analyysi CI:ssä

Katselmoija näkee pull requestissa satoja rivejä ja väsyy. Koneellinen
analyysi lukee jokaisen rivin joka kerta samalla tarkkuudella. Se ei
korvaa ihmistä, mutta se vapauttaa katselmoinnin asioihin, joita kone ei
ymmärrä: suunnitteluun, logiikkaan ja valtuutukseen.

## Analyysin lajit

| Laji | Mitä se tutkii | Työkaluja | Milloin |
|------|----------------|-----------|---------|
| SAST (staattinen) | lähdekoodia ajamatta: vaaralliset kutsut, tietovirta syötteestä vaaralliseen kohtaan | ruff/Bandit, Semgrep, CodeQL, SpotBugs | joka muutos |
| salaisuusskannaus | koodia ja historiaa: avaimet ja salasanat | gitleaks, trufflehog | joka muutos |
| riippuvuusskannaus (SCA) | riippuvuuksia: tunnetut haavoittuvuudet, lisenssit | osv-scanner, Dependabot, Trivy | joka muutos ja päivittäin |
| kontti- ja IaC-skannaus | kuvia ja infrakoodia: haavoittuvat paketit, väärät asetukset | Trivy, Grype, Checkov | joka muutos |
| DAST (dynaaminen) | käynnissä olevaa sovellusta ulkoapäin | OWASP ZAP | testiympäristöön, ajastettuna |
| fuzzaus | ohjelmaa satunnaisella ja mutatoidulla syötteellä | libFuzzer, Atheris, Jazzer | jatkuvasti (OSS-Fuzz) |

Staattinen analyysi löytää virheluokat, jotka näkyvät koodista:
merkkijonoista koottu SQL, `shell=True`, heikot tiivistefunktiot,
tarkistamaton purku. Dynaaminen analyysi löytää ajonaikaiset ongelmat,
kuten puuttuvat tietoturvaotsakkeet ja virheelliset uudelleenohjaukset.
Kumpikaan ei löydä puuttuvaa valtuutustarkistusta luotettavasti, koska
työkalu ei tiedä, kenen kuuluu nähdä mitäkin.

## Tietoturvasäännöt linterissä

Halvin SAST on linteri, joka on jo käytössä. Tämän tutoriaalin
Python-esimerkit tarkistetaan ruffin `S`-säännöillä (flake8-bandit), ja
alla oleva esimerkki on tarkoituksella kirjoitettu niin, että tarkistus
hylkää sen. Tar-arkiston purku ilman suodatinta antaa arkiston
polkujen (`../`) kirjoittaa minne tahansa:

```{.python tiedosto="esimerkit/08-sast.ei-kaanny.py" osa="pura"}
```

```text
S202 Uses of `tarfile.extractall()`
```

Korjattu versio, jossa merkitty rivi on poistettu, käyttää Pythonin
purkusuodatinta (PEP 706), joka hylkää kohdehakemiston ulkopuolelle
osoittavat polut:

```{.tuloste tiedosto="esimerkit/08-sast.odotettu"}
```

Sama periaate toimii kaikissa kielissä: ESLintin tietoturvaliitännäiset,
SpotBugsin FindSecBugs, `go vet` ja gosec, Clippy ja `cargo audit`.
Linteri on nopea, ajetaan editorissa ja commit-koukussa, ja sen säännöt
ovat koodina repositoriossa (`pyproject.toml`).

Raskaammat työkalut, kuten CodeQL ja Semgrep, seuraavat tietovirtaa:
ne huomaavat, että HTTP-pyynnön parametri päätyy SQL-lauseeseen kolmen
funktion kautta. Ne ajetaan CI:ssä, ja tulokset näytetään pull
requestissa koodirivin kohdalla.

## Väärät hälytykset ja perustaso

Analyysityökalu, joka hälyttää jatkuvasti turhasta, opettaa tiimin
ohittamaan hälytykset. Löydösten hallinta on siksi yhtä tärkeää kuin
niiden löytäminen:

- **Rivikohtainen poikkeus perusteluineen.** `# noqa: S324  md5 vain
  välimuistiavaimena` on katselmoitavissa ja haettavissa. Pelkkä
  `# noqa` ilman syytä ei kelpaa.
- **Perustaso vanhalle koodille.** Kun analyysi otetaan käyttöön
  olemassa olevaan koodiin, nykyiset löydökset kirjataan perustasoon,
  ja CI pysäyttää vain uudet. Ilman perustasoa käyttöönotto jää
  tekemättä, koska satoja löydöksiä ei korjata kerralla.

```{.python tiedosto="esimerkit/08-perustaso.py" osa="arvio"}
```

```{.tuloste tiedosto="esimerkit/08-perustaso.odotettu"}
```

Löydös tunnistetaan sormenjäljestä, joka ei riipu rivinumerosta: muuten
jokainen yläpuolelle lisätty rivi tekisi vanhasta löydöksestä uuden.
Jokaisella poikkeuksella on vanhenemispäivä, joten "korjataan myöhemmin"
ei muutu pysyväksi. Korjatut löydökset poistetaan perustasosta, jotta
se kutistuu ajan myötä. Samaa periaatetta käyttävät esimerkiksi
detect-secretsin `.secrets.baseline` ja SARIF-muotoisten tulosten
vertailu koodialustoilla.

## Dynaaminen analyysi periaatteena

DAST-työkalu, kuten OWASP ZAP, käyttää sovellusta kuten hyökkääjä:
se indeksoi sivut ja rajapinnat ja lähettää niihin haitallisia syötteitä.
Käytännössä:

- Ajo testiympäristöä vastaan, ei tuotantoa: aktiivinen skannaus luo
  dataa ja voi kaataa palveluja.
- Perusskannaus (passiivinen, vain havainnointi) sopii jokaiseen
  julkaisuun; aktiivinen skannaus ajastettuna.
- Rajapinnoille kuvaus (OpenAPI) skannerin syötteeksi, ja tunnukset
  testikäyttäjälle, jotta kirjautumisen takana olevat osat tulevat
  tutkituiksi.

Taito *Web-sovellusten tietoturva* käsittelee web-hyökkäykset, joita
DAST etsii.

## Käytännössä

- **Linterin tietoturvasäännöt ensin.** Halvin ja nopein tarkistus, joka
  toimii editorissa, koukussa ja CI:ssä.
- **CI on portti, ei neuvoja.** Tarkistus, jonka voi ohittaa, ohitetaan.
  Pakolliset tarkistukset haarasuojauksessa.
- **Perustaso ja vanhenevat poikkeukset.** Uudet löydökset estävät,
  vanhat korjataan suunnitellusti.
- **Hälytysten laatu ennen määrää.** Säännöt, jotka tuottavat lähinnä
  vääriä hälytyksiä, kytketään pois perustellusti. Työkalu, jota
  kukaan ei usko, on haitallinen.
- **Tulokset koodin kohdalle.** SARIF-muodossa tulokset näkyvät pull
  requestissa rivin vieressä, missä ne korjataan.

## Itsearviointi

- Osaat erottaa SAST:n, SCA:n, DAST:n ja fuzzauksen ja valita
  oikean työkalun ja ajankohdan.
- Osaat ottaa linterin tietoturvasäännöt käyttöön ja kirjoittaa
  perustellun poikkeuksen.
- Osaat hallita vanhan koodin löydöksiä perustason ja vanhenevien
  poikkeusten avulla.
- Osaat kertoa, miten DAST ajetaan turvallisesti.
