# Salaisuuksien hallinta

Salaisuuksia ovat salasanat, API-avaimet, tietokantatunnukset,
allekirjoitusavaimet ja tokenit. Taito *Tietoturvan perusteet* näytti,
miksi ne eivät kuulu koodiin ja miten sovellus lukee ne ympäristöstä.
Tämä luku käsittelee tiimin käytäntöjä: miten vuodot estetään ennalta,
missä salaisuudet säilytetään, miten niitä kierretään ja mitä tehdään,
kun vuoto silti tapahtuu.

## Mistä salaisuudet vuotavat

| Vuotokanava | Esimerkki | Torjunta |
|-------------|-----------|----------|
| versionhallinta | `.env` commitoitu vahingossa | koukku, CI-skannaus, `.gitignore` |
| CI-lokit | `set -x` tulostaa muuttujan | lokien peitto, ei `set -x` salaisuuksien kanssa |
| kontin kuva | `COPY .env` tai `ARG TOKEN` jää kerrokseen | salaisuudet ajossa, ei kuvassa |
| keskustelut ja tiketit | avain liitetään chattiin "nopeasti" | salaisuusvaraston jakolinkit |
| kehittäjän kone | avaimet kotihakemistossa selväkielisinä | lyhytikäiset tunnukset, levyn salaus |
| asiakkaalle toimitettu koodi | mobiilisovelluksen sisään käännetty avain | avain ei kuulu asiakkaalle lainkaan |

Viimeinen rivi on tärkeä: selaimeen, mobiilisovellukseen tai laitteeseen
toimitettu salaisuus ei ole salaisuus. Sen voi aina kaivaa esiin.
Asiakaspuolen sovellus todentaa käyttäjän, ja palvelin tekee
oikeuksia vaativat kutsut omilla tunnuksillaan.

## Salaisuusskanneri

Salaisuuksien skannaus perustuu kolmeen keinoon: tunnettuihin muotoihin
(palveluntarjoajien avaimilla on tunnistettava etuliite), sijoituksiin
(`password = "..."`) ja satunnaisuuteen eli entropiaan. Periaate on
tuttu taidosta *Tietoturvan perusteet*; tässä skanneri saa rinnalleen
sijoitussäännön ja kytketään seuraavassa osiossa commit-koukkuun:

```{.python tiedosto="esimerkit/03-skanneri.py" osa="saannot"}
```

```{.python tiedosto="esimerkit/03-skanneri.py" osa="skannaa"}
```

```{.tuloste tiedosto="esimerkit/03-skanneri.odotettu"}
```

Tulos näyttää skannauksen vahvuudet ja rajat:

- **Tunnettu muoto** löytyy varmasti (AWS-avain, yksityinen avain).
- **Sijoitus** löytyy, kun arvo näyttää satunnaiselta. Heikko
  salasana `"salasana"` jää löytymättä, koska sen entropia on pieni: se
  ei näytä salaisuudelta, vaikka on sellainen.
- **Entropia** erottaa satunnaisen avaimen tavallisesta tekstistä, mutta
  base64-koodattu tavallinen teksti jää rajan alle. Raja on aina
  kompromissi väärien hälytysten ja ohitettujen vuotojen välillä.
- **Poikkeus** (`salaisuus-sallittu: syy`) on rivillä näkyvissä, joten
  katselmoija näkee sen ja perustelun.

Tuotannossa käytetään valmiita skannereita, kuten **gitleaks** ja
**trufflehog**. Niissä on satoja palvelukohtaisia sääntöjä, ja
trufflehog osaa lisäksi kokeilla, onko löydetty avain voimassa.
Koodialustat (GitHub, GitLab) skannaavat myös itse ja voivat estää
pushin (*push protection*) sekä ilmoittaa vuotaneesta avaimesta
palveluntarjoajalle.

## Commit-koukku: nopein palaute

Skannaus kannattaa tehdä jo ennen kuin salaisuus päätyy historiaan.
Git ajaa `pre-commit`-koukun ennen jokaista committia, ja nollasta
poikkeava paluuarvo estää commitin:

```{.bash tiedosto="esimerkit/03-koukku.sh" osa="koukku"}
```

```{.bash tiedosto="esimerkit/03-koukku.sh" osa="kokeilu"}
```

```{.tuloste tiedosto="esimerkit/03-koukku.odotettu"}
```

Koukku tarkistaa vain lisätyt rivit (`git diff --cached`), joten se on
nopea. Viimeinen kokeilu näyttää koukun rajan: `--no-verify` ohittaa
sen, eikä koukku asennu automaattisesti uuteen kloonaukseen. Koukku on
siis **apu kehittäjälle, ei portti**. Varsinainen portti on CI:n
skannaus, jota ei voi ohittaa, ja koodialustan push protection.

Tiimeissä koukut jaetaan tavallisesti **pre-commit**-kehyksellä
(`.pre-commit-config.yaml` repositoriossa), joka asentaa samat
tarkistukset kaikille ja ajaa ne myös CI:ssä.

## Missä salaisuudet säilytetään

| Ratkaisu | Periaate | Sopii |
|----------|----------|-------|
| ympäristömuuttujat | ajoympäristö antaa arvot käynnistyksessä | yksinkertainen palvelu, kontit |
| salaisuusvarasto (HashiCorp Vault, OpenBao) | keskitetty palvelu, pääsynhallinta, auditointi, lyhytikäiset tunnukset | useita palveluita ja tiimejä |
| pilven avaintenhallinta (AWS KMS ja Secrets Manager, Azure Key Vault, GCP Secret Manager) | pilvialustan IAM ratkaisee, kuka lukee | pilvessä ajettavat palvelut |
| salatut tiedostot repositoriossa (SOPS, git-crypt) | arvot salattuina koodin rinnalla, avain KMS:ssä | GitOps, konfiguraatio koodina |
| CI:n salaisuudet | alustan salattu varasto, annetaan ajolle | CI:n omat tunnukset |

Kehittyneimmät ratkaisut eivät säilytä pysyvää salaisuutta lainkaan:
**dynaaminen tunnus** luodaan pyynnöstä, se on voimassa minuutteja tai
tunteja ja kumotaan automaattisesti. Vault voi esimerkiksi luoda
tietokantakäyttäjän jokaiselle palvelun instanssille. CI-ajo saa
pilvioikeudet OIDC-tunnisteella ilman tallennettua avainta (luku
*CI:n turvallisuus*). Vuotanut lyhytikäinen tunnus on pieni vahinko.

SOPS:n periaate on *kirjekuorisalaus* (taito *Kryptografia*): jokainen
arvo salataan datan avaimella, ja datan avain salataan KMS:n tai
age-avaimen avulla. Repositorioon voi siis tallentaa salatun
konfiguraation, ja muutoshistoria näkyy, mutta arvot eivät.

## Kierto ilman katkoa

Salaisuus vaihdetaan säännöllisesti, aina kun joku sen tunteva lähtee
tiimistä ja heti, kun vuotoa epäillään. Kierto onnistuu vain, jos se on
suunniteltu etukäteen. Allekirjoitusavaimen vaihdossa tarvitaan
avaintunniste (*key id*) ja vaihe, jossa kaksi avainta on voimassa
yhtä aikaa:

```{.python tiedosto="esimerkit/03-kierto.py" osa="avaimet"}
```

```{.python tiedosto="esimerkit/03-kierto.py" osa="kierto"}
```

```{.tuloste tiedosto="esimerkit/03-kierto.odotettu"}
```

```{.ajoituskaavio otsikko="Kierron kolme vaihetta: (1) uusi avain jaetaan, (2) allekirjoitus vaihtuu uuteen, (3) vanha poistetaan. Avaimet ovat päällekkäin voimassa niin kauan, että kaikki instanssit tuntevat uuden ja vanhalla allekirjoitetut tunnisteet ovat vanhentuneet."}
{"signal": [
  {"name": "vaihe", "wave": "====", "data": ["alku", "1", "2", "3"]},
  {"name": "allekirjoittava avain", "wave": "=.=.", "data": ["k1", "k2"]},
  {"name": "k1 hyväksytään", "wave": "1..0"},
  {"name": "k2 hyväksytään", "wave": "01.."}
], "config": {"hscale": 2}}
```

Samaa kolmen vaiheen mallia käytetään kaikessa kierrossa:

- **TLS-varmenteet**: uusi varmenne otetaan käyttöön ennen vanhan
  vanhenemista.
- **Tokenien allekirjoitusavaimet.** Kirjautumispalvelu allekirjoittaa
  käyttäjästä kertovan tunnisteen (*JSON Web Token*, JWT) ja julkaisee
  tarkistukseen tarvittavat julkiset avaimet avainjoukkona (*JSON Web
  Key Set*, JWKS). Joukossa on useita avaimia, ja tunnisteen otsakkeen
  `kid` (*key id*) kertoo, millä niistä se on allekirjoitettu. Tokenit
  käsitellään taidossa *Web-sovellusten tietoturva*.
- **Tietokantasalasanat**: kaksi käyttäjää, joista toinen on aina
  voimassa.

Jos kierto vaatii katkon, sitä ei tehdä, ja avaimesta tulee ikuinen.

## Kun salaisuus vuotaa

Ensimmäinen ajatus on usein poistaa salaisuus repositoriosta. Se ei
riitä, eikä edes historian uudelleenkirjoitus riitä:

```{.bash tiedosto="esimerkit/03-vuoto.sh" osa="vuoto"}
```

```{.bash tiedosto="esimerkit/03-vuoto.sh" osa="etsi"}
```

```{.bash tiedosto="esimerkit/03-vuoto.sh" osa="siivous"}
```

```{.tuloste tiedosto="esimerkit/03-vuoto.odotettu"}
```

Poiston jälkeen avain on yhä historiassa. Historian uudelleenkirjoitus
jättää varmuuskopioviitteet (`refs/original`) ja reflogin, ja vasta
niiden ja vanhojen objektien poisto puhdistaa paikallisen repositorion.
Kollegan kopio, CI:n välimuisti, forkit ja koodialustan välimuistit
sisältävät avaimen edelleen, eikä niitä voi siivota. Siksi järjestys
on aina:

1. **Kumoa** salaisuus heti palveluntarjoajalla. Tämä on ainoa toimi,
   joka oikeasti poistaa vaaran.
2. **Selvitä** käyttö: palveluntarjoajan lokit kertovat, onko avainta
   käytetty vuodon jälkeen ja mistä.
3. **Korvaa** uudella salaisuudella oikeassa paikassa (varasto, ei
   koodi).
4. **Siivoa** historia tarvittaessa (`git filter-repo` on suositeltu
   työkalu; esimerkin `filter-branch` on vanhentunut mutta aina
   saatavilla). Siivous estää uudet löydökset ja skannerien hälytykset,
   mutta ei korjaa vuotoa.
5. **Opi**: miksi koukku ja CI eivät estäneet vuotoa?

## Käytännössä

- **Salaisuus ei kuulu koodiin, kuvaan eikä asiakkaalle.** Ajoympäristö
  tai varasto antaa sen palvelulle ajon aikana.
- **Kerroksellinen skannaus.** Koukku kehittäjälle, CI portiksi ja
  koodialustan push protection viimeiseksi varmistukseksi.
- **Lyhytikäiset ja rajatut tunnukset.** Paras salaisuus on sellainen,
  jota ei tarvitse säilyttää: dynaamiset tunnukset ja OIDC.
- **Suunnittele kierto ennen kuin tarvitset sitä.** Avaintunniste ja
  kahden avaimen vaihe tekevät kierrosta rutiinin.
- **Kumoa ensin, siivoa sitten.** Vuotanut salaisuus on menetetty
  hetkellä, jolloin se tuli näkyviin.
- **Jokaisella palvelulla ja ympäristöllä omat salaisuudet.** Yhteinen
  avain kaikille ympäristöille tekee kehitysympäristön vuodosta
  tuotannon vuodon.

## Itsearviointi

- Osaat luetella salaisuuksien yleisimmät vuotokanavat ja niiden
  torjunnan.
- Osaat selittää, miten salaisuusskanneri toimii, ja arvioida sen väärät
  hälytykset ja ohitetut vuodot.
- Osaat kirjoittaa commit-koukun ja kertoa, miksi se ei yksin riitä.
- Osaat valita salaisuuksien säilytystavan ja suunnitella kierron
  ilman katkoa.
- Osaat toimia oikeassa järjestyksessä, kun salaisuus on vuotanut.
