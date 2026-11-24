# GPU:n muistihierarkia

GPU:n laskentateho kasvaa nopeammin kuin muistin kaista. Nykyisellä
laitteella on kymmeniä teralaskuja sekunnissa mutta "vain" yhdestä
kolmeen teratavua sekunnissa muistikaistaa: jokaista ladattua
neljän tavun lukua kohden ehtisi laskea kymmeniä laskutoimituksia.
Useimmat ytimet ovat siksi **muistisidonnaisia**, ja niiden
optimointi tarkoittaa muistiliikenteen vähentämistä ja järjestämistä.
Suorituskyvyn tutoriaalin roofline-malli pätee sellaisenaan;
ainoastaan harjanne on GPU:lla kauempana.

## Tasot

| Taso | Koko (tyypillinen) | Näkyy | Huomio |
|------------|--------------------|------------|------------------------------|
| rekisterit | 64–256 KiB laskentayksikköä kohden | säikeelle | nopein; määrä rajoittaa käyttöastetta |
| jaettu muisti | 16–128 KiB laskentayksikköä kohden | työryhmälle | ohjelmoijan hallitsema välimuisti |
| L1-välimuisti | jakaa tilan jaetun muistin kanssa | laskentayksikölle | ei koherentti yksiköiden välillä |
| L2-välimuisti | 4–100 MiB | koko laitteelle | atomiset operaatiot tehdään täällä |
| globaali muisti (VRAM) | 8–192 GiB | kaikille | HBM tai GDDR, satojen jaksojen viive |
| isännän muisti | koko RAM | PCIe- tai NVLink-väylän takana | moninkertaisesti hitaampi kuin VRAM |

Ohjelmoijalle näkyviä ovat rekisterit (paikalliset muuttujat), jaettu
muisti (`shared`) ja globaali muisti (puskurit). Välimuistit toimivat
automaattisesti, mutta GPU:n L1 on pieni suhteessa säikeiden määrään,
eikä siihen voi luottaa kuten CPU:n välimuistiin. Jaettu muisti on
siksi GPU-laskennan tärkein optimointikeino: data ladataan sinne
kerran ja luetaan monta kertaa.

## Yhtenäiset muistihaut

Globaalia muistia luetaan 32–128 tavun segmentteinä. Kun aliryhmä
suorittaa latauskäskyn, laitteisto kokoaa kaistojen osoitteet ja hakee
jokaisen tarvittavan segmentin kerran. Jos 32 kaistaa lukee 32
peräkkäistä neljän tavun sanaa, tarvitaan yksi 128 tavun segmentti.
Tätä kutsutaan **yhtenäiseksi muistihauksi** (coalesced access). Jos
kaistat lukevat sanoja, jotka ovat tuhannen sanan päässä toisistaan,
tarvitaan 32 segmenttiä, ja kustakin käytetään vain neljä tavua.
Kaistasta menee hukkaan 97 %.

Lavapipe ei näytä tätä, koska CPU:n välimuisti pehmentää hajanaiset
haut. Esimerkki laskee siksi varjostinten osoitteet myös mallilla:
32 säikeen aalto, 128 tavun segmentit ja jaetussa muistissa 32
neljän tavun pankkia. Malli on yksinkertaistus, mutta se vastaa sitä,
mitä NVIDIA:n ja AMD:n profiloijat raportoivat.

```{.cpp tiedosto="esimerkit/09-transpoosi.cpp" osa="malli"}
```

## Matriisin transpoosi

Transpoosi on hyvä esimerkki, koska siinä ei lasketa mitään. Sen
nopeus on pelkkää muistiliikennettä. Suora toteutus lukee rivejä ja
kirjoittaa sarakkeita:

```{.glsl tiedosto="esimerkit/varjostimet/transpoosi_suora.comp" osa="suora"}
```

Luku on yhtenäinen: aallon kaistat lukevat rivin peräkkäisiä alkioita.
Kirjoitus ei ole: naapurikaistat kirjoittavat sarakkeen peräkkäisille
riveille, jotka ovat 760 sanan päässä toisistaan.

Laatoitettu versio siirtää 32 × 32 alkion laatan jaetun muistin
kautta. Se lukee laatan rivit yhtenäisesti jaettuun muistiin ja
kirjoittaa ne kohteeseen myös riveittäin. Kääntö tapahtuu jaetussa
muistissa, jossa satunnaishaut ovat halpoja:

```{.glsl tiedosto="esimerkit/varjostimet/transpoosi_laatta.comp" osa="laatta"}
```

Sama varjostin käännetään kahdella tavalla. Erikoistusvakio `TAYTE`
määrää jaetun muistin rivin pituudeksi 32 tai 33:

```{.cpp tiedosto="esimerkit/09-transpoosi.cpp" osa="putket"}
```

```{.tuloste tiedosto="esimerkit/09-transpoosi.odotettu"}
```

Suora versio koskee kirjoittaessaan keskimäärin 31 segmenttiä aaltoa
kohden. Arvo ei ole tasan 32, koska reunan aalloissa on vähemmän
mukana olevia kaistoja. Laatoitettu versio koskee lukiessaan ja
kirjoittaessaan alle kahta segmenttiä. Arvo on yli yhden, koska 1 000
ja 760 eivät ole 32:n monikertoja, joten rivit eivät ala segmentin
rajalta.

## Pankkikonfliktit

Jaettu muisti on jaettu 32 **pankkiin** (bank), ja peräkkäiset neljän
tavun sanat ovat peräkkäisissä pankeissa. Jokainen pankki palvelee
yhden sanan kellojaksossa. Jos aallon kaistat osuvat 32 eri pankkiin,
haku valmistuu yhdessä jaksossa. Jos ne osuvat samaan pankkiin eri
sanoissa, haku sarjallistuu: tämä on **pankkikonflikti**. Sama sana
samassa pankissa ei ole konflikti, koska se lähetetään kaikille
kaistoille kerralla.

Laatoitetussa transpoosissa jaettua muistia luetaan sarakkeittain:
`laatta[lx][ly + r]`. Kun rivin pituus on 32, kaistan `lx` osoite on
`lx * 32 + c`, ja kaikki 32 kaistaa osuvat pankkiin `c`. Haku kestää
32 jaksoa. Yhden sanan täyte (rivin pituus 33) siirtää jokaisen rivin
alkua yhdellä pankilla, ja osoitteet `lx * 33 + c` osuvat 32 eri
pankkiin. Konflikti katoaa, ja muistia kuluu 3 % enemmän.

Mittaustilassa lavapipe näytti päinvastaista: suora versio oli
nopein (noin 20 ms) ja laatoitetut hitaampia (35–50 ms). Lavapipen
"jaettu muisti" on tavallista CPU:n muistia, eikä siinä ole pankkeja,
ja este maksaa (luku 3). Oikealla GPU:lla laatoitettu ja täytetty
versio on tyypillisesti moninkertaisesti suoraa nopeampi ja lähellä
pelkän kopioinnin nopeutta.

## Matriisitulo

Matriisitulossa $C = AB$ jokainen tulosalkio tarvitsee A:n rivin ja
B:n sarakkeen. Suora toteutus lataa ne globaalista muistista:

```{.glsl tiedosto="esimerkit/varjostimet/matmul_suora.comp" osa="suora"}
```

Jokainen A:n alkio ladataan $N$ kertaa ja jokainen B:n alkio $M$
kertaa. Laatoitus lataa 16 × 16 laatan A:sta ja B:stä jaettuun
muistiin, ja työryhmän 256 säiettä käyttävät jokaisen ladatun luvun
16 kertaa:

```{.glsl tiedosto="esimerkit/varjostimet/matmul_laatta.comp" osa="laatta"}
```

Reunoilla laattoihin ladataan nollia, jotta kaikki säikeet kulkevat
saman silmukan ja saavuttavat molemmat esteet. Säikeet, joiden
tulosalkio on matriisin ulkopuolella, eivät saa palata aikaisin kuten
suorassa versiossa, koska niiden lataamia laatan osia tarvitaan.
Jälkimmäinen este estää seuraavan laatan latauksen ennen kuin kaikki
säikeet ovat lukeneet nykyisen.

```{.cpp tiedosto="esimerkit/10-matriisitulo.cpp" osa="intensiteetti"}
```

```{.tuloste tiedosto="esimerkit/10-matriisitulo.odotettu"}
```

Laatoitus nostaa **laskentaintensiteetin** 0,25:stä neljään
laskutoimitukseen tavua kohden. Roofline-mallissa (suorituskyvyn
tutoriaalin luku 3) suora versio on syvällä muistisidonnaisella
alueella. Laite, jonka kaista on 1 Tt/s, rajoittaa sen 250
Glaskuun/s, kun laskentateho voi olla kymmeniä teralaskuja.
Laatoitettu versio nostaa rajan 4 Tlaskuun/s. Tuotantotason
matriisitulot laatoittavat useassa tasossa: jaetun muistin laatat,
rekistereissä jokaisen säikeen oma 4 × 4 tai 8 × 8 tulosalkion
laatta ja lopulta matriisiyksiköt (tensor cores, Vulkanin
`VK_KHR_cooperative_matrix`). Ne saavuttavat 70–90 % laitteen
huipusta.

Lavapipellä laatoitettu versio oli mittaustilassa kolme kertaa
hitaampi kuin suora, samasta syystä kuin transpoosissa. Matriisit
mahtuvat CPU:n välimuistiin, ja este maksaa enemmän kuin se säästää.

## Käytännössä

- **Naapurikaistat, naapuriosoitteet.** Järjestä indeksointi niin,
  että `gl_LocalInvocationID.x` kulkee muistissa peräkkäisten
  osoitteiden suuntaan. Rakenteiden taulukko (AoS) kannattaa usein
  muuttaa taulukoiden rakenteeksi (SoA), jotta aallon kaistat lukevat
  samaa kenttää peräkkäisistä alkioista.
- **Jaettu muisti uudelleenkäyttöön ja järjestyksen muuttamiseen.**
  Laatoitus kannattaa, kun samaa dataa luetaan monta kertaa
  (matriisitulo, konvoluutio) tai kun haun järjestys on käännettävä
  (transpoosi, hajautus lajittelussa).
- **Täytä pankit.** Kun jaettua muistia luetaan sarakkeittain, lisää
  riviin yksi sana täytettä.
- **Laske intensiteetti ennen optimointia.** Jos ydin on
  muistisidonnainen, laskennan optimointi ei auta. Jos se on
  laskentasidonnainen, muistihakujen järjestely ei auta.

## Itsearviointi

- Osaat kuvata GPU:n muistihierarkian tasot ja kertoa, mitkä niistä
  ovat ohjelmoijan hallinnassa.
- Osaat selittää yhtenäisen muistihaun ja laskea, montako segmenttiä
  aallon muistikäsky koskee.
- Osaat tunnistaa jaetun muistin pankkikonfliktin ja poistaa sen
  täytteellä.
- Osaat toteuttaa laatoitetun transpoosin ja matriisitulon ja laskea
  niiden laskentaintensiteetin roofline-mallia varten.
