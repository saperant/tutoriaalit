# DMA

DMA-ohjain (direct memory access) siirtää dataa muistin ja
oheislaitteiden välillä ilman suoritinta. Suoritin ohjelmoi siirron,
tekee muuta työtä ja saa keskeytyksen, kun siirto on valmis. Ilman DMA:ta
suoritin kopioisi jokaisen sanan itse, ja nopeat oheislaitteet
(verkko, tallennus, ääni, kamera) kuluttaisivat suurimman osan sen
ajasta.

## Rakenne

Pikku-SoC:n DMA kopioi sanoja muistista muistiin. Sillä on kaksi
liitäntää:

- **APB-orja**: ohjelmisto kirjoittaa lähde- ja kohdeosoitteen, sanojen
  määrän ja käynnistyskäskyn, ja lukee tilan.
- **AXI4-Lite-isäntä**: DMA lukee ja kirjoittaa muistia itse kytkimen
  kautta, samalla tavalla kuin ydin.

Isäntäliitännän signaalit muodostetaan tilasta:

```{.systemverilog tiedosto="esimerkit/rtl/dma.sv" osa="isanta"}
```

Tilakone lukee sanan, kirjoittaa sen ja siirtyy seuraavaan. Virhevastaus
kummassa tahansa vaiheessa keskeyttää siirron ja asettaa virhebitin:

```{.systemverilog tiedosto="esimerkit/rtl/dma.sv" osa="siirto"}
```

## Ohjelmointi

Ajuri asettaa rekisterit ja odottaa keskeytystä:

```{.c tiedosto="esimerkit/sw/dma.c" osa="kaynnista"}
```

Keskeytyskäsittelijä lukee tilan, kuittaa valmis- ja virhebitit
(W1C) ja tallentaa tilan pääohjelmalle. Pääohjelma vertaa suorittimen
ja DMA:n kopiointia:

```{.c tiedosto="esimerkit/sw/dma.c" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/odotettu/dma.odotettu"}
```

DMA on nopeampi, mutta ei paljon: ohjelmiston mittaamana 64 sanaa
kesti 1402 jaksoa eli noin 22 jaksoa sanaa kohden. Luku sisältää
muutakin kuin siirron, ja aaltomuoto erottelee osat:

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/dma-sana.json" otsikko="Kopion toinen sana simulaatiosta: DMA:n tilasta LUE seuraavaan LUE-tilaan kuluu 12 jaksoa. Ylhäällä DMA:n tila ja sen isäntäportin kättelyt, alhaalla ytimen lukupyynnöt samassa kytkimessä."}
```

Yksi sana vie väylällä noin 12 jaksoa: luku (osoite ja data), kirjoitus
(osoite ja data yhtä aikaa) ja vastaus, ja jokaisen välissä DMA
odottaa vuoroaan, koska ytimen pyynnöt (alimmat rivit) käyttävät
samaa kytkintä. Koko 64 sanan kopio vie väylällä 766 jaksoa
ensimmäisestä lukupyynnöstä viimeiseen vastaukseen. Loput noin 640
jaksoa mittauksesta kuluvat neljään rekisterikirjoitukseen, joilla
siirto käynnistetään, ja keskeytyksen käsittelyyn siirron lopussa.
Lyhyessä kopiossa kiinteä hinta on siis lähes yhtä suuri kuin itse
siirto.

Itse siirron hitaudelle on kolme syytä, ja ne kertovat, mistä DMA:n
suorituskyky oikeasti tulee:

1. **Yksi sana kerrallaan.** AXI4-Lite ei tunne purskeita, joten
   jokainen sana tarvitsee oman luvun ja kirjoituksen kättelyineen.
   Täyden AXI4:n purske kuljettaisi 16 sanaa yhdellä osoitteella:
   luvun 4 lohkotestissä sama 64 sanan kopio vei purskeina 140 jaksoa
   eli 2,2 jaksoa sanaa kohden.
2. **Ei avoimia siirtoja.** DMA odottaa jokaisen vastauksen ennen
   seuraavaa pyyntöä. Oikea DMA lähettää useita lukuja ennen
   ensimmäistä vastausta ja kirjoittaa sisäisestä FIFOsta.
3. **Jaettu väylä.** Kun DMA kopioi, ydin odottaa keskeytystä
   silmukassa, joka hakee käskyjä ja lukee muuttujaa RAMista. Kytkin
   vuorottelee ytimen ja DMA:n siirtoja, joten DMA saa vain osan
   väylästä.

Vaikka DMA ei olisi nopeampi, se vapauttaa suorittimen: kopioinnin
aikana ydin voisi laskea, ja siirtojen vuorottelu jakaa väylän
kummallekin.

## Virheet

DMA:n osoitteet ovat fyysisiä, eikä DMA tiedä, mitä muistia ohjelmisto
tarkoitti. Kartoittamaton kohde tuottaa väylävirheen, jonka DMA
raportoi tilarekisterissä:

```{.c tiedosto="esimerkit/sw/dma.c" osa="virhe"}
```

Jos DMA:n osoite on väärä mutta osuu olemassa olevaan muistiin, virhettä
ei tule: DMA kirjoittaa hiljaa jonkin toisen datan päälle. Siksi
tietoturvallisissa järjestelmissä DMA:n osoitteet tarkistetaan
IOMMU:lla, joka rajaa, mihin muistiin kukin laite saa kirjoittaa
(*Virtualisointi*).

## Välimuistit ja yhtenäisyys

Pikku-SoC:ssa ei ole välimuisteja, joten ydin ja DMA näkevät saman
muistin. Välimuistillisessa järjestelmässä ohjelmiston on huolehdittava
yhtenäisyydestä (coherence):

- **Ennen kuin DMA lukee** puskurin, ytimen kirjoitukset on vietävä
  välimuistista muistiin (clean, writeback).
- **Ennen kuin ydin lukee** DMA:n kirjoittaman puskurin, puskurin
  rivit on mitätöitävä välimuistista (invalidate), jotta ydin ei lue
  vanhaa kopiota.

Koherentissa järjestelmässä laitteisto tekee tämän: DMA:n siirrot
kulkevat välimuistin kautta tai nuuskivat (snoop) välimuisteja
(Armin ACE-Lite, CHI). Ohjelmisto tarvitsee silloinkin muistiesteet,
jotta kirjoitukset ovat näkyvissä ennen DMA:n käynnistystä.

## Kehittyneet DMA-ohjaimet

Tuotantolaatuisissa DMA-ohjaimissa on lisäksi:

- **Kuvaajat (descriptors).** Siirrot kuvataan muistissa olevana
  ketjuna; DMA hakee kuvaajat itse. Hajautettu siirto (scatter-gather)
  kokoaa paketin useista puskureista ilman kopiointia.
- **Oheislaitekättely.** DMA siirtää dataa oheislaitteen tahdissa:
  UART pyytää uutta tavua, kun lähetyspuskurissa on tilaa.
- **Kanavat ja prioriteetit.** Useita samanaikaisia siirtoja, joista
  reaaliaikaiset saavat etusijan.
- **Kaksiulotteiset siirrot.** Kuvan suorakulmio siirretään
  rivinpituuden ja askeleen (stride) avulla.

## Käytännössä

- **DMA suurille siirroille.** Muutaman sanan kopiointi on nopeampaa
  suorittimella kuin DMA:n ohjelmointi ja keskeytys. Raja mitataan
  järjestelmästä.
- **Purskeet ja avoimet siirrot.** DMA:n suorituskyky tulee siitä,
  että se pitää väylän täynnä. AXI4-Lite-DMA on opetusmalli; oikea DMA
  käyttää purskeita ja jonottaa pyyntöjä.
- **Puskurit tasattuina.** Välimuistirivin mukaan tasattu puskuri
  välttää osittaiset rivit, joiden mitätöinti tuhoaisi viereisen datan.
- **Valmis vai virhe, aina.** Siirto päättyy joko valmiiseen tai
  virheeseen, ja kumpikin kuitataan. Ajuri, joka odottaa vain
  valmis-bittiä, jumittuu ensimmäiseen väylävirheeseen.
- **Rajaa DMA:n näkymä.** IOMMU tai väylän palomuuri estää viallista
  tai vihamielistä laitetta kirjoittamasta mihin tahansa muistiin.

## Itsearviointi

- Osaat selittää, miksi DMA-ohjain on sekä väyläorja että väyläisäntä.
- Osaat ohjelmoida DMA-siirron ja käsitellä sen valmis- ja
  virhekeskeytyksen.
- Osaat kertoa, mistä DMA:n suorituskyky tulee (purskeet, avoimet
  siirrot, väylän jakaminen) ja miksi Pikku-SoC:n DMA on hidas.
- Osaat selittää välimuistien ja DMA:n yhtenäisyysongelman ja
  sen ratkaisut ohjelmistolla ja laitteistolla.
- Osaat kuvata kuvaajapohjaisen ja hajautetun DMA-siirron idean.
