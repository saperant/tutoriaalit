# Injektiot

Injektio syntyy, kun data ja koodi sekoittuvat: käyttäjän syöte
liitetään osaksi kieltä, jota toinen järjestelmä tulkitsee, kuten
SQL-lausetta, komentotulkin komentoa, HTML-sivua tai LDAP-hakua. Jos
syöte sisältää kielen erikoismerkkejä, se muuttaa tulkittavan lauseen
rakennetta. Kaikkien injektioiden korjaus on sama periaate: **data
välitetään datana, erillään rakenteesta**.

## SQL-injektio

Kirjautumistarkistus kootaan merkkijonosta:

```{.python tiedosto="esimerkit/07-sql.py" osa="haavoittuva"}
```

Kun käyttäjätunnukseksi syötetään `aino' --`, lauseesta tulee

```text
SELECT count(*) FROM kayttaja WHERE nimi = 'aino' --' AND tiiviste = '…'
```

Heittomerkki päättää merkkijonon, ja `--` muuttaa loppurivin
kommentiksi. Salasanaehto katoaa. Muilla syötteillä hyökkääjä voi lukea
muita tauluja (`UNION SELECT`), muuttaa tietoja tai joissain
tietokannoissa ajaa käyttöjärjestelmän komentoja.

Korjaus on **parametrisoitu kysely**: lauseen rakenne on vakio, ja
arvot välitetään tietokannalle erikseen. Tietokanta ei koskaan tulkitse
niitä SQL:nä, joten erikoismerkeillä ei ole merkitystä:

```{.python tiedosto="esimerkit/07-sql.py" osa="korjattu"}
```

```{.tuloste tiedosto="esimerkit/07-sql.odotettu"}
```

Erikoismerkkien "siivoaminen" tai heittomerkkien kahdentaminen ei ole
korjaus. Se unohtuu jostain, siinä on reunatapauksia (merkistökoodaukset,
numerokentät ilman lainausmerkkejä), eikä se ole tarpeen, kun
parametreja käytetään. Taulujen ja sarakkeiden nimiä ei voi
parametrisoida; jos niiden on riiputtava syötteestä, ne valitaan
sallittujen nimien listasta. SQL:n käytöstä sovelluksesta kerrotaan
lisää taidossa *SQL ja relaatiotietokannat*.

## Komentoinjektio

Sama ongelma syntyy, kun ohjelma kutsuu komentotulkkia. Puolipiste,
`&&`, `|`, `$( )` ja rivinvaihto aloittavat uuden komennon:

```{.python tiedosto="esimerkit/07-komentotulkki.py" osa="hyokkays"}
```

```{.tuloste tiedosto="esimerkit/07-komentotulkki.odotettu"}
```

Korjaus on jättää komentotulkki pois ja välittää argumentit listana.
Silloin käyttöjärjestelmä käynnistää ohjelman suoraan, ja jokainen
listan alkio on yksi argumentti, sisälsi se mitä tahansa. Jos
argumentti voi alkaa viivalla, `--` erottaa valitsimet argumenteista.

## Staattinen analyysi löytää injektiot

Tutoriaalin esimerkit tarkistetaan ruffin säännöillä `S`
(flake8-bandit). Ne tunnistavat tyypillisiä vaarallisia rakenteita:

| Sääntö | Löytää |
|--------|--------|
| S602 | `subprocess`-kutsu `shell=True`-valitsimella |
| S608 | merkkijonoista koottu SQL-lause |
| S301 | `pickle`-lataukset (luku *Syöte, polut ja sarjallistus*) |
| S105–S107 | koodiin kirjoitetut salasanat |
| S324 | heikot tiivistefunktiot (MD5, SHA-1) |

Seuraavassa esimerkissä on haavoittuva versio merkitty
`@virhe`-merkinnöin. Sellaisenaan tiedosto ei läpäise tarkistusta:

```{.python tiedosto="esimerkit/07-komento.ei-kaanny.py" osa="tervehdys"}
```

```text
S602 `subprocess` call with `shell=True` identified, security issue
  --> 07-komento.ei-kaanny.py:13:13
```

Kun haavoittuvat rivit poistetaan, tarkistus menee läpi, ja nimi
tulostuu yhtenä argumenttina:

```{.tuloste tiedosto="esimerkit/07-komento.odotettu"}
```

Turvallisellakin kutsulla on `noqa`-kommentti: sääntö S603 muistuttaa
jokaisesta aliprosessista, koska työkalu ei voi tietää, onko kutsu
turvallinen. Perusteltu poikkeus on parempi kuin säännön kytkeminen
kokonaan pois, koska seuraava aliprosessikutsu tarkistetaan taas.
Staattinen analyysi ei löydä kaikkea, mutta se löytää halvalla monta
yleistä virhettä, ja sen paikka on CI-putkessa (taito *Tietoturva
kehitystyössä*).

## Muut injektiot

| Kohde | Esimerkki | Korjaus |
|-------|-----------|---------|
| HTML (XSS) | käyttäjän nimi sivulle sellaisenaan | kontekstin mukainen koodaus, mallipohjien automaattinen koodaus |
| LDAP | `(uid={nimi})` | kirjaston suodatinfunktiot |
| lokit | rivinvaihto syötteessä väärentää lokirivin | rakenteiset lokit (JSON) |
| mallipohjat (SSTI) | käyttäjän syöte mallipohjaksi | syöte vain mallipohjan dataksi |
| polut | `../` tiedostonimessä | luku *Syöte, polut ja sarjallistus* |
| XML (XXE) | ulkoinen entiteetti lukee palvelimen tiedoston | DTD ja ulkoiset entiteetit pois jäsentimestä |
| palvelimen tekemä pyyntö (SSRF) | käyttäjän antama URL osoittaa sisäverkkoon | sallittujen kohteiden lista, sisäverkon osoitteiden esto |

Kahdessa viimeisessä syöte ei muuta lauseen rakennetta vaan sen, mihin
palvelin itse kurottaa: XML-jäsennin tai HTTP-asiakas tekee hyökkääjän
valitseman haun palvelimen oikeuksilla. Periaate on silti sama, eli
syöte ei saa päättää, mitä tulkki tai asiakas tekee.

Ristiinsivustokomentosarjat (XSS) ovat selaimen injektio. XSS, SSRF ja
XXE käsitellään esimerkein taidossa *Web-sovellusten tietoturva*.

## Käytännössä

- **Erota data ja rakenne.** Parametrisoidut kyselyt, argumenttilistat,
  mallipohjien automaattinen koodaus. Merkkijonojen yhdistely kieleen,
  jota toinen järjestelmä tulkitsee, on aina epäilyttävää.
- **Ei siivousta korjauksena.** Erikoismerkkien poisto tai
  kahdentaminen on hauras. Sallittujen arvojen lista on oikea keino
  silloin, kun parametrisointi ei ole mahdollista (tunnisteet,
  järjestyssuunta).
- **Komentotulkki pois.** `subprocess.run([...])` ilman `shell=True`.
  Mieluiten kirjasto kuin ulkoinen komento.
- **Vähimmät oikeudet rajaavat vahinkoa.** Sovelluksen
  tietokantatunnus, jolla ei voi poistaa tauluja eikä lukea muiden
  sovellusten tietoja, tekee onnistuneesta injektiosta pienemmän.
- **Automatisoi löytäminen.** Staattinen analyysi CI:ssä ja
  perustellut poikkeukset rivikohtaisesti.

## Itsearviointi

- Osaat selittää, miksi injektio syntyy, ja tunnistaa sen eri
  kielissä (SQL, komentotulkki, HTML).
- Osaat korjata SQL-injektion parametrisoidulla kyselyllä ja
  komentoinjektion argumenttilistalla.
- Osaat käyttää staattista analyysia injektioiden löytämiseen ja
  kirjata perustellun poikkeuksen.
- Osaat valita sallittujen arvojen listan silloin, kun parametrisointi
  ei ole mahdollista.
