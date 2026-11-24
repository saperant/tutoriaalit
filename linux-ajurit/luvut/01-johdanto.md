# Johdanto {.runko-johdanto}

Laiteajuri on ytimen osa, joka tuntee yhden laitteen: sen rekisterit,
keskeytykset, muistisiirrot ja virhetilanteet. Muu ydin ja käyttäjän
ohjelmat näkevät laitteen yleisen rajapinnan kautta, kuten tiedostona
`/dev`-hakemistossa, verkkoliitäntänä, lohkolaitteena tai
lämpöanturina `sysfs`issä. Ajuri kääntää yleisen pyynnön, kuten
"lue 64 tavua" tai "anna lämpötila", laitteen kielelle ja laitteen
vastauksen takaisin.

Linuxissa on enemmän ajurikoodia kuin mitään muuta: hakemisto `drivers/`
on yli puolet ytimen lähdekoodista. Siksi ytimeen on rakennettu laaja
ajurimalli, joka hoitaa sen, mikä on kaikille ajureille yhteistä:
laitteiden löytäminen ja sitominen ajureihin, resurssien hallinta,
virranhallinta, laitetiedostot ja tilan näyttäminen. Hyvä ajuri on
lyhyt, koska se käyttää näitä palveluja eikä toteuta niitä itse.

Tutoriaali käsittelee

- **ytimen moduuleja**: ulkopuolisen moduulin kääntäminen Kbuildilla,
  parametrit, lisenssi ja tahrat, symbolien vienti ja riippuvuudet
- **merkkilaiteajureita**: laitenumerot, `cdev`, `file_operations`,
  estävä ja ei-estävä luku, `poll`, `ioctl` ja kopiointi käyttäjän
  muistiin ja sieltä
- **platform-ajureita ja laitepuuta**: `compatible`-sidonta, `probe` ja
  `remove`, `devm_`-resurssit, rekisterien käyttö ja laitepuun
  ominaisuudet
- **keskeytyksiä**: ylä- ja alapuolisko, keskeytyssäikeet, työjonot ja
  lukitus eri konteksteissa
- **DMA:ta**: koherentti ja virtauskuvaus, DMA-maski ja välimuistin
  koherenssi ARM64:ssä
- **I2C- ja SPI-ajureita**: alijärjestelmien rakenne, regmap, hwmon ja
  oma SPI-ohjain
- **sysfsiä ja debugfsiä**: laitteen attribuutit ja kehittäjän
  työkalut
- **ytimen vianetsintää**: lokitasot, dynaaminen debug, ftrace,
  kaatumisilmoitukset ja lukkotarkistimet.

Esitietoina oletetaan taidot *Sulautettu Linux* (ytimen konfigurointi,
ristiinkääntäminen, laitepuun perusteet ja initramfs) ja
*Oheislaiteväylät* (UART, SPI, I2C ja DMA bare-metal-ohjelmasta käsin).
Tämä tutoriaali tekee samat asiat Linux-ytimen sisällä ja vertaa niitä
bare-metal-ajureihin. *Käyttöjärjestelmät*-taidosta oletetaan ydin- ja
käyttäjätilan ero, järjestelmäkutsut ja synkronoinnin perusteet, ja
C-kieltä on osattava hyvin.

## Ydintilan ohjelmointi

Ajuri on C-koodia, mutta ympäristö poikkeaa käyttäjätilan ohjelmasta:

| Asia | Käyttäjätila | Ydin |
|----------|------------------|--------------------------------------|
| Kirjasto | C-kirjasto, POSIX | ytimen omat funktiot: `kmalloc`, `printk`, `kstrtou32` |
| Muistivirhe | prosessi kaatuu | koko järjestelmä voi kaatua tai vioittua |
| Muisti | virtuaalinen, sivutettava | ei sivutusta; `GFP_KERNEL` voi nukkua, `GFP_ATOMIC` ei |
| Pino | megatavuja | 16 kt ARM64:ssä: ei suuria paikallisia taulukoita |
| Samanaikaisuus | säikeet, jos itse luot | aina: monta prosessia, keskeytykset ja CPU:ta |
| Liukuluvut | vapaasti | ei käytössä ilman erityistoimia |
| Virheet | `errno`, poikkeukset | negatiivinen virhekoodi paluuarvona, `ERR_PTR` |

Ytimen sisällä ei ole erillistä suojaa ajurin virheitä vastaan. Väärä
osoitin, unohtunut lukko tai vapautettu muisti näkyy myöhemmin jossain
muualla, usein satunnaisesti. Siksi ajurikehityksessä käytetään ytimen
omia tarkistimia (luku *Vianetsintä*) ja testataan jokaista muutosta
emulaattorissa ennen oikeaa laitetta.

Ytimen sisäiset rajapinnat eivät ole vakaita: funktion parametrit ja
nimet muuttuvat versiosta toiseen, ja muutoksen tekijä korjaa kaikki
ytimen lähdepuussa olevat käyttäjät. Ytimen ulkopuolinen ajuri jää
tästä paitsi ja hajoaa päivityksissä. Tämän tutoriaalin koodi on
kirjoitettu versiolle 6.8, ja sen rajapinnat on tarkistettu sitä
vasten. Käyttäjätilan rajapinnat, kuten järjestelmäkutsut ja
`sysfs`-tiedostot, ovat sen sijaan vakaita: kerran julkaistua ei
muuteta.

## Laboratorio

Esimerkit ajetaan QEMU:n `virt`-koneessa samalla ympäristöllä kuin
*Sulautettu Linux* -tutoriaalissa. Hakemisto `esimerkit/ymparisto/` on
siitä kopioitu: `ydin.mk` kääntää ytimen, `aja-qemu.sh` käynnistää
koneen ja `tarkista-config.sh` varmistaa, että kaikki pyydetyt asetukset
otettiin käyttöön. Ydin saa lisäksi oman fragmentin:

```{.ini tiedosto="esimerkit/ymparisto/ajurit.config" osa="vianetsinta"}
```

```{.ini tiedosto="esimerkit/ymparisto/ajurit.config" osa="vaylat"}
```

Vianetsinnän asetukset tekevät ytimestä suuremman ja hitaamman, joten
tuotantoydin käännetään ilman lukkotarkistimia ja jäljitystä. Kehityksen
aikana ne kuitenkin löytävät virheitä, joita testit eivät muuten
paljastaisi.

Laitteita on vähän, koska `virt`-kone on tehty virtuaalikoneille eikä
jäljittele mitään piirilevyä:

| Laite | Osoite | Tutoriaalissa |
|-------|--------|---------------|
| PL011-sarjaportti | `0x9000000` | konsoli |
| PL031-reaaliaikakello | `0x9010000` | oman platform-ajurin laite: rekisterit ja keskeytys |
| fw_cfg | `0x9020000` | DMA: QEMU kopioi tiedostoja vieraan muistiin |
| I2C | ei ole | ytimen testiväylä `i2c-stub` tarjoaa piirien rekisterit |
| SPI | ei ole | oma ohjelmallinen ohjain ja simuloitu muistipiiri |

Puuttuvat väylät on korvattu ohjelmalla, ja tekstissä sanotaan, mikä on
simuloitua. Ajurin kannalta ero on pieni: I2C- tai SPI-laitteen ajuri
puhuu alijärjestelmän rajapinnalle eikä tiedä, onko väylän takana piiri
vai ohjelma. Juuri tämä kerrosrakenne tekee Linuxin ajureista
siirrettäviä laitteesta toiseen.

## Testit initinä

Jokainen testi on oma pieni järjestelmänsä: initramfs, jossa on
moduulit, testiohjelmat ja vaiheajuri `/init`. Vaiheajuri lukee
tiedoston `/vaiheet` ja suorittaa sen rivit yksi kerrallaan. Komennot
ovat sellaisia, joita kehittäjä kirjoittaisi kuoreen: moduulin lataus,
tiedoston luku ja kirjoitus sekä ohjelman ajo. Jokaisen komennon jälkeen
vaiheajuri näyttää ytimen lokin uudet rivit, jos ne alkavat jollain
suodatettavista etuliitteistä:

```{.c tiedosto="esimerkit/kayttaja/ajo.c" osa="loki"}
```

Ytimen loki luetaan laitteesta `/dev/kmsg`, joka antaa yhden tietueen
lukua kohden. Tietueessa on lokitaso, järjestysnumero ja aika
mikrosekunteina, joten tulosteesta poistetaan kaikki muu kuin viesti.
Huomaa myös, että `/dev/kmsg` näyttää muut kuin tulostettavat
ASCII-merkit muodossa `\xc3\xa4`. Ytimen lokiviestit kirjoitetaan siksi
ASCII-merkein, kuten tämän tutoriaalin ajureissakin.

Moduulit ladataan järjestelmäkutsulla `finit_module`, kuten
`modprobe` tekee lopulta itsekin:

```{.c tiedosto="esimerkit/kayttaja/ajo.c" osa="lataa"}
```

Ytimen oma konsoli on hiljennetty (`loglevel=0` ja
`printk.console_no_auto_verbose=1`), jotta lokirivit eivät sekoitu
testin tulosteeseen. Lokiviestit näkyvät vain vaiheajurin kautta
suodatettuina, ja tulosteesta tulee toistettava. `esimerkit/Makefile`
kokoaa jokaiselle testille initramfs-luettelon ja käynnistää sen:

```{.make tiedosto="esimerkit/Makefile" osa="testi"}
```

Kokonainen ajo kääntää ytimen ensimmäisellä kerralla (noin 10 minuuttia
kuormitetulla nelinytimisellä koneella ja noin 2 Gt levyä) ja sen
jälkeen moduulit, ohjelmat ja kolmetoista testijärjestelmää alle
minuutissa. Testin voi myös käynnistää päätteeseen komennolla `make aja
T=02-jono`, jolloin ytimen konsoli on päällä ja käynnistysloki näkyy.

## Koodityyli

Ytimen koodityyli (`Documentation/process/coding-style.rst`) sisentää
sarkaimilla, joiden leveys on kahdeksan merkkiä. Tämän tutoriaalin koodi
on sisennetty neljällä välilyönnillä, jotta se mahtuu sivun leveyteen.
Muuten koodi noudattaa ytimen tyyliä: aaltosulkeiden paikat, `goto`-
siivous virhepoluilla ja negatiiviset virhekoodit. Ytimeen lähetettävä
koodi tarkistetaan skriptillä `scripts/checkpatch.pl`, joka huomauttaa
myös sisennyksestä.

Tunnisteet ovat suomeksi, kuten muissakin tämän sarjan tutoriaaleissa.
Ytimen rajapinnan nimet (`probe`, `remove`, `show`, `store`) ja
makrojen odottamat nimet (`laskuri_show` makrolle `DEVICE_ATTR_RO`)
ovat englanniksi, koska ytimen makrot muodostavat nimet niistä.
