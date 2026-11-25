# Verkko-ohjelmointi

Tiivis suomenkielinen tutoriaali verkkopalvelujen ja -protokollien
toteutuksesta Linuxin sokettirajapinnalla C23:lla ja C++23:lla: TCP- ja
UDP-soketit, tavuvirta ja viestien rajaus, protokollan suunnittelu ja
sarjallistaminen, moniasiakaspalvelimet prosesseilla, säikeillä, `poll`-
ja `epoll`-kutsuilla, tapahtumasilmukka ja korutiinit, oma pieni RPC
sekä aikakatkaisut, uudelleenyritys, idempotenssi ja siisti sammutus.
Valmiit dokumentit:
[verkko-ohjelmointi.pdf](https://saperant.github.io/tutoriaalit/materiaalit/verkko-ohjelmointi.pdf)
ja pikaopas
[verkko-ohjelmointi-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/verkko-ohjelmointi-pikaopas.pdf).

Esitiedot: Tietoverkot (protokollat) ja Käyttöjärjestelmät
(kuvaajat, prosessit, säikeet, signaalit). Jatkotaidot: Hajautetut
järjestelmät ja Reaaliaikaiset moninpelit.

## Sisältö

1. Johdanto – rajaus, esitiedot, esimerkit ja testaus
2. Soketit ja TCP-yhteys – palvelin ja asiakas, `getaddrinfo`,
   kuuntelujono, sulkeminen, `SIGPIPE`, RST ja `TIME_WAIT`
3. Tavuvirta ja viestien rajaus – osittaiset luvut ja kirjoitukset,
   pituusetuliite, erotin, Naglen algoritmi
4. UDP ja luotettavuus – datagrammit, koko ja katkaisu, yhdistetty
   UDP-soketti, pysähdy ja odota -protokolla simuloidulla häviöllä
5. Protokollan suunnittelu ja sarjallistaminen – tavujärjestys,
   TLV, versiointi, varint ja zigzag, sumea testaus
6. Moniasiakaspalvelimet: prosessit ja säikeet – `fork` ja `SIGCHLD`,
   säie yhteyttä kohden, säiepooli, hitaat asiakkaat
7. Moniasiakaspalvelimet: poll ja epoll – estämätön I/O, taso- ja
   reunaliipaisu, usea ydin
8. Asynkroninen I/O – tapahtumasilmukka, ajastimet, lähtevän datan
   puskurointi ja vastapaine, TLS tapahtumasilmukassa, C++-korutiinit,
   io_uring
9. Etäproseduurikutsut – oma RPC putkituksella ja määräajoilla,
   gRPC ja Protocol Buffers, JSON-RPC
10. Vikasietoisuus ja aikakatkaisut – `connect` määräajassa,
    keepalive, uudelleenyritys ja satunnaisuus, idempotenssi, siisti
    sammutus
11. Testaus ja vianetsintä – paikalliset testit, vikojen injektointi,
    `ss`, `strace` ja `tcpdump`
12. Lopuksi – nyrkkisäännöt, työkalut, jatkotaidot ja lähteet

## Esimerkit

Esimerkit ovat hakemistossa `esimerkit/`. Jokainen ohjelma käynnistää
itse sekä palvelimen että asiakkaan (lapsiprosessi tai säie) ja käyttää
vain silmukkaosoitetta ja ytimen valitsemia portteja, joten testit
voi ajaa rinnakkain ilman verkkoa. Testaaja kääntää ne GCC 14- ja
Clang 20 -kääntäjillä (`-std=c23` ja `-std=c++23`, `-Wall -Wextra
-Wpedantic -Werror`, AddressSanitizer ja UndefinedBehaviorSanitizer),
ajaa säikeitä käyttävät myös ThreadSanitizerilla ja vertaa tulosteita
`.odotettu`-tiedostoihin. Häviöt ja sumea syöte tuotetaan kiinteällä
siemenellä, joten tulosteet ovat samat joka ajossa.

```text
make testaa                 # rakenteen tarkistus ja esimerkit
make pdf                    # tutoriaali ja pikaopas PDF:ksi
make kuvat                  # piirtää kuvaajan uudelleen (Matplotlib)
```

Kehityskontti: `.devcontainer/verkko-ohjelmointi` (mukana strace,
netcat ja tcpdump).

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

CC BY-SA 4.0.
