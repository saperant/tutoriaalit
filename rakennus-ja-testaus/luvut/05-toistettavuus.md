# Toistettava rakennus

Rakennus on *toistettava* (*reproducible build*), jos samasta lähteestä
samoilla työkaluilla syntyy bitilleen sama tulos riippumatta siitä,
kuka rakentaa, missä hakemistossa ja milloin. Ominaisuus kuulostaa
akateemiselta, mutta sillä on käytännön seurauksia:

- **Varmennus.** Kun kaksi toisistaan riippumatonta rakennusta tuottaa
  saman tiivisteen, binääri vastaa lähdettä eikä rakennuskoneelle ole
  ujutettu mitään. Debian, Arch Linux, NixOS ja monet muut jakelut
  tarkistavat pakettinsa näin.
- **Välimuistit.** Käännösvälimuisti (ccache, sccache) ja
  rakennusjärjestelmien etävälimuistit (Bazel) toimivat vain, jos sama
  syöte tuottaa saman tuloksen.
- **Vianetsintä.** Kun julkaistun ohjelman vika on selvitettävä, sama
  binääri on voitava rakentaa uudelleen. Jos rakennus ei ole
  toistettava, ei voi tietää, onko paikallinen versio sama kuin
  asiakkaalla.

Tavallisesti epätoistettavuuden syyt ovat pieniä ja helposti
korjattavia: käännöshakemiston polku debug-tiedossa, kellonaika
makroissa ja arkistoissa, tiedostojärjestelmän palauttama
tiedostojärjestys ja ympäristön muuttujat.

## Polut

Valitsin `-g` tallentaa debug-tietoon lähdetiedostojen polut, jotta
debuggeri löytää ne. Jos sama koodi käännetään kehittäjän kotihakemistossa
ja CI:n työhakemistossa, objektitiedostot eroavat. Valitsin
`-ffile-prefix-map=VANHA=UUSI` korvaa polun alun sekä debug-tiedossa
että `__FILE__`-makrossa:

```{.bash tiedosto="esimerkit/05-toistettava/aja.sh" osa="polut"}
```

Funktio kääntää saman tiedoston kahdessa eri hakemistossa ja vertaa
objektitiedostojen SHA-256-tiivisteitä. Ilman polkujen kuvausta
tiedostot eroavat, kuvauksen kanssa ne ovat samat. Debuggeri löytää
lähteet tällöin suhteessa omaan työhakemistoonsa, tai sille kerrotaan
oikea paikka komennolla `set substitute-path`.

## Aika

Makrot `__DATE__` ja `__TIME__` laajenevat käännöshetkeen. Ne ovat
suosittu tapa merkitä versio, ja ne tekevät jokaisesta rakennuksesta
erilaisen:

```{.c tiedosto="esimerkit/05-toistettava/versio.c"}
```

Toistettavien rakennusten yhteisö on sopinut ympäristömuuttujasta
`SOURCE_DATE_EPOCH`: se on Unix-aikaleima, jota työkalujen kuuluu
käyttää nykyhetken sijaan. GCC ja Clang tukevat sitä suoraan. Arvoksi
asetetaan tavallisesti viimeisen commitin aika
(`git log -1 --format=%ct`), jolloin aika kertoo silti jotain
hyödyllistä:

```{.bash tiedosto="esimerkit/05-toistettava/aja.sh" osa="aika"}
```

Parempi ratkaisu on olla käyttämättä makroja ja kirjoittaa versioksi
Git-tunniste, jonka rakennusjärjestelmä välittää lipulla
`-DVERSIO="..."`. Silloin versio kertoo, mistä lähteestä ohjelma
rakennettiin, eikä vain milloin.

## Arkistot

Staattinen kirjasto on `ar`-arkisto, joka tallentaa jäseniensä
muutosajat, omistajat ja oikeudet. Valitsin `D` (*deterministinen
tila*) kirjoittaa niiden tilalle nollat. Monissa jakeluissa se on
oletus, mutta sitä ei kannata olettaa:

```{.bash tiedosto="esimerkit/05-toistettava/aja.sh" osa="arkisto"}
```

```{.tuloste tiedosto="esimerkit/05-toistettava.odotettu"}
```

Aikaleima on Unix-ajan alku ja omistaja `0/0`, joten arkisto ei
paljasta, kuka sen rakensi ja milloin. Sama ongelma koskee kaikkia
pakkausmuotoja: `tar`-arkistossa tarvitaan valitsimet `--mtime`,
`--sort=name`, `--owner=0` ja `--group=0` ja `gzip`-pakkauksessa `-n`.

## Muut lähteet

Polkujen ja aikojen lisäksi tavallisia syitä ovat:

- **Tiedostojärjestys.** `$(wildcard)` ja hakemiston lukeminen voivat
  palauttaa tiedostot missä järjestyksessä tahansa, ja linkkerin syötteen
  järjestys vaikuttaa tulokseen. GNU Make 4.3 lajittelee `wildcard`-tuloksen,
  vanhemmat eivät; `$(sort ...)` on varma tapa.
- **Ympäristö.** Kieli- ja aikavyöhykeasetukset (`LANG`, `TZ`), käyttäjänimi
  ja koneen nimi päätyvät joskus tuloksiin. CI:ssä ne kannattaa
  kiinnittää (`LC_ALL=C`, `TZ=UTC`).
- **Työkalujen versiot.** Eri kääntäjäversio tuottaa eri koodin.
  Toistettavuus koskee samoja työkaluja, joten niiden versiot
  kuuluvat rakennusympäristön kuvaukseen: kontin kuvaan, Nix-määrittelyyn
  tai vähintään CI:n asennuskomentoihin tarkkoine versioineen.
- **Satunnaisuus.** Jotkin työkalut käyttävät satunnaisia
  tunnisteita; GCC:n `-frandom-seed` kiinnittää ne.

Työkalu `diffoscope` vertaa kahta binääriä tai pakettia rekursiivisesti
ja näyttää, missä kohdassa ne eroavat. Se on ensimmäinen työkalu, kun
kaksi rakennusta tuottaa eri tiivisteen.

## Käytännössä

- **Tarkista toistettavuus CI:ssä.** Kaksi rakennusta eri
  hakemistoihin ja tiivisteiden vertailu on halpa testi, joka estää
  regressiot. Ilman testiä toistettavuus rikkoutuu huomaamatta.
- **`SOURCE_DATE_EPOCH` commitin ajasta.** Muuttuja kertoo
  työkaluille, mitä aikaa käyttää, ja commitin aika on lähteen
  ominaisuus eikä rakennushetken.
- **Versio Gitistä, ei kellosta.** `git describe --tags --dirty`
  kertoo tarkasti, mistä lähteestä binääri on rakennettu, ja merkitsee
  paikalliset muutokset.
- **Kiinnitä työkalut.** Sama kääntäjäversio kaikkialla on
  toistettavuuden edellytys. Kehityskontti ja CI:n kuva ovat tähän
  luonteva paikka.

## Itsearviointi

- Osaat kertoa, mitä toistettava rakennus tarkoittaa ja miksi se on
  hyödyllinen.
- Osaat poistaa käännöshakemiston polun objektitiedostoista
  valitsimella `-ffile-prefix-map`.
- Osaat kiinnittää käännösajan muuttujalla `SOURCE_DATE_EPOCH` ja
  luoda arkiston, jossa ei ole aikaleimoja.
- Osaat luetella tavallisimmat epätoistettavuuden syyt ja keinot
  löytää kahden binäärin ero.
