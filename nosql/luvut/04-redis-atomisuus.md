# Redis: atomisuus, virrat ja pysyvyys

Yksittäinen Redis-komento on atominen, mutta sovellusten logiikka on
harvoin yksi komento. Tämä luku näyttää, miten useampi operaatio
tehdään turvallisesti, miten Redisiä käytetään viestijonona ja mitä
datalle tapahtuu, kun palvelin kaatuu.

## Kadonnut päivitys

Kaksi asiakasta myy saman tuotteen yhtä aikaa. Kumpikin lukee varaston,
vähentää yhden ja kirjoittaa tuloksen:

```{.python tiedosto="esimerkit/luku04/kilpailu.py" osa="kadonnut"}
```

Kaksi myyntiä vähensi varastoa yhdellä: toinen päivitys katosi.
Virhe on sama kuin relaatiotietokannassa ilman lukitusta tai
sopivaa eristystasoa (*SQL ja relaatiotietokannat*), mutta Redisissä
ei ole eristystasoja, joiden taakse piiloutua.

Yksinkertaisin korjaus on tehdä laskutoimitus palvelimella:

```{.python tiedosto="esimerkit/luku04/kilpailu.py" osa="atominen"}
```

## Optimistinen lukitus: WATCH ja MULTI

Kun päivitys riippuu luetusta arvosta monimutkaisemmin, Redisin
transaktio auttaa. `MULTI` aloittaa jonon, ja `EXEC` suorittaa jonon
komennot yhtenä atomisena kokonaisuutena. `WATCH` tekee siitä
optimistisen: jos vahdittu avain muuttuu ennen `EXEC`iä, transaktio
hylätään, ja sovellus voi yrittää uudelleen.

```{.python tiedosto="esimerkit/luku04/kilpailu.py" osa="watch"}
```

```{.tuloste tiedosto="esimerkit/luku04/kilpailu.odotettu"}
```

Redisin transaktio ei ole relaatiotietokannan transaktio. Siinä ei
ole peruutusta: jos jokin jonon komennoista epäonnistuu suoritettaessa,
muut suoritetaan silti. Se takaa vain, että jonon komennot suoritetaan
peräkkäin ilman muiden asiakkaiden komentoja välissä.

## Lua-skriptit

Ehtoja ja silmukoita vaativa logiikka kirjoitetaan Lua-skriptiksi,
jonka Redis suorittaa atomisesti palvelimella. Skripti saa avaimet
`KEYS`-taulukossa ja muut argumentit `ARGV`-taulukossa:

```{.python tiedosto="esimerkit/luku04/skripti.py" osa="lua"}
```

Asiakas rekisteröi skriptin kerran, ja sen jälkeen kutsu lähettää vain
skriptin tiivisteen:

```{.python tiedosto="esimerkit/luku04/skripti.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/luku04/skripti.odotettu"}
```

Tarkistus ja muutos tehtiin yhdessä, joten kukaan ei voi varata samaa
tuotetta välissä. Hinta on, että skriptin ajon aikana palvelin ei
palvele muita, joten skriptin on oltava lyhyt. Redis 7 lisäsi
*funktiot* (`FUNCTION LOAD`), jotka ovat palvelimelle tallennettuja ja
nimettyjä skriptejä; periaate on sama.

Avaimet kannattaa antaa `KEYS`-taulukossa eikä muodostaa skriptin
sisällä. Redis-klusterissa palvelin tarkistaa niistä, että kaikki
avaimet ovat samassa osiossa.

## Virrat

Virta (*stream*) on Redisin lokirakenne: lisäyksiä vain loppuun,
jokaisella merkinnällä yksilöllinen, aikaan perustuva tunniste.
Kuluttajaryhmä jakaa merkinnät ryhmän jäsenille ja muistaa, mitkä
on kuitattu käsitellyiksi. Se on kevyt viestijono, kun Kafka tai
RabbitMQ olisi liian raskas.

```{.python tiedosto="esimerkit/luku04/virrat.py" osa="tuottaja"}
```

Kaksi kuluttajaa lukee ryhmässä, ja kumpikin saa eri viestit. Kuluttaja
`b` kaatuu ennen kuittausta, joten sen viestit jäävät odottamaan:

```{.python tiedosto="esimerkit/luku04/virrat.py" osa="kuluttajat"}
```

Toinen kuluttaja ottaa liian kauan odottaneet viestit haltuunsa
(`XAUTOCLAIM`) ja käsittelee ne:

```{.python tiedosto="esimerkit/luku04/virrat.py" osa="siirto"}
```

```{.tuloste tiedosto="esimerkit/luku04/virrat.odotettu"}
```

Tämä on *vähintään kerran* -toimitusta: kaatunut kuluttaja on ehkä
jo käsitellyt viestin ennen kaatumistaan, joten sama viesti voi tulla
käsitellyksi kahdesti. Käsittelyn on siksi oltava idempotentti, kuten
taidossa *Hajautetut järjestelmät* perustellaan. Virta kasvaa, kunnes
sitä lyhennetään (`XTRIM` tai `MAXLEN` lisäyksessä).

## Pysyvyys

Redisin data on muistissa. Levylle se tallennetaan kahdella tavalla,
jotka voi yhdistää:

- **RDB** on tilannekuva koko muistista. Se tehdään taustalla
  asetusten mukaan (`save 60 1000` = 60 sekunnin välein, jos vähintään
  1000 muutosta) tai komennolla. Kaatuessa menetetään kaikki
  edellisen tilannekuvan jälkeen.
- **AOF** (*append-only file*) kirjoittaa jokaisen muuttavan komennon
  lokiin, joka toistetaan käynnistyksessä. `appendfsync` päättää, kuinka
  usein loki pakotetaan levylle: `always` jokaisella kirjoituksella,
  `everysec` kerran sekunnissa tai `no` käyttöjärjestelmän päätöksellä.

Esimerkki kirjoittaa 1000 tilausta ja tappaa Redis-prosessin
signaalilla `SIGKILL` (kuin `kill -9`), jolloin Redis ei ehdi tehdä
mitään siistiä sammutusta, ja käynnistää sen uudelleen:

```{.python tiedosto="esimerkit/luku04/pysyvyys.py" osa="kokeet"}
```

```{.tuloste tiedosto="esimerkit/luku04/pysyvyys.odotettu"}
```

Ilman tallennusta ja ennen ensimmäistä RDB-tilannekuvaa kaikki
katoaa. AOF säilyttää datan. `everysec`-asetuksella prosessin
kaatuminen heti kirjoitusten jälkeen voi viedä viimeisen sekunnin
kirjoitukset: tätä kirjoittaessa kokeillussa ajossa, jossa prosessi
tapettiin välittömästi, 914 tilausta tuhannesta säilyi. Siksi
testattu esimerkki odottaa puolitoista sekuntia ennen kaatumista.

`fsync` suojaa käyttöjärjestelmän tai virran katkeamiselta. Pelkän
prosessin kaatuessa käyttöjärjestelmän välimuistiin kirjoitettu data
säilyy, mutta Redis kirjoittaa AOF:ään taustalla, joten jono voi silti
jäädä kirjoittamatta.

| Asetus | Menetys kaatuessa | Hinta |
|----------------|-------------------------|-------------------------|
| ei tallennusta | kaikki | ei mitään |
| RDB | edellisen tilannekuvan jälkeiset | tilannekuva kopioi muistin (fork) |
| AOF `everysec` | enintään noin sekunti | pieni |
| AOF `always` | ei mitään kuitattua | jokainen kirjoitus odottaa levyä |

Välimuistille riittää usein, ettei mitään tallenneta: data haetaan
uudelleen lähteestä. Jos Redis on ainoa paikka jollekin tiedolle,
tarvitaan AOF ja replikointi (luku 10).

## Käytännössä

- Älä lue, laske ja kirjoita takaisin. Käytä atomisia komentoja
  (`INCR`, `HINCRBY`, `SETNX`, `SET ... NX`) tai Lua-skriptiä.
- `WATCH`-transaktio sopii harvoin törmääviin päivityksiin; yritä
  uudelleen, kun `EXEC` hylätään, ja rajaa yritysten määrä.
- Pidä skriptit lyhyinä ja anna kaikki avaimet `KEYS`-taulukossa.
- Virtojen käsittelyn on oltava idempotentti, ja kuittaamattomia
  viestejä on valvottava (`XPENDING`).
- Valitse pysyvyys sen mukaan, mitä datan menetys maksaa: ei mitään
  välimuistille, AOF `everysec` tavalliselle datalle, `always` vain jos
  jokainen kuitattu kirjoitus on säilyttävä.

## Itsearviointi

- Osaat näyttää, miten kadonnut päivitys syntyy, ja korjata sen
  atomisella komennolla, `WATCH`-transaktiolla tai Lua-skriptillä.
- Osaat kertoa, miten Redisin `MULTI`/`EXEC` eroaa relaatiotietokannan
  transaktiosta.
- Osaat käyttää virtaa kuluttajaryhmän kanssa ja ottaa kaatuneen
  kuluttajan viestit haltuun.
- Osaat valita RDB:n ja AOF:n välillä ja kertoa, mitä kumpikin menettää
  kaatuessa.
