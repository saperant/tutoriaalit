# Signaalit

Signaali on ytimen tapa ilmoittaa prosessille tapahtumasta
asynkronisesti: Ctrl-C päätteessä (`SIGINT`), lapsen päättyminen
(`SIGCHLD`), virheellinen muistiviittaus (`SIGSEGV`), ajastimen
laukeaminen (`SIGALRM`) tai toisen prosessin `kill`-kutsu.
Komentorivitaidossa signaaleja lähetettiin `kill`-komennolla. Tässä
luvussa niitä vastaanotetaan, ja se on vaikeampaa kuin näyttää:
signaali voi keskeyttää ohjelman missä kohdassa tahansa.

## Toimitus

Jokaisella signaalilla on *toiminto*: oletus (`SIG_DFL`), ohitus
(`SIG_IGN`) tai käsittelijäfunktio. Oletustoiminto on signaalin
mukaan lopetus, lopetus ja muistivedos (core dump), pysäytys,
jatkaminen tai ohitus. `SIGKILL`- ja `SIGSTOP`-signaalien toimintoa
ei voi muuttaa, eikä niitä voi estää.

Ydin merkitsee lähetetyn signaalin *odottavaksi* kohdesäikeelle tai
-prosessille. Toimitus tapahtuu, kun säie seuraavan kerran palaa
ytimestä käyttäjätilaan – järjestelmäkutsusta, keskeytyksestä tai
vuorontajalta. Jos toiminto on käsittelijä, ydin rakentaa käyttäjän
pinoon kehyksen, joka näyttää siltä kuin käsittelijää olisi kutsuttu
keskeytyskohdasta, ja käsittelijän palattua erityinen
`rt_sigreturn`-kutsu palauttaa alkuperäiset rekisterit.

Käsittelijä asennetaan `sigaction`-kutsulla. Vanhempi `signal`-funktio
on epämääräinen: sen käyttäytyminen eri järjestelmissä vaihtelee, joten
sitä käytetään vain asetuksiin `SIG_IGN` ja `SIG_DFL`. Lipulla
`SA_SIGINFO` käsittelijä saa lisätietoa: lähettäjän PID:n, syyn ja
`sigqueue`-kutsulla lähetetyn arvon:

```{.c tiedosto="esimerkit/13-signaalit.c" osa="kasittelija"}
```

```{.c tiedosto="esimerkit/13-signaalit.c" osa="asenna"}
```

## Estäminen ja jonoutuminen

Säikeen *signaalimaski* kertoo, mitkä signaalit ovat estettyjä.
Estetty signaali jää odottamaan, ja se toimitetaan heti, kun esto
poistetaan. Tavalliset signaalit eivät kuitenkaan jonoudu: odottavista
on vain bitti, joten kolme estettynä lähetettyä `SIGUSR1`:tä
toimitetaan yhtenä. *Reaaliaikaiset* signaalit (`SIGRTMIN` …
`SIGRTMAX`) jonoutuvat ja kantavat mukanaan arvon, ja ne toimitetaan
lähetysjärjestyksessä:

```{.c tiedosto="esimerkit/13-signaalit.c" osa="esto"}
```

```{.c tiedosto="esimerkit/13-signaalit.c" osa="ohita"}
```

```{.tuloste tiedosto="esimerkit/13-signaalit.odotettu"}
```

Jonoutumattomuudesta seuraa tärkeä sääntö: signaali kertoo, että
*jotain* tapahtui, ei montako kertaa. `SIGCHLD`-käsittelijän on siksi
korjattava silmukassa kaikki päättyneet lapset, ei vain yhtä.

Estämisellä suojataan kriittisiä kohtia: ohjelma estää signaalin,
päivittää tietorakenteen, jota käsittelijäkin käyttää, ja poistaa
eston. `sigaction`-rakenteen `sa_mask` estää lisäksi muut signaalit
käsittelijän ajaksi. `fork` perii maskin ja käsittelijät; `exec`
palauttaa käsittelijät oletuksiin mutta säilyttää maskin ja ohitukset.

## Signaaliturvallisuus

Käsittelijä voi keskeyttää ohjelman keskellä mitä tahansa funktiota,
myös `malloc`- tai `printf`-kutsua, joka on juuri muuttamassa sisäistä
tietorakennettaan tai pitää lukkoa. Jos käsittelijä kutsuu samaa
funktiota, rakenne turmeltuu tai ohjelma lukkiutuu itseensä. Siksi
käsittelijässä saa kutsua vain *async-signal-safe*-funktioita.
POSIX luettelee ne (`man 7 signal-safety`); niitä ovat muun muassa:

| Turvallinen | Ei turvallinen |
|-------------|----------------|
| `write`, `read`, `close`, `open` | `printf`, `fprintf`, `puts` |
| `_exit`, `kill`, `raise` | `exit` (ajaa `atexit`-funktiot) |
| `sigaction`, `sigprocmask` | `malloc`, `free` |
| `waitpid`, `execve`, `dup2` | `pthread_mutex_lock` |

Lisäksi käsittelijän ja ohjelman jakamat muuttujat on määriteltävä
tyypillä `volatile sig_atomic_t` (tai lukottomilla atomisilla
tyypeillä), jotta kääntäjä ei pidä arvoa rekisterissä ja kirjoitus
on kokonainen. Käsittelijän on myös säilytettävä `errno`, koska se
voi keskeyttää koodin juuri järjestelmäkutsun ja `errno`n lukemisen
välissä.

Turvallisin käsittelijä tekee vähiten: asettaa lipun tai kirjoittaa
tavun putkeen (*self-pipe trick*), ja varsinainen työ tehdään
pääsilmukassa. Esimerkin käsittelijä tekee juuri niin:

```{.c tiedosto="esimerkit/13-keskeytys.c" osa="kasittelija"}
```

## Keskeytetyt järjestelmäkutsut

Kun signaali toimitetaan säikeelle, joka on estävässä kutsussa
(`read` putkesta, `accept`, `sleep`), kutsu keskeytetään ja
käsittelijä ajetaan. Sen jälkeen kutsu joko palauttaa virheen `EINTR`
tai, jos käsittelijä asennettiin lipulla `SA_RESTART`, ydin aloittaa
kutsun uudelleen automaattisesti:

```{.c tiedosto="esimerkit/13-keskeytys.c" osa="kokeile"}
```

```{.tuloste tiedosto="esimerkit/13-keskeytys.odotettu"}
```

Ilman lippua `read` palasi heti virheellä, vaikka käsittelijä oli jo
kirjoittanut putkeen tavun. Lipun kanssa `read` jatkui ja luki tavun.
`SA_RESTART` ei koske kaikkia kutsuja: `poll`, `select`, `nanosleep`
ja aikarajalliset odotukset palauttavat aina `EINTR`. Kestävä ohjelma
toistaa siksi estävät kutsut silmukassa, kun `errno` on `EINTR`, kuten
luvun 12 esimerkki `sem_wait`-kutsulle.

## Signaalit tiedostokuvaajina

Linuxin `signalfd` kääntää koko asetelman: signaali estetään, ja se
luetaan tiedostokuvaajasta tavallisena tietueena. Käsittelijää ei ole,
joten signaaliturvallisuusongelmaakaan ei ole, ja kuvaajaa voi odottaa
`poll`- tai `epoll`-kutsulla muiden tapahtumien kanssa. Useimmat
tapahtumasilmukkakirjastot toimivat näin (tai self-pipe-tempulla
muissa järjestelmissä):

```{.c tiedosto="esimerkit/13-signalfd.c" osa="signalfd"}
```

```{.tuloste tiedosto="esimerkit/13-signalfd.odotettu"}
```

Silmukka korjaa jokaisen herätyksen jälkeen kaikki päättyneet lapset
`WNOHANG`-lipulla. Viisi `SIGCHLD`:tä voi yhdistyä yhdeksi tai
kahdeksi luettavaksi tietueeksi, mutta lopputulos on aina sama.

### Signaalit ja säikeet

Prosessille lähetetty signaali toimitetaan mille tahansa säikeelle,
joka ei estä sitä. Monisäikeisessä ohjelmassa signaalit kannattaa siksi
estää kaikissa säikeissä (maski periytyy `pthread_create`-kutsussa)
ja käsitellä yhdessä paikassa: omassa säikeessä `sigwait`-kutsulla
tai `signalfd`-kuvaajalla tapahtumasilmukassa. Laitteiston aiheuttamat
signaalit (`SIGSEGV`, `SIGFPE`) toimitetaan aina aiheuttaneelle
säikeelle.

## Käytännössä

- **`sigaction`, ei `signal`:** määritelty ja siirrettävä käytös.
- **Pidä käsittelijä minimissä:** lippu tai tavu putkeen. Ei
  `printf`iä, ei `malloc`ia, ei lukkoja.
- **Tallenna `errno` käsittelijässä:** muuten keskeytetty koodi näkee
  väärän virhekoodin.
- **Toista estävät kutsut `EINTR`:n jälkeen:** tai käytä
  `SA_RESTART`ia ja tiedä, mitkä kutsut se kattaa.
- **Korjaa lapset silmukassa:** yksi `SIGCHLD` voi edustaa monta
  päättynyttä lasta.
- **Monisäikeisessä ohjelmassa yksi signaalien käsittelypaikka:**
  `signalfd` tai `sigwait`, signaalit estettynä muualla.

## Itsearviointi

- Osaat asentaa käsittelijän `sigaction`-kutsulla ja selittää, milloin
  ydin toimittaa signaalin.
- Osaat estää signaaleja, tutkia odottavia signaaleja ja selittää,
  miksi tavalliset signaalit eivät jonoudu mutta reaaliaikaiset
  jonoutuvat.
- Osaat kirjoittaa signaaliturvallisen käsittelijän ja kertoa, miksi
  `printf` ja `malloc` eivät sovi siihen.
- Osaat käsitellä `EINTR`-virheen ja selittää `SA_RESTART`-lipun
  vaikutuksen.
- Osaat käsitellä signaaleja tiedostokuvaajan kautta `signalfd`llä.
