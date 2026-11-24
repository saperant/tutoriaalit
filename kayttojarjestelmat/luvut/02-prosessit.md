# Prosessit ja järjestelmäkutsut

Prosessi on käynnissä oleva ohjelma. Ohjelmatiedosto on vain tavuja
levyllä; prosessi on ytimen tietorakenne, johon kuuluvat oma
virtuaalinen osoiteavaruus, yksi tai useampi säie rekistereineen,
avoimet tiedostokuvaajat, nykyinen hakemisto, käyttäjä- ja
ryhmätunnisteet, signaalien käsittelijät ja resurssirajat. Linuxissa
tämä *prosessin ohjauslohko* (engl. process control block) on
`struct task_struct`, ja jokaisella säikeellä on omansa.

Prosessin tunnistaa PID-numerosta. Jokaisella prosessilla on
vanhempi (PPID), joten prosessit muodostavat puun, jonka juuressa on
PID 1, yleensä `systemd` tai kontissa sen korvike. Komentorivitaidossa
puuta tarkasteltiin `ps`- ja `pstree`-komennoilla; tässä luvussa
katsotaan, miten puu syntyy ja purkautuu järjestelmäkutsuilla.

## Käyttäjätila ja ydintila

Tietokonearkkitehtuurin luvussa *Ansat ja I/O* nähtiin, että
prosessorilla on etuoikeustasot. Tavalliset ohjelmat suoritetaan
käyttäjätilassa (RISC-V:n U-taso, x86:n rengas 3), jossa
etuoikeutetut käskyt, sivutaulujen muuttaminen ja laiterekisterit
ovat kiellettyjä. Ydin suoritetaan ydintilassa (S-taso, rengas 0).
Ainoa tapa siirtyä käyttäjätilasta ytimeen on ansa: keskeytys,
poikkeus (esimerkiksi sivuvirhe) tai tarkoituksellinen
järjestelmäkutsukäsky.

### Järjestelmäkutsun polku

Kun C-ohjelma kutsuu `write(fd, puskuri, n)`, tapahtuu seuraavaa
(x86-64 Linux):

1. C-kirjaston kääre sijoittaa kutsun numeron rekisteriin `rax` (write
   on 1) ja argumentit rekistereihin `rdi`, `rsi`, `rdx` (lisää
   tarvittaessa `r10`, `r8`, `r9`).
2. Käsky `syscall` vaihtaa etuoikeustason, tallentaa paluuosoitteen ja
   hyppää ytimen sisääntulokohtaan, jonka ydin on asettanut
   käynnistyksessä erikoisrekisteriin.
3. Sisääntulokoodi vaihtaa ytimen pinoon, tallentaa käyttäjän
   rekisterit ja hakee käsittelijän järjestelmäkutsutaulukosta
   numeron perusteella.
4. Käsittelijä (`ksys_write`) tarkistaa argumentit: onko kuvaaja auki,
   onko puskuri käyttäjän muistissa. Ydin ei koskaan luota käyttäjän
   osoittimiin, vaan kopioi datan erikseen (`copy_from_user`).
5. Paluuarvo sijoitetaan rekisteriin `rax`, rekisterit palautetaan ja
   käsky `sysret` palaa käyttäjätilaan seuraavaan käskyyn.
6. Virheessä ydin palauttaa negatiivisen virhekoodin, esimerkiksi
   `-EBADF`. Kääre tallentaa sen säiekohtaiseen `errno`-muuttujaan ja
   palauttaa -1.

RISC-V:ssä sama toimii käskyllä `ecall`: numero on rekisterissä `a7`
ja argumentit rekistereissä `a0`–`a5`. Kutsujen numerot ovat
arkkitehtuurikohtaisia, joten ohjelmat käyttävät makroja kuten
`SYS_write`. Kääreen voi myös ohittaa funktiolla `syscall`:

```{.c tiedosto="esimerkit/02-jarjestelmakutsu.c" osa="kaare"}
```

Virheen tapauksessa paluuarvo on -1 ja syy `errno`ssa. Arvo on
tarkistettava heti, koska seuraava onnistunutkin kutsu saa muuttaa
sitä:

```{.c tiedosto="esimerkit/02-jarjestelmakutsu.c" osa="errno"}
```

```{.tuloste tiedosto="esimerkit/02-jarjestelmakutsu.odotettu"}
```

### Siirtymän hinta

Järjestelmäkutsu maksaa nykyprosessorilla satoja nanosekunteja, eli
satoja tavallisia käskyjä. Aikaa kuluu tilanvaihtoon, rekisterien
tallennukseen, argumenttien tarkistukseen sekä Spectre- ja
Meltdown-haavoittuvuuksien vastatoimiin, jotka voivat tyhjentää
välimuisteja ja vaihtaa sivutaulut. Siksi:

- **Puskurointi:** stdio kerää pienet kirjoitukset ja tekee yhden
  `write`-kutsun (luku 8).
- **vDSO:** ydin kartoittaa jokaiseen prosessiin pienen jaetun
  kirjaston, jonka `clock_gettime` ja `gettimeofday` lukevat ajan
  jaetusta muistista ilman ansaa.
- **Eräkutsut:** `readv`, `sendmmsg` ja `io_uring` siirtävät monta
  operaatiota yhdellä siirtymällä.

## Jäljitys straceliä

`strace` näyttää ohjelman järjestelmäkutsut argumentteineen ja
paluuarvoineen. Se käyttää `ptrace`-rajapintaa: ydin pysäyttää
jäljitettävän jokaisen kutsun alussa ja lopussa, ja strace lukee sen
rekisterit. Pieni ohjelma kirjoittaa tiedoston ja lukee sen takaisin:

```{.c tiedosto="esimerkit/02-viesti.c" osa="viesti"}
```

```{.tuloste tiedosto="esimerkit/02-viesti.odotettu"}
```

Esimerkkien Makefile kääntää ohjelman staattisesti ja jäljittää vain
tiedostokutsut. Dynaamisesti linkitetyn ohjelman jäljessä näkyisi
ensin dynaamisen linkittäjän työ: `ld.so.cache`-tiedoston ja
`libc.so.6`:n avaus ja kartoitus (ks. taito *Objektitiedostot, linkitys
ja ABI*).

```text
strace -qq -o viesti.strace -e trace=openat,read,write,close ./viesti
```

```{.tuloste tiedosto="esimerkit/jaljitys/02-viesti.odotettu"}
```

Jäljestä näkee asioita, joita lähdekoodi ei kerro: C-kirjaston `open`
on ytimelle `openat(AT_FDCWD, …)`, uusi kuvaaja saa pienimmän vapaan
numeron 3, ja `read` pyysi 64 tavua mutta sai 13. Hyödyllisiä
valitsimia ovat `-f` (seuraa lapsiprosesseja), `-c` (yhteenveto
kutsujen määristä ja ajoista), `-e trace=%file` tai `%process`
(kutsuryhmät), `-T` (kunkin kutsun kesto) ja `-p PID` (liity
käynnissä olevaan prosessiin). Jäljitys hidastaa ohjelmaa paljon,
joten ajoitusongelmat voivat kadota jäljitettäessä.

Kaikissa ympäristöissä `ptrace` ei ole sallittu: kontit ja
tietoturvamoduulit (Yama, AppArmor) rajoittavat sitä. Esimerkkien
Makefile ohittaa jäljityksen, jos strace puuttuu tai ei pääse
jäljittämään.

## fork, exec ja wait

Unix luo prosesseja kahdessa vaiheessa. `fork` kopioi kutsuvan
prosessin: lapsi saa kopion osoiteavaruudesta, avoimista kuvaajista ja
signaaliasetuksista. Kutsu palaa kahdesti: vanhemmalle se palauttaa
lapsen PID:n, lapselle nollan. `exec` korvaa prosessin ohjelman
uudella, mutta prosessi (PID, kuvaajat, vanhempi) säilyy. Erottelu
tekee helpoksi muuttaa lapsen ympäristöä ennen `exec`-kutsua:
uudelleenohjata kuvaajia, vaihtaa hakemistoa tai pudottaa oikeuksia.

```{.c tiedosto="esimerkit/02-fork.c" osa="fork"}
```

Lapsi muuttaa omaa kopiotaan muuttujasta, eikä vanhempi näe muutosta.
Muistia ei silti kopioida heti, vaan sivut jaetaan ja kopioidaan vasta
kirjoitettaessa (copy-on-write, luku 5). Vanhempi odottaa lasta
`waitpid`-kutsulla ja saa *tilasanan*, jota luetaan makroilla:

| Makro | Merkitys |
|-------|----------|
| `WIFEXITED(t)`, `WEXITSTATUS(t)` | päättyi itse; koodi 0–255 |
| `WIFSIGNALED(t)`, `WTERMSIG(t)` | signaali lopetti |
| `WIFSTOPPED(t)`, `WSTOPSIG(t)` | pysäytetty (`WUNTRACED`) |
| `WIFCONTINUED(t)` | jatkoi pysäytyksen jälkeen (`WCONTINUED`) |

Usean lapsen odotusjärjestyksen määrää vanhempi, ei se, kuka päättyy
ensin: esimerkki luo kolme lasta ja odottaa ne `waitpid`-kutsuilla
käänteisessä järjestyksessä. Kun lapsia ei ole, `wait` palauttaa
virheen `ECHILD`:

```{.tuloste tiedosto="esimerkit/02-fork.odotettu"}
```

Lapsi lopettaa `_exit`-kutsulla eikä `exit`-funktiolla. `exit` ajaa
`atexit`-käsittelijät ja tyhjentää stdio-puskurit – vanhemman kopiot
niistä. Jos puskurissa on tekstiä forkin hetkellä, se tulostuu
kahdesti:

```{.c tiedosto="esimerkit/02-puskuri.c" osa="puskuri"}
```

```{.tuloste tiedosto="esimerkit/02-puskuri.odotettu"}
```

Päätteeseen tulostettaessa stdout on rivipuskuroitu, ja rivi näkyy
kerran. Putkeen tai tiedostoon tulostettaessa puskuri tyhjenee vasta
täyttyessään, ja sama ohjelma tulostaa rivin kahdesti. Siksi
esimerkit kutsuvat `fflush(stdout)` ennen jokaista `fork`-kutsua.

### exec-perhe

`exec`-funktioiden nimet kertovat argumenttien muodon: `l` = lista
(`execl("/bin/ls", "ls", "-l", nullptr)`), `v` = taulukko, `p` =
etsi ohjelma `PATH`-muuttujan hakemistoista, `e` = anna ympäristö
erikseen. Ainoa järjestelmäkutsu on `execve`; muut ovat kirjaston
kääreitä. Onnistunut `exec` ei palaa koskaan, joten sen jälkeinen
koodi suoritetaan vain virheessä. Komentotulkkien käytäntö on lopettaa
silloin koodilla 127 (ohjelmaa ei löytynyt) tai 126 (ei suoritettava).

```{.c tiedosto="esimerkit/02-exec.c" osa="exec"}
```

Esimerkki kokeilee samalla rakenteella myös ohjelmaa, jota ei ole:
`execvp` palaa virheellä `ENOENT`, ja lapsi lopettaa koodilla 127.

Signaalin tappama lapsi ei palauta koodia. Tilasana kertoo signaalin,
ja komentotulkki näyttää sen muodossa 128 + signaalin numero:

```{.c tiedosto="esimerkit/02-exec.c" osa="tapettu"}
```

`posix_spawn` yhdistää forkin ja execin yhdeksi kutsuksi.
Toimintoluettelolla (`posix_spawn_file_actions_t`) voi silti
uudelleenohjata kuvaajia. Se on suositeltava tapa käynnistää ohjelmia
suuresta prosessista, koska glibc toteuttaa sen `clone`-kutsulla
kopioimatta sivutauluja. Esimerkin viimeinen kohta käynnistää sillä
komentotulkin, joka päättyy koodilla 3:

```{.tuloste tiedosto="esimerkit/02-exec.odotettu"}
```

Linuxissa `fork`, säikeen luonti ja `posix_spawn` ovat kaikki saman
`clone`-kutsun muunnelmia; liput kertovat, mitä jaetaan (`CLONE_VM`,
`CLONE_FILES` …). Nimiavaruuksien liput ovat konttien perusta (taito
*Virtualisointi*).

## Prosessin tilat

Prosessi (tarkemmin säie) on aina jossain seuraavista tiloista. Kirjain
on se, jonka `ps` ja `/proc/<pid>/stat` näyttävät:

| Tila | Nimi | Merkitys |
|------|------|----------|
| `R` | ajossa tai ajovalmis | suorittimella tai valmiusjonossa |
| `S` | keskeytettävä uni | odottaa tapahtumaa; signaali herättää |
| `D` | keskeytymätön uni | odottaa I/O:ta; signaali ei herätä |
| `T` | pysäytetty | `SIGSTOP` tai `SIGTSTP`; jatkuu `SIGCONT`:lla |
| `Z` | zombi | päättynyt, vanhempi ei ole vielä lukenut tilaa |

Vuorontajan kannalta ajossa oleva ja ajovalmis ovat eri tiloja, mutta
Linux käyttää molemmille samaa kirjainta. Tila luetaan
`/proc/<pid>/stat`-tiedoston kolmannesta kentästä. Ohjelman nimi
kentässä 2 voi sisältää välilyöntejä ja sulkeita, joten esimerkin
funktio `tila` hakee kirjaimen viimeisen sulkeen jälkeen.

Esimerkki vie lapsen kaikkien tilojen läpi. Lapsi ensin laskee
silmukassa, sitten nukkuu `pause`-kutsussa, vanhempi pysäyttää ja
jatkaa sen ja lopulta lopettaa sen signaalilla. `waitid`-kutsun lippu
`WNOWAIT` kertoo päättymisestä korjaamatta lasta, joten zombi ehditään
nähdä:

```{.c tiedosto="esimerkit/02-tilat.c" osa="elinkaari"}
```

```{.tuloste tiedosto="esimerkit/02-tilat.odotettu"}
```

Pitkään näkyvä `D`-tila kertoo yleensä levyn tai verkkolevyn
ongelmasta: prosessia ei saa tapettua edes `SIGKILL`illä.

## Zombit ja orvot

Päättynyt prosessi vapauttaa muistinsa ja kuvaajansa heti, mutta sen
PID ja tilasana jäävät ytimeen, kunnes vanhempi lukee ne
`wait`-kutsulla. Tällainen *zombi* ei kuluta muuta kuin
prosessitaulun paikan, mutta paikkoja on rajallisesti
(`/proc/sys/kernel/pid_max`), ja palvelin, joka ei koskaan korjaa
lapsiaan, täyttää taulun lopulta. Ratkaisuja on kolme: kutsu `wait`
säännöllisesti, käsittele `SIGCHLD` (luku 12) tai aseta sen
käsittelijäksi `SIG_IGN`, jolloin ydin korjaa lapset itse.

Jos vanhempi päättyy ennen lastaan, lapsesta tulee *orpo*. Ydin
siirtää sen lähimmälle esivanhemmalle, joka on merkitty korjaajaksi
(engl. subreaper), tai muuten PID 1:lle. Init-prosessin tehtäviin
kuuluu korjata adoptoidut lapset; kontin PID 1 ei aina tee sitä, ja
siksi konteissa käytetään pieniä init-ohjelmia kuten `tini`. Esimerkki
asettaa itsensä korjaajaksi, jotta tulos ei riipu siitä, mikä
prosessi ajaa testejä:

```{.c tiedosto="esimerkit/02-orpo.c" osa="orpo"}
```

```{.tuloste tiedosto="esimerkit/02-orpo.odotettu"}
```

Lapsenlapsi odottaa putken sulkeutumista: `read` palauttaa nollan
vasta, kun kaikki kirjoituspäät on suljettu. Tämä on luotettava tapa
odottaa toisen prosessin tapahtumaa ilman ajastimia (luku 11).

## Käytännössä

- **Tarkista jokainen paluuarvo:** järjestelmäkutsu voi epäonnistua
  aina. Lue `errno` heti ja vain, kun kutsu ilmoitti virheestä.
- **`fflush` ennen `fork`-kutsua ja `_exit` lapsessa:** muuten
  stdio-puskurit tulostuvat kahdesti.
- **Korjaa lapsesi:** jokaiselle `fork`-kutsulle `wait`, tai
  `SIGCHLD`-käsittely. Zombit ovat vuoto, vaikka ne eivät vie muistia.
- **`posix_spawn` ohjelmien käynnistykseen:** se on nopeampi suuresta
  prosessista ja turvallisempi monisäikeisessä ohjelmassa kuin
  `fork` + `exec`.
- **strace ensimmäiseksi:** kun ohjelma ei löydä tiedostoa, jumittuu
  tai saa oudon virheen, `strace -f` näyttää yleensä syyn
  minuutissa.

## Itsearviointi

- Osaat kuvata järjestelmäkutsun polun käyttäjätilan kääreestä
  ytimen käsittelijään ja takaisin sekä selittää, miten virhe päätyy
  `errno`-muuttujaan.
- Osaat käyttää `fork`-, `exec`- ja `waitpid`-kutsuja ja tulkita
  tilasanan makroilla.
- Osaat nimetä prosessin tilat ja kertoa, mikä siirtää prosessin
  tilasta toiseen.
- Osaat selittää, mikä on zombi ja mikä orpo, ja miten kumpikin
  hoidetaan.
- Osaat jäljittää ohjelman järjestelmäkutsut straceliä ja lukea
  jäljestä, mitä ohjelma teki.
