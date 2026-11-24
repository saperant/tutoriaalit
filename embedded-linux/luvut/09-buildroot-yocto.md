# Buildroot ja Yocto

Edellisissä luvuissa järjestelmä koottiin käsin: ytimen fragmentti,
staattiset ohjelmat, `gen_init_cpio`-luettelot, `mke2fs` ja `mkimage`.
Tuotantolaitteessa ohjelmia on kymmeniä tai satoja, ja niillä on
riippuvuuksia, lisenssejä ja tietoturvapäivityksiä. Rakennustyökalu
(*build system*) tekee kaiken saman yhdellä komennolla: hakee lähteet
ja tarkistaa niiden tiivisteet, rakentaa työkaluketjun, ytimen,
käynnistimen ja paketit, kokoaa juuritiedostojärjestelmän ja tuottaa
valmiit levykuvat. Kaksi yleisintä ovat Buildroot ja Yocto Project.

Tämän tutoriaalin ympäristöstä ei ole yhteyttä Buildrootin ja Yocton
lähteisiin, joten luvun asetustiedostoja ei ole ajettu. Ne on
kirjoitettu Buildroot 2025.02 LTS:n ja Yocto 5.0 Scarthgapin muotoon,
ja niiden viittaukset tarkistetaan (luvun lopussa). Käytä niitä mallina
ja tarkista yksityiskohdat käyttämäsi version käsikirjasta.

## Buildroot

Buildroot on joukko Makefileja ja Kconfig-valikko. Konfiguraatio
valitaan samalla tavalla kuin ytimen: valmiista defconfigista ja
valikosta, ja tulos tallennetaan `make savedefconfig` -komennolla.
Seuraava defconfig on tehty Buildrootin oman QEMU-konfiguraation
`qemu_aarch64_virt_defconfig` pohjalta:

```{.ini tiedosto="esimerkit/09-buildroot/tutoriaali_defconfig" osa="arkkitehtuuri"}
```

Arkkitehtuuri ja prosessori valitsevat kääntäjän liput, ja
`BR2_TOOLCHAIN_BUILDROOT_GLIBC` rakentaa työkaluketjun glibc:llä.
Ulkoinen, valmis työkaluketju olisi `BR2_TOOLCHAIN_EXTERNAL`.

```{.ini tiedosto="esimerkit/09-buildroot/tutoriaali_defconfig" osa="jarjestelma"}
```

Järjestelmäosa valitsee initiksi BusyBoxin (vaihtoehdot ovat SysV init,
OpenRC ja systemd), konsolin `getty`-portin ja koneen nimen.
`BR2_PACKAGE_MINIT` ottaa mukaan tämän tutoriaalin oman paketin.

```{.ini tiedosto="esimerkit/09-buildroot/tutoriaali_defconfig" osa="ydin"}
```

Ydin haetaan valitusta versiosta, konfiguroidaan arkkitehtuurin
oletuskonfiguraatiosta ja täydennetään fragmentilla, aivan kuten luvussa
3. Buildroot tarkistaa jokaisen ladatun lähteen tiivisteen paketin
`.hash`-tiedostosta. Omalle ytimen versiolle tiiviste lisätään
ulkopuun hakemistoon, joka annetaan asetuksella `BR2_GLOBAL_PATCH_DIR`
(tiedosto `linux/linux.hash`), ja asetus
`BR2_DOWNLOAD_FORCE_CHECK_HASHES` tekee tarkistuksesta pakollisen.

```{.ini tiedosto="esimerkit/09-buildroot/tutoriaali_defconfig" osa="kuvat"}
```

Lopuksi valitaan tuotettavat kuvat: ext4-juuri, U-Boot ja QEMU, jolla
kuvan voi käynnistää. Työnkulku on:

1. `make BR2_EXTERNAL=../external tutoriaali_defconfig`
2. `make menuconfig` (valinnainen muutos) ja `make savedefconfig`
3. `make`, ensimmäisellä kerralla tunti tai pari
4. tulokset hakemistossa `output/images/`: `Image`, `rootfs.ext4`,
   `u-boot.bin`.

Buildroot ei seuraa konfiguraation muutosten vaikutuksia: jos
esimerkiksi C-kirjasto vaihdetaan, on tehtävä `make clean` ja
rakennettava kaikki uudelleen. Yksittäinen paketti rakennetaan
uudelleen kohteella `make <paketti>-rebuild`.

## Oma paketti: BR2_EXTERNAL

Omia paketteja ei lisätä Buildrootin puuhun vaan erilliseen
*ulkopuuhun* (BR2_EXTERNAL), jolloin Buildrootin version voi päivittää
koskematta omiin tiedostoihin. Ulkopuun nimi tulee tiedostosta
`external.desc`:

```{.text tiedosto="esimerkit/09-buildroot/external/external.desc"}
```

Nimestä muodostuu muuttuja `BR2_EXTERNAL_TUT_PATH`, joka osoittaa
ulkopuun hakemistoon. `Config.in` lisää paketin valikkoon ja
`external.mk` ottaa mukaan pakettien Makefilet:

```{.text tiedosto="esimerkit/09-buildroot/external/Config.in"}
```

```{.make tiedosto="esimerkit/09-buildroot/external/external.mk"}
```

Paketin valikkokohta on Kconfig-symboli. (Buildrootin tyyliohje
sisentää sarkaimin; Kconfig hyväksyy myös välilyönnit.)

```{.text tiedosto="esimerkit/09-buildroot/external/package/minit/Config.in"}
```

Paketin `.mk`-tiedosto kertoo, mistä lähteet tulevat ja miten ne
käännetään ja asennetaan. Tämä paketti on luvun 7 init-järjestelmä:

```{.make tiedosto="esimerkit/09-buildroot/external/package/minit/minit.mk"}
```

`generic-package` on Buildrootin infrastruktuuri paketeille, joilla on
oma käännöskomento. Autotools-, CMake-, Meson- ja Python-paketeille on
omat infrastruktuurinsa (`autotools-package`, `cmake-package` jne.),
joissa riittää lähde ja lisenssi. `$(TARGET_CC)` on Buildrootin
ristikääntäjä ja `$(TARGET_DIR)` kokoamisvaiheen juurihakemisto.
`MINIT_LICENSE` päätyy lisenssiluetteloon, jonka `make legal-info`
kokoaa kaikkien pakettien lähteineen ja lisenssiteksteineen.

Ulkopuun ytimen fragmentti:

```{.ini tiedosto="esimerkit/09-buildroot/external/ydin.config"}
```

## Yocto Project

Yocto Project on laajempi ja raskaampi. Sen rakennustyökalu BitBake
suorittaa *reseptejä* (`.bb`), jotka on järjestetty *kerroksiksi*
(layers). Perustana on OpenEmbedded-Core, valmistajat toimittavat
piiriensä tuen BSP-kerroksina (esim. `meta-raspberrypi`,
`meta-freescale`), ja oma tuote on yksi tai useampi oma kerros.
Kerroksen kuvaus:

```{.text tiedosto="esimerkit/09-buildroot/meta-tutoriaali/conf/layer.conf"}
```

Resepti kertoo samat asiat kuin Buildrootin paketti, mutta BitBaken
kielellä:

```{.text tiedosto="esimerkit/09-buildroot/meta-tutoriaali/recipes-core/minit/minit_1.0.bb"}
```

`SRC_URI`:n `file://`-tiedostot haetaan reseptin viereisestä
hakemistosta `minit/` tai `files/`. `LIC_FILES_CHKSUM` on Yocton
lisenssitarkistus: BitBake laskee tiedoston tai sen rivien
MD5-tiivisteen ja pysäyttää rakennuksen, jos se muuttuu. Näin
lisenssin muutos ei koskaan mene läpi huomaamatta.

Kokonaisuuden valitsevat muuttujat `MACHINE` (laite, esim.
`qemuarm64`), `DISTRO` (järjestelmän käytännöt, esim. `poky`) ja
kuvaresepti (esim. `core-image-minimal`), joka luettelee kuvaan
tulevat paketit. Oma resepti lisätään kuvaan rivillä
`IMAGE_INSTALL:append = " minit"`.

Yocton vahvuudet ovat jaettu välimuisti (*sstate*), joka tekee
uudelleenrakennuksista nopeita, tarkka riippuvuuksien seuranta (muutos
rakentaa uudelleen vain sen, mihin se vaikuttaa), *SDK*
(`bitbake -c populate_sdk`), joka antaa sovelluskehittäjille saman
työkaluketjun ja sysrootin, ja `devtool`, jolla reseptejä muokataan.
Hinta on oppimiskäyrä ja levytila: täysi rakennus vie kymmeniä tai
satoja gigatavuja.

## Vertailu

| Ominaisuus | Buildroot | Yocto |
|------------|-----------|-------|
| konfigurointi | Kconfig, yksi defconfig | kerrokset, reseptit, `local.conf` |
| tuotos | levykuva | levykuva, paketit, SDK |
| uudelleenrakennus | koko järjestelmä konfiguraation muuttuessa | vain muuttunut, sstate-välimuisti |
| paketinhallinta laitteessa | ei | valinnainen (rpm, ipk, deb) |
| oppimiskäyrä | loiva | jyrkkä |
| sopii | pienet ja keskisuuret laitteet, yksi tuote | tuoteperheet, pitkä elinkaari, toimittajien BSP:t |

Kumpikaan ei ole vain rakennustyökalu vaan myös toimitusketjun
dokumentti. Molemmat tuottavat lisenssiluettelon, voivat tuottaa
SPDX-muotoisen ohjelmistoluettelon (SBOM, Yoctossa oletuksena) ja
tarkistaa tunnetut haavoittuvuudet (CVE) pakettiversioista. EU:n
kyberkestävyyssäädös (CRA) edellyttää verkkoon kytkettäviltä tuotteilta
ohjelmistoluetteloa ja haavoittuvuuksien käsittelyä, joten nämä
ominaisuudet ovat nyt vaatimus eivätkä lisä.

## Viittausten tarkistus

Koska esimerkkejä ei ajeta, tarkistetaan edes se, minkä voi tarkistaa
ilman rakennustyökalua: reseptin lisenssitiiviste lasketaan
lähdetiedostosta, lähdetiedostot ovat olemassa, ja ulkopuun nimi on
kaikkialla sama.

```{.tuloste tiedosto="esimerkit/testit/09-viitteet.odotettu"}
```

## Käytännössä

- **Valitse Buildroot, jos tuote on yksi ja tiimi pieni.** Koko
  järjestelmän näkee yhdestä defconfigista, ja rakennuksen ymmärtää
  päivässä.
- **Valitse Yocto, jos piirin toimittaja tukee sitä tai tuotteita on
  monta.** Toimittajan BSP-kerros, sstate ja SDK maksavat
  oppimiskäyrän takaisin.
- **Pidä omat lisäykset omassa puussaan tai kerroksessaan.** Älä muokkaa
  Buildrootin tai Pokyn tiedostoja: silloin version päivitys on
  yhdistämistä eikä vaihtoa.
- **Lukitse versiot ja tallenna lähteet.** Buildrootin ja Yocton
  latausvälimuisti (`dl/`, `DL_DIR`) kannattaa arkistoida tuotteen
  julkaisun yhteydessä: kymmenen vuoden päästä osa lähteistä on
  kadonnut verkosta.
- **Tuota lisenssiluettelo ja SBOM jokaisesta julkaisusta.** Ne
  tarvitaan GPL-velvoitteisiin (lähdekoodin tarjoaminen),
  asiakkaille ja säädösten noudattamiseen.

## Itsearviointi

- Osaat kertoa, mitä rakennustyökalu tekee käsin kootun järjestelmän
  sijaan.
- Osaat lukea Buildrootin defconfigin ja kirjoittaa oman paketin
  BR2_EXTERNAL-ulkopuuhun.
- Osaat selittää Yocton kerrokset, reseptit, `MACHINE`- ja
  `DISTRO`-muuttujat ja `LIC_FILES_CHKSUM`in tarkoituksen.
- Osaat vertailla Buildrootia ja Yoctoa ja perustella valinnan.
- Osaat kertoa, miksi lisenssiluettelo, SBOM ja lähteiden arkistointi
  kuuluvat julkaisuun.
