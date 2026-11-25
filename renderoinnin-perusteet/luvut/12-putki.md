# Grafiikkaputki

Edellisissä luvuissa putken palaset on rakennettu yksi kerrallaan:
muunnokset, leikkaus, rasterointi, perspektiivikorjaus, syvyystesti,
karsinta, valaistus ja tekstuurit. Tässä luvussa ne kootaan
kokonaisuudeksi ja verrataan näytönohjaimen putkeen. Rakenne on
sama: kiinteät vaiheet, joita ohjataan asetuksilla, ja kaksi
ohjelmoitavaa vaihetta, **verteksivarjostin** ja
**fragmenttivarjostin**.

## Vaiheet

```{.dot otsikko="Grafiikkaputken vaiheet. Ohjelmoitavat vaiheet (tummempi tausta) kirjoittaa sovellus; muut ovat kiinteitä ja niitä ohjataan asetuksilla."}
digraph {
  rankdir=LR; nodesep=0.2; ranksep=0.3;
  node [shape=box, style="rounded,filled", fillcolor="#EEF0F2"];
  syote [label="kärjet ja\nindeksit"];
  vv [label="verteksi-\nvarjostin", fillcolor="#C9CEEE"];
  kok [label="kolmion kokoaminen,\nleikkaus, jako,\nkarsinta"];
  rast [label="rasterointi"];
  z [label="syvyystesti"];
  fv [label="fragmentti-\nvarjostin", fillcolor="#C9CEEE"];
  out [label="väri- ja\nsyvyyspuskuri"];
  syote -> vv -> kok -> rast -> z -> fv -> out;
}
```

| Vaihe | Tässä toteutuksessa | Näytönohjaimessa |
|-------|---------------------|------------------|
| syötteen kokoaminen | `Malli`, kolmioiden indeksit | verteksi- ja indeksipuskurit |
| verteksivaihe | funktio `Verteksi -> Tulos<N>` | verteksivarjostin |
| primitiivien kokoaminen | kolme tulosta kolmioksi | kiinteä |
| hylkäys ja leikkaus | `kokonaan_ulkona`, lähitaso | kiinteä, suojakaista |
| jako ja näkymäportti | `ruudulle` | kiinteä |
| karsinta | kiertosuunnan ristitulo | kiinteä, asetus |
| rasterointi | reunafunktiot, kiinteä pilkku | kiinteä, lohkoittain |
| syvyystesti | ennen varjostusta | early-z, hierarkkinen z |
| fragmenttivaihe | funktio `vaihtelevat -> Vari` | fragmenttivarjostin |
| kirjoitus | väri- ja syvyyspuskuri | ROP: sekoitus, MSAA |

Verteksivaihe käsittelee jokaisen kärjen kerran, vaikka sama kärki
kuuluisi moneen kolmioon. Siksi mallit tallennetaan indekseinä:
yhteiset kärjet muunnetaan vain kerran. Näytönohjaimet pitävät
viimeksi muunnetut kärjet välimuistissa, ja kolmioiden järjestys
optimoidaan välimuistia varten.

## Putki koodina

Koko putki yhdelle mallille on muutama silmukka:

```{.cpp tiedosto="esimerkit/yhteinen/putki.hpp" osa="piirra"}
```

Verteksivarjostimen tuloksen tyyppi päätellään funktiosta
(`std::invoke_result_t`), joten putki tietää vaihtelevien arvojen
määrän käännösaikana. Fragmenttivarjostin saa interpoloidut arvot ja
pikselin tiedot, ja derivaatat, jos asetus pyytää niitä:

```{.cpp tiedosto="esimerkit/yhteinen/putki.hpp" osa="fragmentti"}
```

Asetukset ovat putken kiinteiden vaiheiden tila. Näytönohjaimissa
sama tila on putkiolion (Vulkanin pipeline) tai OpenGL:n globaalin
tilan osa: syvyystesti, karsinta, sekoitus ja niin edelleen.

## Varjostin funktio-oliona

GPU:n varjostinohjelma koostuu kolmesta osasta: **yhteiset arvot**
(uniform), jotka ovat samat koko piirtokutsulle, **sisääntulot**
(attribuutit tai interpoloidut arvot) ja **tulokset**. C++:ssa
luonteva vastine on funktio-olio, jonka jäsenet ovat yhteiset arvot ja
jonka kutsuoperaattorit ovat varjostinvaiheet:

```{.cpp tiedosto="esimerkit/12-putki/varjostin.hpp" osa="yhteiset"}
```

```{.cpp tiedosto="esimerkit/12-putki/varjostin.hpp" osa="varjostin"}
```

Sama olio annetaan putkelle kahdesti, ja ylikuormitus valitsee oikean
vaiheen. Tekstuurin osoitin vastaa varjostimen näytteenotinta
(sampler): varjostin ei omista tekstuuria vaan lukee sitä.
Vaihtelevat arvot ovat kahdeksan lukua; GLSL:ssä ne olisivat
`out`-muuttujat verteksivarjostimessa ja samannimiset `in`-muuttujat
fragmenttivarjostimessa.

## Kohtaus

Kohtauksessa on kolme kappaletta: tekstuuroitu lattia, joka ulottuu
kameran taakse, tekstuuroitu kuutio ja kiiltävä pallo. Jokainen
kappale on yksi piirtokutsu omilla yhteisillä arvoillaan ja omalla
materiaalillaan:

```{.cpp tiedosto="esimerkit/12-putki/main.cpp" osa="kohtaus"}
```

```{.cpp tiedosto="esimerkit/12-putki/main.cpp" osa="piirtokutsut"}
```

```{.cpp tiedosto="esimerkit/12-putki/main.cpp" osa="tulos"}
```

```{.tuloste tiedosto="esimerkit/12-putki.odotettu"}
```

![Koko putken tulos: mipmapattu lattia, tekstuuroitu kuutio ja
pikseleittäin valaistu pallo, 2 × 2 -ylinäytteistys. Kirjan kuva on
renderöity nelinkertaisella tarkkuudella (`make kuvat`); testin
tarkistussumma on 120 × 80 pikselin kuvasta.](kuvat/12-putki.png){width=80%}

Tilastot kertovat, mitä putki teki. Lattian kahdesta kolmiosta yksi
leikattiin lähitasoa vastaan, koska lattia jatkuu kameran taakse.
Kuutiosta ja pallosta karsittiin noin puolet kolmioista takapintoina.
Pallon 512 kolmiota tuottavat vähemmän fragmentteja kuin lattian kaksi,
ja syvyystesti ei hylännyt yhtään fragmenttia, koska kappaleet
piirrettiin takaa eteen: jokainen uusi fragmentti oli lähempänä kuin
puskurissa jo oleva. Lattian pikselit kuution ja pallon kohdalla
varjostettiin siis turhaan. Edestä taakse -järjestyksessä (pallo ja
kuutio ennen lattiaa) syvyystesti hylkäisi ne ennen varjostusta.

Tarkistussumma tekee koko kohtauksesta regressiotestin: jos mikä
tahansa vaihe muuttuu, summa muuttuu. Tilastot auttavat paikantamaan
muutoksen vaiheeseen.

## Mitä nopea toteutus tekisi toisin

Tämä putki on kirjoitettu luettavaksi, ja se käsittelee yhden
pikselin kerrallaan. Tuotantokäyttöön tarkoitetut ohjelmistorasteroijat
(llvmpipe, SwiftShader, pelien okkluusiorasteroijat) ovat
kertaluokkia nopeampia, koska ne:

- **laskevat reunafunktiot inkrementaalisesti** ja hylkäävät kokonaisia
  lohkoja yhdellä testillä lohkon kulmissa,
- **käsittelevät pikseleitä SIMD-käskyillä** neljän tai kahdeksan
  ryhminä ja varjostavat $2 \times 2$ -ryhminä, joista derivaatat
  saadaan ilmaiseksi,
- **jakavat ruudun ruutuihin** (tiles), jotka rasteroidaan rinnakkain
  eri säikeissä niin, että kukin säie omistaa oman ruutunsa puskurit,
- **kääntävät varjostimet konekoodiksi** (llvmpipe LLVM:llä), jolloin
  asetusten haarat ja virtuaalikutsut katoavat,
- **pitävät syvyydestä hierarkiaa**, joka hylkää peitetyt kolmiot jo
  ennen rasterointia.

Näytönohjaimissa samat ideat ovat laitteistossa: tuhannet
varjostinytimet suorittavat samaa ohjelmaa eri pikseleille
(SIMT-malli), rasteroija ja syvyystesti ovat kiinteää logiikkaa, ja
mobiilipiireissä koko ruutu käsitellään ruutu kerrallaan sirun
sisäisessä muistissa. Taito *GPU-ohjelmointi: OpenGL ja Vulkan* rakentaa saman
kohtauksen OpenGL:llä ja Vulkanilla.

## Käytännössä

- **Ajattele vaiheittain.** Kun kuva on väärä, kysy, missä vaiheessa
  arvo on viimeksi oikein: kärjet, leikkausavaruus, ruutu,
  interpoloidut arvot vai varjostimen tulos.
- **Pidä varjostimet puhtaina funktioina.** Kun varjostin lukee vain
  yhteisiä arvoja ja sisääntuloja, sen voi testata erikseen ja
  ajaa rinnakkain.
- **Mittaa tilastoja.** Kolmiot, karsitut, leikatut, fragmentit ja
  syvyystestin hylkäämät kertovat, missä työ tehdään. Näytönohjaimen
  profiloijat (RenderDoc, Nsight, Radeon GPU Profiler) näyttävät samat
  luvut.
- **Ohjelmistorasteroija on hyvä vertailukohta.** Kun GPU-toteutus
  näyttää väärältä, tarkka ja hidas vertailutoteutus kertoo, kumpi on
  oikeassa.

## Itsearviointi

- Osaat luetella grafiikkaputken vaiheet ja kertoa, mitkä niistä ovat
  ohjelmoitavia.
- Osaat kirjoittaa verteksi- ja fragmenttivarjostimen funktioina ja
  selittää yhteisten ja vaihtelevien arvojen eron.
- Osaat tulkita putken tilastoja ja päätellä niistä, missä työ
  tehdään.
- Osaat kertoa, miten nopea ohjelmisto- tai laitteistoputki eroaa
  tästä toteutuksesta.
