# Asynkroninen I/O

Luvun 7 palvelin luki pyynnöt ja kirjoitti vastaukset suoraan, koska
vastaukset olivat pieniä. Oikea palvelin tarvitsee enemmän: lähtevän
datan on voitava odottaa, kun vastapuoli lukee hitaasti; joutilaat
yhteydet on suljettava; signaalit ja ajastimet on otettava vastaan
samassa silmukassa. Tämä luku rakentaa pienen *tapahtumasilmukan*
(event loop), joka kutsuu rekisteröityjä käsittelijöitä, ja
kirjoittaa saman palvelinlogiikan lopuksi C++-korutiineina.

## Tapahtumasilmukka

Silmukka tietää kuvaajista vain sen, mitä käsittelijää niihin kutsutaan.
`epoll_event.data.ptr` osoittaa *kohteeseen*, jossa on
käsittelijäfunktio ja sen tila. Silmukka on näin tietämätön
protokollasta ja yhteyksistä:

```{.c tiedosto="esimerkit/08-silmukka.c" osa="silmukka"}
```

```{.dot otsikko="Reaktori. Kaikki herätteet ovat kuvaajia yhdessä epoll-joukossa. Silmukka odottaa yhdessä kohdassa ja kutsuu valmiin kuvaajan käsittelijää, joka ei saa jäädä odottamaan."}
digraph {
  rankdir=LR; nodesep=0.18; ranksep=0.5;
  k [label="kuunteleva soketti"]; y [label="yhteyssoketit"];
  t [label="timerfd"]; s [label="signalfd"];
  e [label="epoll_wait", shape=ellipse];
  hk [label="hyväksy yhteys"]; hy [label="lue, käsittele,\nkirjoita"];
  ht [label="sulje joutilas"]; hs [label="aloita sammutus"];
  k -> e; y -> e; t -> e; s -> e;
  e -> hk; e -> hy; e -> ht; e -> hs;
  hy -> e [style=dashed, constraint=false, label="takaisin odottamaan"];
}
```

Tämä on *reaktori*-malli: ydin ilmoittaa valmiudesta, ja sovellus
tekee varsinaisen I/O:n itse. Toinen malli on *proaktori*, jossa
sovellus antaa ytimelle koko operaation (lue tähän puskuriin) ja saa
ilmoituksen, kun se on valmis. Windowsin I/O completion ports ja
Linuxin io_uring ovat proaktoreita. Boost.Asio tarjoaa
proaktorirajapinnan ja toteuttaa sen Linuxissa epollilla.

## Kaikki kuvaajiksi

Silmukka odottaa vain kuvaajia, joten kaikki herätteet muutetaan
kuvaajiksi. Linuxissa tähän on omat kutsunsa:

| Heräte | Kuvaaja | Luettava data |
|-----------------|---------------------------|----------------------------|
| ajastin | `timerfd_create` | laukeamiskerrat (`uint64_t`) |
| signaali | `signalfd` | `struct signalfd_siginfo` |
| toinen säie | `eventfd` | laskuri (`uint64_t`) |
| lapsiprosessi | `pidfd_open` | luettavissa, kun lapsi päättyy |
| tiedoston muutos | `inotify_init1` | muutostapahtumat |

Siirrettävä mutta kömpelömpi vaihtoehto on *self-pipe*: signaalinkäsittelijä
kirjoittaa tavun putkeen, jonka lukupäätä silmukka seuraa.
Ajastimille tavallinen ratkaisu on myös `epoll_wait`-kutsun aikaraja:
silmukka pitää ajastimia järjestetyssä rakenteessa (keko tai
ajastinpyörä) ja odottaa enintään seuraavan laukeamiseen asti. Se
skaalautuu paremmin kuin kuvaaja jokaista ajastinta kohden.

## Lähtevän datan puskurointi

Estämätön `send` hyväksyy vain sen, mikä mahtuu soketin
lähetyspuskuriin. Kun vastapuoli lukee hitaasti tai vastaus on suuri,
loppu jää ohjelman omaan puskuriin. Ohjelma pyytää silmukalta
ilmoitusta (`EPOLLOUT`), kun ydin ottaa taas dataa vastaan. Ilmoitus
on päällä vain, kun lähtevää on jonossa: tyhjä lähetyspuskuri on aina
kirjoitettavissa, ja jatkuva `EPOLLOUT` herättäisi silmukan
tauotta.

```{.c tiedosto="esimerkit/08-silmukka.c" osa="yhteys"}
```

Samassa kohdassa toteutuu *vastapaine* (backpressure). Kun lähtevää on
jonossa yli rajan, yhteydestä ei lueta uusia pyyntöjä. Asiakas, joka
lähettää pyyntöjä nopeammin kuin lukee vastauksia, täyttää ensin
palvelimen vastaanottopuskurin, ja sitten TCP:n vuonohjaus pysäyttää
asiakkaan lähetykset. Ilman vastapainetta palvelin puskuroisi
vastauksia, kunnes muisti loppuu. Sama periaate pätee kaikkialla, missä
nopea tuottaja syöttää hidasta kuluttajaa: jono rajataan, ja täysi jono
hidastaa tuottajaa.

Soketin omat puskurit ovat ketjun osa. Ydin varaa jokaiselle
soketille lähetys- ja vastaanottopuskurin, ja TCP ilmoittaa
vastapuolelle ikkunana, paljonko vastaanottopuskuriin mahtuu. Linux
mitoittaa puskurit itse yhteyden mukaan (`net.ipv4.tcp_rmem` ja
`tcp_wmem`). Valitsimet `SO_SNDBUF` ja `SO_RCVBUF` kiinnittävät koon
ja kytkevät automaattisen mitoituksen pois, joten niitä käytetään vain
perustellusti: pienellä lähetyspuskurilla vastapaine alkaa aiemmin
(esimerkki tekee näin, jotta `EPOLLOUT` näkyy), ja suuri
vastaanottopuskuri auttaa nopealla, pitkäviiveisellä yhteydellä.
Ohjelman oma puskuri tulee näiden lisäksi, joten muistinkulutusta
arvioitaessa lasketaan kaikki kolme.

Käsittelijät reagoivat kolmeen herätteeseen: uusi yhteys, soketin
valmius ja joutilaisuusajastimen laukeaminen:

```{.c tiedosto="esimerkit/08-silmukka.c" osa="kasittelijat"}
```

Testissä on kaksi asiakasta. Lataaja pyytää neljä mebitavua, ja
palvelimen lähetyspuskuri on tarkoituksella pieni, joten lähetys
jatkuu useasta `EPOLLOUT`-tapahtumasta. Joutilas asiakas yhdistää eikä
lähetä mitään, ja palvelin sulkee sen 200 millisekunnin kuluttua:

```{.tuloste tiedosto="esimerkit/08-silmukka.odotettu"}
```

Joutilaisuusajastin nollataan aina, kun yhteys etenee kumpaan
tahansa suuntaan. Muuten suuri, hitaasti etenevä lataus katkaistaisiin
kesken. Ajastin torjuu myös luvussa 6 mainitun slowloris-hyökkäyksen:
yhteys, joka ei etene, suljetaan, eikä se varaa muuta kuin
tilarakenteen.

## TLS tapahtumasilmukassa

Tuotannossa soketin ja protokollan väliin tulee TLS-kirjasto (OpenSSL,
BoringSSL, rustls). Kirjasto ei muuta tämän luvun rakennetta, mutta se
muuttaa kolmea oletusta. Tässä ne kuvataan periaatteina; kutsut ovat
kirjaston dokumentaatiossa, ja TLS:n kättely ja varmenteen tarkistus
näytetään testattuna taidossa *Tietoverkot*.

- **Luku voi vaatia kirjoituksen ja päinvastoin.** TLS-yhteys alkaa
  kättelyllä, ja kirjasto voi joutua lähettämään omia viestejään kesken
  sovelluksen luvun. Estämättömällä soketilla kirjaston luku- ja
  kirjoitusfunktio palauttaa siksi tiedon, kumpaa valmiutta se odottaa
  (OpenSSL:ssä `SSL_ERROR_WANT_READ` ja `SSL_ERROR_WANT_WRITE`), ja
  silmukka tilaa `EPOLLIN`- tai `EPOLLOUT`-ilmoituksen sen mukaan, ei
  sen mukaan, kumpaa funktiota kutsuttiin.
- **Kirjastolla on oma puskuri.** Kirjasto lukee soketista kokonaisen
  tietueen ja voi palauttaa siitä sovellukselle vain osan. Loppu on
  kirjaston muistissa, eikä `epoll` tiedä siitä mitään. Lue siis
  silmukassa, kunnes kirjasto ilmoittaa, ettei dataa ole
  (reunaliipaisun sääntö luvusta 7 pätee tässä aina).
- **Vastapuoli on todennettava.** Salaus ilman varmenteen ja nimen
  tarkistusta suojaa vain salakuuntelulta, ei välimieheltä. Asiakkaan
  on vaadittava varmenteen tarkistus ja kerrottava kirjastolle odotettu
  palvelimen nimi; monessa kirjastossa nimen tarkistus ei ole oletuksena
  päällä. Tarkistuksen virhe on pysyvä virhe, jota ei yritetä uudelleen.

Aikarajat (luku 10) koskevat myös kättelyä: yhteys, joka on avattu
mutta jonka kättely ei etene, suljetaan joutilaisuusajastimella kuten
mikä tahansa muu.

## Takaisinkutsut ja niiden hinta

Takaisinkutsumallissa jokainen odotus katkaisee logiikan. Peräkkäinen
algoritmi "lue pyyntö, hae data, kirjoita vastaus" pilkkoutuu
käsittelijöiksi, ja tila, joka peräkkäisessä koodissa olisi
paikallisissa muuttujissa, siirtyy yhteyden rakenteeseen. Monimutkainen
protokolla muuttuu tilakoneeksi, jota on vaikea lukea ja jossa
virheenkäsittely toistuu jokaisessa käsittelijässä. JavaScriptissä
tämä tunnetaan nimellä callback hell, ja siihen on vastattu
lupauksilla (promise) ja `async`/`await`-syntaksilla.

## Korutiinit

C++20:n korutiini on funktio, joka voi keskeyttää itsensä
(`co_await`) ja jatkaa myöhemmin samasta kohdasta paikallisine
muuttujineen. Kääntäjä tekee peräkkäisestä koodista tilakoneen.
Tapahtumasilmukka pysyy samana: se vain jatkaa korutiinia
takaisinkutsun kutsumisen sijaan.

Kieli antaa mekanismin mutta ei kirjastoa, joten esimerkki määrittelee
pienimmän mahdollisen tehtävätyypin. Se käynnistyy heti ja vapauttaa
kehyksensä päättyessään:

```{.cpp tiedosto="esimerkit/08-korutiini.cpp" osa="tehtava"}
```

Reaktori tarjoaa *odotettavan* (awaitable) `luettavissa(fd)`.
`await_suspend` saa keskeytetyn korutiinin kahvan ja rekisteröi sen
epolliin kertaluonteisena (`EPOLLONESHOT`). Kun kuvaaja on valmis,
silmukka jatkaa korutiinia kahvasta:

```{.cpp tiedosto="esimerkit/08-korutiini.cpp" osa="reaktori"}
```

Nyt istunto on tavallinen silmukka. Odotus näkyy koodissa vain sanana
`co_await`, ja yhteyden tila on paikallisissa muuttujissa:

```{.cpp tiedosto="esimerkit/08-korutiini.cpp" osa="istunto"}
```

```{.tuloste tiedosto="esimerkit/08-korutiini.odotettu"}
```

Malli on edelleen yksisäikeinen: korutiinit vuorottelevat vain
`co_await`-kohdissa, joten jaettua tilaa ei tarvitse lukita niiden
välillä. Samasta syystä estävä kutsu korutiinissa pysäyttää kaikki.
Korutiinin kehys varataan keosta, ja viittausparametrit ovat vaarallisia:
jos kutsuja palaa ennen korutiinin loppua, viittaus jää roikkumaan.
Tässä reaktori elää koko ohjelman ajan. Tuotantoon kannattaa käyttää
valmista kirjastoa: Boost.Asio (myös standardoitavaksi ehdotetun
verkkorajapinnan pohja), libunifex ja C++26:n `std::execution`
tarjoavat tehtävätyypit, peruutuksen ja ajastimet.

## io_uring

Linuxin io_uring (5.1, 2019) on proaktori. Sovellus ja ydin jakavat
kaksi rengaspuskuria: sovellus kirjoittaa pyyntöjä (lue, kirjoita,
hyväksy, yhdistä) lähetysrenkaaseen, ja ydin kirjoittaa valmistuneet
täydennysrenkaaseen. Monta operaatiota voidaan lähettää yhdellä
järjestelmäkutsulla tai pollaustilassa jopa ilman kutsua, ja sama
rajapinta kattaa sekä soketit että tiedostot, joita epoll ei osaa
odottaa. Hintana on monimutkaisuus. io_uringin ydinkoodista on
löytynyt useita haavoittuvuuksia, ja siksi monet ympäristöt, kuten
Dockerin oletusasetukset ja Android, estävät sen. Kirjasto liburing
peittää matalan tason rajapinnan.

## Käytännössä

- **Yksi silmukka, kaikki herätteet kuvaajina:** soketit, ajastimet,
  signaalit ja säikeiden väliset herätteet (`eventfd`).
- **Puskuroi lähtevä data ja kytke `EPOLLOUT` vain tarpeeseen:**
  muuten silmukka pyörii tyhjää.
- **Vastapaine:** rajaa jokaisen yhteyden lähtevä puskuri ja lopeta
  lukeminen, kun raja ylittyy.
- **Joutilaisuusaikaraja jokaiselle yhteydelle:** nollaa se, kun yhteys
  etenee kumpaan tahansa suuntaan.
- **Korutiinit tai async/await monimutkaiseen logiikkaan:** peräkkäinen
  koodi on luettavampaa kuin tilakone, mutta estävät kutsut ovat yhä
  kiellettyjä.
- **Valmis kirjasto tuotantoon:** libuv, Boost.Asio tai kielen oma
  ajonaikainen ympäristö (Tokio Rustissa, asyncio Pythonissa) on
  testattu reunatapauksissa, joita oma silmukka ei vielä tunne.

## Itsearviointi

- Osaat kertoa, mitä TLS-kirjasto muuttaa tapahtumasilmukassa: valmiuden
  suunta, kirjaston oma puskuri ja vastapuolen todennus.
- Osaat rakentaa tapahtumasilmukan, joka kutsuu kuvaajiin
  rekisteröityjä käsittelijöitä, ja selittää reaktori- ja
  proaktorimallin eron.
- Osaat puskuroida lähtevän datan, käyttää `EPOLLOUT`-ilmoitusta vain
  tarvittaessa ja toteuttaa vastapaineen.
- Osaat käyttää `timerfd`- ja `signalfd`-kuvaajia tapahtumasilmukassa.
- Osaat kirjoittaa yksinkertaisen palvelimen C++-korutiineina ja kertoa,
  mitä `co_await` tekee ja mitä se ei muuta.
