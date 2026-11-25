# Vianetsintä kohteessa

Käynnistystesti kertoo, että jokin on rikki. Tässä luvussa etsitään
syy. Työasemalla vian selvittäminen alkaa debuggerista tai `strace`sta,
mutta kohteessa niitä ei ole: ohjelmat on riisuttu symboleista, levytilaa
on vähän, juuri on vain luku -tilassa, ja yhteys laitteeseen on usein
pelkkä sarjakonsoli. Siksi työ jaetaan kahtia. Kohteessa ajetaan vain
pieni apuohjelma tai käytetään ytimen omia palveluja, ja isännällä ovat
symbolit, lähdekoodi ja raskaat työkalut.

```{.dot otsikko="Vianetsinnän työnjako: kohteesta tuodaan osoite, ydinvedos tai etäyhteys, ja tulkinta tehdään isännällä."}
digraph {
  rankdir=LR; node [shape=box];
  subgraph cluster_k { label="kohde: riisuttu ohjelma"; style=rounded;
    ydin [label="ytimen loki"];
    vedos [label="ydinvedos\n(core_pattern)"];
    palvelin [label="gdbserver\n(ptrace)"];
  }
  subgraph cluster_i { label="isäntä: ohjelma symboleineen, sysroot"; style=rounded;
    a2l [label="addr2line"];
    gdb [label="gdb-multiarch"];
  }
  ydin -> a2l [label="pc-osoite"];
  vedos -> gdb [label="tiedosto"];
  palvelin -> gdb [label="etäprotokolla\n(TCP tai sarjaportti)", dir=both];
}
```

Luvun keinot ovat halvimmasta kalleimpaan: virhekoodi, järjestelmäkutsujen
jäljitys, ytimen loki, ydinvedos ja etädebuggaus. Useimmat viat
selviävät jo kahdella ensimmäisellä.

## Symbolit jäävät isännälle

Esimerkkinä on pieni anturipalvelu, jossa on kaksi vikaa. Ensimmäinen
on huono virheilmoitus:

```{.c tiedosto="esimerkit/11-vianetsinta/anturi.c" osa="lue"}
```

Toinen on jäsennin, joka olettaa, että rivillä on aina `=`-merkki:

```{.c tiedosto="esimerkit/11-vianetsinta/anturi.c" osa="jasenna"}
```

Ohjelma käännetään virheenjäljitystiedoin (`-g`) ja kevyellä
optimoinnilla (`-Og`). Kohteeseen menee siitä riisuttu kopio:

```{.make tiedosto="esimerkit/Makefile" osa="symbolit"}
```

`strip` poistaa symbolitaulun ja DWARF-tiedot, joita laite ei tarvitse
ohjelman ajamiseen. Koodi ja sen osoitteet säilyvät samoina, joten
kohteesta saatu osoite tai ydinvedos voidaan tulkita isännällä
riisumatonta tiedostoa vasten. Tämä toimii vain, jos tiedostot ovat
samasta käännöksestä. Linkittäjä kirjoittaa ohjelmaan *build-id*-
tunnisteen (`readelf -n`), joka säilyy riisutussakin kopiossa ja jolla
oikean symbolitiedoston voi hakea arkistosta. Rakennustyökalut tekevät
jaon valmiiksi: Buildroot riisuu kohteen juuren ja säilyttää
riisumattomat tiedostot rakennushakemistossaan, ja Yocto tuottaa
symbolit erillisiin `-dbg`-paketteihin.

## Ohjelma ei käynnisty

Yleisin vika uudessa kuvassa on ohjelma, joka ei käynnisty lainkaan.
`execve`-järjestelmäkutsun virhekoodi kertoo syyn, mutta kuoren
ilmoitus on usein harhaanjohtava. Seuraava init kokeilee samaa pientä
ohjelmaa eri tavoin kelvottomana ja kolmea laitetiedostoa:

```{.c tiedosto="esimerkit/11-vianetsinta/kokeile.c" osa="kaynnista"}
```

```{.c tiedosto="esimerkit/11-vianetsinta/kokeile.c" osa="yritykset"}
```

Initramfsissä ei ole dynaamista linkittäjää eikä kuorta, yksi ohjelma on
käännetty isännän arkkitehtuurille, yhdeltä puuttuu suoritusoikeus ja
yksi on kopioitu `noexec`-valitsimella kiinnitettyyn hakemistoon `/run`:

```{.tuloste tiedosto="esimerkit/testit/11-kaynnistys.odotettu"}
```

| Virhe | Tavallisin syy | Tarkistus |
|-------|----------------|-----------|
| `ENOENT`, vaikka tiedosto on olemassa | ohjelman tulkki puuttuu: dynaaminen linkittäjä tai skriptin `#!`-rivin ohjelma | `readelf -l`, skriptin ensimmäinen rivi |
| `ENOEXEC` | väärä arkkitehtuuri tai ABI, tai ytimestä puuttuu muodon tuki | `readelf -h`, `file` |
| `EACCES` | suoritusoikeus puuttuu tai tiedostojärjestelmä on kiinnitetty `noexec`-valitsimella | `ls -l`, `/proc/mounts` |
| `ENOENT` laitetiedostolle | laitetta ei ole löytynyt: ajuri puuttuu tai laitepuun solmu on pois käytöstä | `/sys/bus/*/devices`, ytimen loki |
| `ENXIO` laitetiedostolle | tiedosto on olemassa, mutta sen laitenumerolla ei ole ajuria | `/proc/devices` |

Ensimmäinen rivi hämää eniten: tiedosto `/bin/dynaaminen` on olemassa,
ja silti virhe on *No such file or directory*. Puuttuva tiedosto on
ohjelman otsakkeessa nimetty tulkki `/lib/ld-linux-aarch64.so.1`. Sama
virhe syntyy, kun ohjelma on linkitetty eri C-kirjastoa vasten kuin
kohteessa on (glibc:n ja muslin linkittäjät ovat eri nimisiä) tai kun
32-bittinen ohjelma ajetaan järjestelmässä, jossa on vain 64-bittiset
kirjastot. Jos tulkki löytyy mutta jokin kirjasto puuttuu, ohjelma
käynnistyy ja dynaaminen linkittäjä tulostaa itse virheen *cannot open
shared object file*.

Syyt näkyvät ohjelmatiedostosta jo isännällä, ennen kuin kuva
kirjoitetaan laitteeseen (luku 2). Skripti poimii `readelf`in tulosteesta
arkkitehtuurin, tulkin ja tarvittavat kirjastot:

```{.bash tiedosto="esimerkit/11-vianetsinta/elf.sh" osa="tiedot"}
```

```{.tuloste tiedosto="esimerkit/testit/11-elf.odotettu"}
```

Rakennuksen viimeiseksi vaiheeksi sopii tarkistus, joka käy juuren
ohjelmat läpi ja varmistaa, että jokaisen tulkki ja `NEEDED`-kirjastot
ovat juuressa ja että arkkitehtuuri on kohteen.

## Järjestelmäkutsujen jäljitys

Anturipalvelu kertoo puuttuvasta asetustiedostosta vain, että alustus
epäonnistui. Lähdekoodia lukematta syy selviää katsomalla, mitä ohjelma
pyytää ytimeltä. `strace` tulostaa jokaisen järjestelmäkutsun
argumentteineen ja paluuarvoineen. Kohteeseen se kopioidaan staattisesti
linkitettynä, ja tuloste ohjataan tiedostoon (`strace -f -o /run/jalki
ohjelma`), jotta se ei sekoitu ohjelman omaan tulosteeseen. Valitsin
`-f` seuraa lapsiprosesseja, `-p` liittyy käynnissä olevaan prosessiin,
`-e trace=file` rajaa kutsut tiedostoihin ja `-T` näyttää kunkin kutsun
keston.

Kehitysvaiheessa saman saa ilman kohdetta: QEMU:n käyttäjätilan
emulaattori tulostaa valitsimella `-strace` kutsut, jotka se välittää
isännän ytimelle.

```{.make tiedosto="esimerkit/Makefile" osa="jaljitys"}
```

```{.tuloste tiedosto="esimerkit/testit/11-jaljitys.odotettu"}
```

Jäljityksestä on tässä suodatettu tiedostokutsut. Ensimmäinen niistä
kertoo syyn: ohjelma yrittää avata tiedoston `/etc/anturi.conf`, ja ydin
vastaa `ENOENT`. Seuraava kutsu kirjoittaa 28 merkin virheilmoituksen
virhevirtaan (tiedostokuvaaja 2), ja ohjelma päättyy paluuarvolla 1.
Jäljitys vastaa kysymyksiin, joihin lokit eivät vastaa: mitä tiedostoa
ohjelma etsi ja mistä hakemistoista, mihin osoitteeseen se yritti
yhteyttä ja mihin kutsuun se jäi odottamaan.

Kirjastokutsuja jäljittää vastaavasti `ltrace`. Molemmat hidastavat
ohjelmaa selvästi, koska jokainen kutsu pysäyttää prosessin kahdesti,
joten ajoituksesta riippuva vika voi kadota jäljityksen ajaksi.

## Kaatuminen: ytimen loki ja osoite

Kun asetustiedostossa on rivi ilman `=`-merkkiä, palvelu kaatuu. Init
näkee vain, että lapsi kuoli signaaliin 11. Ydin tietää enemmän, ja
kaksi asetusta saa sen kertomaan tietonsa:

```{.c tiedosto="esimerkit/11-vianetsinta/tutki.c" osa="asetukset"}
```

`exception-trace` kirjaa ytimen lokiin jokaisen käyttäjätilan ohjelman,
joka kuolee käsittelemättömään poikkeukseen. `core_pattern` kertoo,
minne ydin kirjoittaa kaatuneen prosessin muistin, ja siihen palataan
seuraavassa osiossa. Molemmat ovat tiedostoja hakemistossa `/proc/sys`,
ja ne vaativat ytimeltä muutaman asetuksen, jotka `tinyconfig` jättää
pois:

```{.ini tiedosto="esimerkit/11-vianetsinta/vianetsinta.config" osa="vedos"}
```

Init käynnistää palvelun viallisella asetustiedostolla, odottaa sen
päättymistä ja näyttää palvelua koskevat ytimen lokirivit (lokin luku
laitteesta `/dev/kmsg` kuten luvussa 3):

```{.c tiedosto="esimerkit/11-vianetsinta/tutki.c" osa="aja"}
```

Järjestelmä käynnistetään kirjoitettavan datalevyn kanssa, koska
ydinvedos tarvitsee paikan, johon sen voi tallentaa:

```{.make tiedosto="esimerkit/Makefile" osa="kaatuminen"}
```

```{.tuloste tiedosto="esimerkit/testit/11-kaatuminen.odotettu" asti="== addr2line"}
```

Lokirivi kertoo poikkeuksen lajin: *DABT (lower EL)* on käyttäjätilan
datan käsittelyssä tapahtunut keskeytys (data abort), ja *translation
fault* tarkoittaa, ettei osoitteelle ole sivutaulumerkintää. Ohjelma
siis käytti osoitetta, jota sen osoiteavaruudessa ei ole. Lokissa on
sen perässä rekisterivedos, josta init näyttää rivin `pc`: käskyn
osoitteen, jossa poikkeus tapahtui. Testi korvaa osoitteet pisteillä,
koska ne muuttuvat kääntäjän version mukana.

Osoite ei kerro riisutusta ohjelmasta mitään, mutta isännällä on sama
ohjelma symboleineen. `addr2line` muuntaa osoitteen funktioksi ja
lähdekoodin riviksi:

```{.make tiedosto="esimerkit/Makefile" osa="addr2line"}
```

```{.tuloste tiedosto="esimerkit/testit/11-kaatuminen.odotettu" alkaen="== addr2line"}
```

Rivi 19 on jäsentimen `*erotin = '\0';`. Pelkkä lokirivi ja oikea
symbolitiedosto riittivät vian paikantamiseen, eikä laitteeseen
tarvinnut asentaa mitään. Staattisesti linkitetyssä ohjelmassa osoite
kelpaa sellaisenaan. Jaetussa kirjastossa ja paikkariippumattomassa
ohjelmassa (PIE) lokin osoitteesta on ensin vähennettävä latausosoite,
joka näkyy lokirivin lopussa ja tiedostossa `/proc/<pid>/maps`.

Ytimen loki katoaa uudelleenkäynnistyksessä. Kentällä olevan laitteen
viimeiset lokirivit saa talteen *pstore*-tuella (`ramoops`), joka
kirjoittaa lokin muistialueelle, jota käynnistys ei nollaa.

## Ydinvedos

*Ydinvedos* (core dump) on tiedosto, johon ydin kirjoittaa kaatuneen
prosessin muistin ja rekisterit. Siitä näkee kaatumishetken koko tilan:
kutsupinon, muuttujat ja tietorakenteet. Vedos syntyy, kun kolme ehtoa
täyttyy: ytimessä on tuki (`COREDUMP` ja `ELF_CORE`), prosessin
`RLIMIT_CORE`-raja sallii sen (`ulimit -c unlimited`) ja
`core_pattern`in osoittamaan paikkaan voi kirjoittaa. Vain luku -juurella
viimeinen ehto ei täyty itsestään, joten esimerkissä vedos ohjataan
datalevylle. Jos `core_pattern` alkaa putkimerkillä (`|/sbin/kerain
%e %p`), ydin käynnistää nimetyn ohjelman ja syöttää vedoksen sen
vakiosyötteeseen. Näin toimivat `systemd-coredump` ja laitevalmistajien
omat kaatumisraportoijat, jotka pakkaavat vedoksen, rajoittavat niiden
määrää ja lähettävät ne palvelimelle.

Esimerkin Makefile lukee vedoksen levykuvasta `debugfs`-työkalulla;
oikeasta laitteesta se haetaan verkon yli tai muistikortilta. Isännällä
vedos avataan riisumattoman ohjelman kanssa:

```{.text tiedosto="esimerkit/11-vianetsinta/vedos.gdb"}
```

```{.make tiedosto="esimerkit/Makefile" osa="vedos"}
```

```{.tuloste tiedosto="esimerkit/testit/11-vedos.odotettu"}
```

`gdb-multiarch` on gdb, joka ymmärtää myös muiden arkkitehtuurien
ohjelmia ja vedoksia. Testi korvaa tulosteen osoitteet merkinnällä
`0x..`. Kutsupino kertoo saman rivin kuin `addr2line` ja
lisäksi reitin sinne. `erotin` on nolla, eli `strchr` ei löytänyt
merkkiä. Komento `up` siirtyy kutsujan kehykseen, jossa `numero` kertoo,
että kyse on tiedoston kolmannesta rivistä, ja `rivi` näyttää sen
sisällön. Arvo `<optimized out>` tarkoittaa, että kääntäjä ei ole
säilyttänyt muuttujaa kaatumiskohtaan asti; `-Og` säilyttää niitä
enemmän kuin `-O2`.

Dynaamisesti linkitetyn ohjelman vedosta varten gdb tarvitsee lisäksi
kohteen kirjastot. Komento `set sysroot /polku/sysrootiin` kertoo,
mistä ne löytyvät isännällä (luku 2). Kirjastojen on oltava täsmälleen
samat kuin laitteessa, muuten kutsupino on roskaa.

## Etädebuggaus

Kun vika ei kaada ohjelmaa tai tila on tutkittava ennen kaatumista,
tarvitaan debuggeri. gdb jaetaan kahtia: kohteessa ajetaan pieni
`gdbserver`, joka hallitsee prosessia `ptrace`-järjestelmäkutsulla, ja
isännällä `gdb-multiarch`, jolla ovat symbolit ja lähdekoodi. Ne
puhuvat gdb:n etäprotokollaa TCP-yhteyden tai sarjaportin yli:

| Missä | Komento |
|-------|---------|
| kohde | `gdbserver :2345 /bin/anturi /etc/rikki.conf` |
| kohde, käynnissä oleva prosessi | `gdbserver --attach :2345 <pid>` |
| isäntä | `gdb-multiarch build/anturi`, sitten `target remote laite:2345` |

Tämän tutoriaalin pienessä ytimessä ei ole verkkoa, joten esimerkissä
gdb-palvelimena on QEMU:n käyttäjätilan emulaattori: valitsimella `-g`
se pysäyttää ohjelman alkuun ja odottaa gdb:n yhteyttä annetussa
portissa. Protokolla on sama, joten isännän puoli on täsmälleen sama
kuin oikean laitteen kanssa. Istunto on kirjoitettu komentotiedostoksi,
jotta sen voi ajaa testinä:

```{.text tiedosto="esimerkit/11-vianetsinta/istunto.gdb"}
```

```{.make tiedosto="esimerkit/Makefile" osa="gdb"}
```

```{.tuloste tiedosto="esimerkit/testit/11-gdb.odotettu"}
```

Katkaisukohta pysäyttää ohjelman jokaisella jäsennettävällä rivillä.
Ensimmäinen rivi käsitellään oikein, toisella ohjelma saa signaalin
`SIGSEGV`, ja gdb pysäyttää sen ennen kuin ydin lopettaa prosessin.
Tilaa voi nyt tutkia kuten vedoksesta, ja lisäksi ohjelmaa voi
askeltaa, muuttujia voi muuttaa ja suoritusta jatkaa.

Etädebuggauksen tavallisimmat kompastukset ovat samat kuin vedoksen:
väärä tai puuttuva sysroot ja symbolitiedosto, joka ei vastaa laitteen
ohjelmaa. Jos lähdekoodi on isännällä eri polussa kuin käännöskoneella,
`set substitute-path` korjaa polut.

## Työkalun valinta

| Keino | Kertoo | Vaatii kohteelta |
|-------|--------|------------------|
| virhekoodi ja `readelf` | miksi ohjelma ei käynnisty | ei mitään |
| `strace`, `ltrace` | mitä ohjelma pyytää ytimeltä ja kirjastoilta | staattinen työkalu, `ptrace` |
| ytimen loki ja `addr2line` | missä ohjelma kaatui | `exception-trace`, loki talteen |
| ydinvedos | kaatumishetken koko tila | ytimen tuki, kirjoitettava paikka |
| `gdbserver` | tila ja askellus ajon aikana | työkalu, verkko tai sarjaportti |
| `/proc/<pid>/` | muistikartta, avoimet tiedostot, tila | `procfs` |
| `perf` | mihin aika kuluu | ytimen `PERF_EVENTS`, työkalu |

Suorituskyvyn mittaamista käsittelee taito *Suorituskyvyn analyysi ja
optimointi* ja ytimen puolen vianetsintää (ftrace, kaatumisilmoitukset,
lukkotarkistimet) taito *Linux-laiteajurit*.

## Käytännössä

- **Arkistoi riisumattomat ohjelmat ja sysroot jokaisesta julkaisusta.**
  Kentältä tullut osoite tai vedos on arvoton ilman täsmälleen samaa
  käännöstä. Build-id yhdistää ne.
- **Aloita halvimmasta keinosta.** Paluuarvo, virhekoodi ja loki ensin,
  sitten jäljitys, vedos ja vasta lopuksi debuggeri.
- **Kirjoita virheilmoitukseen syy.** `strerror(errno)` ja tiedoston
  nimi ilmoituksessa säästävät jäljityksen. Esimerkin palvelu hukkasi
  molemmat.
- **Päätä etukäteen, minne loki ja vedokset menevät.** Vain luku
  -juurella ja ilman konsolia tieto kaatumisesta katoaa, ellei sille ole
  varattu paikkaa (dataosio, pstore) ja kokorajaa.
- **Pidä vianetsinnän portit kiinni tuotannossa.** `gdbserver` antaa
  täyden pääsyn prosessiin, ja ydinvedoksessa on prosessin koko muisti
  avaimineen. Kehityskuva ja tuotantokuva rakennetaan samasta lähteestä
  eri asetuksin (taito *Sulautettujen järjestelmien tietoturva*).

## Itsearviointi

- Osaat päätellä `execve`- ja `open`-kutsun virhekoodista, miksi
  ohjelma tai laite ei toimi kohteessa, ja tarkistaa ohjelmatiedoston
  arkkitehtuurin, tulkin ja kirjastot isännällä.
- Osaat jäljittää ohjelman järjestelmäkutsut ja löytää jäljityksestä
  epäonnistuvan kutsun.
- Osaat ottaa käyttäjätilan kaatumisen ytimen lokiin ja muuntaa
  osoitteen lähdekoodin riviksi riisumattomalla ohjelmalla.
- Osaat ottaa ydinvedokset käyttöön, tuoda vedoksen isännälle ja avata
  sen `gdb-multiarch`illa.
- Osaat kuvata `gdbserver`in ja isännän gdb:n työnjaon ja ajaa
  debuggausistunnon etäkohdetta vasten.
- Osaat perustella, miksi symbolit säilytetään isännällä ja miksi
  vianetsinnän työkalut eivät kuulu tuotantokuvaan.
