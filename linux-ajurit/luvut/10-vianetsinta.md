# Ytimen vianetsintä

Ajurin virhe ei näy käyttäjätilan ohjelman tapaan siistinä
kaatumisena ja ytimenkuvana. Ydin voi jatkaa vioittuneena, jumittua tai
kaatua kokonaan, ja oire näkyy usein kaukana syystä. Siksi ytimessä on
omat välineensä: lokit, joita voi kytkeä päälle ajon aikana, jäljitys,
kaatumisilmoitus ja tarkistimet, jotka löytävät virheen ennen kuin se
aiheuttaa oireita.

Luvun harjoitusmoduuli `vika` on tarkoituksella virheellinen. Sen
debugfs-tiedostot käynnistävät kukin yhden tyypillisen virheen.

## printk ja lokitasot

`printk` kirjoittaa ytimen lokipuskuriin, jonka `dmesg` ja `/dev/kmsg`
näyttävät. Viestillä on taso:

| Taso | Funktio | Käyttö |
|-----|------------------------|------------------------------|
| 0–2 | `pr_emerg`, `pr_alert`, `pr_crit` | järjestelmä ei toimi |
| 3 | `pr_err`, `dev_err` | ajuri tai laite ei toimi |
| 4 | `pr_warn`, `dev_warn` | jotain odottamatonta, toiminta jatkuu |
| 5–6 | `pr_notice`, `pr_info`, `dev_info` | tavallinen tieto, kuten löydetty laite |
| 7 | `pr_debug`, `dev_dbg` | kehittäjän tieto, oletuksena pois |

Laitteeseen liittyvä viesti kirjoitetaan `dev_*`-funktiolla, joka lisää
alkuun ajurin ja laitteen nimen. Toistuvassa polussa, kuten
keskeytyksessä, käytetään rajoitettua muotoa (`dev_err_ratelimited`)
tai kertaviestiä (`dev_warn_once`), jotta virhe ei täytä lokia ja
hidasta järjestelmää. Hyvä ajuri on hiljainen: yksi rivi, kun laite
löytyy, ja virheet. Kaikki muu on `dev_dbg`-tasolla.

## Dynaaminen debug

Ytimen asetus `DYNAMIC_DEBUG` tekee jokaisesta `pr_debug`- ja
`dev_dbg`-kutsusta erikseen kytkettävän. Kytkimet ovat tiedostossa
`/proc/dynamic_debug/control`, ja niitä voi valita moduulin, tiedoston,
funktion tai rivin mukaan:

```{.c tiedosto="esimerkit/07-vianetsinta/vika.c" osa="laske"}
```

```{.text tiedosto="esimerkit/07-vianetsinta/dyndbg.vaiheet" osa="vaiheet"}
```

```{.tuloste tiedosto="esimerkit/testit/07-dyndbg.odotettu" osa="vaiheet"}
```

Ensimmäisellä kerralla debug-rivit ovat pois päältä. Funktion mukaan
valittu kytkin tuo esiin vain funktion `vika_summa` rivit. Moduulin
parametri `dyndbg=+p` kytkee kaikki moduulin rivit päälle jo
latauksessa, jolloin myös alkufunktion viestit näkyvät. Ytimen
komentorivillä sama on `dyndbg="module vika +p"`. Luvun 8 SPI-ohjain
käytti samaa mekanismia väylän liikenteen näyttämiseen. Pois päältä
oleva kutsu maksaa hyvin vähän (asetuksella `JUMP_LABEL` yhden hypyn),
joten debug-rivejä voi jättää tuotantokoodiin.

## ftrace

ftrace on ytimen sisäänrakennettu jäljitin. *Funktiojäljitin*
kirjaa jokaisen valitun funktion kutsun ja kutsujan. Ydin on käännetty
niin, että jokaisen funktion alussa on muutama tyhjä käsky, jotka
ftrace korvaa ajon aikana hypyllä jäljittimeen:

```{.text tiedosto="esimerkit/07-vianetsinta/ftrace.vaiheet" osa="vaiheet"}
```

```{.make tiedosto="esimerkit/Makefile" osa="jalki"}
```

```{.tuloste tiedosto="esimerkit/testit/07-ftrace.odotettu" osa="vaiheet"}
```

Suodatin `:mod:vika` valitsee moduulin kaikki funktiot. Jäljitys näyttää
kutsuketjun debugfs-tiedoston kirjoituksesta (`full_proxy_write`)
harjoitusmoduulin funktioihin. Funktio `vika_summa` näkyy nimellä
`vika_summa.constprop.0`: kääntäjä on tehnyt siitä version, johon
vakioargumentti on sijoitettu valmiiksi. Jäljitys näyttää siis sen koodin,
joka oikeasti ajetaan.

Muita jäljittimiä ovat `function_graph` (kutsupuu ja kestot),
tapahtumat (`events/`, esimerkiksi jokainen keskeytys ja
I2C-siirto) sekä `kprobe`-pisteet mihin tahansa käskyyn. Komentorivin
työkalut `trace-cmd` ja `perf` käyttävät samaa jäljitintä. Jäljitys on
nopea, joten sitä voi käyttää ajoitusvikojen etsimiseen, joihin
lokirivit ovat liian hitaita.

## Kaatumisilmoitus

NULL-osoittimen käyttö ytimessä ei kaada koko järjestelmää, jos se
tapahtuu prosessin järjestelmäkutsussa: ydin tulostaa
kaatumisilmoituksen (*oops*), lopettaa prosessin ja jatkaa. Ydin on
kuitenkin sen jälkeen epäluotettava. Prosessi saattoi pitää lukkoa,
joka jää varatuksi, ja tila voi olla vioittunut. Tuotantolaitteessa
asetetaan siksi usein `panic_on_oops=1` ja vahtikoira, joka
käynnistää laitteen uudelleen.

```{.c tiedosto="esimerkit/07-vianetsinta/vika.c" osa="kaada"}
```

```{.text tiedosto="esimerkit/07-vianetsinta/oops.vaiheet" osa="vaiheet"}
```

```{.tuloste tiedosto="esimerkit/testit/07-oops.odotettu"}
```

Ilmoituksen tärkeimmät rivit:

- **`Unable to handle kernel NULL pointer dereference at virtual
  address 0000000000000008`**: osoite 8 kertoo, että osoitin oli NULL
  ja luettiin kenttää, jonka siirtymä on 8. Tässä se on `arvo`
  rakenteessa `mittaus`.
- **`Tainted: G O`**: `G` tarkoittaa, että kaikki moduulit ovat
  GPL-lisensoituja, ja `O` ulkopuolista moduulia. Kaatumisen jälkeen
  `tainted` on 4224 eli lisäksi bitti 7 (`D`).
- **`pc :`** on käsky, jossa virhe tapahtui, ja **`lr :`** paluuosoite
  eli kutsuja. Merkintä `funktio+0xc/0x14` tarkoittaa siirtymää 0xc
  funktiossa, jonka pituus on 0x14 tavua.
- **`Call trace:`** on kutsupino. Tämän tutoriaalin ytimessä on
  symbolitaulu (`KALLSYMS`); ilman sitä pinossa olisi vain osoitteita.

Siirtymä muunnetaan lähdekoodin riviksi ytimen skriptillä
`faddr2line`, joka tarvitsee moduulin virheenjäljitystiedot. Ne
saadaan Kbuild-tiedoston `ccflags-y := -g` -rivillä:

```{.make tiedosto="esimerkit/07-vianetsinta/Kbuild"}
```

```{.make tiedosto="esimerkit/Makefile" osa="faddr2line"}
```

Rivi 45 on `return viimeisin->arvo;`. Testi korvaa siirtymät
tulosteessa pisteillä ja muuntaa ne erikseen, koska ne voivat muuttua
kääntäjäversion mukana. Lukeminen samassa järjestyksessä toimii
kentältä tulleeseen ilmoitukseen: osoite, `pc`, tahrat ja kutsupino,
sitten `faddr2line` samaa käännöstä vastaan.

## Tarkistimet

Osa virheistä ei aiheuta oiretta joka kerta: lukkiutuminen vaatii
kahden säikeen osuvan kohdalleen ja nukkuminen spinlockissa kaataa
järjestelmän vain, jos toinen CPU tarvitsee samaa lukkoa samaan aikaan.
Ytimen tarkistimet löytävät nämä heti, kun virheellistä polkua ajetaan
kerrankin.

```{.c tiedosto="esimerkit/07-vianetsinta/vika.c" osa="jarjestys"}
```

```{.c tiedosto="esimerkit/07-vianetsinta/vika.c" osa="nuku"}
```

```{.tuloste tiedosto="esimerkit/testit/07-lukot.odotettu" osa="vaiheet"}
```

- **lockdep** (`PROVE_LOCKING`) kirjaa jokaisen lukko-otteen
  järjestyksen. Kun `vika_palauta` ottaa lukot eri järjestyksessä kuin
  `vika_tallenna` ensin otti, lockdep tietää, että kaksi säiettä voisi
  lukkiutua toisiinsa, vaikka tässä ajossa kaikki tapahtui yhdessä
  säikeessä peräkkäin. Raportissa näkyvät lukkojen nimet, ketju ja
  kummankin otteen kutsupino; testi näyttää sen alusta vain otsikot.
- **`DEBUG_ATOMIC_SLEEP`** tarkistaa jokaisen nukkumaan mahdollisesti
  menevän funktion alussa, ollaanko atomisessa kontekstissa. Mutexin
  otto spinlockin sisällä huomataan, vaikka mutex olisi vapaa eikä
  nukkumista tapahtuisi.

Lockdep raportoi kunkin ongelman vain kerran ja sammuttaa itsensä
ensimmäisen raportin jälkeen, joten ensimmäinen raportti on se, jolla on
väliä. Muita tarkistimia:

| Tarkistin | Löytää |
|---------------|------------------------------------------------|
| KASAN | puskurin ylivuodot ja vapautetun muistin käytön, kuten ASan käyttäjätilassa |
| KFENCE | samat näytteenotolla, kevyt tuotantokäyttöön |
| kmemleak | vapauttamatta jääneen muistin |
| UBSAN | määrittelemättömän käytöksen, kuten ylivuodot ja väärät siirrot |
| `DEBUG_OBJECTS` | ajastimien ja töiden käytön vapautuksen jälkeen |
| KCSAN | datakilpailut |

Kehitysydin kannattaa kääntää niin monella tarkistimella kuin aika ja
muisti sallivat, ja ajureiden testit ajetaan sitä vasten. Tämän
tutoriaalin ytimessä on lockdep ja nukkumistarkistus; KASAN kasvattaisi
muistinkulutusta ja käännösaikaa niin paljon, että se on jätetty pois.

## Debuggeri

QEMU:n gdb-palvelin (`-s -S`) antaa ajaa ydintä debuggerissa: katkaisukohdat,
muuttujat ja askellus toimivat kuten käyttäjätilan ohjelmassa, kun gdb
saa `vmlinux`-tiedoston ja moduulien virheenjäljitystiedot. Ytimen
gdb-skriptit (`scripts/gdb`, asetus `GDB_SCRIPTS`) lisäävät komennot
`lx-dmesg` ja `lx-symbols`, jotka lukevat ytimen lokin ja lataavat
moduulien symbolit. Oikeassa laitteessa sama onnistuu JTAG-sovittimella
tai `kgdb`:llä sarjaportin yli. Useimmiten nopein tie on kuitenkin
lokirivi, jäljitys tai tarkistin, koska debuggeri pysäyttää koko
järjestelmän ja muuttaa ajoitusta.

## Käytännössä

- **Kehitä tarkistimilla varustettua ydintä vasten.** lockdep,
  `DEBUG_ATOMIC_SLEEP`, KASAN ja UBSAN löytävät virheet, joita testit
  eivät muuten näe.
- **Käytä `dev_dbg`-funktiota ja dynaamista debugia lisätulosteiden
  sijaan.** Rivit voi kytkeä päälle kentällä ilman uutta käännöstä.
- **Lue kaatumisilmoitus järjestyksessä**: osoite, `pc`, tahrat ja
  kutsupino. Muunna osoite riviksi `faddr2line`-skriptillä samaa
  käännöstä vastaan.
- **Säilytä debug-tiedot jokaisesta toimitetusta ytimestä ja
  moduulista.** Kentän kaatumisilmoitusta ei voi tulkita ilman niitä.
- **Käytä ftracea ajoitusvikoihin.** Lokirivit muuttavat ajoitusta
  enemmän kuin jäljitys.

## Itsearviointi

- Osaat valita lokitason ja `dev_*`-funktion ja kytkeä `dev_dbg`-rivit
  päälle dynaamisella debugilla moduulin, funktion tai rivin mukaan.
- Osaat jäljittää moduulin funktioiden kutsut ftracella ja selittää
  `.constprop`-päätteen.
- Osaat lukea kaatumisilmoituksen ja muuntaa sen osoitteen lähdekoodin
  riviksi.
- Osaat tulkita lockdepin ja nukkumistarkistuksen raportit ja nimetä
  tarkistimen, joka löytää muistivirheet.
