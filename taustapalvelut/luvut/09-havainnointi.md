# Havainnointi

Tuotannossa palvelua ei voi pysäyttää debuggeriin. Ainoa tieto sen
toiminnasta on se, minkä se itse kertoo: lokit, metriikat, jäljitys
(*traces*) ja terveystarkistukset. *Havainnoitavuus* (*observability*)
tarkoittaa, että näistä voi vastata myös kysymyksiin, joita ei
osattu ennakoida: miksi juuri tämä asiakas sai virheen klo 14.03.

## Lokit ja korrelaatiotunnus

Yhden pyynnön lokirivit ovat hajallaan tuhansien muiden seassa. Siksi
jokainen pyyntö saa tunnisteen, joka liitetään sen jokaiseen
lokiriviin. Suodatin asettaa tunnuksen SLF4J:n *MDC*:hen
(*mapped diagnostic context*, säiekohtainen avain–arvo-taulu), ja
lokimuoto tulostaa sen (`logging.pattern.correlation` luvun 4
asetuksissa):

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/havainnointi/KorrelaatioSuodatin.java" osa="suodatin"}
```

Kolme yksityiskohtaa:

- Kutsujan antama tunnus hyväksytään vain, jos se on kelvollinen.
  Muuten lokiin voisi syöttää rivinvaihtoja ja väärennettyjä rivejä
  (*log injection*).
- Tunnus palautetaan vastauksessa, jolloin asiakkaan tukipyynnössä on
  suoraan hakuavain lokeihin.
- `finally` poistaa tunnuksen, koska säie (myös virtuaalisäikeen
  kantasäie) käsittelee seuraavaksi toisen pyynnön.

Lokirivi kertoo tapahtuman, ei tarinaa: `tilaus 42 luotu, 2 riviä`.
Parametrit annetaan paikkamerkkeinä (`{}`), jolloin merkkijonoa ei
koota, jos taso on pois päältä. Tuotannossa lokit kirjoitetaan
*rakenteisina* (JSON-rivi kerrallaan), jotta lokipalvelu voi hakea
kentittäin: Spring Bootissa `logging.structured.format.console: ecs`
(Elastic Common Schema) tai `logstash`. MDC:n kentät tulevat mukaan
automaattisesti.

Palvelujen välillä tunnus välitetään eteenpäin. Standardi tähän on
W3C:n `traceparent`-otsake, ja Micrometer Tracing ja OpenTelemetry
tekevät sen automaattisesti: jokainen HTTP-kutsu, tietokantakysely ja
viesti näkyy jäljityksessä osana samaa pyyntöä kestoineen. Oma
korrelaatiosuodatin on tämän yksinkertaisin muoto, ja sen voi korvata
jäljityksellä, kun palveluja on useita.

## Metriikat

Loki kertoo yksittäisistä tapahtumista, metriikka määristä ajan yli:
pyyntöjä sekunnissa, virheiden osuus, vasteajan jakauma. Spring Boot
mittaa HTTP-pyynnöt, yhteysaltaan, JVM:n ja roskienkeruun
automaattisesti Micrometerillä. Liiketoimintamittarit lisätään itse:

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/tilaus/TilausPalvelu.java" osa="mittari"}
```

Mittareita on kolmea perustyyppiä: laskuri (*counter*, vain kasvaa),
mittari (*gauge*, nykyarvo, kuten jonon pituus) ja ajastin (*timer*,
kestot ja niiden jakauma). Hyvä lähtökohta on *RED*-menetelmä
jokaiselle rajapinnalle: *rate* (pyynnöt), *errors* (virheet) ja
*duration* (kesto, persentiileinä p50, p95, p99 eikä keskiarvona).

Mittarin tunnisteisiin (*tags*) ei laiteta arvoja, joita on rajattomasti,
kuten käyttäjätunnusta tai tilauksen numeroa: jokainen eri arvo on oma
aikasarjansa, ja metriikkapalvelu täyttyy (*cardinality explosion*).

Metriikat haetaan `/actuator/metrics`-päätepisteestä tai, tuotannossa
tavallisemmin, Prometheus-muodossa lisäämällä riippuvuus
`micrometer-registry-prometheus`.

## Terveystarkistukset

Actuatorin `/actuator/health` kertoo, toimiiko palvelu. Boot lisää
siihen automaattisesti tietokannan, levytilan ja muiden riippuvuuksien
tarkistukset. Kontinhallinta (Kubernetes) käyttää kahta eri
kysymystä:

- **Liveness** (`/actuator/health/liveness`): onko prosessi elossa? Jos
  ei, kontti käynnistetään uudelleen. Tähän ei kytketä tietokantaa:
  tietokannan katko ei korjaudu palvelun uudelleenkäynnistyksellä,
  vaan kaikki instanssit käynnistyisivät silmukassa.
- **Readiness** (`/actuator/health/readiness`): voiko palvelu ottaa
  pyyntöjä vastaan? Käynnistyksen ja sammutuksen aikana ei, ja
  kuormantasaaja ohjaa liikenteen muualle.

Testi tarkistaa terveyden, korrelaatiotunnuksen ja liiketoimintamittarin:

```{.java tiedosto="esimerkit/kauppa/src/test/java/fi/tutoriaalit/kauppa/tilaus/TilausIntegraatioTest.java" osa="havainnointi"}
```

Actuatorin päätepisteet paljastavat sisäistä tietoa (ympäristö,
asetukset, metriikat), joten luvun 8 ketju päästää niistä vain
terveyden kaikille ja loput ylläpitäjälle. Tuotannossa ne usein
siirretään omaan porttiinsa (`management.server.port`), johon pääsee
vain sisäverkosta.

## Siisti sammutus

Kun palvelu sammutetaan uuden version tieltä, käynnissä olevat pyynnöt
saavat valmistua: Boot lopettaa uusien vastaanoton ja odottaa
(`server.shutdown: graceful`, oletuksena päällä,
`spring.lifecycle.timeout-per-shutdown-phase`). Readiness muuttuu
heti sammutuksen alkaessa, jotta kuormantasaaja lakkaa ohjaamasta
pyyntöjä. Miten kontinhallinta käyttää näitä tarkistuksia ja
sammutussignaalia, kerrotaan taidossa *Kontit ja
pilvi-infrastruktuuri*; palvelutasotavoitteet ja hälytysten
mitoitus ovat taidossa *Palvelinympäristöt*.

## Käytännössä

- **Korrelaatiotunnus tai jäljitys jokaiseen pyyntöön** ja jokaiseen
  lokiriviin. Ilman sitä tuotantovian selvitys on arvailua.
- **Rakenteiset lokit**, tapahtumat paikkamerkein, ei henkilötietoja
  eikä salaisuuksia.
- **RED-mittarit rajapinnoille, liiketoimintamittarit tärkeimmille
  toiminnoille** (tilaukset, maksut). Hälytys perustuu oireisiin
  (virheosuus, p99-vasteaika), ei syihin (prosessorin käyttö).
- **Liveness ja readiness erikseen**, eikä livenessiin ulkoisia
  riippuvuuksia.
- **Hinta:** lokirivin kirjoitus maksaa mikrosekunteja, mutta
  lokipalvelun tallennustila maksaa rahaa: `DEBUG` tuotannossa koko
  ajan on kallis. Jäljitys otetaan suuressa kuormassa näytteenä
  (esim. 10 % pyynnöistä).

## Itsearviointi

- Osaat toteuttaa korrelaatiotunnuksen MDC:llä ja selittää, miksi
  kutsujan antama arvo tarkistetaan.
- Osaat lisätä liiketoimintamittarin ja valita mittarityypin ja
  tunnisteet oikein.
- Osaat selittää RED-menetelmän ja persentiilien edun keskiarvoon.
- Osaat erottaa liveness- ja readiness-tarkistukset.
