# Soketit ja TCP-yhteys

Soketti on yhteyden päätepiste, jonka ydin antaa ohjelmalle
tiedostokuvaajana. Berkeleyn sokettirajapinta syntyi 4.2BSD:ssä
vuonna 1983, ja se on sittemmin standardoitu POSIXissa. Sama rajapinta
palvelee TCP:tä, UDP:tä, UNIX-soketteja ja monia muita protokollia:
`socket`-kutsun kolme argumenttia valitsevat osoiteperheen, soketin
tyypin ja protokollan.

| Argumentti | Yleiset arvot | Merkitys |
|---------------|-------------------------------|-------------------------------|
| perhe (domain) | `AF_INET`, `AF_INET6`, `AF_UNIX` | osoitteen muoto |
| tyyppi | `SOCK_STREAM`, `SOCK_DGRAM` | tavuvirta vai datagrammit |
| protokolla | 0 | perheen ja tyypin oletus (TCP tai UDP) |

TCP-yhteydellä on kaksi roolia. *Palvelin* luo soketin, sitoo sen
osoitteeseen (`bind`), alkaa kuunnella (`listen`) ja hyväksyy
yhteyksiä (`accept`). *Asiakas* luo soketin ja yhdistää (`connect`).
Kättelyn jälkeen kummallakin on yhdistetty soketti, jolla lähetetään
(`send`) ja vastaanotetaan (`recv`), kunnes jompikumpi sulkee sen.

| Vaihe | Palvelin | Asiakas |
|---------------------|----------------------------|-------------------------|
| luonti | `socket` | `socket` |
| osoite | `bind` | (ydin valitsee) |
| odotus | `listen`, `accept` | `connect` |
| data | `recv`, `send` | `send`, `recv` |
| lopetus | `close` | `shutdown`, `close` |

## Palvelin ja asiakas

Kaikupalvelin palauttaa kaiken saamansa. Se sitoutuu
silmukkaosoitteeseen ja pyytää portin 0, jolloin ydin valitsee vapaan
portin. `getsockname` kertoo, minkä:

```{.c tiedosto="esimerkit/02-kaiku.c" osa="palvelin"}
```

Kaksi asiaa vaatii huomiota. Ensinnäkin osoiterakenteen kentät
ovat *verkon tavujärjestyksessä* (big-endian), joten portti ja osoite
muunnetaan funktioilla `htons` ja `htonl` (host to network, short ja
long) ja takaisin funktioilla `ntohs` ja `ntohl`. Toiseksi `bind`
ottaa geneerisen osoittimen `struct sockaddr *`; todellinen rakenne
on perheen mukainen (`sockaddr_in`, `sockaddr_in6`), ja pituus
kertoo, kumpi se on.

`listen`-kutsun jälkeen ydin hoitaa kättelyt itse ja panee valmiit
yhteydet jonoon. `accept` ottaa jonosta seuraavan ja palauttaa *uuden*
soketin; kuunteleva soketti jää ennalleen odottamaan seuraavia.
Palvelin lukee, kunnes `recv` palauttaa 0, mikä tarkoittaa, että
vastapuoli on sulkenut oman lähetyssuuntansa:

```{.c tiedosto="esimerkit/02-kaiku.c" osa="palvele"}
```

Asiakas tekee saman toisin päin. Se muuntaa tekstimuotoisen osoitteen
binääriseksi funktiolla `inet_pton` (presentation to network) ja
yhdistää. Asiakas ei kutsu `bind`-funktiota, vaan ydin valitsee sille
lähdeosoitteen ja lyhytaikaisen portin (engl. ephemeral port,
Linuxissa oletuksena 32768–60999):

```{.c tiedosto="esimerkit/02-kaiku.c" osa="asiakas"}
```

```{.tuloste tiedosto="esimerkit/02-kaiku.odotettu"}
```

Asiakas lähettää rivin ja lukee täsmälleen yhtä monta tavua takaisin
funktiolla `lue_tasan`. Se on tarpeen, koska TCP ei säilytä
lähetysten rajoja: yksi `recv` voisi palauttaa puolikkaan rivin.
Tähän palataan luvussa 3.

## Osoitteet ja getaddrinfo

Osoiterakenteita ei kannata täyttää käsin, jos ohjelman pitää toimia
sekä IPv4:llä että IPv6:lla. `getaddrinfo` muuntaa isäntänimen ja
palvelun listaksi valmiita osoiterakenteita, ja `getnameinfo` tekee
päinvastoin. Virheessä ne palauttavat oman virhekoodinsa, jonka
`gai_strerror` muuntaa tekstiksi; `errno`a ne eivät aseta:

```{.c tiedosto="esimerkit/02-osoitteet.c" osa="nayta"}
```

```{.tuloste tiedosto="esimerkit/02-osoitteet.odotettu"}
```

`AI_NUMERICHOST` kieltää nimipalvelukyselyt, joten `esimerkki.fi`
ei kelpaa. Ilman lippua `getaddrinfo` kysyisi nimeä DNS:stä
(`/etc/nsswitch.conf` määrää lähteet). Kysely voi kestää sekunteja, ja
siksi sitä ei tehdä tapahtumasilmukassa (luku 7). `sockaddr_in` on 16
ja `sockaddr_in6` 28 tavua. Rakenne `sockaddr_storage` on niin suuri,
että siihen mahtuu kumpi tahansa, joten sitä käytetään, kun perhettä
ei tiedetä etukäteen.

Nimi voi vastata useaa osoitetta, ja osa niistä voi olla
tavoittamattomia. Siksi asiakas kokeilee osoitteita järjestyksessä,
kunnes yksi onnistuu:

```{.c tiedosto="esimerkit/02-osoitteet.c" osa="yhdista"}
```

```{.c tiedosto="esimerkit/02-osoitteet.c" osa="kaytto"}
```

Kun isäntä on `nullptr`, lista sisältää silmukkaosoitteet `::1` ja
`127.0.0.1`. Testikoneessa ilman IPv6:ta `socket(AF_INET6, …)`
epäonnistuu (`EAFNOSUPPORT`), ja IPv6:lla varustetussa koneessa
`::1`:ssä ei ole kuuntelijaa (`ECONNREFUSED`). Kummassakin tapauksessa
silmukka siirtyy seuraavaan osoitteeseen ja tuloste on sama. Kun
yhteyttä ei saada nopeasti, peräkkäinen kokeilu on hidas, ja
selaimet käyttävät siksi *Happy Eyeballs* -menetelmää (RFC 8305):
IPv6- ja IPv4-yhteyttä yritetään limittäin, ja ensimmäinen
onnistunut voittaa.

Palvelin voi kuunnella molempia perheitä yhdellä soketilla:
`AF_INET6`-soketti, joka on sidottu osoitteeseen `::` ja jolta on
kytketty pois valitsin `IPV6_V6ONLY`, ottaa vastaan myös IPv4-yhteydet.
Ne näkyvät IPv4-kuvattuina IPv6-osoitteina (`::ffff:127.0.0.1`).
Oletusarvo vaihtelee järjestelmittäin, joten valitsin asetetaan aina
itse.

## Kuuntelujono

`listen`-kutsun toinen argumentti (backlog) rajaa jonoa, jossa
valmiit mutta hyväksymättömät yhteydet odottavat `accept`-kutsua.
Linuxissa yläraja on `net.core.somaxconn` (nykyään 4096), ja
`SOMAXCONN` pyytää sen. Kun jono on täynnä, ydin jättää uudet
SYN-segmentit huomiotta, ja asiakas lähettää ne uudelleen sekunnin,
kahden ja neljän sekunnin päästä. Täysi jono näkyy asiakkaalle
viiveenä eikä virheenä. Luvussa 10 tätä käytetään aikakatkaisun
esimerkkinä.

## Yhteyden sulkeminen

`close` vapauttaa kuvaajan. Jos se oli viimeinen viittaus sokettiin,
ydin lähettää jonossa olevan datan perään FIN-segmentin. `shutdown`
sen sijaan sulkee vain toisen suunnan riippumatta kuvaajien
määrästä. `SHUT_WR` on *puolisulkeminen*: "en lähetä enää, mutta
luen vielä". Sillä asiakas voi ilmaista pyynnön päättyneen ja lukea
silti vastauksen:

```{.c tiedosto="esimerkit/02-sulkeminen.c" osa="puoli"}
```

Kun vastapuoli on sulkenut yhteyden, ensimmäinen kirjoitus näyttää
onnistuvan: data menee verkkoon, ja vastapuoli vastaa siihen
RST-segmentillä. Vasta seuraava kirjoitus epäonnistuu virheellä
`EPIPE`. Samalla ydin lähettää prosessille signaalin `SIGPIPE`, jonka
oletustoiminto lopettaa prosessin:

```{.c tiedosto="esimerkit/02-sulkeminen.c" osa="epipe"}
```

Suljettu yhteys voi siis tappaa palvelimen, jos signaalia ei
käsitellä. Lippu `MSG_NOSIGNAL` estää signaalin yksittäiseltä
`send`-kutsulta (Linux; macOS:ssä on soketin valitsin `SO_NOSIGPIPE`),
ja `signal(SIGPIPE, SIG_IGN)` koko prosessilta. Otsakkeen
`kirjoita_kaikki` käyttää lippua.

Kolmas tapa on katkaista yhteys heti: kun `SO_LINGER` on päällä
nollan sekunnin ajalla, `close` hylkää lähettämättömän datan ja
lähettää RST-segmentin. Vastapuolen seuraava `recv` palauttaa virheen
`ECONNRESET`. Ydin tekee saman, jos ohjelma sulkee soketin, jonka
vastaanottopuskurissa on lukematonta dataa.

```{.c tiedosto="esimerkit/02-sulkeminen.c" osa="rst"}
```

```{.tuloste tiedosto="esimerkit/02-sulkeminen.odotettu"}
```

Ilman lippua lapsiprosessi kuoli signaaliin `PIPE` eikä ehtinyt
tulostaa toisen kirjoituksen tulosta. Ensimmäinen rivi näkyy vain,
koska esimerkki tyhjentää tulostuspuskurin (`fflush`) ennen toista
kirjoitusta.

## TIME_WAIT ja SO_REUSEADDR

Yhteyden ensin sulkenut osapuoli jää tilaan `TIME_WAIT` kahden
segmentin enimmäiselinajan ajaksi (Linuxissa 60 sekuntia). Näin
myöhästyneet segmentit eivät sotke samaa osoite- ja porttiparia
käyttävää uutta yhteyttä. Palvelin sulkee yhteydet yleensä itse, joten
sen portilla on usein yhteyksiä tässä tilassa. Kun palvelin käynnistyy
uudelleen, `bind` epäonnistuu:

```{.c tiedosto="esimerkit/02-time-wait.c" osa="sido"}
```

```{.c tiedosto="esimerkit/02-time-wait.c" osa="kulku"}
```

```{.tuloste tiedosto="esimerkit/02-time-wait.odotettu"}
```

`SO_REUSEADDR` sallii sitomisen, vaikka portilla on
`TIME_WAIT`-yhteyksiä. Linuxissa valitsimen on oltava päällä sekä
uudessa että vanhassa soketissa, joten palvelin asettaa sen aina ennen
`bind`-kutsua. Valitsin ei salli kahta kuuntelijaa samaan porttiin;
siihen tarvitaan `SO_REUSEPORT` (luku 7). Tilassa olevat yhteydet
näkyvät komennolla `ss -tan state time-wait`.

## Käytännössä

- **`SO_REUSEADDR` aina palvelimelle:** muuten uudelleenkäynnistys
  epäonnistuu minuutin ajan.
- **`getaddrinfo` eikä käsin täytettyjä rakenteita:** sama koodi
  toimii IPv4:llä ja IPv6:lla, ja kaikki osoitteet kokeillaan.
- **`MSG_NOSIGNAL` tai `SIGPIPE` pois:** yksi katkennut asiakas ei
  saa kaataa palvelinta. Käsittele `EPIPE` ja `ECONNRESET` tavallisina
  paluuarvoina.
- **Puolisulkeminen viestii lopun:** `shutdown(SHUT_WR)` kertoo
  vastapuolelle, ettei dataa enää tule, ja yhteydestä voi silti lukea.
- **Porttiin 0 testeissä:** ydin valitsee vapaan portin, eivätkä
  rinnakkaiset testit törmää.
- **Tarkista jokainen paluuarvo:** verkossa "ei voi tapahtua" tapahtuu
  ensimmäisenä huonona päivänä.

## Itsearviointi

- Osaat kirjoittaa TCP-palvelimen ja -asiakkaan ja selittää, mitä
  `bind`, `listen`, `accept` ja `connect` tekevät.
- Osaat muuntaa osoitteita ja portteja verkon tavujärjestykseen ja
  takaisin sekä käyttää `getaddrinfo`-funktiota osoiteperheestä
  riippumattomasti.
- Osaat selittää eron `close`- ja `shutdown`-kutsujen välillä sekä
  sen, milloin vastapuoli saa tiedoston lopun, `EPIPE`-virheen tai
  `ECONNRESET`-virheen.
- Osaat estää `SIGPIPE`-signaalin ja kertoa, miksi se on palvelimessa
  tarpeen.
- Osaat selittää `TIME_WAIT`-tilan ja käyttää `SO_REUSEADDR`-valitsinta.
