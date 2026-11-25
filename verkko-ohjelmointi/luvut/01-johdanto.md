# Johdanto {.runko-johdanto}

Verkko-ohjelma on kaksi tai useampi prosessi, jotka eivät jaa muistia
eivätkä kelloa ja joiden välissä on epäluotettava ja viiveellinen
kanava. Siksi verkko-ohjelmoinnin vaikeus ei ole sokettirajapinnan
kutsuissa, joita on vain kymmenkunta. Vaikeus on siinä, mitä
kutsujen välissä voi tapahtua: viesti saapuu paloina tai kahden viestin
tavut yhdessä, vastapuoli katoaa kesken lauseen, vastaus jää tulematta
tai tulee liian myöhään ja kaksi pyyntöä ohittaa toisensa. Tämä
tutoriaali käy läpi, miten nämä tilanteet käsitellään C:llä ja
C++:lla Linuxin sokettirajapinnan päällä.

- **Soketit:** TCP-yhteyden avaaminen ja sulkeminen, osoitteet
  osoiteperheestä riippumatta, `TIME_WAIT`, `SIGPIPE` ja `RST`.
- **Tavuvirta ja datagrammit:** osittaiset luvut ja kirjoitukset,
  viestien rajaus, UDP:n viestirajat ja luotettavuus häviöllisen
  kanavan päällä.
- **Protokollat:** tavujärjestys, TLV-koodaus, versiointi,
  vaihtuvanmittaiset kokonaisluvut ja jäsentimen kestävyys sumealla
  testauksella.
- **Moniasiakaspalvelimet:** prosessi ja säie asiakasta kohden,
  `poll`, `epoll` taso- ja reunaliipaisuineen, tapahtumasilmukka,
  ajastimet, vastapaine ja C++-korutiinit.
- **RPC ja vikasietoisuus:** oma pieni RPC pyyntötunnisteineen ja
  määräaikoineen, aikakatkaisut, keepalive, uudelleenyritys ja
  satunnaisuus, idempotenssi ja siisti sammutus.
- **Testaus:** paikalliset asiakas–palvelin-testit, vikojen injektointi
  ja vianetsinnän työkalut.

## Esitiedot ja rajaus

Tutoriaali rakentuu kahden taidon päälle. *Tietoverkot* opettaa
protokollat: IPv4 ja IPv6, portit, TCP:n kättelyn ja tilakoneen, UDP:n,
DNS:n ja liikenteen analyysin tcpdumpilla. Niitä ei toisteta, vaan
tässä katsotaan, miltä samat asiat näyttävät ohjelman sisältä.
*Käyttöjärjestelmät* opettaa tiedostokuvaajat, prosessit ja `fork`-kutsun,
säikeet ja synkronoinnin, signaalit, putket ja UNIX-soketit. Soketti on
tiedostokuvaaja, joten kaikki sieltä opittu pätee: `read`, `write`,
`close`, `dup` ja `poll` toimivat soketeille sellaisinaan.

| Taito | Näkökulma | Tässä tutoriaalissa |
|------------------|-------------------------------|----------------------------|
| Tietoverkot | protokollat, otsakkeet, tilat | mitä ohjelma näkee rajapinnasta |
| Käyttöjärjestelmät | kuvaajat, prosessit, säikeet, signaalit | palvelimen rakenne |
| Taustapalvelut | HTTP-palvelut kehyksillä | mitä kehyksen alla on |
| Palveluarkkitehtuurit | RPC ja viestinvälitys arkkitehtuurina | RPC:n toteutus |
| Kryptografia | TLS ja avaimet | salaus jätetään kirjastolle |

C ja C++ oletetaan tutuiksi taidoista *C-kieli* ja *Moderni C++*.
*Rinnakkaisohjelmointi* käsittelee muistimallit ja lukottomat
rakenteet; tässä säikeitä käytetään vain palvelimen rakennusaineena.

Tutoriaali käsittelee soketteja suoraan käyttävää ohjelmointia:
ensisijaisesti Linuxin rajapintaa, joka on POSIXin mukainen.
Linux-kohtaiset laajennukset (`epoll`, `accept4`, `signalfd`,
`timerfd`, `MSG_NOSIGNAL`) merkitään tekstissä. BSD-järjestelmissä
vastaavat palvelut tarjoaa `kqueue` ja Windowsissa I/O completion
ports, mutta rakenne on sama.

Salausta ei toteuteta itse. Tuotannossa TCP-yhteyden päälle tulee TLS
valmiilla kirjastolla (OpenSSL, BoringSSL, rustls), ja tässä opitut
asiat – kehykset, aikakatkaisut, estämätön I/O – pätevät sellaisinaan
TLS-yhteyden sisällä. Luku 8 kertoo, mitä TLS-kirjasto muuttaa
tapahtumasilmukassa. HTTP ja kehykset kuuluvat taitoon
*Taustapalvelut*.

Luvut 2–5 käsittelevät yhtä yhteyttä (soketit, tavuvirta, UDP ja
protokollan muoto), luvut 6–8 monen asiakkaan palvelemista ja luvut
9–11 sitä, mitä yhteyksien päälle rakennetaan ja miten se pidetään
toimivana: RPC, vikasietoisuus ja testaus.

## Esimerkit ja testaus

Jokainen esimerkki on itsenäinen ohjelma, joka käynnistää sekä
palvelimen että asiakkaan: toinen ajetaan `fork`-kutsulla
lapsiprosessissa ja toinen vanhemmassa. Testaaja kääntää esimerkit
GCC 14:llä ja Clang 20:llä (C23 ja C++23) varoitukset virheinä,
AddressSanitizerin ja UndefinedBehaviorSanitizerin kanssa, ja säikeitä
käyttävät esimerkit lisäksi ThreadSanitizerilla. Tulostetta verrataan
tallennettuun tulosteeseen.

Verkko-ohjelman testi on luotettava vain, jos se ei riipu ajoituksesta
eikä ympäristöstä. Siksi esimerkit noudattavat neljää sääntöä:

1. **Vain silmukkaosoite:** palvelimet kuuntelevat osoitteessa
   `127.0.0.1`, joten testi ei tarvitse verkkoa eikä näy siihen.
2. **Ytimen valitsema portti:** palvelin sitoutuu porttiin 0 ja
   kysyy saamansa portin `getsockname`-kutsulla. Kiinteä portti
   törmäisi, kun testejä ajetaan rinnakkain.
3. **Ei ajoitusta tulosteessa:** tulosteessa on tuloksia, virhekoodien
   nimiä ja totuusarvoja, ei aikoja eikä porttinumeroita. Aikarajat
   ovat väljiä, ja tapahtumien järjestys varmistetaan odottamalla,
   ei nukkumalla.
4. **Ei jumiutumista:** lapsiprosessi kuolee vanhempansa mukana, ja
   vahtikoira (`alarm`) lopettaa jumiutuneen ohjelman.

Yhteiset apufunktiot ovat otsakkeessa `verkko.h`. Virheentarkistus
noudattaa taidon *Käyttöjärjestelmät* mallia:

```{.c tiedosto="esimerkit/verkko.h" osa="tarkista"}
```

Lapsiprosessi käynnistetään ja odotetaan näin:

```{.c tiedosto="esimerkit/verkko.h" osa="prosessit"}
```

Esimerkkien alussa oleva `#define _GNU_SOURCE` avaa C23-tilassa
POSIX- ja Linux-laajennukset. `make testaa` ajaa esimerkit, ja
kehityskontissa (`.devcontainer/verkko-ohjelmointi`) on lisäksi
`strace`, `nc` ja `tcpdump` omia kokeiluja varten.
