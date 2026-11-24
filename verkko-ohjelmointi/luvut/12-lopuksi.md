# Lopuksi {.runko-lahteet}

Verkko-ohjelmoinnin rajapinta on pieni, mutta sen ympärillä on paljon
varovaisuutta. Lähes kaikki tämän tutoriaalin säännöt palautuvat
kolmeen havaintoon. Ensinnäkin TCP on tavuvirta eikä viestijono.
Toiseksi vastapuoli on vieras ohjelma, joka voi olla hidas, rikki tai
vihamielinen. Kolmanneksi jokainen odotus voi kestää ikuisesti, ellei
sille aseteta rajaa.

## Nyrkkisäännöt

1. **Kehys jokaiseen TCP-protokollaan:** pituusetuliite tai erotin, ja
   kokoraja ennen varausta.
2. **Silmukka jokaiseen luku- ja kirjoituskutsuun:** osittaiset
   siirrot ja `EINTR` ovat normaaleja.
3. **`SIGPIPE` pois ja `SO_REUSEADDR` päälle:** jokaisessa palvelimessa.
4. **`getaddrinfo` ja kaikki osoitteet:** sama koodi IPv4:lle ja
   IPv6:lle.
5. **Tiukka purkaja:** jokainen pituus rajoja vastaan; purkaja
   puhtaaksi funktioksi ja sumeaan testaukseen sanitoijien kanssa.
6. **Versio ja laajennettavuus alusta asti:** versiokenttä ja
   ohitettavat tuntemattomat kentät.
7. **Valitse rinnakkaisuusmalli kuorman mukaan:** prosessi tai säie
   yhteyttä kohden pienelle määrälle, tapahtumasilmukka suurelle.
8. **Estämättömässä silmukassa ei estetä:** nimipalvelu, levy ja
   raskas laskenta työsäikeille.
9. **Vastapaine:** rajatut puskurit ja jonot, ja täysi jono hidastaa
   tuottajaa.
10. **Aikaraja ja määräaika jokaiseen odotukseen:** yhteys, vastaus,
    koko operaatio ja joutilaisuus.
11. **Uudelleenyritys eksponentiaalisella viiveellä ja satunnaisuudella:**
    vain ohimeneviin virheisiin ja idempotentteihin operaatioihin.
12. **Siisti sammutus:** `SIGTERM` silmukkaan, kuuntelija kiinni,
    keskeneräiset loppuun.
13. **Testaa viat:** pilkottu data, katkaisu, häviö ja hidas
    vastapuoli toistettavasti.

## Työkalut

| Työkalu | Käyttö |
|------------------|----------------------------------------------------|
| `ss` | soketit, tilat, jonot ja TCP:n sisäiset tiedot |
| `strace` | järjestelmäkutsut ja niiden virheet, virheiden injektointi |
| `tcpdump`, Wireshark | verkossa kulkevat segmentit (*Tietoverkot*) |
| `nc`, `socat` | protokollan kokeilu käsin, välitykset |
| `tc netem`, Toxiproxy | viive, häviö ja katkaisut testeihin |
| AddressSanitizer, ThreadSanitizer | muisti- ja kilpavirheet |
| libFuzzer, AFL++ | purkajien sumea testaus |

## Jatkotaidot

- **Hajautetut järjestelmät:** konsensus, replikointi, kellot ja
  järjestys. Siellä vikasietoisuus laajenee yhdestä yhteydestä koko
  järjestelmään.
- **Rinnakkaisohjelmointi:** muistimallit, lukottomat rakenteet ja
  työn jako säikeille, joita tapahtumasilmukka tarvitsee raskaaseen
  työhön.
- **Taustapalvelut ja Palveluarkkitehtuurit:** HTTP-kehykset,
  viestinvälittäjät ja RPC arkkitehtuurin osana.
- **Reaaliaikaiset moninpelit:** reaaliaikainen tilan synkronointi UDP:n päällä,
  viiveen kompensointi ja ennustus.
- **Web-sovellusten tietoturva ja Palveluarkkitehtuurin tietoturva:**
  TLS,
  tunnistus ja palvelunestohyökkäysten torjunta.

## Lähteet

Kirjat:

- W. Richard Stevens, Bill Fenner, Andrew M. Rudoff: *UNIX Network
  Programming, Volume 1: The Sockets Networking API*, 3. painos.
  Addison-Wesley, 2003. Sokettiohjelmoinnin perusteos.
- Michael Kerrisk: *The Linux Programming Interface*. No Starch Press,
  2010. Luvut 56–61 käsittelevät soketit, ja `epoll` on luvussa 63.
- Brian "Beej" Hall: *Beej's Guide to Network Programming*.
  <https://beej.us/guide/bgnet/> – vapaasti luettava johdanto.
- Martin Kleppmann: *Designing Data-Intensive Applications*.
  O'Reilly, 2017. Luku 8 käsittelee hajautettujen järjestelmien vikoja.

Määrittelyt:

- RFC 9293: Transmission Control Protocol (TCP). 2022.
- RFC 768: User Datagram Protocol. 1980.
- RFC 8085: UDP Usage Guidelines. 2017. Ohjeet UDP-sovelluksille:
  koko, ruuhkanhallinta ja luotettavuus.
- RFC 8305: Happy Eyeballs Version 2. 2017.
- RFC 9000: QUIC: A UDP-Based Multiplexed and Secure Transport. 2021.
- RFC 9413: Maintaining Robust Protocols. 2023.
- POSIX.1-2024 (IEEE Std 1003.1): `socket`, `getaddrinfo`, `poll`.
  <https://pubs.opengroup.org/onlinepubs/9799919799/>
- Linuxin man-sivut: `socket(7)`, `tcp(7)`, `udp(7)`, `ip(7)`,
  `epoll(7)`, `signalfd(2)`, `timerfd_create(2)`.
  <https://man7.org/linux/man-pages/>
- JSON-RPC 2.0 Specification. <https://www.jsonrpc.org/specification>
- gRPC ja Protocol Buffers: <https://grpc.io/docs/> ja
  <https://protobuf.dev/programming-guides/encoding/>

Artikkelit:

- Andrew D. Birrell, Bruce Jay Nelson: Implementing Remote Procedure
  Calls. *ACM Transactions on Computer Systems* 2(1), 1984.
- Jim Waldo, Geoff Wyant, Ann Wollrath, Sam Kendall: A Note on
  Distributed Computing. Sun Microsystems Laboratories, 1994.
- Dan Kegel: The C10K problem. <http://www.kegel.com/c10k.html>
- Marc Brooker: Exponential Backoff And Jitter. AWS Architecture
  Blog, 2015.
- Lewis Baker: C++ Coroutines: Understanding operator co_await. 2017.
  <https://lewissbaker.github.io/>
- Jens Axboe: Efficient IO with io_uring. 2019.
  <https://kernel.dk/io_uring.pdf>

## Lisenssi

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0). Esimerkkien koodi on
saman lisenssin alainen.
