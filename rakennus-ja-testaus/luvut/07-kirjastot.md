# Kirjastot ja riippuvuudet

Kirjasto on tapa jakaa koodi osiin, joita voi käyttää useassa
ohjelmassa ja kehittää erikseen. C:ssä kirjastoja on kahta lajia.
*Staattinen kirjasto* (`.a`) liitetään ohjelmaan linkitysvaiheessa, ja
ohjelma sisältää sen jälkeen tarvitsemansa koodin. *Jaettu kirjasto*
(`.so`) ladataan vasta ohjelman käynnistyessä, ja sama kirjasto on
muistissa vain kerran kaikille sitä käyttäville ohjelmille.

| | Staattinen (`.a`) | Jaettu (`.so`) |
|-|-------------------|----------------|
| Liitetään | linkitettäessä | käynnistettäessä |
| Ohjelma | itsenäinen, suurempi | pienempi, tarvitsee kirjaston |
| Päivitys | ohjelma rakennetaan uudelleen | kirjasto vaihdetaan |
| Riippuvuudet | käyttäjä linkittää ne | kirjasto kertoo ne itse |
| Rajapinnan muutos | näkyy käännöksessä | voi rikkoa ohjelmat ajossa |

## Staattinen kirjasto

Staattinen kirjasto on pelkkä arkisto objektitiedostoja. Linkkeri ottaa
siitä vain ne jäsenet, joita tarvitaan puuttuvien symbolien
täyttämiseen:

```{.bash tiedosto="esimerkit/06-kirjastot/aja.sh" osa="staattinen"}
```

Valitsin `-L.` lisää hakemiston kirjastojen hakupolkuun ja `-ltilasto`
etsii tiedoston `libtilasto.so` tai `libtilasto.a`. Ohjelma tarvitsee
ajon aikana vain C- ja matematiikkakirjaston (`NEEDED`), koska
tilastofunktiot on kopioitu ohjelmaan. Huomaa, että `-lm` on annettava
itse: arkisto ei tiedä riippuvuuksistaan mitään.

## Jaettu kirjasto

Jaetun kirjaston koodi on käännettävä sijaintiriippumattomaksi
(`-fPIC`), koska kirjasto ladataan eri ohjelmissa eri osoitteisiin.
Kirjastolle annetaan *soname*, joka kertoo sen rajapinnan
pääversion, ja *versioskripti*, joka rajaa näkyvät symbolit:

```{.text tiedosto="esimerkit/06-kirjastot/tilasto.map"}
```

```{.bash tiedosto="esimerkit/06-kirjastot/aja.sh" osa="jaettu"}
```

Nimeämiskäytäntö on kolmiportainen. Tiedosto `libtilasto.so.1.2.0` on
varsinainen kirjasto. Linkki `libtilasto.so.1` on sen soname: ohjelma
tallentaa sen ja etsii ajon aikana juuri sitä. Linkki `libtilasto.so`
on vain linkitystä varten, ja se kuuluu kehityspakettiin (Debianissa
`libtilasto-dev`). Kun kirjastosta julkaistaan versio 1.3.0 samalla
rajapinnalla, linkki `.so.1` siirretään osoittamaan siihen, ja
vanhat ohjelmat käyttävät uutta versiota rakentamatta niitä uudelleen.
Kun rajapinta muuttuu yhteensopimattomasti, soname vaihtuu muotoon
`.so.2`, ja vanhat ohjelmat jatkavat vanhan kirjaston kanssa.

Versioskripti tekee kaksi asiaa. Se piilottaa kaikki symbolit, joita ei
ole lueteltu (`local: *`), joten sisäinen `vertaa`-funktio ei ole osa
rajapintaa eikä kukaan voi alkaa käyttää sitä. Lisäksi se merkitsee
viedyt symbolit versiolla `TILASTO_1`, minkä avulla kirjasto voi
myöhemmin tarjota saman funktion kahtena versiona. Tavallisempi tapa
piilottaa symbolit on kääntää valitsimella `-fvisibility=hidden` ja
merkitä julkiset funktiot attribuutilla
`__attribute__((visibility("default")))`. Rajapinnan ja ABI:n
yhteensopivuutta käsitellään tarkemmin taidossa *Objektitiedostot,
linkitys ja ABI*.

## Ajonaikainen haku

Jaettu kirjasto on löydyttävä myös ajon aikana, ja ajonaikainen
linkkeri `ld.so` etsii sitä eri paikoista kuin käännösaikainen:

```{.bash tiedosto="esimerkit/06-kirjastot/aja.sh" osa="haku"}
```

Ensimmäinen ohjelma linkittyy, koska `-L.` kertoo linkkerille, mistä
kirjasto löytyy, mutta käynnistys epäonnistuu: ajonaikainen linkkeri
etsii vain järjestelmän hakemistoista (`/lib`, `/usr/lib` ja
`/etc/ld.so.conf`), ympäristömuuttujan `LD_LIBRARY_PATH` hakemistoista
ja ohjelmaan tallennetusta hakupolusta (`RUNPATH`). Hakupolun erikoisarvo
`$ORIGIN` tarkoittaa ohjelman omaa hakemistoa, joten ohjelma ja kirjasto
voidaan siirtää yhdessä minne tahansa. Tämä on hyvä ratkaisu ohjelmalle,
joka toimitetaan omine kirjastoineen. Järjestelmään asennettavat
kirjastot kuuluvat järjestelmän hakemistoihin, eikä niille tarvita
hakupolkua. `LD_LIBRARY_PATH` sopii kokeiluun mutta ei pysyväksi
ratkaisuksi, koska se koskee kaikkia ympäristössä ajettavia ohjelmia.

## pkg-config

Kirjaston käyttäjän on tiedettävä otsakkeiden ja kirjaston hakemistot
ja kirjaston omat riippuvuudet. `pkg-config` lukee nämä tiedot
kirjaston asentamasta `.pc`-tiedostosta:

```{.text tiedosto="esimerkit/06-kirjastot/tilasto.pc.in"}
```

`Libs.private` luettelee riippuvuudet, joita tarvitaan vain staattisessa
linkityksessä: jaettu kirjasto kertoo ne itse. Esimerkki asentaa
kirjaston ja otsakkeen hakemistoon ja kysyy liput `pkg-config`-ohjelmalta:

```{.bash tiedosto="esimerkit/06-kirjastot/aja.sh" osa="pkgconfig"}
```

```{.tuloste tiedosto="esimerkit/06-kirjastot.odotettu"}
```

`PKG_CONFIG_PATH` lisää hakemiston, josta `.pc`-tiedostoja etsitään.
Ilman sitä etsitään vain järjestelmän hakemistoista
(`/usr/lib/x86_64-linux-gnu/pkgconfig` ja muut). Make-projektissa
liput haetaan tavallisesti näin:

```text
CFLAGS += $(shell pkg-config --cflags tilasto)
LDLIBS += $(shell pkg-config --libs tilasto)
```

CMake-projekti asentaa `.pc`-tiedoston lisäksi oman
`tilastoConfig.cmake`-määrittelynsä komennoilla `install(TARGETS ...
EXPORT ...)` ja `install(EXPORT ...)`, jolloin muut CMake-projektit
löytävät sen komennolla `find_package(tilasto)`.

## Mistä riippuvuudet tulevat

Kun projekti tarvitsee ulkopuolisen kirjaston, sen voi hankkia neljällä
tavalla:

| Tapa | Esimerkki | Hyvää | Huonoa |
|------|-----------|-------|--------|
| järjestelmän paketit | `apt install libz-dev` | yksinkertainen, tietoturvapäivitykset jakelulta | versio riippuu jakelusta |
| vendorointi | kirjaston lähde hakemistoon `vendor/` | ei ulkoisia riippuvuuksia, täysi hallinta | päivitykset käsin, koodi paisuu |
| lataus rakennettaessa | CMaken `FetchContent` | tarkka versio, ei erillistä työkalua | lataa verkosta joka konfiguroinnissa |
| paketinhallinta | Conan, vcpkg | tarkat versiot, binäärivälimuisti, transitiiviset riippuvuudet | uusi työkalu ja sen opettelu |

Kirjastoissa ja jakelujen paketeissa käytetään järjestelmän paketteja,
koska jakelu haluaa yhden kopion kustakin kirjastosta. Sovelluksissa,
jotka toimitetaan sellaisenaan (sulautettu laite, työpöytäsovellus,
palvelinkontti), tarkka versio on tärkeämpi, ja paketinhallinta tai
vendorointi on parempi.

*Vendorointi* tarkoittaa riippuvuuden lähdekoodin kopioimista omaan
versionhallintaan. Se on järkevää pienelle, harvoin muuttuvalle
kirjastolle, kuten yhden tiedoston JSON-jäsentimelle tai testikehykselle.
Kopion alkuperä ja versio on kirjattava (esimerkiksi tiedostoon
`vendor/README`), eikä kopioon tehdä paikallisia muutoksia ilman,
että ne dokumentoidaan. Muuten päivittäminen muuttuu mahdottomaksi.
Gitin alimoduuli (*submodule*) on vendoroinnin muunnelma, jossa
kopion sijaan tallennetaan viittaus toisen tietovaraston committiin.

*Conan* ja *vcpkg* ovat C- ja C++-kirjastojen paketinhallintoja.
Molemmat lukevat projektin riippuvuusluettelon (`conanfile.txt` tai
`vcpkg.json`), rakentavat tai lataavat kirjastot ja kertovat ne CMakelle
niin, että tavallinen `find_package` löytää ne. vcpkg:n luettelo
näyttää tältä:

```text
{
  "name": "tilasto",
  "version": "1.2.0",
  "dependencies": [ "zlib", "cmocka" ],
  "builtin-baseline": "<vcpkg-tietovaraston commit>"
}
```

`builtin-baseline` kiinnittää kaikkien pakettien versiot tiettyyn
vcpkg:n committiin, ja Conan tekee saman lukitustiedostolla
(`conan.lock`). Kiinnitys on tärkeä: ilman sitä sama projekti saa eri
päivinä eri kirjastoversiot. Riippuvuuksien eheyden tarkistaminen ja
toimitusketjun hyökkäykset käsitellään taidossa *Tietoturva
kehitystyössä*.

## Käytännössä

- **Staattinen oletukseksi sovelluksen omille kirjastoille.** Projektin
  sisäiset kirjastot kannattaa linkittää staattisesti: ohjelma on
  itsenäinen, eikä ajonaikaisia hakupolkuja tarvita. Jaettu kirjasto on
  perusteltu, kun sama kirjasto jaetaan monen ohjelman kesken tai kun se
  on päivitettävä erikseen.
- **Jaetulle kirjastolle soname ja rajattu rajapinta.** Soname tekee
  päivitykset hallituiksi, versioskripti tai `-fvisibility=hidden`
  estää sisäisten funktioiden päätymisen rajapintaan.
- **`$ORIGIN`, ei `LD_LIBRARY_PATH`.** Ohjelman mukana toimitettavat
  kirjastot löytyvät suhteellisesta hakupolusta. Ympäristömuuttuja
  sopii vain kokeiluun.
- **Kirjasto kertoo käyttönsä.** Asenna `.pc`-tiedosto ja
  CMake-määrittely, niin käyttäjät eivät joudu arvaamaan lippuja.
- **Kiinnitä riippuvuuksien versiot.** Lukitustiedosto tai
  vendoroidun kopion versiomerkintä kertoo tarkasti, mitä rakennetaan.

## Itsearviointi

- Osaat rakentaa staattisen ja jaetun kirjaston ja kertoa niiden erot.
- Osaat antaa jaetulle kirjastolle sonamen, rajata sen viedyt symbolit
  ja selittää kolmiportaisen nimeämiskäytännön.
- Osaat selvittää, miksi ohjelma ei löydä jaettua kirjastoa, ja
  korjata sen hakupolulla `$ORIGIN`.
- Osaat kirjoittaa `.pc`-tiedoston ja käyttää `pkg-config`-ohjelmaa.
- Osaat valita riippuvuuksien hankintatavan (järjestelmän paketit,
  vendorointi, `FetchContent`, Conan tai vcpkg) ja perustella valinnan.
