# Prosessien välinen kommunikaatio

Prosessit on eristetty toisistaan tarkoituksella: kummallakin on oma
osoiteavaruutensa, eikä kumpikaan näe toisen muistia. Kun prosessien
on tehtävä yhteistyötä, ydin tarjoaa niille kanavia. Ne eroavat
siinä, kulkeeko data ytimen kautta (putket, viestijonot, soketit) vai
jaetaanko muisti suoraan, säilyvätkö viestirajat ja tarvitsevatko
osapuolet yhteisen esivanhemman.

| Mekanismi | Data | Rajat | Osapuolet |
|----------------|----------------------|-------------|----------------------|
| putki | tavuvirta ytimen kautta | ei | sukulaiset (periytyvä kuvaaja) |
| nimetty putki (FIFO) | tavuvirta ytimen kautta | ei | kuka tahansa polun kautta |
| jaettu muisti | suoraan, ei kopiota | – | nimi tai periytyvä kartoitus |
| viestijono | viestit ytimen kautta | kyllä, prioriteetit | nimi |
| UNIX-soketti | virta tai viestit ytimen kautta | valittavissa | polku tai sokettipari |
| signaali | numero ja pieni arvo | – | PID (luku 13) |

## Putket

`pipe` luo kaksi kuvaajaa: lukupään ja kirjoituspään. Ydin pitää
välissä puskuria (Linuxissa oletuksena 64 KiB). Kirjoittaja estyy, kun
puskuri on täynnä, ja lukija, kun se on tyhjä. Putki on yksisuuntainen,
joten kaksisuuntaiseen keskusteluun tarvitaan kaksi:

```{.c tiedosto="esimerkit/12-putki.c" osa="putket"}
```

Tärkein yksityiskohta on käyttämättömien päiden sulkeminen. `fork`
kopioi kuvaajataulukon (luku 8), joten sen jälkeen kummallakin
prosessilla on putken molemmat päät:

```{.dot otsikko="Yksi putki vanhemmalta lapselle kolmessa vaiheessa. Numerot ovat kuvaajia: 4 on kirjoituspää ja 3 lukupää."}
digraph {
  node [shape=box, width=1.3]; nodesep=0.5;
  subgraph cluster_1 { label="1. pipe"; color=gray60;
    v1 [label="vanhempi"]; p1 [label="putki", shape=cylinder];
    v1:sw -> p1:nw [xlabel="4  "]; p1:ne -> v1:se [xlabel="  3"]; }
  subgraph cluster_2 { label="2. fork"; color=gray60;
    v2 [label="vanhempi"]; p2 [label="putki", shape=cylinder];
    l2 [label="lapsi"];
    v2:sw -> p2:nw [xlabel="4  "]; p2:ne -> v2:se [xlabel="  3"];
    p2:sw -> l2:nw [xlabel="3  "]; l2:ne -> p2:se [xlabel="  4"]; }
  subgraph cluster_3 { label="3. sulkemisten jälkeen"; color=gray60;
    v3 [label="vanhempi"]; p3 [label="putki", shape=cylinder];
    l3 [label="lapsi"];
    v3:sw -> p3:nw [xlabel="4  "]; p3:sw -> l3:nw [xlabel="3  "]; }
}
```

Lukija saa tiedoston lopun (`read` palauttaa 0) vasta, kun *kaikki*
kirjoituspään kuvaajat on suljettu. Jos lapsi jättäisi vaiheessa 2
oman kopionsa kirjoituspäästä auki, se odottaisi ikuisesti dataa
itseltään.
Komentotulkin putkiketju `a | b | c` on juuri tämä: putket, forkit,
`dup2`-kutsut ja huolellinen sulkeminen.

Kun putkella ei ole yhtään lukijaa, kirjoittaja saa signaalin
`SIGPIPE`, joka oletuksena lopettaa sen. Näin `yes | head -1`
päättyy: `head` lopettaa, ja `yes` kuolee seuraavaan kirjoitukseensa.
Palvelinohjelma ohittaa yleensä signaalin
(`signal(SIGPIPE, SIG_IGN)`) ja käsittelee kirjoituksen virheen
`EPIPE`, kuten esimerkin loppu:

```{.tuloste tiedosto="esimerkit/12-putki.odotettu"}
```

Kirjoitus, joka on enintään `PIPE_BUF` tavua, on atominen: useamman
kirjoittajan viestit eivät sekoitu toisiinsa. Suuremmat kirjoitukset
voivat lomittua. Nimetty putki (`mkfifo`) on sama asia tiedostonimen
takana, joten osapuolten ei tarvitse olla sukua.

## Jaettu muisti

Nopein tapa siirtää dataa on olla siirtämättä sitä. *Jaettu muisti*
kartoittaa samat fyysiset sivut kahden prosessin osoiteavaruuteen.
POSIXissa jaettu muistiolio luodaan `shm_open`-kutsulla, joka
palauttaa tiedostokuvaajan (Linuxissa tiedosto `/dev/shm`-hakemiston
muistitiedostojärjestelmässä). Sen koko asetetaan `ftruncate`-kutsulla
ja se kartoitetaan `mmap`-kutsulla jaettuna:

```{.c tiedosto="esimerkit/12-jaettu.c" osa="luo"}
```

Nimi poistetaan heti, mutta muisti säilyy, kunnes viimeinen kartoitus
puretaan – sama periaate kuin poistetulla mutta avoimella tiedostolla.
Näin olio ei jää järjestelmään, vaikka ohjelma kaatuisi. Sukulaisille
prosesseille riittäisi myös `mmap(MAP_SHARED | MAP_ANONYMOUS)` ennen
forkia.

Jaettu muisti ei tarjoa synkronointia. Jos usea prosessi kasvattaa
samaa laskuria, päivityksiä katoaa. Esimerkki sijoittaa siksi jaettuun
muistiin myös *semaforin*. Se on ytimen tukema laskuri: `sem_wait`
vähentää sitä ja odottaa, jos arvo on nolla, ja `sem_post` kasvattaa
sitä ja herättää odottajan. Kun alkuarvo on 1, vain yksi prosessi
kerrallaan pääsee `sem_wait`- ja `sem_post`-kutsujen väliin.
Semaforeihin ja muihin synkronointivälineisiin palataan luvussa 14;
tässä semafori alustetaan prosessien väliseksi (`pshared = 1`):

```{.c tiedosto="esimerkit/12-jaettu.c" osa="rakenne"}
```

```{.c tiedosto="esimerkit/12-jaettu.c" osa="kayta"}
```

```{.tuloste tiedosto="esimerkit/12-jaettu.odotettu"}
```

Samoin pthread-mutexin ja ehtomuuttujan voi jakaa prosessien kesken
ominaisuudella `PTHREAD_PROCESS_SHARED`. Jaetussa muistissa ei saa
olla osoittimia, koska alue voi olla kartoitettu eri osoitteeseen eri
prosesseissa; käytä siirtymiä alueen alusta.

## Viestijonot

POSIX-viestijono (`mq_open`) säilyttää viestirajat: jokainen
`mq_receive` saa täsmälleen yhden lähetetyn viestin. Viesteillä on
prioriteetti, ja jono luovuttaa aina korkeimman prioriteetin vanhimman
viestin ensin. Jonon koko on kiinteä, ja täysi jono estää lähettäjän,
mikä antaa luonnollisen vastapaineen:

```{.c tiedosto="esimerkit/12-viestijono.c" osa="ydin"}
```

Esimerkki lähettää neljä viestiä prioriteeteilla 1, 5, 3 ja 1,
yrittää viidettä täyteen jonoon estämättömänä ja tyhjentää jonon:

```{.tuloste tiedosto="esimerkit/12-viestijono.odotettu"}
```

Linuxissa viestijonon kuvaaja on tiedostokuvaaja, joten sitä voi
odottaa `poll`-kutsulla yhdessä muiden kuvaajien kanssa (ks. osio
*Monen kuvaajan odottaminen*). Vanhempi
System V -rajapinta (`msgget`, `shmget`, `semget`) tekee saman
numeroavaimilla ja on yhä yleinen, mutta sen oliot eivät ole
tiedostoja, ja ne jäävät järjestelmään ohjelman kaaduttua (`ipcs`,
`ipcrm`).

## UNIX-soketit

UNIX-soketti on paikallinen soketti: sama rajapinta kuin verkossa
(`socket`, `bind`, `connect`, `send`), mutta data kulkee vain ytimen
puskureiden kautta. Tyyppejä on kolme: `SOCK_STREAM` (tavuvirta kuten
TCP), `SOCK_DGRAM` (viestit, luotettavat paikallisesti) ja
`SOCK_SEQPACKET` (järjestetyt viestit yhteydellä). `socketpair` luo
valmiiksi yhdistetyn parin, kuten kaksisuuntaisen putken.
Datagrammiparissa kaksi `send`-kutsua tuottaa kaksi erillistä
viestiä, ja kumpikin `recv` saa yhden niistä (ks. tuloste).

UNIX-soketeilla on kaksi ominaisuutta, joita muilla kanavilla ei ole.
Ensinnäkin niillä voi lähettää *avoimen tiedostokuvaajan*
apudatana (`SCM_RIGHTS`). Vastaanottaja saa uuden kuvaajan, joka
osoittaa samaan avoimeen tiedostoon – ydin tekee käytännössä
prosessien välisen `dup`-kutsun. Näin etuoikeutettu prosessi voi avata
tiedoston tai soketin ja antaa sen rajoitetulle prosessille ilman,
että tämä saa itse oikeutta avata sitä:

```{.c tiedosto="esimerkit/12-soketti.c" osa="lahetys"}
```

Vastaanotto on peilikuva: `recvmsg` samanlaisella ohjauspuskurilla,
ja kuvaajan numero luetaan `CMSG_DATA`-kohdasta. Vanhempi lähettää
avaamansa tiedoston kuvaajan lapselle:

```{.c tiedosto="esimerkit/12-soketti.c" osa="siirto"}
```

Toiseksi palvelin voi kysyä ytimeltä yhdistäneen prosessin PID:n,
UID:n ja GID:n (`SO_PEERCRED`). Tieto tulee ytimeltä eikä asiakkaalta,
joten siihen voi luottaa pääsynvalvonnassa. Näin esimerkiksi D-Bus,
Docker-palvelu ja systemd tunnistavat asiakkaansa. Nimetty soketti
sidotaan tiedostojärjestelmän polkuun (`bind`, `listen`, `accept`
kuten TCP:ssä), ja polun oikeudet rajaavat, kuka voi yhdistää.
Esimerkin lopussa palvelin tunnistaa näin itseensä yhdistäneen
asiakkaan:

```{.tuloste tiedosto="esimerkit/12-soketti.odotettu"}
```

Sokettitiedosto on poistettava itse, eikä `bind` onnistu, jos polku
on jo olemassa. Linuxissa on lisäksi *abstrakti nimiavaruus*:
polku, joka alkaa nollatavulla, ei näy tiedostojärjestelmässä ja
katoaa itsestään, kun soketti suljetaan.

## Monen kuvaajan odottaminen

Tähän asti jokainen `read` on odottanut yhtä kuvaajaa. Palvelin, jolla
on monta asiakasta, tai ohjelma, joka seuraa sekä putkea että sokettia,
ei voi jäädä odottamaan yhtä niistä, koska data voi tulla ensin
toisesta. Ratkaisussa on kaksi osaa.

Ensimmäinen on *estämätön* kuvaaja. Lippu `O_NONBLOCK` muuttaa
kutsut `read` ja `write` niin, että ne palaavat heti virheellä
`EAGAIN`, jos ne muuten jäisivät odottamaan:

```{.c tiedosto="esimerkit/12-poll.c" osa="eagain"}
```

Pelkkä estämätön luku silmukassa polttaisi suoritinta turhaan. Toinen
osa on kutsu, joka odottaa *mitä tahansa* annetuista kuvaajista.
`poll` saa taulukon kuvaajia ja kiinnostavia tapahtumia (`POLLIN`:
luettavaa, `POLLOUT`: tilaa kirjoittaa), nukkuu, kunnes jokin niistä
on valmis tai aikaraja täyttyy, ja kertoo kentässä `revents`, mitkä.
Esimerkissä kaksi lasta kirjoittaa omaan putkeensa vanhemman
määräämässä järjestyksessä, ja vanhempi palvelee molempia yhdellä
säikeellä:

```{.c tiedosto="esimerkit/12-poll.c" osa="poll"}
```

```{.tuloste tiedosto="esimerkit/12-poll.odotettu"}
```

Kun kirjoittaja sulkee putken, `poll` ilmoittaa tapahtuman `POLLHUP`
ja `read` palauttaa 0. Koska putket, soketit, viestijonot, päätteet ja
luvun 13 `signalfd` ovat kaikki kuvaajia, sama silmukka riittää niille
kaikille. Tämä *tapahtumasilmukka* on useimpien palvelinten ja
käyttöliittymien runko. `poll` käy koko taulukon läpi joka kutsulla,
joten tuhansille yhteyksille Linuxissa käytetään `epoll`-rajapintaa,
jossa ydin muistaa seurattavat kuvaajat; se ja palvelinmallit ovat
taidon *Verkko-ohjelmointi* aihetta.

## Valinta

- **Putki:** vanhempi ja lapsi, yksisuuntainen tavuvirta,
  komentoketjut. Yksinkertaisin ja aina saatavilla.
- **UNIX-soketti:** paikallinen asiakas–palvelin-yhteys, viestirajat
  tai kuvaajien siirto, luotettava tunnistus. Hyvä oletusvalinta.
- **Jaettu muisti:** suuret datamäärät ja pieni viive (videokehykset,
  mittausdata). Vaatii erillisen synkronoinnin ja huolellisen
  rakenteen.
- **Viestijono:** prioriteetit ja vastapaine pienille viesteille,
  esimerkiksi sulautetuissa järjestelmissä.

## Käytännössä

- **Sulje käyttämättömät päät:** muuten tiedoston loppu ei koskaan tule,
  ja lukija jää odottamaan.
- **Ohita `SIGPIPE` palvelimissa:** käsittele `EPIPE` paluuarvona, älä
  anna yhden katkenneen yhteyden tappaa prosessia.
- **Poista nimet heti:** `shm_unlink`, `mq_unlink` ja `unlink` heti
  avauksen jälkeen, jos muiden ei tarvitse avata nimeä myöhemmin.
- **Ei osoittimia jaettuun muistiin:** käytä siirtymiä.
- **Tunnista asiakas ytimen avulla:** `SO_PEERCRED`, ei asiakkaan
  omaa ilmoitusta.

- **Odota kuvaajia `poll`-kutsulla, älä silmukassa:** estämätön luku
  ilman odotusta polttaa suorittimen.

## Itsearviointi

- Osaat odottaa usean kuvaajan dataa `poll`-kutsulla ja selittää, mitä
  `O_NONBLOCK` ja `EAGAIN` tarkoittavat.
- Osaat rakentaa kaksisuuntaisen putkiyhteyden vanhemman ja lapsen
  välille ja selittää, milloin lukija saa tiedoston lopun.
- Osaat luoda POSIX-jaetun muistin ja synkronoida sen käytön
  prosessien välisellä semaforilla.
- Osaat käyttää viestijonoa ja kertoa, miten prioriteetit ja täysi
  jono vaikuttavat.
- Osaat siirtää tiedostokuvaajan UNIX-soketin kautta ja tunnistaa
  yhdistäneen prosessin.
- Osaat valita tilanteeseen sopivan IPC-mekanismin ja perustella
  valinnan.
