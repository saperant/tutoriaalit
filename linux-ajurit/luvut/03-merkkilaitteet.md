# Merkkilaiteajurit

Merkkilaite (*character device*) on laite, jota käytetään tavuvirtana
tavallisilla tiedostokutsuilla: `open`, `read`, `write`, `poll`,
`ioctl` ja `close`. Sarjaportit, päätteet, `/dev/null`, `/dev/random`,
GPIO-laitteet, I2C-väylän `/dev/i2c-N` ja suuri osa sulautettujen
laitteiden omista ajureista ovat merkkilaitteita. Lohkolaitteet
(levyt) ja verkkoliitännät ovat omia luokkiaan, joilla on omat
rajapintansa.

Luvun esimerkkiajuri `jono` on prosessien välinen viestijono: yksi
prosessi kirjoittaa laitteeseen `/dev/jono0` ja toinen lukee sen.
Laitteistoa ei tarvita, joten luvussa voi keskittyä ajurin ja
käyttäjätilan väliseen rajapintaan.

## Laitenumerot ja laitetiedostot

Ydin tunnistaa merkkilaitteen *laitenumerosta*, jossa on kaksi osaa:
pääluku (*major*) valitsee ajurin ja sivuluku (*minor*) ajurin sisällä
laitteen. Tiedosto `/dev/jono0` on vain nimi laitenumerolle; sen
avaaminen ohjaa kutsut numeron omistavalle ajurille. Ajuri varaa
numeronsa ja rekisteröi laitteensa neljässä vaiheessa:

```{.c tiedosto="esimerkit/02-merkkilaite/jono.c" osa="alku"}
```

1. **`alloc_chrdev_region`** varaa vapaan pääluvun ja halutun määrän
   sivulukuja. Kiinteitä päälukuja (`register_chrdev_region`) käyttävät
   vain vanhat, standardoidut laitteet.
2. **`class_create`** luo laiteluokan, joka näkyy hakemistona
   `/sys/class/jono`.
3. **`cdev_init` ja `cdev_add`** liittävät laitenumeron ajurin
   `file_operations`-tauluun. Laite on käytettävissä heti `cdev_add`in
   jälkeen, joten kaiken muun on oltava valmiina sitä ennen.
4. **`device_create`** luo laitteen ajurimalliin. Ydin lähettää siitä
   tapahtuman (*uevent*), ja `devtmpfs` luo tiedoston `/dev/jono0`.
   Täydessä järjestelmässä `udev` asettaa sen jälkeen oikeudet ja
   symboliset linkit.

Virhepolku käyttää ytimen tavallista `goto`-siivousta: jokainen
nimiö purkaa yhden vaiheen, ja vaiheet puretaan käänteisessä
järjestyksessä. Testijärjestelmä näyttää luodut laitteet ja niiden
uevent-tiedot:

```{.text tiedosto="esimerkit/02-merkkilaite/jono.vaiheet" osa="vaiheet"}
```

```{.tuloste tiedosto="esimerkit/testit/02-jono.odotettu" osa="vaiheet"}
```

Pääluku 254 on ytimen valitsema. Laitteen nimi ja numero ovat
tiedostossa `uevent` juuri niin kuin `udev` ne saa.

## Tiedosto-operaatiot

`file_operations` on taulu funktio-osoittimia. Ydin kutsuu niitä
laitetiedoston järjestelmäkutsuista:

```{.dot otsikko="Lukukutsun polku käyttäjän ohjelmasta ajuriin. Katkoviivan alapuoli on ydintä."}
digraph {
  rankdir=TB; node [shape=box];
  ohjelma [label="ohjelma: read(fd, puskuri, 64)"];
  subgraph cluster_ydin { label="ydin"; labeljust=l; style=dashed;
    kutsu [label="järjestelmäkutsu: fd → struct file"];
    vfs [label="VFS: tiedoston f_op-taulu"];
    ajuri [label="ajuri: jono_lue()"];
    jono [label="odotusjono ja kfifo"];
  }
  ohjelma -> kutsu [label="siirtymä ydintilaan"];
  kutsu -> vfs;
  vfs -> ajuri [label="f_op->read"];
  ajuri -> jono [label="nukkuu, jos tyhjä"];
  ajuri -> ohjelma [label="copy_to_user,\npaluuarvo: tavujen määrä", constraint=false];
}
```

```{.c tiedosto="esimerkit/02-merkkilaite/jono.c" osa="fops"}
```

Kenttä `owner` kasvattaa moduulin viittauslaskuria aina, kun laite on
auki, joten moduulia ei voi poistaa kesken käytön. Puuttuva operaatio
palauttaa yleisen virheen, esimerkiksi puuttuva `write` virheen
`EINVAL`. `llseek = no_llseek` kertoo, ettei jonossa voi siirtyä.

Laitekohtainen tila liitetään avattuun tiedostoon. Inoden `i_cdev`
osoittaa ajurin rakenteen sisällä olevaan `cdev`-jäseneen, ja
`container_of` palauttaa koko rakenteen:

```{.c tiedosto="esimerkit/02-merkkilaite/jono.c" osa="rakenne"}
```

```{.c tiedosto="esimerkit/02-merkkilaite/jono.c" osa="avaa"}
```

`container_of` on ytimen tavallisin tapa siirtyä upotetusta
rakenteesta sen omistajaan. Sama malli toistuu kaikkialla: `kobject`
laitteen sisällä, `work_struct` ajurin tilassa ja `list_head` alkion
sisällä.

## Luku ja kirjoitus

Lukufunktio saa käyttäjän puskurin osoitteen ja pituuden. Puskuri on
käyttäjän muistissa, eikä ydin saa käyttää sitä suoraan: osoite voi
olla virheellinen, sivu voi olla levyllä tai osoite voi osoittaa
ytimen muistiin. Kopiointi tehdään aina funktioilla `copy_to_user` ja
`copy_from_user` tai niitä käyttävillä apufunktioilla, kuten
`kfifo_to_user`. Ne tarkistavat osoitteen ja palauttavat virheen
`EFAULT` kaatumisen sijaan.

```{.c tiedosto="esimerkit/02-merkkilaite/jono.c" osa="lue"}
```

Funktiossa on estävän luvun tavallinen malli:

- **Ehto tarkistetaan lukon kanssa.** Jos jonossa on dataa, luetaan
  heti. Lukko tarvitaan, koska kaksi prosessia voi lukea ja kirjoittaa
  samaa jonoa yhtä aikaa eri CPU:illa. Tässä riittää mutex, koska
  kaikki käyttäjät ovat prosesseja; lukon valinta, kun mukana on
  keskeytys, käsitellään luvussa 5.
- **Ei-estävä tila (`O_NONBLOCK`) palauttaa `EAGAIN`.** Ohjelma, joka
  käyttää `poll`- tai `epoll`-kutsua, avaa laitteen näin.
- **Nukutaan lukon ulkopuolella.** `wait_event_interruptible` nukkuu,
  kunnes ehto on tosi tai prosessi saa signaalin. Jos nukkuja pitäisi
  lukkoa, kirjoittaja ei pääsisi koskaan lisäämään dataa.
- **Herätyksen jälkeen ehto tarkistetaan uudelleen.** Toinen lukija on
  voinut ehtiä ensin.
- **Signaali palauttaa `-ERESTARTSYS`.** Ydin joko käynnistää kutsun
  uudelleen signaalinkäsittelijän jälkeen tai palauttaa ohjelmalle
  virheen `EINTR`.

Paluuarvo on luettujen tavujen määrä, joka voi olla pyydettyä pienempi.
Kirjoitus on peilikuva: se odottaa tilaa ja herättää lukijat.

## poll

`poll` kertoo, onko laite valmis lukuun tai kirjoitukseen nukkumatta
itse:

```{.c tiedosto="esimerkit/02-merkkilaite/jono.c" osa="poll"}
```

`poll_wait` ei odota, vaan liittää kutsujan odotusjonoihin. Kun ajuri
myöhemmin herättää jonon, ydin kutsuu `poll`-funktiota uudelleen ja
herättää `poll`-, `select`- tai `epoll`-kutsussa odottavan prosessin,
jos maski on muuttunut. Sama funktio palvelee kaikkia kolmea
järjestelmäkutsua.

## ioctl

`ioctl` on laitteen omien komentojen kanava: asetukset, tilan kysely ja
toiminnot, jotka eivät sovi lukuun ja kirjoitukseen. Komennot
määritellään otsakkeessa, jonka sekä ajuri että käyttäjätilan ohjelma
ottavat mukaan:

```{.c tiedosto="esimerkit/02-merkkilaite/jono.h" osa="ioctl"}
```

Makrot `_IO`, `_IOR`, `_IOW` ja `_IOWR` koodaavat komentonumeroon
suunnan, argumentin koon, ajurin tunnusmerkin (*magic*) ja järjestysnumeron.
Ydin ja `strace` osaavat siksi tulkita komennon, ja väärälle laitteelle
lähetetty komento ei osu sattumalta johonkin olemassa olevaan.
Rakenteessa käytetään kiinteän kokoisia tyyppejä (`__u32`), jotta se on
sama 32- ja 64-bittisellä ohjelmalla:

```{.c tiedosto="esimerkit/02-merkkilaite/jono.c" osa="ioctl"}
```

Tuntematon komento palauttaa `-ENOTTY`, kuten POSIX määrää.
Uutta rajapintaa suunnitellessa `ioctl` kannattaa varata toiminnoille.
Yksittäiset asetukset ja tilatiedot sopivat usein paremmin
sysfs-attribuuteiksi (luku 5), joita voi lukea ja kirjoittaa ilman
omaa ohjelmaa.

## Testi käyttäjätilassa

Ajurin rajapinta testataan käyttäjätilan ohjelmalla, joka ajetaan
QEMU:ssa ladatun moduulin kanssa:

```{.c tiedosto="esimerkit/02-merkkilaite/jonotesti.c" osa="perus"}
```

```{.c tiedosto="esimerkit/02-merkkilaite/jonotesti.c" osa="taysi"}
```

Estävää lukua varten lapsiprosessi lukee tyhjää jonoa ja nukkuu
ytimessä, kunnes vanhempi kirjoittaa:

```{.c tiedosto="esimerkit/02-merkkilaite/jonotesti.c" osa="esto"}
```

Tuloste näkyy yllä luvun alun vaiheiden tulosteessa. Virheellinen osoite
on virhe `EFAULT`, tuntematon `ioctl` virhe `ENOTTY`, ja täyttynyt jono
palauttaa ei-estävässä tilassa virheen `EAGAIN`, kun 64 tavua on
kirjoitettu.

## misc-laitteet

Yksittäiselle laitteelle edellä kuvatut neljä vaihetta ovat
raskaita. `miscdevice` on valmis luokka, jonka kaikki laitteet jakavat
pääluvun 10: ajuri täyttää rakenteen, jossa on nimi ja
`file_operations`-taulu, ja kutsuu `misc_register`. Luvun 4 ajuri
käyttää sitä. Oma luokka ja pääluku kannattavat, kun laitteita on
useita samanlaisia, kuten tämän luvun jonoja, tai kun laitteet
halutaan omaan hakemistoonsa `/sys/class`-hakemistossa.

## mmap: puskuri käyttäjän osoiteavaruuteen

`read` ja `write` kopioivat jokaisen tavun ytimen ja käyttäjän muistin
välillä ja maksavat järjestelmäkutsun. Kun dataa on paljon tai sitä
luetaan jatkuvasti, kuten kameran kuvapuskurissa, äänilaitteen
rengaspuskurissa tai jaetussa tilalohkossa, ajuri voi *kuvata* oman
muistinsa suoraan prosessin osoiteavaruuteen. Sen jälkeen ohjelma lukee
ja kirjoittaa muistia tavallisilla osoittimilla ilman
järjestelmäkutsuja.

Esimerkkiajuri `kartta` on misc-laite, jolla on yksi sivu muistia:

```{.c tiedosto="esimerkit/02-merkkilaite/kartta.c" osa="fops"}
```

```{.c tiedosto="esimerkit/02-merkkilaite/kartta.c" osa="mmap"}
```

Ydin on jo varannut prosessin osoiteavaruudesta alueen
(`vm_area_struct`), ja ajurin tehtävä on kertoa, mitkä sivut sen
taakse tulevat. `vm_pgoff` on `mmap`-kutsun siirtymä sivuina. Ajurin on
tarkistettava siirtymä ja koko itse, tai ohjelma voi pyytää kuvauksen
puskurin ohi. `vm_insert_page` sopii ytimen tavallisille sivuille.
Laitteen rekisterialue kuvataan funktiolla `io_remap_pfn_range` ja
DMA-puskuri funktiolla `dma_mmap_coherent` (luku 6).

```{.c tiedosto="esimerkit/02-merkkilaite/karttatesti.c" osa="kuvaus"}
```

```{.tuloste tiedosto="esimerkit/testit/02-kartta.odotettu" osa="vaiheet"}
```

Ohjelman kirjoitus näkyy heti sekä `read`-kutsulle että toiselle
kuvaukselle, koska kaikki kolme käyttävät samaa fyysistä sivua. Liian
suuri kuvaus ja siirtymä puskurin ohi hylätään virheellä `EINVAL`.

Kuvauksen hinta on, että ajuri ei näe käyttöä: lukuja ja kirjoituksia
ei voi tarkistaa, lukita eikä odottaa. Ohjelman ja ajurin on sovittava
puskurin rakenteesta ja synkronoinnista erikseen, tavallisesti niin,
että data kulkee kuvauksen kautta ja herätykset `poll`-kutsulla.
Kuvattu muisti ei myöskään saa kadota ohjelman alta: sivu vapautetaan
vasta, kun viimeinen kuvaus on purettu, ja avoin tiedosto estää
moduulin poiston.

## Käytännössä

- **Kopioi käyttäjän muistiin ja sieltä vain `copy_*_user`-funktioilla,
  ja palauta niiden virheestä `-EFAULT`.** Käyttäjän osoite ei ole
  koskaan luotettava.
- **Älä nuku lukko hallussa.** Tarkista ehto lukon kanssa, vapauta lukko
  ja odota `wait_event_interruptible`-makrolla. Tarkista ehto uudelleen
  herättyäsi.
- **Tue `O_NONBLOCK`-tilaa ja `poll`-kutsua.** Tapahtumasilmukkaa
  käyttävä ohjelma ei voi käyttää laitetta, joka osaa vain estää.
- **Palauta signaalista `-ERESTARTSYS`.** Prosessin pitää voida keskeyttää
  odottava luku.
- **Tarkista `mmap`-kutsun siirtymä ja koko.** Kuvaus puskurin ohi
  antaa ohjelmalle ytimen muistia.
- **Pidä `ioctl`-rakenteet kiinteän kokoisina ja otsake yhteisenä.**
  Käyttäjätilan rajapinta on ikuinen: kenttää ei voi poistaa, kun
  ohjelmat käyttävät sitä.

## Itsearviointi

- Osaat varata laitenumerot, rekisteröidä `cdev`in ja luoda
  laitetiedoston laiteluokan kautta sekä purkaa ne virhepolulla
  oikeassa järjestyksessä.
- Osaat toteuttaa estävän ja ei-estävän luvun odotusjonolla ja
  selittää, miksi nukkuminen tapahtuu lukon ulkopuolella.
- Osaat toteuttaa `poll`-operaation ja `ioctl`-komennot ja määritellä
  komentonumerot `_IOR`- ja `_IO`-makroilla.
- Osaat selittää, miksi käyttäjän puskuria ei saa käyttää suoraan ja
  mitä `copy_to_user` tarkistaa.
- Osaat toteuttaa `mmap`-operaation, joka kuvaa ajurin sivun
  käyttäjän osoiteavaruuteen, ja kertoa, mitä ajurin on siinä
  tarkistettava.
