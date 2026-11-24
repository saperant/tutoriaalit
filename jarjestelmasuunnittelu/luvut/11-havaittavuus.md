# Monitorointi ja havaittavuus

Monitorointi kertoo, että jokin on vialla; havaittavuus (*observability*)
auttaa selvittämään miksi. Hajautetussa järjestelmässä yksi
käyttäjän pyyntö kulkee kuormantasaajan, usean palvelun, välimuistin ja
tietokannan kautta, eikä yhden palvelimen loki kerro, missä aika kului.
Tarvitaan kolme signaalia: *metriikat* (laskurit ja jakaumat ajan yli),
*lokit* (tapahtumat yksityiskohtineen) ja *jäljet* (yhden pyynnön kulku
palvelujen läpi). Lokien ja korrelaatiotunnuksen perusteet yhdessä
palvelussa ovat taidossa *Taustapalvelut*, hälytysten hygienia taidossa
*Palvelinympäristöt*. Tässä katsotaan, mitä järjestelmän mittakaava
lisää.

## Mitä mitataan: RED ja USE

Kaksi muistisääntöä kattaa useimmat tarpeet:

| Menetelmä | Kohde | Metriikat |
|-----------|-------|-----------|
| RED | palvelut ja rajapinnat | pyyntöjen määrä (*rate*), virheet (*errors*), kesto (*duration*) |
| USE | resurssit: suoritin, muisti, levy, yhteysallas, jono | käyttöaste (*utilization*), kyllästyminen (*saturation*), virheet (*errors*) |

RED kertoo, mitä käyttäjä kokee; USE kertoo, mikä resurssi on
pullonkaula. Kyllästyminen on usein ennakoivin signaali: jonon pituus,
odottavat yhteyspyynnöt ja säikeet, jotka odottavat allasta. Lisäksi
jokaiselle välimuistille osumasuhde (luku 6) ja jonolle vanhimman viestin
ikä (luku 8).

## Persentiilit histogrammeista

Latenssin persentiileistä tehdään helposti väärä johtopäätös, kun
palvelimia on useita. Jokainen palvelin voi laskea oman p99-arvonsa,
mutta niistä ei voi laskea koko palvelun p99:ää, ei keskiarvona eikä
painotettuna keskiarvona:

```{.python tiedosto="esimerkit/luku11/persentiilit.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/luku11/persentiilit.odotettu"}
```

Oikea p99 on 350 ms. Keskiarvo antaa 388 ms ja painotettu keskiarvo
101 ms, vaikka 1,2 % pyynnöistä kestää yli 250 ms ja tavoite "p99 alle
250 ms" ei siis täyty. Siksi palvelimet raportoivat *histogrammin*:
laskurin kullekin kestolokerolle. Laskurit voi laskea yhteen palvelimien
ja aikavälien yli, ja persentiili arvioidaan yhdistetystä histogrammista
interpoloimalla lokeron sisällä:

```{.python tiedosto="esimerkit/jarjestelma/histogrammi.py" osa="kvantiili"}
```

Arvio on 332 ms, koska lokero 250–500 ms on leveä. Lokerorajat valitaan
niin, että tavoitteen raja (tässä 250 ms) on lokeroraja: silloin
SLO-osuus saadaan tarkasti, vaikka persentiili on likiarvo.

## Metriikat Prometheus-muodossa

Prometheus hakee metriikat palveluilta HTTP:llä tekstimuodossa.
Laskuri kasvaa, ja sen nopeus lasketaan kyselyssä (`rate`); histogrammi
on joukko kertyviä lokerolaskureita (`_bucket` ja yläraja `le`) sekä
summa ja määrä:

```{.python tiedosto="esimerkit/jarjestelma/histogrammi.py" osa="prometheus"}
```

```{.python tiedosto="esimerkit/jarjestelma/seurattu.py" osa="metrics"}
```

Nimiöt (*labels*) kuten `reitti` ja `koodi` tekevät metriikasta
moniulotteisen, mutta jokainen nimiöarvojen yhdistelmä on oma aikasarjansa.
Käyttäjätunnus, pyynnön tunnus tai täysi polku nimiönä luo miljoonia
aikasarjoja (*kardinaliteettiräjähdys*) ja kaataa metriikkajärjestelmän.
Nimiöiden arvojoukon on oltava pieni ja tunnettu; yksittäiset tunnukset
kuuluvat lokeihin ja jälkiin.

## Jäljitys

Jälki (*trace*) koostuu väleistä (*span*): jokainen palvelu kirjaa
osuutensa pyynnöstä välinä, jolla on alku, kesto ja vanhemman välin
tunnus. Jäljen tunnus kulkee palvelusta toiseen pyynnön mukana; W3C:n
Trace Context -standardissa se on otsakkeessa `traceparent`:

```{.python tiedosto="esimerkit/jarjestelma/seurattu.py" osa="jalki"}
```

```{.python tiedosto="esimerkit/jarjestelma/seurattu.py" osa="valitys"}
```

Esimerkissä kauppa kutsuu varastoa. Varasto on hidas tilauksilla 7 ja
17 ja epäonnistuu tilauksilla 9 ja 19. Lopuksi luetaan kummankin palvelun
metriikat ja kootaan hitaan tilauksen jälki lokiriveistä:

```{.python tiedosto="esimerkit/luku11/havainnot.py" osa="kokoaminen"}
```

```{.tuloste tiedosto="esimerkit/luku11/havainnot.odotettu"}
```

Metriikat kertovat, että kaupassa on kaksi virhettä (`502`) ja kaksi
yli 250 ms:n pyyntöä, ja varaston metriikat näyttävät saman. Jälki
kertoo, että tilauksen 7 aika kului varastossa: kaupan väli on hidas
vain siksi, että sen lapsi on hidas. Tämä on jäljityksen tärkein käyttö:
latenssin *kriittisen polun* löytäminen pyynnöstä, joka kulkee monen
palvelun läpi.

Tuotannossa välejä ei kirjata lokiriveinä vaan lähetetään
jäljityspalvelulle (Jaeger, Tempo, pilvipalvelun jäljitys).
OpenTelemetry on avoin standardi ja kirjastojoukko, joka tuottaa
metriikat, lokit ja jäljet samoilla käsitteillä ja välittää jäljen
tunnuksen automaattisesti HTTP- ja gRPC-kirjastojen ja jonojen yli.
Kaikkia jälkiä ei tallenneta: *näytteistys* valitsee esimerkiksi 1 %
jäljistä, mutta virheelliset ja hitaat tallennetaan aina (*tail
sampling*), jotta mielenkiintoiset jäljet eivät karsiudu.

## Rakenteiset lokit

Lokirivi kirjoitetaan rakenteisena (JSON) eikä vapaana tekstinä, jotta
sitä voi hakea kentittäin: kaikki rivit, joissa `jalki` on tietty,
`koodi` on 5xx tai `kesto_ms` yli rajan. Jäljen tunnus lokirivillä
yhdistää lokit ja jäljet: hälytyksestä metriikkaan, metriikasta
esimerkkijälkeen ja jäljestä lokiriveihin. Lokien määrä kasvaa
liikenteen mukana, joten onnistuneiden pyyntöjen rivit näytteistetään
tai tiivistetään, ja säilytysaika rajataan.

## Hälytykset tavoitteesta

Hälytys herättää ihmisen, joten sen on tarkoitettava, että käyttäjät
kärsivät nyt tai pian. Hyvä peruste on SLO:n virhebudjetin
kulumisnopeus (luku 10). Monen ikkunan sääntö hälyttää, kun budjetti
kuluu nopeasti sekä pitkällä että lyhyellä ikkunalla:

```{.yaml tiedosto="esimerkit/luku11/halytykset.yaml" osa="saanto"}
```

Suoritinkäyttö, muisti ja levy eivät yleensä ole päivystyshälytyksiä
vaan syitä, joita tutkitaan, kun käyttäjiin vaikuttava hälytys on
lauennut. Poikkeus ovat ennakoivat hälytykset, kuten levyn täyttyminen
ennusteen mukaan muutamassa tunnissa.

## Käytännössä

- **RED jokaiselle palvelulle, USE jokaiselle resurssille.** Lisäksi
  osumasuhteet ja jonojen ikä.
- **Raportoi histogrammit, älä persentiilejä.** Kokoa palvelimien ja
  aikavälien yli laskureina, ja valitse lokerorajat tavoitteiden mukaan.
- **Pidä nimiöt pieninä.** Tunnukset kuuluvat lokeihin ja jälkiin, eivät
  metriikoiden nimiöihin.
- **Välitä jäljen tunnus kaikkialle.** HTTP, jonot ja taustatyöt; kirjaa
  se jokaiselle lokiriville.
- **Hälytä oireista, tutki syyt.** Päivystyshälytys virhebudjetin
  kulumisesta, resurssimetriikat vianetsintään.
- **Testaa havaittavuus.** Kun vika simuloidaan, löytyykö se
  hallintapaneelista ja jäljestä? Jos ei, puuttuu signaali.

## Itsearviointi

- Osaat valita palvelun ja resurssien metriikat RED- ja USE-menetelmillä.
- Osaat selittää, miksi persentiilejä ei voi keskiarvoistaa, ja koota
  persentiilin histogrammeista.
- Osaat tuottaa Prometheus-muotoiset metriikat ja välttää
  kardinaliteettiräjähdyksen.
- Osaat välittää jäljen tunnuksen palvelusta toiseen, koota jäljen ja
  löytää siitä latenssin kriittisen polun.
- Osaat kirjoittaa virhebudjetin kulumisnopeuteen perustuvan hälytyksen.
