# Staattinen linkitys ja arkistot

Staattinen kirjasto (`libnimi.a`) on *arkisto*: objektitiedostojen
kokoelma ja hakemisto niiden määrittelemistä symboleista. Se ei ole
yksi suuri objektitiedosto. Linkkeri ottaa arkistosta vain ne
jäsenet, joita se tarvitsee puuttuvien symbolien ratkaisemiseen, ja
kopioi ne ohjelmaan kokonaisina. Tämä yksinkertainen sääntö selittää
staattisen linkityksen kaikki yllätykset.

## Arkiston rakentaminen

Esimerkin tilastokirjastossa on kolme funktiota kolmessa tiedostossa.
`hajonta` käyttää funktiota `keskiarvo`, joten jäsenten välillä on
riippuvuus:

```{.c tiedosto="esimerkit/05-arkisto/tilasto.h"}
```

```{.c tiedosto="esimerkit/05-arkisto/hajonta.c"}
```

```{.bash tiedosto="esimerkit/05-arkisto/aja.sh" osa="arkisto"}
```

`ar`:n valitsimet: `r` lisää tai korvaa jäsenet, `c` luo arkiston
kysymättä ja `s` kirjoittaa symbolihakemiston (sama kuin `ranlib`).
`ar t` luettelee jäsenet. `nm libtilasto.a` näyttää jokaisen jäsenen
symbolit erikseen.

## Järjestys ratkaisee

GNU-linkkeri käy syötteensä läpi kerran vasemmalta oikealle ja pitää
kirjaa ratkaisemattomista symboleista. Kun se kohtaa arkiston, se
ottaa jäsenet, jotka määrittelevät jonkin *sillä hetkellä*
ratkaisemattoman symbolin, ja jatkaa eteenpäin. Arkistoon ei palata.
Jos kirjasto on ennen ohjelmaa, mitään ei vielä puutu, eikä
arkistosta oteta mitään:

```{.bash tiedosto="esimerkit/05-arkisto/aja.sh" osa="vaara"}
```

```{.bash tiedosto="esimerkit/05-arkisto/aja.sh" osa="oikein"}
```

Linkkerikartta (`-Map`) kertoo, mitkä jäsenet otettiin ja minkä
viittauksen vuoksi:

```{.bash tiedosto="esimerkit/05-arkisto/aja.sh" osa="jasenet"}
```

```{.tuloste tiedosto="esimerkit/05-arkisto/odotettu"}
```

`main.o` tarvitsee symbolit `keskiarvo` ja `hajonta`, joten kaksi
jäsentä otetaan. `mediaani.o` jää pois kokonaan, eikä sen tarvitsema
`qsort` päädy ohjelmaan. Saman arkiston jäsenten keskinäiset
riippuvuudet ratkeavat, koska linkkeri käy arkiston hakemistoa läpi,
kunnes yksikään uusi jäsen ei ratkaise mitään. Arkistojen väliset
riippuvuudet eivät ratkea itsestään.

Säännöt riippuvuuksien järjestykselle:

| Tilanne | Ratkaisu |
|---------|----------|
| ohjelma käyttää kirjastoa | kirjasto ohjelman objektien *jälkeen* |
| `liba` käyttää `libb`:tä | `-la -lb` |
| `liba` ja `libb` käyttävät toisiaan | `-Wl,--start-group -la -lb -Wl,--end-group` |
| matematiikkakirjasto | `-lm` viimeisenä C-kirjastoja |

Ryhmä (`--start-group`) käy arkistoja läpi toistuvasti, mikä on
hitaampaa ja kätkee kehän. Kehä kirjastojen välillä kertoo yleensä,
että jako on väärä. Uudemmat linkkerit, kuten LLVM:n `lld` ja `mold`,
muistavat kaikki arkistot eivätkä riipu järjestyksestä. Rakennus, joka
toimii vain niillä, rikkoutuu GNU `ld`:llä, joten järjestys kannattaa
pitää oikeana.

> Jaetut kirjastot (`-lnimi` löytää ensisijaisesti `libnimi.so`:n)
> käyttäytyvät toisin: linkkeri lukee kaikki niiden symbolit kerralla.
> Järjestyksellä on silti merkitystä, ja valitsin `--as-needed`
> (Ubuntun oletus) jättää riippuvuuden pois, jos kirjastoa ei
> tarvittu sen kohdalla. Sama sääntö pätee siis molempiin.

## Jäsenen koko ratkaisee koon

Linkkeri ottaa jäsenen kokonaan. Jos kaikki kirjaston funktiot ovat
yhdessä tiedostossa, yhden funktion käyttö tuo ohjelmaan kaikki.
Siksi C-kirjastot jaetaan usein yksi funktio tiedostoa kohti. Sama
tulos saadaan valitsimilla `-ffunction-sections -fdata-sections` ja
linkkerin `--gc-sections`, jolloin linkkeri karsii käyttämättömät
osiot jäsenten sisältä.

Arkistosta otettu jäsen tuo kaiken, mitä se määrittelee, ja kaiken,
mihin se viittaa. Jäsenen alustusfunktiot (`constructor`, luku 12)
ajetaan vain, jos jäsen otettiin mukaan. Tämä yllättää
rekisteröintimallissa, jossa jäsen rekisteröi itsensä eikä mikään
viittaa siihen: jäsentä ei oteta, ja rekisteröinti puuttuu. Ratkaisu
on `-Wl,--whole-archive -lnimi -Wl,--no-whole-archive`, joka ottaa
kaikki jäsenet, tai suora viittaus jäseneen.

## Kaksoismäärittely

Kun sama globaali symboli määritellään vahvasti kahdessa
objektitiedostossa, linkkeri ei voi valita:

```{.c tiedosto="esimerkit/05-arkisto/versio_a.c"}
```

```{.c tiedosto="esimerkit/05-arkisto/versio_b.c"}
```

```{.bash tiedosto="esimerkit/05-arkisto/aja.sh" osa="kaksois"}
```

Tämä koodi linkittyi ennen GCC 10:tä, koska alustavat määrittelyt
olivat yhteisiä symboleita (luku 4). Arkistojen kohdalla
kaksoismäärittely voi myös jäädä huomaamatta: jos symboli on jo
määritelty, linkkeri ei ota toista jäsentä sen vuoksi. Jos jäsen
otetaan jonkin toisen symbolin takia, kaksoismäärittely paljastuu.
Ohjelman toiminta riippuu siis siitä, mitä funktioita käytetään.

## Staattinen vai jaettu

| Ominaisuus | Staattinen (`.a`) | Jaettu (`.so`) |
|------------|-------------------|----------------|
| ajonaikaiset riippuvuudet | ei | kirjasto on asennettava |
| koko | vain käytetyt jäsenet, kopio jokaiseen ohjelmaan | yksi kopio levyllä ja muistissa |
| tietoturvapäivitys | ohjelma linkitetään uudelleen | kirjasto vaihdetaan |
| käynnistys | nopea, ei lataajaa | kirjastojen haku ja sidonta |
| optimointi | linkitysaikainen optimointi (LTO) koko ohjelmalle | rajapinta pysäyttää LTO:n |
| lisenssi | LGPL vaatii uudelleenlinkitettävyyden | LGPL täyttyy helposti |

Täysin staattinen ohjelma (`-static`) ei tarvitse edes C-kirjastoa
ajossa, mikä sopii kontteihin ja pelastustyökaluihin. glibc ei
kuitenkaan tue staattista linkitystä täysin: nimipalvelut (`getpwnam`,
`getaddrinfo`) lataavat moduuleja dynaamisesti ja varoittavat
linkityksessä. musl-kirjasto on suunniteltu staattiseen käyttöön.

## Käytännössä

- **Kirjastot objektien jälkeen, riippuvat ennen riippuvuuksia.**
  `gcc main.o -lkorkea -lmatala -lm`. Kun järjestystä ei voi
  päätellä, korjaa kirjastojen jako ennen kuin käytät ryhmää.
- **Lue linkkerikartta.** `-Wl,-Map=ohjelma.map` kertoo jokaisen
  otetun jäsenen ja syyn. Se vastaa kysymyksiin "miksi ohjelma on
  näin suuri" ja "mistä tämä symboli tuli".
- **Varo itsensä rekisteröiviä jäseniä.** Jäsen, johon mikään ei
  viittaa, jää pois arkistosta linkitettäessä. Käytä
  `--whole-archive`-valitsinta tai objektikirjastoa (CMaken
  `OBJECT`-kirjasto).
- **Käännä varoitukset virheiksi myös linkkerissä.** `-Wl,--fatal-warnings`
  ja `-Wl,--warn-common` paljastavat vanhan koodin kaksoismäärittelyt.

## Itsearviointi

- Osaat rakentaa staattisen kirjaston `ar`:llä ja tutkia sen jäseniä
  ja symboleita.
- Osaat selittää, miksi kirjaston paikka komentorivillä ratkaisee, ja
  järjestää kirjastot oikein, myös keskenään riippuvat.
- Osaat lukea linkkerikartasta, mitkä jäsenet otettiin ja miksi.
- Osaat kertoa, miksi kaksoismäärittely voi näkyä tai jäädä
  näkymättä arkistoja käytettäessä.
- Osaat verrata staattista ja jaettua linkitystä koon, päivitysten ja
  käynnistyksen kannalta.
