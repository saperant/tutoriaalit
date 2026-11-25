# Juuritiedostojärjestelmä ja päivitykset

Initramfs on aina puhdas, mutta se ei säily: kaikki muutokset katoavat
uudelleenkäynnistyksessä, ja koko järjestelmä vie RAMia. Useimmissa
laitteissa juuri on pysyvällä tallennusvälineellä, kuten eMMC:llä,
SD-kortilla tai flashilla. Silloin on päätettävä, mikä juuressa saa
muuttua, miten se suojataan virran katkeamiselta ja miten koko
järjestelmä päivitetään kentällä.

## Hakemistorakenne

Linux-järjestelmät noudattavat *Filesystem Hierarchy Standardia* (FHS)
väljästi. Sulautetussa laitteessa jakolinja kulkee sen mukaan, mikä
muuttuu:

| Hakemisto | Sisältö | Muuttuu |
|-----------|---------|---------|
| `/bin`, `/sbin`, `/lib`, `/usr` | ohjelmat ja kirjastot | vain päivityksessä |
| `/etc` | asetukset | joskus: verkkoasetukset, laitekohtaiset arvot |
| `/var` | lokit, välimuistit, tietokannat | jatkuvasti |
| `/run`, `/tmp` | ajonaikaiset tiedostot | jatkuvasti, tyhjenee käynnistyksessä |
| `/dev`, `/proc`, `/sys` | ytimen virtuaaliset tiedostojärjestelmät | ytimen hallinnassa |
| `/data` tai `/var/lib` | sovelluksen pysyvä data | jatkuvasti |

Uusissa jakeluissa `/bin`, `/sbin` ja `/lib` ovat linkkejä `/usr`in
vastaaviin (*merged /usr*), jolloin koko ohjelmisto on yhden hakemiston
alla ja voidaan kiinnittää tai päivittää kerralla. Laitekohtaiset tiedot,
kuten sarjanumero, kalibrointiarvot ja sertifikaatit, kannattaa pitää
omassa osiossaan tai muistissaan, joka ei muutu päivityksissä.

## Tiedostojärjestelmän valinta

| Tiedostojärjestelmä | Väline | Ominaisuudet |
|---------------------|--------|--------------|
| ext4 | eMMC, SD, SSD | journal, luku ja kirjoitus, yleisin |
| SquashFS | mikä tahansa | pakattu, vain luku |
| EROFS | mikä tahansa | pakattu, vain luku, nopea satunnaisluku |
| F2FS | eMMC, SD | suunniteltu flashille |
| UBIFS | raaka NAND (UBI:n päällä) | kulumisen tasaus, virrankatkon kestävä |
| JFFS2 | pieni NOR-flash | vanha, hidas kiinnittää suurilla levyillä |

eMMC:ssä ja SD-kortissa on oma ohjain, joka hoitaa kulumisen tasauksen
ja huonot lohkot, joten niillä käytetään tavallisia tiedostojärjestelmiä.
Raaka NAND-flash näkyy ytimelle MTD-laitteena, ja sen päällä käytetään
UBI-kerrosta ja UBIFS:ää. Halvat SD-kortit ovat tunnetusti epäluotettavia
virrankatkoissa ja kuluvat nopeasti, jos niille kirjoitetaan jatkuvasti
lokia, joten teollisuuslaitteissa käytetään teollisuusluokan korttia tai
eMMC:tä.

## Vain luku -juuri

Turvallisin juuri on sellainen, johon ei kirjoiteta lainkaan. Virran
katkeaminen kesken kirjoituksen ei voi rikkoa sitä, laitteen tila on
aina tunnettu, ja tehdasasetuksiin palautus tarkoittaa vain muuttuvan
datan poistamista. Vain luku -juuren eheyden voi lisäksi tarkistaa
lohko kerrallaan *dm-verity*llä: ydin laskee lohkojen tiivisteet
luettaessa ja vertaa niitä allekirjoitettuun juurihajautusarvoon, joten
muutettu juuri huomataan heti. Tästä lisää taidossa *Sulautettujen
järjestelmien tietoturva*.

Esimerkin juuri on ext4-levykuva, joka kiinnitetään vain luku -tilaan
ytimen komentorivin parametrilla `ro`. Kuva tehdään samalla
`mke2fs -d` -menetelmällä kuin luvun 5 levykuva, ja ydin käynnistää
pysyvältä juurelta parametrin `init=` ohjelman:

```{.make tiedosto="esimerkit/Makefile" osa="juuri"}
```

Init näyttää ensin, ettei juureen voi kirjoittaa:

```{.c tiedosto="esimerkit/08-juuri/init.c" osa="vainluku"}
```

## Overlayfs

Monet ohjelmat olettavat voivansa kirjoittaa `/etc`iin: verkkoasetukset,
aikavyöhyke, laitteen nimi. *Overlayfs* yhdistää kaksi hakemistoa
yhdeksi: *alempi* kerros (lowerdir) on vain luku -juuren hakemisto ja
*ylempi* (upperdir) kirjoitettava hakemisto. Lukiessa näkyy ylemmän
kerroksen tiedosto, jos se on olemassa, muuten alemman. Kirjoitettaessa
tiedosto kopioidaan ensin ylempään kerrokseen (*copy-up*), ja muutos
tehdään kopioon. Poistettu tiedosto merkitään ylempään kerrokseen
erityisellä *whiteout*-tiedostolla. Työhakemisto (workdir) on
overlayfs:n oma apuhakemisto, ja sen on oltava samassa
tiedostojärjestelmässä kuin ylemmän kerroksen.

```{.dot otsikko="Overlayfs: yhdistetty näkymä lukee ylemmästä kerroksesta, jos tiedosto on siellä, muuten alemmasta. Kirjoitus kopioi tiedoston ensin ylempään kerrokseen."}
digraph {
  rankdir=TB; node [shape=box];
  nakyma [label="/etc (yhdistetty näkymä)\nlaite.conf"];
  yla [label="ylempi kerros: /run/etc/yla (tmpfs, kirjoitettava)\nlaite.conf: nimi=kentalla-muutettu"];
  ala [label="alempi kerros: juuren /etc (ext4, vain luku)\nlaite.conf: nimi=tehdasasetus"];
  nakyma -> yla [label="luku ja kirjoitus"];
  nakyma -> ala [style=dashed, label="luku, jos tiedostoa\nei ole ylempänä"];
  ala -> yla [label="copy-up ensimmäisessä\nkirjoituksessa"];
}
```

```{.c tiedosto="esimerkit/08-juuri/init.c" osa="overlay"}
```

Init avasi `/etc`-hakemiston ennen kiinnitystä. Hakemistokahva osoittaa
yhä alkuperäiseen hakemistoon, joten sen kautta näkee alemman kerroksen
myös kiinnityksen jälkeen:

```{.c tiedosto="esimerkit/08-juuri/init.c" osa="kerrokset"}
```

```{.tuloste tiedosto="esimerkit/testit/08-juuri.odotettu"}
```

Esimerkissä ylempi kerros on `tmpfs`:ssä, joten muutokset katoavat
sammutuksessa ja laite palaa joka käynnistyksessä tehdasasetuksiin.
Kun muutosten on säilyttävä, ylempi kerros sijoitetaan pysyvälle
dataosiolle. Tehdasasetuksiin palautus on silloin ylemmän kerroksen
tyhjennys. Sama periaate on konttien kerroksellisten kuvien perusta
(taito *Kontit ja pilvi-infrastruktuuri*).

## Kirjoitus ja virrankatkos

Sulautetun laitteen virta voi katketa milloin tahansa. Tiedostojärjestelmän
journal suojaa sen omat rakenteet, mutta ei sovelluksen dataa. Sovellus
tallentaa tiedoston turvallisesti näin:

1. kirjoita uusi sisältö väliaikaiseen tiedostoon samaan hakemistoon
2. kutsu `fsync` tiedostolle
3. nimeä väliaikainen tiedosto lopulliseksi (`rename`, joka on atominen)
4. kutsu `fsync` hakemistolle, jotta nimenmuutos on levyllä.

Näin tiedostossa on aina joko vanha tai uusi sisältö, ei koskaan puolikas.
Pelkkä `write` ja `close` jättää datan välimuistiin sekunneiksi, ja
katkos sinä aikana tuottaa tyhjän tai katkenneen tiedoston.

## Päivitykset: A/B-osiot

Kentällä olevan laitteen päivityksen on kestettävä virrankatkos ja
viallinen päivitys. Yleisin ratkaisu on kaksi juuriosiota, A ja B.
Laite käynnistyy A:lta, päivitys kirjoitetaan B:hen kokonaan, ja vasta
sen jälkeen käynnistin ohjataan käynnistämään B. Jos päivityksen
kirjoitus keskeytyy, laite käynnistyy yhä A:lta.

Uusi järjestelmä voi kuitenkin olla rikki niin, että se kaatuu
käynnistyksessä. Siksi käynnistin laskee käynnistyskertoja: U-Bootin
`bootcount`-laskuri kasvaa jokaisessa käynnistyksessä, ja kun se
ylittää muuttujan `bootlimit`, U-Boot ajaa `altbootcmd`-komennon, joka
käynnistää vanhan osion. Uusi järjestelmä nollaa laskurin vasta, kun se
on todennut toimivansa (*commit*).

```{.dot otsikko="A/B-päivityksen tilat. Viallinen päivitys päättyy takaisin vanhaan osioon ilman käyttäjän toimia."}
digraph {
  rankdir=TB; node [shape=box];
  a [label="käynnissä A:lta"];
  kirj [label="päivitys kirjoitetaan B:hen\nja tarkistetaan"];
  koe [label="B merkitty kokeiltavaksi,\nlaskuri = 0"];
  b [label="käynnistys B:ltä,\nlaskuri kasvaa"];
  ok [label="käynnissä B:ltä, vahvistettu"];
  a -> kirj [label="uusi versio"];
  kirj -> koe [label="tarkistus ok"];
  kirj -> a [label="katkos tai virhe:\nmikään ei muutu"];
  koe -> b [label="uudelleenkäynnistys"];
  b -> ok [label="palvelut valmiit: commit"];
  b -> b [label="kaatui, laskuri ≤ raja"];
  b -> a [label="laskuri > raja:\naltbootcmd"];
}
```

Valmiita toteutuksia ovat SWUpdate,
RAUC ja Mender, jotka hoitavat myös päivityspaketin allekirjoituksen
tarkistuksen. OSTree ja vastaavat tekevät saman tiedostotasolla
kokonaisten osioiden sijaan.

| Ratkaisu | Periaate | Hinta |
|----------|----------|-------|
| A/B-osiot | kaksi täyttä juurta, vaihto käynnistimessä | kaksinkertainen tila |
| palautusjärjestelmä | pieni palautusjuuri päivittää pääjuuren | päivityksen aikana laite on palautustilassa |
| tiedostotason päivitys (OSTree) | sisältöosoitteinen tallennus, vaihto linkeillä | monimutkaisempi |
| pakettipäivitys | kuten jakeluissa | ei atominen, ei sovi useimpiin laitteisiin |

## Käytännössä

- **Tee juuresta vain luku -tilainen.** Erota muuttuva data omaksi
  osiokseen tai overlayksi ja tiedä tarkalleen, mihin laite kirjoittaa.
- **Tallenna tiedostot atomisesti.** Väliaikainen tiedosto, `fsync`,
  `rename` ja hakemiston `fsync`.
- **Säästä flashia.** Pidä lokit RAMissa (`tmpfs`, journald:n
  `Storage=volatile`) tai rajoita niiden kokoa ja kirjoitustiheyttä.
- **Suunnittele päivitys ensimmäisenä, ei viimeisenä.** Osiointi,
  käynnistimen logiikka ja palautus on vaikea muuttaa sen jälkeen, kun
  laitteita on kentällä. Testaa virrankatkos jokaisessa vaiheessa.
- **Pidä laitekohtainen data erillään.** Sarjanumero, kalibrointi ja
  avaimet eivät saa kadota päivityksessä eikä tehdasasetusten
  palautuksessa.

## Itsearviointi

- Osaat jakaa juuren hakemistot muuttumattomiin ja muuttuviin ja
  perustella vain luku -juuren.
- Osaat valita tiedostojärjestelmän tallennusvälineen mukaan ja kertoa,
  miten raaka NAND eroaa eMMC:stä.
- Osaat kiinnittää overlayfs:n ja selittää alemman ja ylemmän kerroksen,
  copy-upin ja whiteout-tiedoston.
- Osaat tallentaa tiedoston niin, että virrankatkos ei jätä sitä
  puolikkaaksi.
- Osaat kuvata A/B-päivityksen ja käynnistyskertojen laskennan, jolla
  viallinen päivitys perutaan.
