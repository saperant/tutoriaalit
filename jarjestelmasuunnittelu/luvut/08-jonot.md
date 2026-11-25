# Viestijonot ja asynkroninen käsittely

Kaikkea ei tarvitse tehdä pyynnön aikana. Kun käyttäjä tilaa, palvelun
on tallennettava tilaus ja vastattava, mutta laskun lähetys,
varastosaldon päivitys, suositusten laskenta ja sähköposti voidaan tehdä
myöhemmin. Jono erottaa työn tekijän työn pyytäjästä: pyytäjä kirjoittaa
viestin jonoon ja jatkaa, ja kuluttajat käsittelevät viestit omaan
tahtiinsa. Viestinvälityksen mallit, kuten komennot ja tapahtumat, aiheet,
saga ja outbox, ovat taidossa *Palveluarkkitehtuurit*. Tässä jonoa
katsotaan kapasiteetin ja vikasietoisuuden välineenä.

## Jono kuorman tasaajana

Jono muuttaa kapasiteettiongelman viiveeksi. Ilman jonoa jokainen
pyyntö, joka ylittää käsittelykapasiteetin, on hylättävä tai se
ylikuormittaa palvelun. Jonon kanssa ylimäärä odottaa ja käsitellään,
kun kuorma laskee. Esimerkissä kampanja tuo 15 minuutin ajan nelinkertaisen
määrän tilauksia, ja käsittelijät ehtivät 80 tilausta sekunnissa:

```{.python tiedosto="esimerkit/luku08/tasaus.py" osa="virtaus"}
```

```{.tuloste tiedosto="esimerkit/luku08/tasaus.odotettu"}
```

![Sama laskelma kuvana. Jono kasvaa niin kauan kuin saapuva kuorma
ylittää kapasiteetin, ja purkautuu sen jälkeen kulmakertoimella, jonka
määrää ylijäämäkapasiteetti.](kuvat/jono.png){width=72%}

Ilman jonoa 108 000 tilausta hylättäisiin. Jonon kanssa yksikään ei
katoa, mutta pahimmillaan tilaus odottaa käsittelyä 22 minuuttia, ja jono
tyhjenee vasta tunti kampanjan jälkeen. Purkuaika riippuu vain
*ylijäämäkapasiteetista*: kun kuorma palaa 50:een, jono lyhenee 30
tilausta sekunnissa. Jos ylijäämä olisi 5 tilausta sekunnissa, sama jono
purkautuisi kuudessa tunnissa. Odotusaika saadaan Littlen laista: jonon
pituus jaettuna käsittelynopeudella.

Laskelma kertoo, mitä on päätettävä: kauanko tilaus saa odottaa, ja
kuinka nopeasti kuluttajia on lisättävä jonon kasvaessa. Jonon pituus ja
vanhimman viestin ikä ovat siksi tärkeimmät jonon metriikat ja
automaattisen skaalauksen perusteet.

## Vähintään kerran ja idempotentti kuluttaja

Toimitusmallit ovat tuttuja taidosta *Hajautetut järjestelmät*:
täsmälleen kerran on mahdollinen vain vaikutuksena, kun vähintään
kerran toimitetun viestin vastaanottaja tunnistaa toiston. Jonossa
toisto syntyy kuluttajan päässä: kuluttaja voi kaatua sen jälkeen, kun
se on tehnyt työn, mutta ennen kuin se on kuitannut viestin, ja jono
toimittaa viestin uudelleen. Käytännön malli on siksi vähintään kerran
-toimitus ja idempotentti kuluttaja.

Redis Streams toteuttaa vähintään kerran -toimituksen kuluttajaryhmillä:
viesti on ryhmässä *odottava*, kunnes kuluttaja kuittaa sen (`XACK`),
ja kaatuneen kuluttajan odottavat viestit voi ottaa haltuun
(`XAUTOCLAIM`). Tuottaja lisää tilaukset virtaan:

```{.python tiedosto="esimerkit/luku08/virta.py" osa="tuottaja"}
```

Kuluttaja laskuttaa tilauksen ja kuittaa sen. Idempotenssiavain on
`SET NX`: jos tilaus on jo laskutettu, toista laskua ei tehdä.
Esimerkissä kuluttaja k1 kaatuu tilauksen t3 kohdalla laskutuksen ja
kuittauksen välissä:

```{.python tiedosto="esimerkit/luku08/virta.py" osa="kasittely"}
```

Kuluttaja, joka ottaa haltuun kuittaamattomat, tarkistaa samalla, kuinka
monta kertaa viesti on jo toimitettu. Viesti, jota ei voi käsitellä (tässä
summa "kaksi"), siirretään kolmannen yrityksen jälkeen kuolleiden
viestien virtaan, jotta se ei tukki jonoa:

```{.python tiedosto="esimerkit/luku08/virta.py" osa="haltuunotto"}
```

```{.tuloste tiedosto="esimerkit/luku08/virta.odotettu"}
```

Tilaus t3 käsiteltiin kahdesti, mutta laskutettiin kerran. Tilaus t4
yritettiin kolmesti ja siirrettiin sitten kuolleisiin, ja kaikki muut
kuitattiin. Huomaa, että idempotenssiavaimen ja työn on oltava samassa
tallennuksessa ja samassa atomisessa operaatiossa. Jos lasku
kirjoitettaisiin tietokantaan ja avain Redisiin, kaatuminen niiden
välissä toisi ongelman takaisin. Tietokannassa avain on
yksikäsitteisyysrajoite samassa transaktiossa kuin työ.

## Järjestys ja osiot

Yksi jono yhdellä kuluttajalla säilyttää järjestyksen, mutta ei
skaalaudu. Kun kuluttajia on monta, viestit käsitellään rinnakkain eikä
järjestyksessä. Kafka ja Redis Cluster ratkaisevat tämän osioilla:
viestit jaetaan avaimen mukaan osioihin (luku 5), ja järjestys säilyy
osion sisällä. Kaikki saman asiakkaan tai saman tilauksen viestit
menevät samaan osioon ja käsitellään järjestyksessä, ja eri asiakkaiden
viestit rinnakkain. Rinnakkaisuuden yläraja on osioiden määrä, joten
osioita luodaan alussa riittävästi.

Kuolleiden viestien jono rikkoo järjestyksen: jos t4 siirretään syrjään
ja saman asiakkaan t5 käsitellään, t5 voi riippua t4:stä. Jos järjestys
on tärkeä, viallinen viesti pysäyttää osion, kunnes se korjataan, tai
myös saman avaimen myöhemmät viestit siirretään syrjään.

## Vastapaine

Jono ei saa kasvaa rajatta. Muisti tai levy loppuu, ja viestit
vanhenevat käyttökelvottomiksi: tunnin vanha "näytä ilmoitus nyt" on
hyödytön. Rajattu jono pakottaa päättämään, mitä tehdään, kun se on
täynnä:

- **Tuottaja odottaa** (vastapaine, *backpressure*). Hidastus etenee
  ketjussa taaksepäin aina käyttäjään asti; sopii eräajoihin.
- **Uusin hylätään** virheellä, jonka tuottaja käsittelee: "yritä
  myöhemmin" (HTTP 429 tai 503). Sopii käyttäjän pyyntöihin.
- **Vanhin hylätään tai viestit vanhenevat** (TTL jonossa). Sopii
  tietoon, jonka arvo laskee nopeasti, kuten sijainteihin ja mittauksiin.

## Kafka, RabbitMQ ja muut

Jonojärjestelmät eroavat siinä, säilyykö viesti lukemisen jälkeen,
missä laajuudessa järjestys pätee ja kuka järjestelmää ylläpitää.
Taulukko vertaa tavallisimpia näiden ominaisuuksien mukaan:

| Ominaisuus  | Kafka              | RabbitMQ              | Redis Streams          | pilven jonot (SQS, Pub/Sub) |
|------------------|------------------|------------------|------------------|------------------|
| malli | pysyvä loki, osiot | välittäjä, jonot ja reititys | loki muistissa, kuluttajaryhmät | hallinnoitu jono |
| säilytys | päiviä tai pysyvästi | kuittaukseen asti | muistin rajoissa | päiviä |
| uudelleenluku | kyllä, siirtymästä | ei | kyllä, tunnisteesta | ei |
| järjestys | osion sisällä | jonon sisällä | virran sisällä | FIFO-jonoissa |
| läpäisy | hyvin suuri | suuri | suuri | skaalautuu automaattisesti |
| sopii | tapahtumavirrat, integraatio, analytiikka | tehtäväjonot, monimutkainen reititys | kevyet jonot, kun Redis on jo käytössä | kun ei haluta ylläpitää välittäjää |

## Käytännössä

- **Siirrä jonoon työ, jonka ei tarvitse valmistua pyynnön aikana.**
  Vastausaika lyhenee, ja kuormapiikit tasaantuvat.
- **Laske purkuaika.** Ylijäämäkapasiteetti ratkaisee, kuinka nopeasti
  jono palautuu. Mitoita kuluttajat sen mukaan, kuinka vanha viesti saa
  olla.
- **Seuraa jonon pituutta ja vanhimman viestin ikää.** Ne ovat jonon
  latenssi ja automaattisen skaalauksen ohjaussuure.
- **Oleta vähintään kerran ja tee kuluttajasta idempotentti.**
  Idempotenssiavain samaan atomiseen operaatioon kuin työ.
- **Rajaa yritykset ja käytä kuolleiden viestien jonoa.** Seuraa sitä ja
  päätä etukäteen, kuka käsittelee sen sisällön.
- **Valitse osioavain järjestyksen mukaan.** Järjestys säilyy vain osion
  sisällä.

## Itsearviointi

- Osaat laskea, kuinka pitkäksi jono kasvaa purskeessa ja kuinka nopeasti
  se purkautuu.
- Osaat toteuttaa vähintään kerran -käsittelyn kuluttajaryhmällä,
  kaatuneen kuluttajan viestien haltuunoton ja idempotentin kuluttajan.
- Osaat käyttää kuolleiden viestien jonoa ja kertoa, miten se vaikuttaa
  järjestykseen.
- Osaat valita jonolle rajan ja täyden jonon käsittelytavan sekä
  verrata tavallisimpia jonojärjestelmiä.
