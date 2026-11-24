# Käyttöjärjestelmät

Tiivis suomenkielinen tutoriaali käyttöjärjestelmän periaatteista ja
POSIX-järjestelmäohjelmoinnista C23:lla: prosessit ja
järjestelmäkutsut, säikeet ja vuorontaminen, virtuaalimuisti ja
muistinvaraajat, tiedostot, oma tiedostojärjestelmä ja laitteet,
prosessien välinen kommunikaatio, signaalit sekä synkronointi ja
lukkiutuminen. Ytimen keskeiset osat – vuorontaja, sivunkorvaus,
muistinvaraaja, levyn vuorontaminen ja tiedostojärjestelmä – toteutetaan
pieninä deterministisinä simulaatioina. Valmiit dokumentit:
[kayttojarjestelmat.pdf](https://saperant.github.io/tutoriaalit/materiaalit/kayttojarjestelmat.pdf)
ja pikaopas
[kayttojarjestelmat-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/kayttojarjestelmat-pikaopas.pdf).

Esitiedot: Tietokonearkkitehtuuri (etuoikeustasot, ansat, sivutaulu ja
TLB) ja C-kieli. Jatkotaidot: Rinnakkaisohjelmointi,
Verkko-ohjelmointi, Reaaliaikakäyttöjärjestelmät, Sulautettu Linux ja
Takaisinmallinnus.

## Sisältö

1. Johdanto – ytimen tehtävät ja rakenteet, esimerkit ja testaus
2. Prosessit ja järjestelmäkutsut – käyttäjä- ja ydintila, kutsun
   polku, strace, fork/exec/wait, tilat, zombit ja orvot
3. Säikeet ja kontekstinvaihto – pthreadit, säiekohtainen data,
   vapaaehtoiset ja tahattomat vaihdot, säiemallit
4. Vuorontaminen – FCFS, SJF, SRTF, RR ja prioriteetit simuloituina,
   prioriteetin inversio, MLFQ, CFS:n virtuaaliaika
5. Virtuaalimuisti ja muistikartoitukset – alueet, mmap, laiska
   varaus, sivuvirheet, copy-on-write, SIGSEGV
6. Sivunkorvaus – FIFO, LRU, Clock ja OPT, Béládyn anomalia,
   työjoukko ja ruuhkautuminen
7. Muistinvaraajat – implisiittinen lista, first ja best fit,
   pirstoutuminen, slab- ja buddy-varaaja
8. Tiedostot ja I/O – kuvaajat ja avoimet tiedostot, inodet ja linkit,
   puskurointi, fsync ja atominen tallennus
9. Oma tiedostojärjestelmä – superlohko, bittikartat, inodet,
   hakemistot, tarkistus ja journalointi
10. Laitteet ja ajurit – merkki- ja lohkolaitteet, ioctl,
    pseudopääte, levyn vuorontaminen
11. Prosessien välinen kommunikaatio – putket, jaettu muisti,
    viestijonot, UNIX-soketit ja kuvaajien siirto
12. Signaalit – toimitus, estäminen, jonoutuminen,
    signaaliturvallisuus, EINTR ja signalfd
13. Synkronointi – futex, mutex ja ehtomuuttuja, semafori,
    tuottaja–kuluttaja, lukijat–kirjoittajat
14. Lukkiutuminen – Coffmanin ehdot, lukkojärjestys, odotusgraafi ja
    pankkiirin algoritmi
15. Lopuksi – nyrkkisäännöt, työkalut, jatkotaidot ja lähteet

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

```text
make testaa                 # rakenteen tarkistus, esimerkit, jäljitys
make pdf                    # tutoriaali ja pikaopas PDF:ksi
make -C esimerkit           # pelkkä strace-jäljitys
```

Kehityskontti: `.devcontainer/kayttojarjestelmat` (mukana strace).

## Lisenssi

CC BY-SA 4.0.
