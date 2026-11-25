# Ensimmäinen käynnistys: initramfs ja init

Käännetty ydin ei vielä tee mitään hyödyllistä. Kun se on alustanut
muistinhallinnan, keskeytykset, ajastimet ja ajurit, se tarvitsee
juuritiedostojärjestelmän ja siellä ohjelman, jonka se käynnistää
ensimmäisenä käyttäjätilan prosessina. Tämä prosessi on *init*, sen
prosessinumero on 1, ja kaikki muut käyttäjätilan prosessit ovat sen
jälkeläisiä. Tässä luvussa tehdään pienin mahdollinen järjestelmä:
ydin ja yksi ohjelma muistissa.

## Ytimen komentorivi

Käynnistin antaa ytimelle *komentorivin*, merkkijonon parametreja.
QEMU:n suorassa käynnistyksessä se annetaan valitsimella `-append`,
U-Bootissa muuttujassa `bootargs` ja laitepuussa solmun `/chosen`
ominaisuudessa `bootargs`. Tärkeimmät parametrit:

| Parametri | Merkitys |
|-----------|----------|
| `console=ttyAMA0` | konsoli PL011-sarjaporttiin (x86:ssa `ttyS0`) |
| `loglevel=1` | konsolille vain hätätilanteen viestit (0–7) |
| `panic=-1` | uudelleenkäynnistys heti paniikin jälkeen |
| `root=/dev/vda` | juuritiedostojärjestelmän laite |
| `ro`, `rw` | juuren kiinnitys vain luku- tai luku–kirjoitustilaan |
| `rootwait` | odota juurilaitetta (USB ja SD-kortit ilmestyvät viiveellä) |
| `init=/sbin/init` | pysyvän juuren init-ohjelma |
| `rdinit=/init` | initramfsin init-ohjelma (oletus `/init`) |
| `quiet` | sama kuin `loglevel=4` |

Parametrit, joita ydin ei tunne, välitetään init-ohjelmalle:
pisteettömät (`kaynnistys=extlinux`) ympäristömuuttujina tai
argumentteina, pisteelliset (`moduuli.asetus=1`) moduulien
parametreina. Koko rivi näkyy käyttäjätilassa tiedostossa
`/proc/cmdline`.

## Ytimen käynnistysloki

Ilman `loglevel`-parametria ydin kirjoittaa konsoliin satoja rivejä.
Seuraavassa on niistä valittu muutama, ja aikaleimat ja osoitteet on
suodatettu pois:

```{.make tiedosto="esimerkit/Makefile" osa="loki"}
```

```{.tuloste tiedosto="esimerkit/testit/04-loki.odotettu"}
```

Rivit kertovat käynnistyksen vaiheet. Ensimmäisenä on ytimen versio,
käännöksen tekijä ja kone (luvun 3 toistettavat arvot). *Machine model*
tulee laitepuusta (luku 6), ja komentorivi tulee käynnistimeltä.
Muistirivi kertoo, paljonko muistia jäi käyttäjätilalle ja paljonko
ydin itse vie. PL011-ajuri löytää sarjaportin, ja siitä lähtien
konsoli toimii; aiemmat viestit ydin on puskuroinut ja tulostaa ne nyt.
Sitten ydin purkaa initramfsin ja käynnistää `/init`-ohjelman.

Ytimen viestit ovat myös ytimen lokipuskurissa, josta niitä luetaan
komennolla `dmesg` tai laitteesta `/dev/kmsg`. Sulautetussa
laitteessa, jossa sarjakonsolia ei ole kytketty, puskuri on usein
ainoa tieto käynnistyksestä. Ennen sarjaportin ajurin käynnistymistä
syntyvät viestit saa näkyviin *early console* -tuella
(`earlycon`-parametri), jolla vika löytyy, vaikka ydin pysähtyisi
ennen konsolin alustusta.

## Initramfs

*Initramfs* on cpio-arkisto, jonka käynnistin lataa muistiin ytimen
viereen. Ydin purkaa sen RAM-levyn tapaiseen tiedostojärjestelmään
(*rootfs*, käytännössä `tmpfs` tai `ramfs`), joka toimii
ensimmäisenä juurena. Jos arkistossa on ohjelma `/init`, ydin
käynnistää sen. Jakeluissa initramfsin tehtävä on valmistella oikea
juuri: ladata levyohjaimen ajuri, avata salattu osio tai koota RAID ja
vaihtaa sitten juureksi oikea tiedostojärjestelmä (`switch_root`).
Sulautetussa laitteessa initramfs voi olla myös koko järjestelmä: se on
aina puhdas, koska se luetaan joka käynnistyksessä uudelleen.

Arkisto tehdään ytimen omalla työkalulla `gen_init_cpio`, joka lukee
tekstimuotoisen luettelon:

```{.text tiedosto="esimerkit/04-init/initramfs.lista"}
```

Työkalun etu tavalliseen `cpio`-komentoon verrattuna on, että se voi
luoda laitetiedoston `/dev/console` ja asettaa tiedostojen omistajaksi
pääkäyttäjän ilman pääkäyttäjän oikeuksia. Laitetiedosto on
tarpeen, koska ydin avaa konsolin init-prosessin vakiosyötteeksi ja
-tulosteiksi juuri tästä polusta ennen kuin mitään on kiinnitetty.
Ilman sitä init käynnistyy, mutta sen tulosteet katoavat, ja ydin
varoittaa: *Warning: unable to open an initial console*.

```{.make tiedosto="esimerkit/Makefile" osa="initramfs"}
```

Valitsin `-t` asettaa kaikille tiedostoille saman aikaleiman, ja
`gzip -n` jättää pakkaukseen tallentamatta tiedostonimen ja ajan.
Molemmat tarvitaan, jotta arkisto on tavulleen sama jokaisella
rakennuskerralla.

Initramfs voidaan myös kääntää ytimen sisään asetuksella
`CONFIG_INITRAMFS_SOURCE`, jolloin käynnistin lataa vain yhden
tiedoston. Erillinen arkisto on joustavampi, koska sen voi vaihtaa
ytimeen koskematta. Vanhempi *initrd* on eri asia: lohkolaitteen kuva,
joka kiinnitetään ajurilla ja vaatii tiedostojärjestelmän tuen
ytimeen. Nimeä käytetään yhä, esimerkiksi QEMU:n valitsimessa
`-initrd`, vaikka arkisto olisi initramfs.

## Init-ohjelma

Pienin hyödyllinen init kiinnittää ytimen virtuaaliset
tiedostojärjestelmät, kertoo, mihin järjestelmään se heräsi, ja
sammuttaa koneen. Kiinnitys on yhden funktion asia:

```{.c tiedosto="esimerkit/04-init/init.c" osa="kiinnita"}
```

```{.c tiedosto="esimerkit/04-init/init.c" osa="main"}
```

Ohjelma käännetään staattisesti, joten initramfsiin ei tarvita
C-kirjastoa eikä dynaamista linkittäjää. Käynnistys:

```{.make tiedosto="esimerkit/Makefile" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/testit/04-init.odotettu"}
```

Neljä tiedostojärjestelmää ovat jokaisen Linux-järjestelmän perusta:

- **`/proc`** (`proc`): prosessit (`/proc/<pid>/`), ytimen tila ja
  asetukset (`/proc/cmdline`, `/proc/meminfo`, `/proc/sys/`).
- **`/sys`** (`sysfs`): ytimen laitemalli: väylät, laitteet, ajurit ja
  niiden attribuutit sekä laitepuu (`/sys/firmware/devicetree`).
- **`/dev`** (`devtmpfs`): ytimen luomat laitetiedostot jokaiselle
  löytyneelle laitteelle. Ilman sitä laitetiedostot pitäisi luoda
  käsin `mknod`illa tai jättää `udev`in tai `mdev`in tehtäväksi.
- **`/run`** (`tmpfs`): ajonaikaiset tiedostot, kuten prosessinumerot,
  soketit ja lukot. Se tyhjenee jokaisessa käynnistyksessä.

Kiinnitysvalitsimet `MS_NOSUID`, `MS_NODEV` ja `MS_NOEXEC` estävät
setuid-ohjelmat, laitetiedostot ja ohjelmien suorittamisen
hakemistoissa, joissa niitä ei tarvita. Ne ovat halpaa suojausta:
hyökkääjä ei voi esimerkiksi kirjoittaa ajettavaa tiedostoa `/run`iin ja
käynnistää sitä.

Rivi `/dev/vda ei` kertoo, että virtio-levyä ei ole, koska QEMU:lle ei
annettu levyä. Kun sama initramfs käynnistetään luvussa 5 U-Bootin
kautta levyltä, `devtmpfs` sisältää myös laitteen `/dev/vda`.

## PID 1 on erityinen

Prosessi 1 eroaa muista kolmella tavalla, jotka init-ohjelman on
otettava huomioon:

1. **Se ei saa päättyä.** Jos init päättyy, ydin pysähtyy
   paniikkiin: *Kernel panic - not syncing: Attempted to kill init!*
   Siksi esimerkin init ei palaa `main`ista vaan sammuttaa koneen
   järjestelmäkutsulla `reboot(RB_POWER_OFF)`. ARM64:ssä ydin välittää
   sammutuspyynnön laiteohjelmistolle PSCI-rajapinnan kautta, ja QEMU
   päättyy.
2. **Se perii orvot.** Kun prosessin vanhempi päättyy, prosessin
   vanhemmaksi tulee init. Initin on kutsuttava `wait`-funktioita, tai
   päättyneet orvot jäävät *zombeiksi*, jotka varaavat prosessitaulun
   paikan.
3. **Signaalit eivät tapa sitä.** Ydin ei toimita prosessille 1
   signaalia, jolle sillä ei ole käsittelijää, joten edes `SIGKILL`
   ei pysäytä sitä. Init sammutetaan pyytämällä sitä itse sammuttamaan
   järjestelmä, tavallisesti signaalilla, jolle sillä on käsittelijä.

Ennen sammutusta kutsutaan `sync()`, joka kirjoittaa puskuroidut
tiedot levylle. Initramfs-järjestelmässä sillä ei ole väliä, mutta
pysyvällä juurella (luku 8) ilman sitä viimeiset muutokset katoavat.

## Käytännössä

- **Testaa ydin ensin initramfsillä ja staattisella initillä.** Kun
  tämä toimii, ydin, konsoli ja käynnistys ovat kunnossa, ja vika
  myöhemmin on juuritiedostojärjestelmässä, ajureissa tai palveluissa.
- **Tee initramfsistä toistettava.** Kiinteä aikaleima, `gzip -n` ja
  `gen_init_cpio` ilman pääkäyttäjän oikeuksia tuottavat saman arkiston
  joka kerta, ja muutokset näkyvät tarkistussummasta.
- **Älä anna initin päättyä.** Kaikki virhepolut päättyvät joko
  uudelleenyritykseen, hätäkonsoliin tai hallittuun uudelleen-
  käynnistykseen. Paniikki on pahin vaihtoehto, koska syy jää usein
  näkymättä.
- **Kiinnitä virtuaaliset tiedostojärjestelmät rajoittavin
  valitsimin.** `nosuid`, `nodev` ja `noexec` kaikkialla, missä niitä ei
  tarvita.
- **Pidä `earlycon` mielessä.** Kun ydin ei tulosta mitään, vika on
  usein ennen konsoliajurin käynnistymistä: väärä konsolin nimi,
  puuttuva ajuri tai laitepuun virhe.

## Itsearviointi

- Osaat selittää, mitä ydin tekee ennen ensimmäistä käyttäjätilan
  prosessia ja miten se löytää init-ohjelman.
- Osaat käyttää ytimen komentorivin keskeisiä parametreja ja lukea
  käynnistyslokin vaiheet.
- Osaat rakentaa initramfs-arkiston `gen_init_cpio`lla ilman
  pääkäyttäjän oikeuksia ja selittää, miksi `/dev/console` tarvitaan.
- Osaat kirjoittaa init-ohjelman, joka kiinnittää `/proc`, `/sys`,
  `/dev` ja `/run` ja sammuttaa järjestelmän siististi.
- Osaat kertoa, mikä tekee prosessista 1 erityisen.
