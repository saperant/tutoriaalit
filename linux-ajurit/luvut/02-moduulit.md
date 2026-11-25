# Ytimen moduulit

Moduuli on ytimeen ajon aikana ladattava objektitiedosto (`.ko`,
*kernel object*). Ladattu moduuli on osa ydintä: se ajetaan ytimen
oikeuksin, sen muisti on ytimen muistia ja se voi kutsua mitä tahansa
ytimen viemää funktiota. Moduuli ei siis ole eristetty kuten prosessi,
vaan tapa jakaa ydin osiin, jotka ladataan tarpeen mukaan.

*Sulautettu Linux* -tutoriaalissa käännettiin pienin mahdollinen moduuli
ja ladattiin se. Tässä luvussa tehdään kaksi moduulia, joista toinen
käyttää toisen funktiota, ja käydään läpi parametrit, virheet
latauksessa, lisenssit ja riippuvuudet.

## Rakenne

Esimerkkimoduuli `tilasto` pitää kirjaa mittausarvoista, joita muut
moduulit sille antavat. Moduulin alku- ja loppufunktio:

```{.c tiedosto="esimerkit/01-moduulit/tilasto.c" osa="alku"}
```

- **`module_init` ja `module_exit`** nimeävät funktiot, jotka ydin
  kutsuu latauksessa ja poistossa. Jos moduuli käännetään ytimeen
  (`=y`), alkufunktio kutsutaan käynnistyksessä eikä loppufunktiota
  koskaan.
- **`__init` ja `__exit`** sijoittavat funktiot omiin osioihinsa.
  Ydin vapauttaa `__init`-koodin latauksen jälkeen, ja ytimeen
  käännetystä moduulista `__exit`-koodi jätetään kokonaan pois.
- **Alkufunktion paluuarvo** on 0 tai negatiivinen virhekoodi. Jos
  alkufunktio epäonnistuu, latauskin epäonnistuu, eikä moduulia jää
  ytimeen. Alkufunktion on silloin siivottava itse kaikki, minkä se ehti
  varata.
- **`MODULE_LICENSE`** on pakollinen. Se ratkaisee, mitä ytimen symboleja
  moduuli saa käyttää (ks. *Lisenssi ja tahrat*).
- **`pr_fmt`** tiedoston alussa lisää jokaisen `pr_info`-, `pr_warn`- ja
  `pr_err`-rivin alkuun moduulin nimen. Ilman sitä lokiriviltä on vaikea
  tietää, mistä se tuli.

Moduuli käännetään ytimen käännöshakemistoa vasten. Hakemiston
`Kbuild`-tiedosto luettelee moduulit:

```{.make tiedosto="esimerkit/01-moduulit/Kbuild"}
```

`esimerkit/Makefile` kopioi lähteet käännöshakemistoon ja ajaa ytimen
käännösjärjestelmän valitsimella `M=`. Muuttuja `YMAKE` on ytimen
`make` ristiinkääntäjän ja käännöshakemiston valitsimineen (luku 1):

```{.make tiedosto="esimerkit/Makefile" osa="moduulit"}
```

## Parametrit

Moduulin parametrit ovat muuttujia, joille annetaan arvo latauksessa:
`modprobe tilasto raja=10` tai ytimen komentorivillä `tilasto.raja=10`,
jos moduuli on käännetty ytimeen.

```{.c tiedosto="esimerkit/01-moduulit/tilasto.c" osa="parametrit"}
```

Kolmas argumentti on tiedoston oikeudet hakemistossa
`/sys/module/tilasto/parameters/`. Arvo `0444` tekee parametrista
luettavan ja `0644` myös pääkäyttäjän muutettavan ajon aikana, `0`
piilottaa sen. Ajon aikana muuttuva parametri luetaan `READ_ONCE`-
makrolla, koska kirjoitus voi tapahtua milloin tahansa toisella CPU:lla.
Taulukkoparametri hyväksyy pilkuin erotellut arvot ja kertoo niiden
määrän:

```{.c tiedosto="esimerkit/01-moduulit/mittaus.c" osa="taulukko"}
```

Parametrin arvo on tarkistettava alkufunktiossa, koska ydin tarkistaa
vain tyypin. Moduulin `tilasto` raja ei saa olla nolla, joten
alkufunktio palauttaa silloin `-EINVAL`.

## Symbolien vienti

Moduuli näkee vain ne ytimen funktiot ja muuttujat, jotka on *viety*
(exported). Muu ytimen sisäinen koodi on piilossa, vaikka se olisi
linkitetty samaan osoiteavaruuteen. Moduuli voi viedä omia symbolejaan
muille moduuleille:

```{.c tiedosto="esimerkit/01-moduulit/tilasto.c" osa="vienti"}
```

`EXPORT_SYMBOL` vie symbolin kaikille moduuleille, `EXPORT_SYMBOL_GPL`
vain GPL-yhteensopivan lisenssin moduuleille. Uudet ytimen rajapinnat
viedään lähes aina GPL-muodossa. Viedyn funktion esittely on omassa
otsakkeessaan (`tilasto.h`), jonka käyttäjä ottaa mukaan.

Kun moduulit käännetään, `modpost` kirjoittaa vientien luettelon
tiedostoon `Module.symvers` ja tarkistaa, että jokaisen moduulin kaikki
viittaukset löytyvät joko ytimestä tai jostain toisesta moduulista.
Riippuvuus tallentuu moduulin tietoihin, jotka `modinfo` näyttää:

```{.make tiedosto="esimerkit/Makefile" osa="modinfo"}
```

```{.tuloste tiedosto="esimerkit/testit/01-modinfo.odotettu"}
```

*vermagic* on merkkijono, jonka on täsmättävä ytimen omaan: ydin
kieltäytyy lataamasta muuta varten käännettyä moduulia. Riippuvuuksien
perusteella `depmod` kirjoittaa laitteen tiedostoon
`/lib/modules/<versio>/modules.dep`, josta `modprobe` lukee, mitkä
moduulit on ladattava ensin. Tämän tutoriaalin testijärjestelmässä ei
ole `modprobe`a, joten järjestys on vaiheissa itse oikea, ja ensimmäinen
yritys on tahallaan väärä:

```{.text tiedosto="esimerkit/01-moduulit/parametrit.vaiheet" osa="riippuvuus"}
```

```{.tuloste tiedosto="esimerkit/testit/01-parametrit.odotettu" osa="riippuvuus"}
```

Ensimmäinen lataus epäonnistuu, koska `tilasto_kirjaa` puuttuu
ytimestä. Toinen epäonnistuu alkufunktion tarkistukseen, ja virhekoodi
`-EINVAL` näkyy lataajalle tekstinä *Invalid argument*. Kolmas ja
neljäs onnistuvat.

## Viittauslaskenta ja poisto

Ladattu moduuli näkyy hakemistossa `/sys/module/`. Sieltä näkee
parametrien nykyiset arvot, moduulit, jotka käyttävät tätä moduulia
(`holders`), ja viittausten määrän (`refcnt`):

```{.tuloste tiedosto="esimerkit/testit/01-parametrit.odotettu" osa="sysfs"}
```

Ydin ei poista moduulia, jota jokin käyttää. Viittauksia ovat toiset
moduulit, jotka käyttävät sen symboleja, ja avoimet tiedostot, joiden
`file_operations`-taulun `owner` on moduuli (luku 3):

```{.tuloste tiedosto="esimerkit/testit/01-parametrit.odotettu" osa="poisto"}
```

`rmmod` käyttää järjestelmäkutsua `delete_module`, joka ei odota
viittausten vapautumista vaan palauttaa virheen `EAGAIN`. Loppufunktion
on siivottava kaikki, minkä moduuli on rekisteröinyt: jos laite,
ajastin tai keskeytyskäsittelijä jää ytimeen poiston jälkeen, ydin
kutsuu myöhemmin funktiota, jonka koodia ei enää ole. Siksi
rekisteröinnit kannattaa tehdä mahdollisuuksien mukaan
resurssienhallinnan kautta (`devm_`, luku 4), jolloin ydin purkaa ne
automaattisesti.

## Lisenssi ja tahrat

Tiedosto `/proc/sys/kernel/tainted` on yllä 4096 eli bitti 12:
ytimeen on ladattu lähdepuun ulkopuolinen moduuli (*out-of-tree*,
merkintä `O`). Tahrat (taints) kertovat vikailmoituksen lukijalle, että
ytimessä on ollut koodia, jota ytimen kehittäjät eivät ole nähneet tai
joka on rikkonut jotain. Yleisimmät:

| Bitti | Kirjain | Syy |
|------|------|------------------------------------------|
| 0 | `P` | suljetun lisenssin moduuli ladattu |
| 7 | `D` | ydin on kaatunut (oops) |
| 9 | `W` | ydin on antanut varoituksen (`WARN`) |
| 12 | `O` | lähdepuun ulkopuolinen moduuli |
| 13 | `E` | allekirjoittamaton moduuli |

Suljetun lisenssin moduuli tahraa ytimen merkinnällä `P`, eikä se voi
käyttää GPL-symboleja. Esimerkki `suljettu.c` yrittää kutsua
`tilasto_kirjaa`-funktiota, ja `modpost` hylkää sen jo käännöksessä:

```{.c tiedosto="esimerkit/01-moduulit/suljettu/suljettu.c"}
```

```{.make tiedosto="esimerkit/Makefile" osa="suljettu"}
```

```{.tuloste tiedosto="esimerkit/testit/01-suljettu.odotettu"}
```

`KBUILD_EXTRA_SYMBOLS` kertoo käännökselle toisen moduulihakemiston
viennit. Ilman sitä `modpost` ei tietäisi, mistä `tilasto_kirjaa`
tulee, ja varoittaisi vain tuntemattomasta symbolista.

Lisenssimerkintä ei ole pelkkä muodollisuus. Ytimen lisenssi on GPLv2,
ja kehittäjät pitävät GPL-symbolia rajana: sitä käyttävä koodi on ytimen
johdannainen. Suljettu ajuri on myös käytännössä ongelma: sitä ei voi
korjata ytimen muutosten mukana, eikä kukaan muu voi selvittää sen
aiheuttamia kaatumisia.

## Kun moduuli kaatuu

Moduulin virhe on ytimen virhe. NULL-osoittimen käyttö alkufunktiossa
tuottaa ytimen lokiin kaatumisilmoituksen (*oops*), `insmod` päättyy
signaaliin, ja moduuli voi jäädä puoliksi ladatuksi niin, ettei sitä saa
poistettua. Testijärjestelmä käynnistetään silloin uudelleen, mikä on
QEMU:ssa sekuntien asia ja hyvä syy kehittää ajuria emulaattorissa.
Ilmoituksen lukeminen ja osoitteen muuntaminen lähdekoodin riviksi
käsitellään luvussa 10; siihen kannattaa palata heti, kun oma moduuli
kaatuu ensimmäisen kerran.

## Moduuli vai ytimeen

Sama koodi voidaan kääntää moduuliksi (`obj-m`) tai ytimeen (`obj-y`).
Ytimeen käännetty ajuri on käytössä heti käynnistyksessä, eikä sitä
tarvitse ladata. Moduuli ladataan, kun laite löytyy: ydin lähettää
käyttäjätilaan tapahtuman (*uevent*), jossa on laitteen *modalias*, ja
`udev` lataa moduulin, jonka `MODULE_DEVICE_TABLE`-taulussa sama
tunniste on (luku 4). Sulautetussa laitteessa, jonka laitteisto ei
muutu, ajurit käännetään usein ytimeen. Moduulit ovat hyödyllisiä
kehityksessä, koska ajurin voi kääntää ja ladata uudelleen ilman ytimen
käännöstä ja käynnistystä.

## Käytännössä

- **Siivoa alkufunktion virhepolulla kaikki, minkä ehdit tehdä.**
  Ytimen tapa on `goto`-ketju, jossa vapautus on käänteisessä
  järjestyksessä (luku 3). Vielä parempi on `devm_`-resurssienhallinta.
- **Tarkista parametrit alkufunktiossa ja kerro syy lokiin.** Lataajalle
  näkyy vain virhekoodi. Ajon aikana muutettavan parametrin käyttäjä
  lukee arvon `READ_ONCE`-makrolla.
- **Vie vain se, mitä toinen moduuli todella tarvitsee, ja käytä
  `EXPORT_SYMBOL_GPL`-muotoa.** Viety symboli on rajapinta, jota on
  ylläpidettävä.
- **Käytä `pr_fmt`-makroa ja laitteeseen liittyvissä viesteissä
  `dev_*`-funktioita.** Lokirivin alusta näkee silloin, mistä se tuli.
- **Pyri saamaan ajuri ytimen lähdepuuhun.** Lähdepuun ajuri pysyy
  ajan tasalla ytimen muutosten mukana; ulkopuolinen ajuri hajoaa
  jokaisessa suuressa päivityksessä.

## Itsearviointi

- Osaat kääntää kahden moduulin ulkopuolisen moduulihakemiston
  Kbuildilla ja selittää, mitä `modpost` ja `Module.symvers` tekevät.
- Osaat määritellä moduulille parametreja, tarkistaa niiden arvot ja
  selittää niiden näkymisen `/sys/module`-hakemistossa.
- Osaat viedä symbolin toiselle moduulille ja selittää riippuvuuden
  vaikutuksen lataus- ja poistojärjestykseen.
- Osaat tulkita `tainted`-arvon ja selittää lisenssin vaikutuksen
  GPL-symbolien käyttöön.
