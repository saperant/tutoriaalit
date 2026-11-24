# Moniasiakaspalvelimet: poll ja epoll

Toinen tapa palvella monta asiakasta on *I/O-multipleksaus*: yksi säie
kysyy ytimeltä, mitkä kuvaajat ovat valmiita, ja käsittelee vain ne.
Kuvaaja on valmis, kun siitä voi lukea tai siihen voi kirjoittaa
estymättä. Kutsut eivät estä, joten odottava yhteys ei varaa säiettä,
vaan vain pienen tilarakenteen. Näin yksi säie voi palvella
kymmeniätuhansia yhteyksiä. Dan Kegelin vuonna 1999 nimeämä
*C10K-ongelma* – kymmenentuhatta samanaikaista yhteyttä yhdellä
koneella – ratkesi tällä mallilla, ja nginx, Redis, Node.js ja HAProxy
rakentuvat sen varaan.

## Estämätön I/O

Multipleksauksessa kaikki soketit ovat *estämättömiä*. Valmius on
vihje eikä lupaus: toinen säie, valeherätys tai jo kulunut data voi
tyhjentää puskurin ennen kuin ohjelma lukee. Estämätön kutsu palauttaa
silloin virheen `EAGAIN` (tai samanarvoisen `EWOULDBLOCK`) sen sijaan,
että pysäyttäisi koko palvelimen:

```{.c tiedosto="esimerkit/07-liipaisu.c" osa="estamaton"}
```

```{.c tiedosto="esimerkit/07-liipaisu.c" osa="eagain"}
```

Hyväksytyn soketin voi tehdä estämättömäksi suoraan kutsulla
`accept4(…, SOCK_NONBLOCK)`, ja uuden soketin tyypillä
`SOCK_STREAM | SOCK_NONBLOCK`, jolloin erillistä `fcntl`-kutsua ei
tarvita.

## select ja poll

`select` (4.2BSD) on vanhin multipleksauskutsu. Sen bittikartat
rajaavat kuvaajien numerot `FD_SETSIZE`-arvon alle (yleensä 1024),
ja kartat on rakennettava uudelleen joka kierroksella. Uudessa koodissa
sitä ei käytetä. `poll` ottaa taulukon, jossa jokainen alkio kertoo
kuvaajan ja kiinnostavat tapahtumat (`events`), ja ydin täyttää
tapahtuneet (`revents`):

```{.c tiedosto="esimerkit/07-poll.c" osa="silmukka"}
```

Yhteyden tila on rakenteessa, joka sisältää vajaan rivin puskurin.
Protokolla on luvun 6 neliöpalvelu, ja sen käsittely on yhteisessä
otsakkeessa, jota käyttävät myös tämän luvun epoll-palvelin ja luvun 8
korutiinipalvelin:

```{.c tiedosto="esimerkit/nelio.h" osa="yhteys"}
```

Kuormittaja avaa kaikki yhteydet ensin ja lähettää sitten kierroksittain
pyynnön jokaiseen ennen vastausten lukemista. Palvelimen on siis
palveltava kaikkia yhtä aikaa:

```{.c tiedosto="esimerkit/nelio.h" osa="kuormita"}
```

```{.tuloste tiedosto="esimerkit/07-poll.odotettu"}
```

Poistossa viimeinen alkio siirretään poistetun paikalle, jotta
taulukko pysyy tiiviinä. Siirretty alkio käsitellään vielä samalla
kierroksella. `poll`-kutsun heikkous on, että koko taulukko
kopioidaan ytimeen joka kierroksella ja ydin käy sen läpi, vaikka
valmiina olisi yksi kuvaaja. Kymmenillä yhteyksillä tällä ei ole
väliä, kymmenillätuhansilla on.

## epoll

`epoll` (Linux 2.6) jakaa työn kahtia. `epoll_ctl` lisää, muuttaa ja
poistaa seurattavia kuvaajia ytimen pitämään joukkoon kerran, ja
`epoll_wait` palauttaa vain valmiit. Kierroksen hinta riippuu siis
valmiiden määrästä eikä kaikkien. Jokaiseen kuvaajaan voi liittää
64-bittisen arvon (`data`), tyypillisesti osoittimen yhteyden
tilaan, joten valmiin kuvaajan tila löytyy ilman hakua.

### Taso- ja reunaliipaisu

epollilla on kaksi tilaa. *Tasoliipaisu* (oletus) ilmoittaa kuvaajasta
niin kauan kuin siinä on luettavaa, kuten `poll`. *Reunaliipaisu*
(`EPOLLET`) ilmoittaa vain muutoksesta: kun uutta dataa saapuu.
Esimerkki seuraa samaa sokettia kahdella epoll-oliolla:

```{.c tiedosto="esimerkit/07-liipaisu.c" osa="tilat"}
```

```{.tuloste tiedosto="esimerkit/07-liipaisu.odotettu"}
```

Kun kymmenen tavua oli luettu ja 90 oli jäljellä, tasoliipaisu
ilmoitti yhä, mutta reunaliipaisu ei. Jos reunaliipaisua käyttävä
ohjelma lukee vain osan, loput jäävät puskuriin, eikä ilmoitusta
tule ennen kuin vastapuoli lähettää lisää – mahdollisesti ei koskaan.
Reunaliipaisussa luetaan siksi aina, kunnes `recv` palauttaa
`EAGAIN`:

```{.c tiedosto="esimerkit/07-liipaisu.c" osa="tyhjenna"}
```

Reunaliipaisu säästää turhia herätyksiä, kun ohjelma ei halua lukea
kaikkea heti (esimerkiksi vastapaineen vuoksi). Tasoliipaisu on
helpompi oikein: lukematon data muistuttaa itsestään. Lippu
`EPOLLRDHUP` kertoo erikseen, että vastapuoli on sulkenut
lähetyssuuntansa:

```{.c tiedosto="esimerkit/07-liipaisu.c" osa="sulkeminen"}
```

### Palvelin epollilla

Kuunteleva soketti on samassa joukossa kuin yhteydet. Sen tilan
osoitin on nolla, joten se erotetaan yhteyksistä. Reunaliipaisussa
myös hyväksyminen tehdään, kunnes jono on tyhjä:

```{.c tiedosto="esimerkit/07-epoll.c" osa="hyvaksy"}
```

```{.c tiedosto="esimerkit/07-epoll.c" osa="lue"}
```

```{.c tiedosto="esimerkit/07-epoll.c" osa="silmukka"}
```

```{.tuloste tiedosto="esimerkit/07-epoll.odotettu"}
```

Kuvaajan sulkeminen poistaa sen epoll-joukosta vain, jos se oli
viimeinen viittaus avoimeen tiedostoon. Jos kuvaaja on kopioitu
(`dup`, `fork`), joukossa on yhä merkintä, ja `epoll_wait` voi
palauttaa tapahtumia jo vapautetulle tilalle. Varmempaa on kutsua
`EPOLL_CTL_DEL` ennen sulkemista. Saman kierroksen myöhemmissä
tapahtumissa voi myös olla osoitin juuri vapautettuun tilaan, jos
yhden yhteyden käsittely sulkee toisen. Yleinen ratkaisu on merkitä
tila suljetuksi ja vapauttaa se vasta kierroksen lopussa.

## Usea säie ja usea ydin

Yksi tapahtumasilmukka käyttää yhtä suoritinydintä. Moniydinkoneessa
on kaksi tavallista rakennetta:

- **Silmukka ydintä kohden:** jokaisella säikeellä on oma epoll-joukko
  ja oma kuunteleva soketti samassa portissa (`SO_REUSEPORT`), ja ydin
  jakaa uudet yhteydet säikeille. nginx ja monet välityspalvelimet
  toimivat näin, eikä säikeiden välillä ole lukkoja.
- **Yhteinen joukko:** monta säiettä odottaa samaa epoll-joukkoa.
  `EPOLLONESHOT` varmistaa, että vain yksi säie saa kuvaajan
  tapahtuman, ja kuvaaja aktivoidaan uudelleen käsittelyn jälkeen.
  `EPOLLEXCLUSIVE` estää kaikkien säikeiden heräämisen samaan
  tapahtumaan (thundering herd).

Muiden järjestelmien vastineet ovat `kqueue` (BSD:t, macOS) ja I/O
completion ports (Windows). Kirjastot libuv, libevent ja Boost.Asio
kätkevät erot yhteisen rajapinnan taakse.

## Käytännössä

- **Kaikki estämättömiksi:** yksikin estävä kutsu tapahtumasilmukassa
  pysäyttää kaikki yhteydet. Tämä koskee myös nimipalvelukyselyjä,
  levy-I/O:ta ja raskasta laskentaa – ne siirretään työsäikeille.
- **`EAGAIN` on normaali tulos:** valmius on vihje, ja jokainen luku
  ja kirjoitus voi silti palauttaa `EAGAIN`.
- **Reunaliipaisussa tyhjennä aina:** lue ja hyväksy `EAGAIN`iin
  asti, tai tapahtumat katoavat.
- **Tila osoittimeen:** `epoll_event.data.ptr` osoittaa yhteyden
  rakenteeseen. Vapauta rakenne vasta, kun kuvaaja on poistettu
  joukosta.
- **Mittaa ennen kuin valitset:** muutamalle sadalle yhteydelle
  säiemalli tai `poll` on usein yksinkertaisempi ja riittää.

## Itsearviointi

- Osaat tehdä soketin estämättömäksi ja käsitellä `EAGAIN`-tuloksen.
- Osaat kirjoittaa yksisäikeisen palvelimen `poll`-kutsulla ja
  selittää, miksi sen hinta kasvaa yhteyksien määrän mukana.
- Osaat käyttää epollia ja selittää taso- ja reunaliipaisun eron sekä
  sen, miksi reunaliipaisussa luetaan `EAGAIN`iin asti.
- Osaat kertoa, miten tapahtumasilmukka skaalataan usealle ytimelle
  `SO_REUSEPORT`-, `EPOLLONESHOT`- ja `EPOLLEXCLUSIVE`-valitsimilla.
