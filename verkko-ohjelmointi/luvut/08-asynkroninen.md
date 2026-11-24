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

- Osaat rakentaa tapahtumasilmukan, joka kutsuu kuvaajiin
  rekisteröityjä käsittelijöitä, ja selittää reaktori- ja
  proaktorimallin eron.
- Osaat puskuroida lähtevän datan, käyttää `EPOLLOUT`-ilmoitusta vain
  tarvittaessa ja toteuttaa vastapaineen.
- Osaat käyttää `timerfd`- ja `signalfd`-kuvaajia tapahtumasilmukassa.
- Osaat kirjoittaa yksinkertaisen palvelimen C++-korutiineina ja kertoa,
  mitä `co_await` tekee ja mitä se ei muuta.
