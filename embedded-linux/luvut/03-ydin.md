# Ytimen konfigurointi ja kääntäminen

Linuxin lähdekoodissa on ajureita tuhansille laitteille,
kymmenille arkkitehtuureille ja lukemattomille ominaisuuksille. Jakelun
ydin kääntää niistä suurimman osan moduuleiksi, jotta sama ydin toimii
mahdollisimman monessa koneessa. Sulautetun laitteen ydin käännetään
päinvastoin: mukaan otetaan vain se, mitä laite tarvitsee. Ydin on
pienempi, käynnistyy nopeammin ja sisältää vähemmän hyökkäyspintaa.

## Lähdepuu

Ytimen lähdepuun tärkeimmät hakemistot:

| Hakemisto | Sisältö |
|-----------|---------|
| `arch/arm64/` | arkkitehtuurikohtainen koodi, `configs/defconfig`, `boot/dts/` |
| `drivers/` | ajurit väylittäin ja laiteluokittain |
| `fs/`, `net/`, `mm/`, `kernel/` | tiedostojärjestelmät, verkko, muistinhallinta, ydin |
| `init/` | käynnistys ja `init/Kconfig`, yleiset asetukset |
| `kernel/configs/` | yleiset fragmentit, kuten `tiny.config` |
| `scripts/` | käännöksen apuohjelmat, `kconfig/merge_config.sh`, `extract-ikconfig` |
| `usr/` | sisäänrakennettu initramfs ja `gen_init_cpio` |

Tämän tutoriaalin ydin on Ubuntun `linux-source-6.8.0`-paketin
versio 6.8.12. Se sisältää Ubuntun omat muutokset ja ylimääräisen
hakemiston `ubuntu/`, mutta käännöksen kannalta se toimii kuten
kernel.orgin ydin. Laitevalmistajat toimittavat usein oman ytimensä
(*vendor kernel*), jossa on piirin ajurit, joita pääkehityshaarassa ei
vielä ole. Sellaisen päivittäminen on työlästä, joten piiriä valitessa
kannattaa selvittää, kuinka hyvin se on tuettu pääkehityshaarassa.

## Kconfig

Jokainen ominaisuus on *Kconfig-symboli*, joka määritellään hakemistojen
`Kconfig`-tiedostoissa. Esimerkiksi `fs/Kconfig` määrittelee symbolin
`TMPFS`: tyyppi `bool` kuvauksineen, riippuvuus `depends on SHMEM`,
valinta `select MEMFD_CREATE` ja ohjeteksti. Symbolin arvo on `y` (käännetään
ytimeen), `m` (käännetään moduuliksi) tai `n` (ei käännetä).
Riippuvuuksia on kahta lajia:

- **`depends on X`**: symbolin voi valita vain, jos `X` on valittu.
  Jos `X` puuttuu, symboli katoaa hiljaa.
- **`select X`**: symbolin valinta pakottaa `X`:n päälle riippuvuuksista
  välittämättä. Arkkitehtuuri valitsee näin esimerkiksi
  keskeytysohjaimensa ajurin.

Konfiguraatio tallennetaan käännöshakemiston tiedostoon `.config`,
jossa on jokainen symboli: tämän tutoriaalin pienessäkin ytimessä
yli 2 000 riviä. Valmiit lähtökohdat ovat *defconfigeja*: täysiä
konfiguraatioita, joista on poistettu oletusarvoiset rivit. ARM64:n
`arch/arm64/configs/defconfig` on laaja ydin, joka käynnistyy useimmilla
kehityskorteilla. Kohteet `allnoconfig` ja `tinyconfig` aloittavat
tyhjästä: kaikki, mikä voidaan jättää pois, on pois.

| Komento | Tulos |
|---------|-------|
| `make defconfig` | arkkitehtuurin oletuskonfiguraatio |
| `make tinyconfig` | pienin mahdollinen ydin |
| `make olddefconfig` | täydentää `.config`in puuttuvat symbolit oletusarvoilla |
| `make menuconfig` | valikko; `/` hakee symbolia ja näyttää riippuvuudet |
| `make savedefconfig` | kirjoittaa `.config`ista minimaalisen defconfigin |

## Fragmentit

Konfiguraatiota ei kannata muokata valikolla ja tallentaa valtavana
`.config`-tiedostona, koska sen muutoksia on vaikea katselmoida. Parempi
tapa on *fragmentti*: lyhyt tiedosto, joka luettelee vain poikkeamat
lähtökohdasta. Tämän tutoriaalin ydin on `tinyconfig` ja kaksi
fragmenttia: perusfragmentti ja luvun 11 vianetsinnän lisäykset.
Perusfragmentin osat:

```{.ini tiedosto="esimerkit/ymparisto/perus.config" osa="konsoli"}
```

Konsoli vaatii TTY-kerroksen, PL011-sarjaportin ajurin ja sen
konsolituen. Ilman `SERIAL_AMBA_PL011_CONSOLE`-symbolia ydin
käynnistyy, mutta ei kirjoita mitään.

```{.ini tiedosto="esimerkit/ymparisto/perus.config" osa="kaynnistys"}
```

Käynnistykseen tarvitaan initramfs-tuki ja sen purku, ELF-ohjelmien ja
skriptien suoritus, `devtmpfs` laitetiedostoille sekä `/proc`, `/sys` ja
`tmpfs`. Pysyvä juuri (luku 8) tarvitsee lisäksi virtio-levyn, ext4:n ja
overlayfs:n:

```{.ini tiedosto="esimerkit/ymparisto/perus.config" osa="levy"}
```

Fragmentit yhdistetään lähtökohtaan ytimen skriptillä
`scripts/kconfig/merge_config.sh`, ja lopuksi `olddefconfig` ratkaisee
riippuvuudet ja täydentää loput symbolit:

```{.make tiedosto="esimerkit/ymparisto/ydin.mk" osa="konfigurointi"}
```

## Hiljaa hylätyt asetukset

Kconfig ei kerro, jos fragmentin asetus ei päädy lopulliseen
konfiguraatioon. Jos riippuvuus puuttuu, `olddefconfig` poistaa
symbolin, ja ydin käännetään ilman sitä. Vika huomataan vasta
laitteessa: kiinnitys epäonnistuu, laite puuttuu tai ominaisuus ei
toimi. Siksi konfiguroinnin jälkeen ajetaan tarkistus, joka vertaa
jokaista fragmentin riviä valmiiseen `.config`-tiedostoon:

```{.bash tiedosto="esimerkit/ymparisto/tarkista-config.sh" osa="silmukka"}
```

Esimerkki `03-ydin/rikki.config` pyytää `tmpfs`:ää mutta unohtaa sen
riippuvuuden:

```{.ini tiedosto="esimerkit/03-ydin/rikki.config"}
```

`tinyconfig` poistaa `SHMEM`-symbolin (jaettu muisti korvataan
yksinkertaisemmalla `ramfs`:llä), joten `TMPFS` ei täyty:

```{.tuloste tiedosto="esimerkit/testit/03-rikki.odotettu"}
```

Tarkistus on ytimen käännöksen ensimmäinen testi. Tämän tutoriaalin
fragmentissa oli alun perin juuri tämä virhe, ja tarkistus löysi sen
ennen kuin ydintä oli edes käännetty. Puuttuvan riippuvuuden löytää
valikon haulla (`/TMPFS` menuconfigissa) tai lukemalla symbolin
`Kconfig`-tiedostosta.

## Kääntäminen

Ydin käännetään erilliseen hakemistoon valitsimella `O=`, jolloin
lähdepuu pysyy puhtaana ja samasta lähteestä voi kääntää monta
konfiguraatiota rinnakkain:

```{.make tiedosto="esimerkit/ymparisto/ydin.mk" osa="kaannos"}
```

Kohde `Image` on ARM64:n pakkaamaton ydinkuva
`arch/arm64/boot/Image`. Kohde `modules` kääntää moduulit ja
`modpost`-työkalun, jota tarvitaan myös ytimen ulkopuolisten moduulien
kääntämiseen. Käännöksessä syntyy myös `vmlinux`, ytimen ELF-tiedosto
symboleineen. Sitä ei käynnistetä, mutta sitä tarvitaan debuggaukseen
(`gdb vmlinux`) ja kaatumisilmoitusten tulkintaan.

Tämän tutoriaalin ytimen kuva on noin 3,7 Mt, ja sen kääntäminen
kestää nelinytimisellä koneella 5–10 minuuttia. Jakelun yleiskäyttöinen ARM64-ydin on moninkertainen, ja sen moduulit
vievät satoja megatavuja lisää. Ero syntyy siitä, mitä jätetään pois:
tinyconfig poistaa muun muassa verkon, symbolitaulun (`KALLSYMS`),
`BUG()`-tarkistukset ja monta järjestelmäkutsua, kuten `eventfd`,
`signalfd`, `timerfd`, AIO ja io_uring. Ohjelma, joka tarvitsee niitä,
epäonnistuu tällaisessa ytimessä virheeseen `ENOSYS`; esimerkiksi
systemd ei käynnisty ilman niitä. Tuotantoytimessä osa poistetusta
kannattaa ottaa takaisin: ilman `KALLSYMS`-symbolia ytimen
kaatumisilmoituksessa on vain osoitteita.

## Toistettava käännös

Ydin kirjoittaa itseensä käännösajan, käyttäjän ja koneen nimen. Ne
näkyvät käynnistyslokin ensimmäisillä riveillä ja tiedostossa
`/proc/version`, ja ne muuttavat ydinkuvaa jokaisella käännöksellä.
Muuttujat `KBUILD_BUILD_TIMESTAMP`, `KBUILD_BUILD_USER` ja
`KBUILD_BUILD_HOST` kiinnittävät ne (ks. `YMAKE` luvussa 1), jolloin
sama lähde, konfiguraatio ja kääntäjä tuottavat saman kuvan. Toistettava
käännös on tietoturvakysymys: kun kuka tahansa voi tuottaa saman kuvan
samoista lähteistä, toimitetun kuvan voi tarkistaa.

Konfiguraatio kannattaa myös tallentaa ytimeen. Symbolit `IKCONFIG` ja
`IKCONFIG_PROC` sisällyttävät pakatun `.config`-tiedoston ytimeen ja
tiedostoon `/proc/config.gz`. Kentällä olevasta laitteesta voi silloin
tarkistaa, millä asetuksilla sen ydin on käännetty, ja ydinkuvasta
asetukset saa ulos ilman laitettakin:

```{.make tiedosto="esimerkit/Makefile" osa="ikconfig"}
```

```{.tuloste tiedosto="esimerkit/testit/03-ikconfig.odotettu"}
```

## Moduulit

Ominaisuus käännetään ytimeen (`y`), kun sitä tarvitaan aina tai jo
käynnistyksessä, kuten juuritiedostojärjestelmän ajuri. Moduuliksi
(`m`) käännetään se, mitä tarvitaan vain joskus, mitä halutaan päivittää
erikseen tai minkä lataamista halutaan ohjata, esimerkiksi
lisävarusteen ajuri. Pienessä laitteessa, jonka laitteisto ei muutu,
kaiken kääntäminen ytimeen on yleistä ja yksinkertaista. Fragmentin
viimeiset osat sallivat moduulit ja nimeävät ytimen:

```{.ini tiedosto="esimerkit/ymparisto/perus.config" osa="moduulit"}
```

```{.ini tiedosto="esimerkit/ymparisto/perus.config" osa="tunniste"}
```

Ytimen ulkopuolinen moduuli käännetään ytimen käännöshakemistoa
vasten. Moduulin hakemistossa on `Kbuild`-tiedosto, joka kertoo
ytimen käännösjärjestelmälle, mistä tiedostoista moduuli koostuu:

```{.make tiedosto="esimerkit/03-ydin/moduuli/Kbuild"}
```

```{.c tiedosto="esimerkit/03-ydin/moduuli/hei.c"}
```

```{.make tiedosto="esimerkit/Makefile" osa="moduuli"}
```

Moduuli sopii vain sille ytimelle, jota vasten se on käännetty.
Moduuliin tallentuu *vermagic*-merkkijono, jossa on ytimen versio ja
keskeiset asetukset (tässä `6.8.12-tutoriaali SMP mod_unload
aarch64`), ja ydin kieltäytyy lataamasta moduulia, jonka merkkijono ei
täsmää. Siksi moduulit ja ydin rakennetaan ja toimitetaan yhdessä.

Laitteessa moduulin lataa tavallisesti `modprobe`, joka lukee riippuvuudet
`depmod`in tuottamasta tiedostosta, tai `udev` automaattisesti, kun
laite löytyy. Ilman niitä moduulin voi ladata suoraan järjestelmäkutsulla
`finit_module`. Esimerkin init tekee juuri niin ja lukee sitten
moduulin rivit ytimen lokista laitteesta `/dev/kmsg`:

```{.c tiedosto="esimerkit/03-ydin/lataaja.c" osa="lataus"}
```

```{.tuloste tiedosto="esimerkit/testit/03-moduuli.odotettu"}
```

Ensimmäinen rivi kertoo, että ydin on nyt *tahrattu* (tainted): siihen
on ladattu koodia, joka ei ole peräisin ytimen omasta lähdepuusta.
Tahramerkintä näkyy kaatumisilmoituksissa, ja ytimen kehittäjät
pyytävät yleensä toistamaan vian ilman tahraavia moduuleja. Moduulin
parametrit, symbolien vienti, riippuvuudet ja lisenssit käsitellään
taidossa *Linux-laiteajurit*; tässä riittää, että moduuli käännetään
ja ladataan.

## Käytännössä

- **Pidä ytimen asetukset fragmentteina versionhallinnassa.** Fragmentti
  kertoo, mitä on muutettu ja miksi; kommentoi jokainen ryhmä.
  Täydellinen `.config` on käännöksen tuotos, ei lähde.
- **Tarkista, että jokainen pyydetty asetus päätyi konfiguraatioon.**
  Kconfig hylkää riippuvuuksiltaan puutteellisen asetuksen hiljaa.
  Buildroot ja Yocto tekevät saman tarkistuksen varoituksena;
  tee siitä virhe.
- **Käännä erilliseen hakemistoon (`O=`) ja tee käännöksestä
  toistettava.** Kiinnitä aikaleima, käyttäjä ja kone ja tallenna
  konfiguraatio ytimeen (`IKCONFIG`).
- **Aloita pienestä ja lisää tarpeen mukaan, tai suuresta ja poista.**
  `tinyconfig` opettaa, mitä kukin osa tekee, mutta oikeaan laitteeseen
  on usein nopeampaa lähteä piirin defconfigista ja poistaa tarpeeton.
  Kummassakin tapauksessa tulos tallennetaan fragmentteina.
- **Älä jätä debuggaustukea pois liian aikaisin.** `KALLSYMS`,
  `PRINTK` ja `BUG()` maksavat muutamia satoja kilotavuja mutta tekevät
  kentällä tapahtuneen kaatumisen selvittämisestä mahdollista.

## Itsearviointi

- Osaat selittää Kconfig-symbolin arvot `y`, `m` ja `n` sekä eron
  `depends on`- ja `select`-riippuvuuden välillä.
- Osaat tehdä ytimen konfiguraation tinyconfigin ja fragmenttien
  avulla ja tarkistaa, että kaikki pyydetyt asetukset otettiin käyttöön.
- Osaat kääntää ARM64-ytimen ristiin erilliseen hakemistoon ja tehdä
  käännöksestä toistettavan.
- Osaat kääntää ytimen ulkopuolisen moduulin, ladata sen ja selittää
  vermagicin ja tahramerkinnän.
- Osaat lukea kentällä olevan ytimen asetukset `/proc/config.gz`-
  tiedostosta tai ydinkuvasta.
