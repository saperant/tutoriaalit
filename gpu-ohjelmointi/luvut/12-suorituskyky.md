# Suorituskyvyn analyysi

GPU-ohjelman pullonkaula on jokin näistä: CPU ei ehdi lähettää
komentoja (piirtokutsut, tilanvaihdot), verteksien käsittely, pikselien
varjostus (ylipiirto, raskas varjostin), muistin kaista (tekstuurit,
kehyspuskuri, sekoitus) tai synkronointi (CPU ja GPU odottavat
toisiaan). Optimointi alkaa aina sen selvittämisestä, mikä näistä
rajoittaa. Yleisen suorituskyvyn mittauksen periaatteet ovat taidossa
*Suorituskyvyn analyysi ja optimointi*.

Tässä luvussa mitataan laskureilla ja puskureilla, ei ajalla:
ohjelmistorenderöijän ajoitukset eivät kerro mitään oikeasta GPU:sta,
mutta varjostinkutsujen ja piirtokutsujen määrät kertovat.

## Ylipiirto ja aikainen syvyystesti

Ylipiirto tarkoittaa, että samaan pikseliin ajetaan fragmenttivarjostin
useita kertoja, vaikka vain viimeinen näkyy. Esimerkki piirtää kuusi
limittäistä neliötä raskaalla varjostimella kahdessa järjestyksessä.
Laskurit ovat putken tilastokysely
(`GL_FRAGMENT_SHADER_INVOCATIONS`) ja sapluunapuskuri, joka kasvaa
jokaisesta syvyystestin läpäisevästä fragmentista:

```{.cpp tiedosto="esimerkit/12-ylipiirto.cpp" osa="glsl"}
```

```{.cpp tiedosto="esimerkit/12-ylipiirto.cpp" osa="mittaus"}
```

```{.tuloste tiedosto="esimerkit/12-ylipiirto.odotettu"}
```

Takaa eteen piirrettäessä jokainen uusi kerros on edellistä lähempänä,
joten syvyystesti päästää sen läpi ja varjostin ajetaan: osa
pikseleistä saa kuusi kirjoitusta. Edestä taakse piirrettäessä
**aikainen syvyystesti** (early-z) hylkää peittyvät fragmentit ennen
varjostinta, ja jokaiseen pikseliin ajetaan varjostin kerran:
1 976 kertaa 8 740:n sijaan.

Aikainen syvyystesti on käytössä vain, jos varjostin ei estä sitä:
`discard`, syvyyden kirjoitus (`gl_FragDepth`) tai sivuvaikutukset
(kirjoitus varastopuskuriin) pakottavat testin varjostimen jälkeen.
Siksi läpinäkymättömät kohteet lajitellaan karkeasti edestä taakse,
ja raskaissa kohtauksissa piirretään ensin pelkkä syvyys
(*depth pre-pass*), jonka jälkeen varjostus tehdään vain näkyville
pikseleille.

## Piirtokutsut ja tilanvaihdot

Jokainen piirtokutsu ja tilanvaihto maksaa CPU-aikaa ajurissa:
OpenGL:ssä tyypillisesti mikrosekunteja, Vulkanissa vähemmän mutta ei
nollaa. Tuhansia samanlaisia kohteita (puut, hiukkaset, ruoho) ei
piirretä yksitellen vaan **instansseina**: yksi kutsu, ja varjostin
hakee instanssikohtaisen datan puskurista `gl_InstanceID`:llä.

```{.cpp tiedosto="esimerkit/12-instanssit.cpp" osa="glsl"}
```

```{.cpp tiedosto="esimerkit/12-instanssit.cpp" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/12-instanssit.odotettu"}
```

Sama kuva syntyy yhdellä kutsulla sadan sijaan. Pidemmälle vietynä
**epäsuora piirto** (`glMultiDrawIndirect`, `vkCmdDrawIndirect`) lukee
piirtokutsujen parametrit GPU:n puskurista, jolloin GPU voi itse
päättää laskentavarjostimella, mitä piirretään (GPU-driven rendering).

Tilanvaihtojen hinta vaihtelee: varjostinohjelman tai putken vaihto on
kallein, tekstuurin ja puskurin sidonta halvempi, uniform-arvo halvin.
Piirrot lajitellaan siksi kalleimman tilan mukaan: ensin putki, sitten
materiaali, sitten kohde.

## Kaistanleveys

Kaistan kulutuksen voi arvioida laskemalla. 1440p-ruutu on 3,7
miljoonaa pikseliä. RGBA8-kehyspuskurin kirjoitus on 15 Mt; sekoitus
lukee sen lisäksi kerran. Kuusinkertainen läpinäkyvä ylipiirto on
siis 180 Mt ruudussa, ja 60 ruudun sekunnissa 11 Gt/s pelkkään
kehyspuskuriin. Lisäksi tulevat syvyys, G-puskuri, tekstuurit ja
jälkikäsittely.

Kaistaa säästävät:

- **Mip-tasot ja pakatut tekstuurit** (luku 5).
- **Pienemmät välipuskurimuodot**: `R11G11B10F` HDR-värille
  `RGBA16F`:n sijaan, kaksikomponenttinen normaali.
- **`loadOp`/`storeOp` oikein** (luku 8), erityisesti ruutupohjaisilla
  GPU:illa.
- **Pienempi resoluutio raskaille vaiheille** ja skaalaus (esim.
  ambient occlusion puolella resoluutiolla, temporaalinen skaalaus).

## Mittaaminen oikealla GPU:lla

| Mittari | Väline |
|---------|--------|
| GPU-aika vaiheittain | aikaleimakyselyt (`GL_TIMESTAMP`, `vkCmdWriteTimestamp2`) |
| varjostinkutsut, primitiivit | putken tilastokyselyt |
| ruudun kutsut, resurssit, välitulokset | RenderDoc |
| laitteistolaskurit (käyttöaste, välimuisti, kaista) | Nsight Graphics, Radeon GPU Profiler, PIX |

GPU:n aika mitataan aikaleimoilla, ei CPU:n kellolla, koska CPU:n
kutsu palaa ennen kuin GPU on tehnyt työtä. Mittaa julkaisuversiolla
ilman validointia ja tarkista, ettei pystytahdistus (vsync) rajoita
ruutunopeutta.

## Käytännössä

- **Selvitä pullonkaula ennen optimointia.** Pienennä resoluutiota:
  jos nopeutuu, pikselit tai kaista rajoittavat. Jos ei, rajoittaa
  CPU, verteksit tai synkronointi.
- **Läpinäkymättömät edestä taakse, tarvittaessa syvyyden esipiirto.**
  Vältä `discard`ia ja `gl_FragDepth`ia tarpeettomasti.
- **Instanssit ja epäsuora piirto** tuhansille samanlaisille
  kohteille; lajittele piirrot tilan mukaan.
- **Laske kaista**: muodot, ylipiirto, sekoitus ja koko ruudun vaiheet
  kertautuvat resoluutiolla ja ruutunopeudella.
- **Älä synkronoi CPU:ta ja GPU:ta kesken ruudun.** Tulosten luku,
  kyselyiden odotus ja puskurien kirjoitus käytössä olevaan muistiin
  pysäyttävät koko putken.

## Itsearviointi

- Osaat mitata ylipiirron tilastokyselyllä tai sapluunalla ja
  selittää aikaisen syvyystestin sekä sen, mikä estää sen.
- Osaat korvata toistuvat piirtokutsut instanssipiirrolla ja selittää
  epäsuoran piirron idean.
- Osaat arvioida kaistan kulutuksen laskemalla ja luetella keinot
  sen vähentämiseen.
- Osaat valita oikean mittausvälineen GPU-ajalle, laskureille ja
  ruudun analyysille.
