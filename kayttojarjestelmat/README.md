# Käyttöjärjestelmät

Tiivis suomenkielinen tutoriaali käyttöjärjestelmän periaatteista ja
POSIX-järjestelmäohjelmoinnista C23:lla: prosessit ja
järjestelmäkutsut, säikeet ja vuorontaminen, virtuaalimuisti ja
muistinvaraajat, tiedostot, käyttäjät ja oikeudet, oma
tiedostojärjestelmä ja laitteet, prosessien välinen kommunikaatio,
signaalit sekä synkronointi ja lukkiutuminen. Ytimen keskeiset osat – vuorontaja, sivunkorvaus,
muistinvaraaja, levyn vuorontaminen ja tiedostojärjestelmä – toteutetaan
pieninä deterministisinä simulaatioina. Valmiit dokumentit:
[kayttojarjestelmat.pdf](https://saperant.github.io/tutoriaalit/materiaalit/kayttojarjestelmat.pdf)
ja pikaopas
[kayttojarjestelmat-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/kayttojarjestelmat-pikaopas.pdf).

Esitiedot: Tietokonearkkitehtuuri (etuoikeustasot, ansat, sivutaulu ja
TLB) ja C-kieli. Jatkotaidot: Rinnakkaisohjelmointi,
Verkko-ohjelmointi, Reaaliaikakäyttöjärjestelmät, Sulautettu Linux,
Virtualisointi ja
Takaisinmallinnus.

## Sisältö

1. Johdanto – ytimen tehtävät ja rakenteet, esimerkit ja testaus
2. Prosessit ja järjestelmäkutsut – käyttäjä- ja ydintila, kutsun
   polku, strace, fork/exec/wait, tilat, zombit ja orvot
3. Säikeet ja kontekstinvaihto – pthreadit, säiekohtainen data,
   vapaaehtoiset ja tahattomat vaihdot, säiemallit
4. Vuorontaminen – FCFS, SJF, SRTF, RR ja prioriteetit simuloituina,
   prioriteetin inversio, MLFQ, CFS:n virtuaaliaika, monta suoritinta
5. Virtuaalimuisti ja muistikartoitukset – alueet, mmap, laiska
   varaus, sivuvirheet, copy-on-write, SIGSEGV
6. Sivunkorvaus – FIFO, LRU, Clock ja OPT, Béládyn anomalia,
   työjoukko ja ruuhkautuminen
7. Muistinvaraajat – implisiittinen lista, first ja best fit,
   pirstoutuminen, slab- ja buddy-varaaja
8. Tiedostot ja I/O – kuvaajat ja avoimet tiedostot, inodet ja linkit,
   puskurointi, fsync ja atominen tallennus
9. Käyttäjät, oikeudet ja suojaus – tunnisteet, oikeuksien
   tarkistus, setuid ja oikeuksien pudotus, kyvyt, resurssirajat,
   nimiavaruudet, cgroupit ja seccomp
10. Oma tiedostojärjestelmä – superlohko, bittikartat, inodet,
    hakemistot, tarkistus ja journalointi
11. Laitteet ja ajurit – merkki- ja lohkolaitteet, ioctl,
    pseudopääte, levyn vuorontaminen
12. Prosessien välinen kommunikaatio – putket, jaettu muisti,
    viestijonot, UNIX-soketit, kuvaajien siirto ja poll
13. Signaalit – toimitus, estäminen, jonoutuminen,
    signaaliturvallisuus, EINTR ja signalfd
14. Synkronointi – futex, mutex ja ehtomuuttuja, semafori,
    tuottaja–kuluttaja, lukijat–kirjoittajat
15. Lukkiutuminen – Coffmanin ehdot, lukkojärjestys, odotusgraafi ja
    pankkiirin algoritmi
16. Lopuksi – nyrkkisäännöt, työkalut, jatkotaidot ja lähteet

## Esimerkit

Esimerkit ovat hakemistossa `esimerkit/`. Testaaja kääntää ne GCC 14-
ja Clang 20 -kääntäjillä (`-std=c23 -Wall -Wextra -Wpedantic -Werror`,
AddressSanitizer ja UndefinedBehaviorSanitizer) ja vertaa tulosteita
`.odotettu`-tiedostoihin. Säikeitä käyttävät esimerkit ajetaan myös
ThreadSanitizerilla. Tulosteissa ei ole prosessinumeroita,
osoitteita tai aikoja, ja ytimen osat simuloidaan kiinteällä
syötteellä, joten tulosteet ovat samat joka koneella. Esimerkkien
Makefile jäljittää yhden ohjelman järjestelmäkutsut straceliä ja
ohittaa jäljityksen, jos strace puuttuu tai ptrace on estetty.

Luvun 9 esimerkit `09-tunnisteet` ja `09-kyvyt` vaihtavat prosessin
tunnisteita ja tarvitsevat siksi pääkäyttäjän oikeudet. Kehityskontissa
ne toimivat sellaisenaan; tavallisena käyttäjänä ne käynnistävät
itsensä uudelleen komennolla `sudo -n`, joten `sudo`n on toimittava
ilman salasanaa (kuten CI:ssä). Muut luvun esimerkit toimivat ilman
oikeuksia.

```text
make testaa                 # rakenteen tarkistus, esimerkit, jäljitys
make pdf                    # tutoriaali ja pikaopas PDF:ksi
make -C esimerkit           # pelkkä strace-jäljitys
make kuvat                  # kuvaajat esimerkkien tulosteista (Matplotlib)
```

Kehityskontti: `.devcontainer/kayttojarjestelmat` (mukana strace).
Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

CC BY-SA 4.0.
