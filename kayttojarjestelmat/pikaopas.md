---
title: Käyttöjärjestelmät
subtitle: Pikaopas · POSIX-kutsut, ytimen algoritmit ja sudenkuopat
---

# Järjestelmäkutsut

- Virhe: paluuarvo -1 ja syy `errno`ssa (säiekohtainen).
  pthread-funktiot palauttavat virhekoodin; `mmap` palauttaa `MAP_FAILED`.
- Lue `errno` heti; `strerror(e)` ja `strerrorname_np(e)` (GNU).
- `EINTR`: signaali keskeytti estävän kutsun → toista silmukassa.
- x86-64: numero `rax`, argumentit `rdi rsi rdx r10 r8 r9`, käsky
  `syscall`. RISC-V: `a7`, `a0`–`a5`, `ecall`.
- `strace -f -e trace=%file -o jalki.txt ./ohjelma`; `-c` yhteenveto,
  `-T` kesto, `-p PID` liity.

# Prosessit

| Kutsu | Tehtävä |
|------------------------------|------------------------------------------|
| `fork()` | kopio; palauttaa lapselle 0, vanhemmalle PID |
| `execvp(nimi, argv)` | korvaa ohjelman; palaa vain virheessä |
| `posix_spawnp(...)` | fork + exec yhdellä kutsulla |
| `waitpid(pid, &t, liput)` | odota; `WNOHANG`, `WUNTRACED`, `WCONTINUED` |
| `waitid(..., WNOWAIT)` | kurkista tilaan korjaamatta |
| `_exit(k)` | lopeta tyhjentämättä stdio-puskureita |
| `prctl(PR_SET_CHILD_SUBREAPER, 1)` | adoptoi orvot jälkeläiset |

- Tilasana: `WIFEXITED`/`WEXITSTATUS`, `WIFSIGNALED`/`WTERMSIG`,
  `WIFSTOPPED`, `WIFCONTINUED`.
- `fflush(stdout)` ennen `fork`-kutsua; lapsessa `_exit`.
- Tilat: `R` ajossa/valmis, `S` uni, `D` keskeytymätön uni,
  `T` pysäytetty, `Z` zombi. Zombi = päättynyt, ei korjattu.

# Säikeet

- `pthread_create(&s, nullptr, f, arg)`, `pthread_join(s, &tulos)`
  tai `pthread_detach(s)`.
- Jaettu: muisti, kuvaajat, käsittelijät, PID. Oma: rekisterit,
  pino, signaalimaski, TID (`gettid`), `errno`, `thread_local`.
- Vaihdot: `getrusage(RUSAGE_THREAD)` → `ru_nvcsw` (vapaaehtoiset),
  `ru_nivcsw` (tahattomat).

# Vuorontaminen

| Algoritmi | Valinta | Keskeyttää | Huomio |
|-----------|---------|------------|--------|
| FCFS | saapumisjärjestys | ei | saattueilmiö |
| SJF | lyhin työ | ei | optimaalinen odotus, nääntyminen |
| SRTF | lyhin jäljellä | kyllä | vaatii kestoarvion |
| RR | vuorotellen, kvantti $q$ | kyllä | vaste $\le (n-1)q$ |
| prioriteetti | tärkein | kyllä | ikääntäminen, inversio |
| CFS | pienin virtuaaliaika | kyllä | osuus $w_i / \sum w$ |

- Läpimeno = valmis − saapuu; odotus = läpimeno − kesto.
- CFS: $\Delta\text{vaika} = \Delta t \cdot 1024 / w$; nice 0 = 1024,
  askel ≈ ×1,25. Uusi tehtävä alkaa pienimmästä virtuaaliajasta.
- Inversio → prioriteetin periytys (`PTHREAD_PRIO_INHERIT`).

# Virtuaalimuisti

| Lippu | Merkitys |
|-------|----------|
| `MAP_PRIVATE` | copy-on-write, muutokset omia |
| `MAP_SHARED` | muutokset näkyvät muille ja tiedostossa |
| `MAP_ANONYMOUS` | ei tiedostoa, nollasivut |
| `MAP_POPULATE` | täytä heti |

- `mprotect` muuttaa oikeudet, `madvise(MADV_DONTNEED)` palauttaa
  sivut, `mincore` kertoo muistissa olevat, `msync` kirjoittaa levylle.
- Sivuvirhe: alue löytyy → nollasivu, sivuvälimuisti, COW-kopio tai
  swap. Ei aluetta tai oikeutta → `SIGSEGV`. Tiedosto lyheni → `SIGBUS`.
- `/proc/<pid>/maps`: `r-xp` koodi, `r--p` vakiot, `rw-p` data.

# Sivunkorvaus

- FIFO: vanhin. LRU: pisimpään käyttämättä. Clock: käyttöbitti,
  toinen mahdollisuus. OPT: kauimpana tulevaisuudessa (mittapuu).
- Béládyn anomalia: FIFO voi tehdä enemmän virheitä useammalla
  kehyksellä. LRU ja OPT ovat pinoalgoritmeja, eivät kärsi siitä.
- Silmukka, joka on yhden sivun muistia suurempi: LRU 100 % virheitä.
- Ruuhkautuminen: työjoukot > muisti → vähennä kuormaa.

# Varaajat

- First fit: ensimmäinen riittävä. Best fit: pienin riittävä.
- Pilko suuri lohko, yhdistä vierekkäiset vapaat (rajamerkit $O(1)$).
- Ulkoinen pirstoutuminen = 1 − suurin vapaa / vapaata yhteensä.
- Slab: saman kokoiset oliot, vapaalista olioiden sisällä, $O(1)$.
- Buddy: kahden potenssit, kaveri löytyy osoitteen bitistä.

# Tiedostot

| Kerros | Sisältö | Jaettu |
|--------|---------|--------|
| kuvaaja | numero, `FD_CLOEXEC` | prosessin säikeet |
| avoin tiedosto | sijainti, tila, `O_APPEND` | `dup`, `fork` |
| inode | koko, oikeudet, lohkot, linkit | kaikki nimet |

- Pienin vapaa numero; `dup2(fd, 1)` = uudelleenohjaus.
- Kova linkki = uusi nimi inodelle; symbolinen = polku tiedostossa.
  Data vapautuu, kun linkit = 0 eikä kukaan pidä auki.
- Atominen tallennus: väliaikainen → `write`-silmukka → `fsync` →
  `rename` → hakemiston `fsync`.
- stdio: pääte rivipuskuroitu, putki/tiedosto täysin, stderr ei.

# Tiedostojärjestelmä

- Asettelu: superlohko, inodebittikartta, lohkobittikartta,
  inodetaulu, datalohkot.
- Suurin tiedosto: (suorat + lohko/4) · lohko yhdellä epäsuoralla.
- Hakemisto = tiedosto (inode, nimi) -pareja; linkkejä 2 +
  alihakemistot.
- Kaatuminen: vuotava lohko, orpo inode, kaksoisvaraus. Korjaus
  `fsck` tai journal (sitoumus, toisto).

# Laitteet

- Merkkilaite: virta (pääte, `/dev/null`). Lohkolaite: lohkot,
  sivuvälimuisti, I/O-jono.
- `stat` → `major(st_rdev)`, `minor(st_rdev)`. `/dev/null` 1:3,
  `/dev/zero` 1:5, `/dev/full` 1:7.
- `ioctl(fd, FIONREAD, &n)`, `TIOCGWINSZ`; tuntematon → `ENOTTY`.
- Levyjono: FCFS, SSTF (nääntyminen), SCAN (hissi), C-LOOK.

# IPC

| Kanava | Valitse kun |
|------------------------------|------------------------------------------|
| `pipe` | vanhempi ja lapsi, yksisuuntainen virta |
| `socketpair`, UNIX-soketti | kaksisuuntainen, viestit, kuvaajien siirto |
| `shm_open` + `mmap` | suuri data; synkronoi itse |
| `mq_open` | viestit prioriteeteilla, vastapaine |

- Sulje käyttämättömät putken päät; EOF vasta kun kaikki
  kirjoittajat poissa. Ei lukijaa → `SIGPIPE`/`EPIPE`.
- `PIPE_BUF` (4096) tavua tai alle = atominen kirjoitus.
- `SCM_RIGHTS` siirtää kuvaajan, `SO_PEERCRED` tunnistaa vertaisen.

# Signaalit

- `sigaction`, ei `signal`. `SA_SIGINFO` lisätietoa,
  `SA_RESTART` jatkaa keskeytettyä kutsua.
- Tavalliset eivät jonoudu (bitti), `SIGRTMIN…` jonoutuvat arvoineen.
- Käsittelijässä vain async-signal-safe: `write`, `_exit`, `kill`;
  ei `printf`, `malloc`, lukkoja. Muuttujat `volatile sig_atomic_t`.
  Tallenna `errno`.
- `sigprocmask` estää, `sigpending` näyttää odottavat, `signalfd`
  lukee signaalit kuvaajasta.

# Synkronointi

```{.c tiedosto="esimerkit/13-tuottaja.c" osa="jono"}
```

- Odota ehtoa `while`-silmukassa; `signal` tai `broadcast` lukon
  sisällä.
- Semafori: P = `sem_wait`, V = `sem_post`; laskeva rajaa
  samanaikaisuuden; `sem_post` on signaaliturvallinen.
- Lukijat–kirjoittajat: valitse suosimissääntö; `pthread_rwlock_t`.

# Lukkiutuminen

- Coffman: poissulkeminen, pito ja odotus, ei pakkoriistoa,
  kehäodotus. Riko yksi.
- Lukkojärjestys: lukitse aina pienempi tunniste ensin.
- Havaitseminen: odotusgraafin sykli. Välttäminen: pankkiiri –
  myönnä vain, jos turvallinen järjestys on olemassa.
- `PTHREAD_MUTEX_ERRORCHECK` → `EDEADLK`; ThreadSanitizer →
  lock-order-inversion; `timedlock` → `ETIMEDOUT`.
