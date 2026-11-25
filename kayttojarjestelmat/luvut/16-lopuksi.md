# Lopuksi {.runko-lahteet}

Käyttöjärjestelmän ydin ylläpitää kolmea harhaa – oma suoritin, oma
muisti, pysyvät tiedostot – ja jakaa niiden alla rajalliset resurssit.
Tutoriaalin luvut asettuvat näiden harhojen ympärille:

| Harha | Ytimen mekanismi | Luvut |
|----------------------|-------------------------------------------|-------|
| oma suoritin | prosessit, säikeet, kontekstinvaihto, vuorontaja | 2–4 |
| oma muisti | alueet, sivuvirheet, copy-on-write, sivunkorvaus, varaajat | 5–7 |
| pysyvät tiedostot | kuvaajat, inodet, sivuvälimuisti, journal, ajurit | 8, 10–11 |
| suojaus | tunnisteet, oikeusbitit, kyvyt, rajat, eristys | 9 |
| yhteistyö eristyksestä huolimatta | IPC, signaalit, synkronointi | 12–15 |

## Nyrkkisäännöt

- **Jokainen järjestelmäkutsu voi epäonnistua.** Tarkista paluuarvo,
  lue `errno` heti ja toista `EINTR`:n jälkeen.
- **Laiskuus on ytimen perusstrategia.** Muistia ei varata ennen
  käyttöä, sivuja ei kopioida ennen kirjoitusta, levylle ei kirjoiteta
  ennen kuin on pakko. Mittaa siksi todellista käyttöä (RSS,
  sivuvirheet), älä varausta.
- **`write` ei ole tallennus.** Pysyvyys vaatii `fsync`-kutsun, ja
  atominen korvaus väliaikaisen tiedoston ja `rename`-kutsun.
- **Sulje mitä et tarvitse.** Käyttämättömät putken päät estävät
  tiedoston lopun, ja periytyvät kuvaajat vuotavat lapsille:
  `O_CLOEXEC` jokaiseen avaukseen.
- **Signaalinkäsittelijä tekee vain merkinnän.** Työ tehdään
  pääsilmukassa; `signalfd` tai self-pipe yhdistää signaalit muihin
  tapahtumiin.
- **Pienin riittävä oikeus.** Avaa etuoikeutetut resurssit ensin,
  pudota oikeudet pysyvästi ja tarkista jokainen paluuarvo.
- **Jaettu data vaatii synkronoinnin, ja lukot vaativat järjestyksen.**
  Odota ehtoa silmukassa, pidä kriittiset alueet lyhyinä ja lukitse
  aina samassa järjestyksessä.
- **Simuloi ytimen algoritmit ennen kuin päättelet.** Vuorontajan,
  sivunkorvauksen ja varaajan käytös riippuu kuormasta yllättävän
  paljon, ja pieni deterministinen simulaatio näyttää sen.

## Työkalut

| Kysymys | Työkalu |
|--------------------------------|----------------------------------------|
| mitä kutsuja ohjelma tekee | `strace -f`, `strace -c` |
| missä tilassa prosessi on | `/proc/<pid>/stat`, `ps -o stat`, `top` |
| mitä muistia prosessilla on | `/proc/<pid>/maps`, `smaps`, `pmap` |
| sivuvirheet ja vaihdot | `getrusage`, `/usr/bin/time -v`, `perf stat` |
| avoimet kuvaajat | `/proc/<pid>/fd`, `lsof` |
| tunnisteet, kyvyt ja rajat | `id`, `/proc/<pid>/status`, `getpcaps`, `prlimit` |
| ytimen varaajat | `/proc/slabinfo`, `slabtop`, `/proc/buddyinfo` |
| kilpatilanteet ja lukkojärjestys | ThreadSanitizer, Helgrind |

## Jatkotaidot

- **Rinnakkaisohjelmointi:** muistimallit, atomiset operaatiot,
  lukottomat tietorakenteet ja työnjako C++:lla.
- **Verkko-ohjelmointi:** soketit verkon yli, `epoll` ja
  tapahtumapohjaiset palvelimet.
- **Reaaliaikakäyttöjärjestelmät:** määräaikavuorontaminen,
  prioriteetin periytys ja ennustettava vasteaika mikro-ohjaimilla.
- **Sulautettu Linux:** ytimen kääntäminen, laitepuu, ajurit ja
  käynnistysketju.
- **Virtualisointi:** kontin rakentaminen nimiavaruuksista ja
  cgroupeista sekä hypervisorit.
- **Takaisinmallinnus:** järjestelmäkutsujen ja muistikartan
  tulkinta ohjelmien analyysissä.

## Lähteet

- Remzi H. Arpaci-Dusseau ja Andrea C. Arpaci-Dusseau: *Operating
  Systems: Three Easy Pieces*, versio 1.10, 2023,
  <https://pages.cs.wisc.edu/~remzi/OSTEP/>. Vapaasti luettava
  oppikirja; virtualisointi, rinnakkaisuus ja pysyvyys samassa
  jaottelussa kuin tässä tutoriaalissa.
- Abraham Silberschatz, Peter B. Galvin ja Greg Gagne: *Operating
  System Concepts*, 10. painos, Wiley, 2018. Vuorontamisen,
  sivunkorvauksen ja levyn vuorontamisen klassiset esimerkkijonot.
- Andrew S. Tanenbaum ja Herbert Bos: *Modern Operating Systems*,
  5. painos, Pearson, 2022. Ytimen rakenteet ja mikroytimet.
- Michael Kerrisk: *The Linux Programming Interface*, No Starch Press,
  2010. Linuxin ja POSIXin järjestelmäohjelmoinnin perusteos:
  prosessit, signaalit, IPC ja tiedostot.
- The Open Group: *POSIX.1-2024 (IEEE Std 1003.1-2024)*,
  <https://pubs.opengroup.org/onlinepubs/9799919799/>. Rajapintojen
  normatiivinen määrittely, mukaan lukien signaaliturvalliset funktiot.
- Linuxin man-sivut, <https://man7.org/linux/man-pages/>; erityisesti
  `syscall(2)`, `mmap(2)`, `signal(7)`, `signal-safety(7)`, `pipe(7)`,
  `unix(7)`, `futex(7)`, `credentials(7)`, `capabilities(7)`,
  `namespaces(7)` ja `seccomp(2)`.
- Linuxin ytimen dokumentaatio, <https://docs.kernel.org/>: *CFS
  Scheduler* ja *EEVDF Scheduler* (scheduler/), *Memory Management*
  (mm/) ja *ext4 Data Structures and Algorithms* (filesystems/ext4/).
- Russ Cox, Frans Kaashoek ja Robert Morris: *xv6: a simple, Unix-like
  teaching operating system*, MIT, <https://pdos.csail.mit.edu/6.1810/>.
  Pieni RISC-V-ydin, jonka järjestelmäkutsut, vuorontaja ja
  tiedostojärjestelmä vastaavat tämän tutoriaalin simulaatioita.
- Dennis M. Ritchie ja Ken Thompson: *The UNIX Time-Sharing System*,
  Communications of the ACM 17(7), 1974. Prosessit, `fork` ja
  inodeihin perustuva tiedostojärjestelmä alkuperäisessä muodossaan.
- Edsger W. Dijkstra: *Cooperating Sequential Processes*, EWD 123,
  1965. Semaforit, poissulkeminen ja pankkiirin algoritmi.
- E. G. Coffman, M. J. Elphick ja A. Shoshani: *System Deadlocks*,
  Computing Surveys 3(2), 1971. Lukkiutumisen neljä ehtoa.
- L. A. Bélády: *A Study of Replacement Algorithms for a
  Virtual-Storage Computer*, IBM Systems Journal 5(2), 1966. Optimaalinen
  korvausalgoritmi; anomalia julkaistiin 1969 (Bélády, Nelson ja
  Shedler, Communications of the ACM 12(6)).
- Jeff Bonwick: *The Slab Allocator: An Object-Caching Kernel Memory
  Allocator*, USENIX Summer Technical Conference, 1994.
- Marshall K. McKusick, William N. Joy, Samuel J. Leffler ja Robert S.
  Fabry: *A Fast File System for UNIX*, ACM Transactions on Computer
  Systems 2(3), 1984. Sylinteriryhmät ja paikallisuus levyllä.

## Lisenssi

Tämä tutoriaali ja sen esimerkkikoodit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0,
<https://creativecommons.org/licenses/by-sa/4.0/deed.fi>). Teosta saa
kopioida, levittää ja muokata, kunhan alkuperäinen lähde mainitaan ja
muokatut versiot jaetaan samalla lisenssillä.
