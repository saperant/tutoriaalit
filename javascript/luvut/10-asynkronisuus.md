# Asynkronisuus ja rinnakkaisuus {.runko-rinnakkaisuus}

JavaScript-koodia ajetaan yhdessä säikeessä. Odottavat toiminnot
(verkko, tiedostot, ajastimet) eivät pysäytä säiettä: ne käynnistetään,
ja tulos käsitellään myöhemmin, kun se on valmis. Tämä *tapahtumasilmukka*
on syy siihen, että Node käsittelee tuhansia samanaikaisia yhteyksiä
yhdellä säikeellä ilman lukkoja. Yleiset rinnakkaisuuden käsitteet ovat
taidossa *Rinnakkaisohjelmointi*.

## Tapahtumasilmukka

Silmukka ottaa jonosta tehtävän (*makrotehtävä*: ajastin, I/O-tapahtuma,
viesti) ja ajaa sen loppuun. Jokaisen tehtävän jälkeen se ajaa kaikki
*mikrotehtävät*: lupausten käsittelijät ja `queueMicrotask`-kutsut.

```{.javascript tiedosto="esimerkit/10-silmukka.js" osa="jarjestys"}
```

```{.javascript tiedosto="esimerkit/10-silmukka.js" osa="tyhjennys"}
```

```{.tuloste tiedosto="esimerkit/10-silmukka.odotettu"}
```

Seuraukset:

- Synkroninen koodi ajetaan aina loppuun ennen yhtäkään takaisinkutsua.
  Kahden `await`-kohdan välissä mikään muu koodi ei muuta tilaa.
- Ajastimen viive on vähimmäisaika, ei lupaus. Raskas laskenta tai
  loputon mikrotehtävien ketju viivästyttää kaikkea muuta.
- Noden `process.nextTick` ajetaan ennen lupauksia CommonJS-koodissa,
  mutta ES-modulin ylimmällä tasolla vasta niiden jälkeen. Järjestykseen
  ei kannata nojata; tarvittaessa käytetään `queueMicrotask`-funktiota.

Selaimen silmukka on sama, mutta makrotehtävien välissä selain voi
piirtää näytön. Pitkä tehtävä jäädyttää käyttöliittymän, joten selaimessa
työ pilkotaan tai siirretään Web Workeriin.

## Lupaukset ja async/await

Lupaus (`Promise`) on tuleva arvo: odottava, täytetty tai hylätty.
`async`-funktio palauttaa aina lupauksen, ja `await` pysäyttää funktion,
kunnes lupaus ratkeaa, vapauttaen säikeen muulle työlle.

```{.javascript tiedosto="esimerkit/10-lupaukset.js" osa="perakkain"}
```

Silmukka, jossa on `await`, tekee työt peräkkäin. Kun työt ovat
toisistaan riippumattomia, ne käynnistetään ensin ja odotetaan yhdessä.
Lupausten yhdistimet:

| Funktio | Valmis, kun | Hylätään, kun |
|---------|-------------|---------------|
| `Promise.all` | kaikki täyttyvät | ensimmäinen hylätään |
| `Promise.allSettled` | kaikki ratkeavat | ei koskaan |
| `Promise.race` | ensimmäinen ratkeaa | ensimmäinen ratkeava hylätään |
| `Promise.any` | ensimmäinen täyttyy | kaikki hylätään (`AggregateError`) |

```{.javascript tiedosto="esimerkit/10-lupaukset.js" osa="yhdistimet"}
```

```{.tuloste tiedosto="esimerkit/10-lupaukset.odotettu"}
```

`Promise.all` ei peru muita töitä, kun yksi epäonnistuu: ne jatkuvat
taustalla. Peruutus on erikseen (alla).

## Rinnakkaisuuden rajoittaminen

Tuhannen pyynnön käynnistäminen kerralla ylikuormittaa palvelun tai
loppuu tiedostokahvoihin. Rajoitin pitää käynnissä enintään *n*
työtä. Toteutus on lyhyt, koska yhteistä tilaa voi muuttaa ilman
lukkoja:

```{.javascript tiedosto="esimerkit/10-rajoitin.js" osa="rajoitin"}
```

```{.javascript tiedosto="esimerkit/10-rajoitin.js" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/10-rajoitin.odotettu"}
```

Tuotannossa sama tehdään usein kirjastolla (p-limit) tai jonolla.

## Peruutus: AbortController

Lupausta ei voi perua sinänsä. Peruutus välitetään signaalina
(`AbortSignal`), jota pitkä työ tarkistaa ja jonka Noden ja selaimen
rajapinnat (`fetch`, ajastimet, virrat, `child_process`) tuntevat:

```{.javascript tiedosto="esimerkit/10-peruutus.js" osa="peruttava"}
```

```{.javascript tiedosto="esimerkit/10-peruutus.js" osa="aikaraja"}
```

```{.tuloste tiedosto="esimerkit/10-peruutus.odotettu"}
```

`AbortSignal.timeout` antaa aikarajan, `AbortSignal.any` yhdistää
signaalit, ja signaalin `reason` kertoo syyn. Sama malli on Go:n
`context` ja .NETin `CancellationToken`: funktio, joka voi kestää
pitkään, ottaa signaalin optiona ja välittää sen eteenpäin.

## Asynkroniset iteraattorit ja putket

`for await` käy läpi asynkronisen iteroitavan, kuten virran rivit.
Async-generaattoreista koottu putki käsittelee datan alkio kerrallaan,
joten muistin käyttö ei riipu datan koosta, ja kuluttaja säätelee
tuottajan tahtia (*backpressure*):

```{.javascript tiedosto="esimerkit/10-putki.js" osa="vaiheet"}
```

```{.javascript tiedosto="esimerkit/10-putki.js" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/10-putki.odotettu"}
```

Noden virrat (`node:stream`) ovat asynkronisia iteroitavia, ja
`stream.pipeline` kytkee virtoja ja generaattoreita yhteen niin, että
virhe tai peruutus sulkee kaikki vaiheet.

## Tapahtumat

`EventEmitter` on Noden havainnoijamalli: olio ilmoittaa tapahtumista,
ja kuuntelijat reagoivat. Virrat, palvelimet ja prosessit ovat
tapahtumalähteitä.

```{.javascript tiedosto="esimerkit/10-tapahtumat.js" osa="havainnoija"}
```

```{.javascript tiedosto="esimerkit/10-tapahtumat.js" osa="once"}
```

```{.tuloste tiedosto="esimerkit/10-tapahtumat.odotettu"}
```

Kuuntelijat kutsutaan synkronisesti `emit`-kutsun aikana ja
rekisteröintijärjestyksessä. `error`-tapahtuma on erikoinen: ilman
kuuntelijaa se heitetään poikkeuksena. Kuuntelija, jota ei poisteta
(`off` tai `{ signal }`-optio), on yleinen muistivuoto.

## Säikeet

Prosessoria kuormittava työ (pakkaus, kuvankäsittely, salaus, suuret
laskut) tukkii tapahtumasilmukan. Se siirretään Worker-säikeisiin.
Säikeillä on oma muistinsa ja oma tapahtumasilmukkansa, ja ne
viestivät kopioimalla dataa (`postMessage`) tai jakamalla
`SharedArrayBuffer`-puskurin `Atomics`-operaatioin.

```{.javascript tiedosto="esimerkit/10-saikeet.js" osa="saikeet"}
```

```{.tuloste tiedosto="esimerkit/10-saikeet.odotettu"}
```

Säikeen käynnistys maksaa kymmeniä millisekunteja ja muistia, joten
palvelimessa käytetään säiepoolia (esim. Piscina). Usean ytimen
hyödyntäminen I/O-painotteisessa palvelussa tehdään yleensä prosesseilla
(`node:cluster`, konttien skaalaus) eikä säikeillä.

## Käytännössä

- **`async`/`await` takaisinkutsujen ja `.then`-ketjujen sijaan.**
  Vanhat takaisinkutsurajapinnat muunnetaan `util.promisify`-funktiolla,
  ja Noden moduleista käytetään lupausversioita (`node:fs/promises`,
  `node:timers/promises`).
- **Riippumattomat työt rinnakkain** (`Promise.all`), mutta rajoitettuna,
  kun töitä on paljon.
- **Peruutussignaali jokaiselle pitkälle työlle**, ja aikaraja jokaiselle
  verkkokutsulle. Ilman aikarajaa yksi jumittunut palvelu jumittaa
  kutsujankin.
- **Älä tuki tapahtumasilmukkaa.** Synkroniset `*Sync`-funktiot sopivat
  käynnistykseen ja komentorivityökaluihin, eivät palvelimen
  pyyntökäsittelyyn. Raskas laskenta Worker-säikeeseen.
- **Virrat ja asynkroniset iteraattorit suurelle datalle**, ei koko
  tiedoston lukemista muistiin.
- **Hinta.** `await` maksaa mikrotehtävän (mikrosekunnin luokkaa), joten
  sitä ei kannata käyttää tiukassa silmukassa synkronisen arvon kanssa.
  Lupausten ja sulkeumien määrä näkyy roskienkeruussa, kun samanaikaisia
  töitä on satoja tuhansia.

## Itsearviointi

- Osaat kertoa, missä järjestyksessä synkroninen koodi, mikrotehtävät
  ja makrotehtävät ajetaan, ja miksi pitkä laskenta pysäyttää palvelimen.
- Osaat ajaa asynkroniset työt peräkkäin, rinnakkain ja rajoitetusti
  rinnakkain sekä valita sopivan lupausten yhdistimen.
- Osaat perua työn `AbortController`-oliolla ja antaa sille aikarajan.
- Osaat koota asynkronisen iteraattoriputken ja käyttää
  `EventEmitter`-havainnoijaa.
- Osaat siirtää laskennan Worker-säikeeseen.
