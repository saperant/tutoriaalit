# Palvelut ja init-järjestelmät

Laitteen varsinainen työ tehdään palveluissa: prosesseissa, jotka
lukevat antureita, puhuvat verkkoon, ohjaavat moottoreita tai
näyttävät käyttöliittymää. Init-järjestelmän tehtävä on käynnistää ne
oikeassa järjestyksessä, valvoa niitä ja pysäyttää ne hallitusti. Tässä
luvussa tehdään pieni init-järjestelmä, jonka jokainen osa vastaa
jotakin oikeiden järjestelmien ominaisuutta, ja verrataan sitä
BusyBoxin initiin ja systemd:hen.

## Init-järjestelmän tehtävät

| Tehtävä | Kysymys |
|---------|---------|
| järjestys | mikä palvelu käynnistetään ennen mitäkin? |
| valmius | milloin palvelu on oikeasti valmis, ei vain käynnistynyt? |
| valvonta | mitä tehdään, kun palvelu kaatuu? kuinka monta kertaa? |
| sammutus | miten palvelut pysäytetään niin, että data ehtii talteen? |
| loki | minne palvelujen tulosteet menevät? |

Järjestys ja valmius ovat eri asioita. Kun lokipalvelu on käynnistetty,
sen prosessi on olemassa, mutta se ei välttämättä ole vielä avannut
sokettiaan. Jos seuraava palvelu käynnistetään heti ja yrittää
kirjoittaa lokiin, ensimmäiset viestit katoavat. Siksi palvelu
ilmoittaa itse, kun se on valmis, ja init odottaa ilmoitusta.

## Palveluluettelo

Pienen init-järjestelmän `minit` asetukset ovat yksinkertainen
tekstitiedosto. Rivi kertoo palvelun nimen, sallittujen
uudelleenkäynnistysten määrän ja komennon:

```{.text tiedosto="esimerkit/03-palvelut/palvelut.conf"}
```

Kolme palvelua kattavat tavalliset tapaukset. `loki` on luotettava
palvelu. `lampo` on anturin lukija, joka epäonnistuu kaksi ensimmäistä
kertaa, koska anturi ei vielä vastaa, kuten oikeassa laitteessa käy,
kun anturin virta kytkeytyy viiveellä. `mittari` ei välitä
pysäytyspyynnöstä, eli se on vikaantunut palvelu, joka on lopulta
pysäytettävä väkisin. Kaikki kolme ovat saman esimerkkiohjelman
`palvelu` eri tiloja.

Jokaisesta palvelusta pidetään kirjaa:

```{.c tiedosto="esimerkit/03-palvelut/minit.c" osa="palvelu"}
```

```{.c tiedosto="esimerkit/03-palvelut/minit.c" osa="asetukset"}
```

## Valmiusilmoitus

Palvelu ilmoittaa valmiudesta luomalla tiedoston
`/run/valmis/<nimi>`. Systemd käyttää samaan tarkoitukseen
`sd_notify`-viestiä `READY=1` UNIX-soketin kautta, ja s6 kirjoittaa
rivin tiedostokuvaajaan. Mekanismi on eri, mutta idea sama: vain palvelu
itse tietää, milloin se on valmis.

```{.c tiedosto="esimerkit/03-palvelut/palvelu.c" osa="valmis"}
```

Palvelun on lisäksi varauduttava siihen, että pysäytyspyyntö tulee
millä hetkellä tahansa, myös heti valmiusilmoituksen jälkeen. Jos
palvelu tarkistaisi lipun ja kutsuisi sitten `pause()`-funktiota,
signaali voisi tulla näiden kahden välissä, ja palvelu jäisi odottamaan
ikuisesti. Siksi `SIGTERM` estetään ennen ilmoitusta, ja
`sigsuspend` vapauttaa sen vasta, kun palvelu jo odottaa:

```{.c tiedosto="esimerkit/03-palvelut/palvelu.c" osa="odota"}
```

Tämä on taidossa *Käyttöjärjestelmät* käsitelty signaalien
kilpatilanne, ja se on init-järjestelmissä todellinen: palvelu, joka
joskus ei pysähdy, viivästää sammutusta satunnaisesti ja on vaikea
toistaa.

## Käynnistys ja valvonta

Init käynnistää palvelut yksi kerrallaan ja odottaa kunkin valmiutta.
Jos palvelu päättyy ennen valmiutta ja uudelleenkäynnistyksiä on
jäljellä, se käynnistetään uudelleen kasvavalla viiveellä:

```{.c tiedosto="esimerkit/03-palvelut/minit.c" osa="odota"}
```

Kasvava viive (*exponential backoff*) on tärkeä. Ilman sitä palvelu,
joka kaatuu heti käynnistyttyään, käynnistyy satoja kertoja sekunnissa,
täyttää lokin ja kuluttaa prosessorin, jota muut palvelut tarvitsevat.
Uudelleenkäynnistysten raja taas estää loputtoman silmukan: jos anturi
on oikeasti rikki, palvelu merkitään epäonnistuneeksi, ja laite voi
siirtyä vikatilaan tai ilmoittaa viasta.

Kaatuva anturipalvelu laskee yrityksensä tiedostoon `/run`issa:

```{.c tiedosto="esimerkit/03-palvelut/palvelu.c" osa="kaatuva"}
```

Lukuun 4 verrattuna init tarvitsee kaksi uutta järjestelmäkutsua:
`fork` ja `execv` käynnistävät palvelun, ja `waitpid` valitsimella
`WNOHANG` kertoo, onko palvelu päättynyt, jäämättä odottamaan. Lapsi
kutsuu ennen `execv`iä `setsid()`-funktiota, jolloin palvelu on omassa
istunnossaan: konsolin näppäimistöltä tuleva `Ctrl-C` ei pysäytä sitä.

## Sammutus

Sammutuksessa palvelut pysäytetään käänteisessä järjestyksessä, jotta
palvelu voi vielä käyttää niitä palveluja, joista se riippuu.
Pysäytyspyyntö on `SIGTERM`. Jos palvelu ei pääty aikarajassa, se
tapetaan `SIGKILL`illä, jota ei voi estää eikä käsitellä:

```{.c tiedosto="esimerkit/03-palvelut/minit.c" osa="pysayta"}
```

```{.c tiedosto="esimerkit/03-palvelut/minit.c" osa="main"}
```

Koko käynnistys ja sammutus:

```{.tuloste tiedosto="esimerkit/testit/03-palvelut.odotettu"}
```

Tuloste on joka ajossa sama, vaikka palvelut ovat erillisiä
prosesseja, jotka kirjoittavat samaan konsoliin. Syy on, että init
odottaa jokaista tapahtumaa ennen seuraavaa: palvelu kirjoittaa
virheilmoituksensa ennen kuin päättyy, ja init huomaa päättymisen vasta
sen jälkeen. Rinnakkain käynnistyvien palvelujen tulosteet sekoittuisivat.
Tämä on syy, miksi oikeat init-järjestelmät keräävät palvelujen
tulosteet putkella ja kirjoittavat ne lokiin rivi kerrallaan
palvelun nimen kanssa.

## BusyBoxin init

BusyBox on yksi ohjelma, joka toteuttaa satoja tavallisia komentoja,
kuten `sh`, `ls`, `mount` ja `init`, ja on pienten Linux-järjestelmien
yleisin käyttäjätila. Sen init lukee tiedoston `/etc/inittab`:

```{.text tiedosto="esimerkit/03-palvelut/vertailu/inittab"}
```

`sysinit`-rivit ajetaan kerran käynnistyksessä ja odotetaan,
`respawn`-rivien ohjelmat käynnistetään uudelleen aina, kun ne
päättyvät, ja `shutdown`-rivit ajetaan sammutuksessa. Kaikki muu on
skriptin `/etc/init.d/rcS` vastuulla: se ajaa tavallisesti hakemiston
`/etc/init.d/` skriptit `S01…`–`S99…` aakkosjärjestyksessä. BusyBoxin
init ei tunne riippuvuuksia, valmiutta eikä uudelleenkäynnistysten
rajaa, ja `respawn` käynnistää kaatuvan ohjelman uudelleen loputtomasti
(tosin vähintään sekunnin välein). Pienessä laitteessa, jossa on
muutama palvelu, tämä riittää, ja se on helppo ymmärtää kokonaan.

## systemd

systemd on työasemien ja palvelinten oletus, ja sitä käytetään myös
suurissa sulautetuissa järjestelmissä, kuten autojen
viihdejärjestelmissä. Sama anturipalvelu systemd-yksikkönä:

```{.ini tiedosto="esimerkit/03-palvelut/vertailu/lampo.service"}
```

Jokaisella minitin ominaisuudella on vastine: `After` ja `Requires`
ovat järjestys ja riippuvuus, `Type=notify` valmiusilmoitus,
`Restart`, `RestartSec` ja `StartLimitBurst` valvonta ja
`TimeoutStopSec` sammutuksen aikaraja, jonka jälkeen tulee `SIGKILL`.
Lisäksi systemd käynnistää riippumattomat palvelut rinnakkain, kerää
tulosteet journaliin, rajoittaa palvelujen resursseja cgroupeilla ja
osaa käynnistää palvelun vasta, kun sen sokettiin otetaan yhteys.

Hinta on koko: systemd tarvitsee käytännössä glibc:n, monta
megatavua levyä ja ytimeen ominaisuuksia, joita luvun 3 pienessä
ytimessä ei ole, kuten cgroupit, `signalfd`, `timerfd`, `eventfd` ja
`inotify`.

| Init | Koko | Riippuvuudet | Valvonta | Käyttö |
|------------------|----------------|----------------|-----------|---------------|
| BusyBox init | osa BusyBoxia | ei | `respawn` | pienet laitteet |
| SysV init + skriptit | pieni | skriptien järjestys | ei | perinteiset järjestelmät |
| OpenRC | pieni | kyllä | valinnainen | Alpine, Gentoo |
| runit, s6 | hyvin pieni | rajattu | kyllä | kontit, minimalistiset järjestelmät |
| procd | pieni | kyllä | kyllä | OpenWrt-reitittimet |
| systemd | suuri | kyllä | kyllä | suuret laitteet, jakelut |

## Vahtikoira

Valvonta ei auta, jos init itse tai koko ydin jumiutuu. Sitä varten
piireissä on *vahtikoira* (watchdog): ajastin, joka käynnistää laitteen
uudelleen, ellei ohjelmisto nollaa sitä säännöllisesti. Linuxissa se
näkyy laitteena `/dev/watchdog`: kun laite avataan, ajastin käynnistyy,
ja jokainen kirjoitus nollaa sen. systemd hoitaa vahtikoiran asetuksella
`RuntimeWatchdogSec` ja voi lisäksi vaatia palveluilta omia
elonmerkkejä (`WatchdogSec` ja `sd_notify("WATCHDOG=1")`). Kun
vahtikoiraa ruokitaan vain, jos tärkeimmät palvelut ovat elossa, jumi
missä tahansa johtaa uudelleenkäynnistykseen.

## Käytännössä

- **Valitse init laitteen koon ja palvelujen määrän mukaan.** Muutaman
  palvelun laitteessa BusyBoxin init tai runit on helpoin ymmärtää ja
  todentaa. Kun palveluja on kymmeniä ja niillä on riippuvuuksia,
  systemd säästää työtä.
- **Tee palveluista valmiutensa ilmoittavia.** Valmiusilmoitus poistaa
  käynnistysjärjestyksen satunnaiset viat, jotka ilmenevät vain
  hitaalla tai kuormitetulla laitteella.
- **Rajaa uudelleenkäynnistykset ja kasvata viivettä.** Loputtomasti
  kaatuva palvelu on vika, joka on raportoitava, ei piilotettava.
- **Käsittele `SIGTERM` ja testaa sammutus.** Palvelun on tallennettava
  tilansa ja suljettava tiedostonsa aikarajassa. Sammutus, jota ei ole
  testattu, korruptoi datan sinä päivänä, kun sitä tarvitaan.
- **Kytke vahtikoira.** Kentällä laitteessa ei ole ketään painamassa
  reset-nappia.

## Itsearviointi

- Osaat luetella init-järjestelmän tehtävät ja selittää käynnistyksen
  ja valmiuden eron.
- Osaat toteuttaa palvelun, joka ilmoittaa valmiudestaan ja käsittelee
  `SIGTERM`in ilman kilpatilannetta.
- Osaat toteuttaa valvonnan, jossa on uudelleenkäynnistysten raja ja
  kasvava viive, sekä sammutuksen `SIGTERM`illä ja `SIGKILL`illä.
- Osaat kirjoittaa saman palvelun BusyBoxin `inittab`-riviksi ja
  systemd-yksiköksi ja vertailla vaihtoehtoja.
- Osaat kertoa, miten vahtikoira toimii ja miten se kytketään
  palvelujen valvontaan.
