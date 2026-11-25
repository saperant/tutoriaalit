# DMA ytimessä

DMA:ssa laite lukee ja kirjoittaa järjestelmän muistia itse, ilman että
CPU kopioi jokaisen tavun. *Oheislaiteväylät*-tutoriaalin bare-metal-
ohjelmassa DMA-ohjaimelle annettiin suoraan muistiosoite. Linuxissa se
ei riitä, koska laitteen näkemä osoite ei välttämättä ole sama kuin
CPU:n:

- **Virtuaali- ja fyysinen osoite.** Ytimen osoitin on virtuaalinen,
  laite tarvitsee väyläosoitteen.
- **IOMMU.** Monessa järjestelmäpiirissä laitteen ja muistin välissä on
  oma muistinhallintayksikkö (Arm SMMU, Intel VT-d), joka kuvaa
  laitteen osoitteet muistiin ja estää laitetta koskemasta muuhun.
- **Osoitteen leveys.** Vanha tai yksinkertainen laite osaa ehkä vain
  32-bittisiä osoitteita, jolloin puskurin on oltava muistin alussa.
- **Välimuistit.** Jos laite ei ole koherentti, CPU:n välimuistissa voi
  olla vanha kopio datasta, jonka laite on kirjoittanut muistiin.

DMA-rajapinta (`linux/dma-mapping.h`) hoitaa nämä kaikki. Ajuri pyytää
puskurille *DMA-osoitteen* (`dma_addr_t`), antaa sen laitteelle ja
noudattaa sääntöjä siitä, milloin puskuri kuuluu CPU:lle ja milloin
laitteelle.

## Laite: fw_cfg

QEMU:n fw_cfg-laite välittää vieraalle tietoa isännältä: laitepuun,
käynnistysjärjestyksen ja mitä tahansa tiedostoja, jotka annetaan
valitsimella `-fw_cfg`. Laitteessa on DMA-rajapinta: ajuri kirjoittaa
muistiin ohjausrakenteen ja rakenteen osoitteen laitteen rekisteriin,
ja laite kopioi pyydetyn tiedoston vieraan muistiin.

```{.make tiedosto="esimerkit/Makefile" osa="fwcfg"}
```

```{.c tiedosto="esimerkit/04-dma/fwcfg.c" osa="rajapinta"}
```

Laitteen kentät ovat isoa tavujärjestystä. Tyypit `__be32` ja `__be64`
merkitsevät sen, ja `sparse` varoittaa, jos arvo kirjoitetaan ilman
muunnosta `cpu_to_be32`.

## DMA-maski

Ensimmäiseksi ajuri kertoo, kuinka leveitä osoitteita laite osaa:

```{.c tiedosto="esimerkit/04-dma/fwcfg.c" osa="probe"}
```

Oletusmaski on 32 bittiä. Jos laite osaa vähemmän, ydin varaa puskurit
sen ulottuville tai kopioi datan välipuskurin kautta (*SWIOTLB*,
*bounce buffer*), mikä on hidasta. Liian suuri maski on vaarallinen:
laite kirjoittaa osoitteen yläbitit pois ja väärään muistiin.

## Koherentti muisti

`dma_alloc_coherent` varaa puskurin, jota CPU ja laite voivat käyttää
yhtä aikaa ilman erillistä synkronointia. Ytimen ja laitteen näkemät
osoitteet palautetaan erikseen. Laitteen ohjausrakenteet, kuvaajarenkaat
ja tilalohkot sijoitetaan koherenttiin muistiin, koska kumpikin osapuoli
lukee ja kirjoittaa niitä jatkuvasti.

```{.c tiedosto="esimerkit/04-dma/fwcfg.c" osa="siirto"}
```

Siirto käynnistyy, kun rakenteen osoitteen alempi puolisko kirjoitetaan
rekisteriin. Rakenteen kenttien on näyttävä laitteelle sitä ennen.
`writel` (jota `iowrite32be` käyttää) takaa sen muistiesteellä, joten
ajurin ei tarvitse lisätä omaa `wmb`-kutsua. QEMU suorittaa siirron
heti ja kirjoittaa ohjauskenttään nollan; oikea laite ilmoittaisi
valmistumisesta keskeytyksellä. Silmukka tarkistaa kentän ja luovuttaa
aikarajan jälkeen, koska ajuri ei saa jäädä odottamaan laitetta
ikuisesti.

Hakemisto, josta tiedoston valitsin etsitään, luetaan väliaikaiseen
koherenttiin puskuriin:

```{.c tiedosto="esimerkit/04-dma/fwcfg.c" osa="etsi"}
```

`dmam_alloc_coherent` (ohjausrakenne) on hallittu versio, jonka ydin
vapauttaa itse; väliaikainen puskuri vapautetaan heti käytön jälkeen.

## Virtauskuvaus

Tiedoston sisältö luetaan tavalliseen `kmalloc`-puskuriin
*virtauskuvauksella* (*streaming mapping*):

```{.c tiedosto="esimerkit/04-dma/fwcfg.c" osa="lue"}
```

Virtauskuvaus on yksisuuntainen ja lyhytaikainen: `dma_map_single`
luovuttaa puskurin laitteelle, ja vasta `dma_unmap_single` palauttaa
sen CPU:lle.

```{.ajoituskaavio otsikko="Puskurin omistus virtauskuvauksessa (periaatekuva). Ajuri ei koske puskuriin sinä aikana, kun se kuuluu laitteelle."}
{"signal": [
  {"name": "ajurin kutsu", "wave": "=..=....=...",
   "data": ["kmalloc", "dma_map_single", "dma_unmap_single"]},
  {"name": "puskurin omistaja", "wave": "=..=....=...",
   "data": ["CPU", "laite", "CPU"]},
  {"name": "laitteen siirto", "wave": "0....1.0...."}
]}
```
 Suunta (`DMA_TO_DEVICE`, `DMA_FROM_DEVICE`,
`DMA_BIDIRECTIONAL`) kertoo ytimelle, mitä välimuistille on tehtävä:

| Suunta | Kuvattaessa | Purettaessa |
|--------------------|--------------------------------|---------------------|
| `DMA_TO_DEVICE` | CPU:n kirjoitukset kirjoitetaan välimuistista muistiin | ei mitään |
| `DMA_FROM_DEVICE` | välimuistin rivit mitätöidään | rivit mitätöidään uudelleen |
| `DMA_BIDIRECTIONAL` | molemmat | molemmat |

Jos puskuria käytetään pitkään, kuvaus voi pysyä voimassa, ja omistus
siirretään funktioilla `dma_sync_single_for_cpu` ja
`dma_sync_single_for_device`. Moneen sivuun hajallaan oleva puskuri
kuvataan kerralla hajautusluettelona (`dma_map_sg`). Koherentti muisti
sopii pysyville ohjausrakenteille, virtauskuvaus datalle, joka kulkee
kerran laitteelle tai laitteelta.

## Välimuistin koherenssi ARM64:ssä

x86:ssa laitteet ovat lähes aina koherentteja: väylä tarkkailee CPU:n
välimuisteja. ARM-järjestelmäpiireissä koherenssi riippuu siitä, miten
laite on kytketty. Laitepuun ominaisuus `dma-coherent` kertoo, että
laite on koherentti, jolloin DMA-rajapinta jättää välimuistitoimet
pois:

```{.text tiedosto="esimerkit/04-dma/dma.vaiheet" osa="vaiheet"}
```

```{.tuloste tiedosto="esimerkit/testit/04-dma.odotettu" osa="vaiheet"}
```

QEMU:n fw_cfg on koherentti. Ei-koherentilla laitteella sama ajuri
toimisi muuttamatta, koska se noudattaa omistussääntöjä: dataa ei
lueta ennen `dma_unmap_single`-kutsua. Jos ajuri lukisi puskuria
kesken kuvauksen, koherentilla laitteella vika ei näkyisi lainkaan,
mutta ei-koherentilla CPU lukisi välimuistista vanhaa dataa. Siksi
koherentilla laitteella testattu ajuri voi silti olla väärin.

Toinen lataus pyytää tiedostoa, jota ei ole. `probe` epäonnistuu, mutta
moduuli latautuu: lataus ja sidonta ovat eri asioita, ja epäonnistunut
`probe` jättää vain lokirivin ja laitteen ilman ajuria.

## dmaengine

Oikeassa järjestelmäpiirissä DMA:n tekee usein erillinen DMA-ohjain,
kuten *Oheislaiteväylät*-tutoriaalin PL081. Linuxissa sen ajuri on
`dmaengine`-palvelu: SPI- tai UART-ajuri pyytää kanavan
(`dma_request_chan`), valmistelee siirron (`dmaengine_prep_slave_sg`)
ja saa takaisinkutsun, kun siirto valmistuu. Laitepuussa asiakaslaite
nimeää kanavansa ominaisuuksilla `dmas` ja `dma-names`. Asiakasajurin
ei tarvitse tuntea DMA-ohjaimen rekistereitä, ja sama ajuri toimii
eri piirien DMA-ohjaimilla.

## Käytännössä

- **Aseta DMA-maski `probe`-funktion alussa.** Laitteen todellinen
  osoiteleveys kuuluu laitteen tietoihin; älä oleta 64:ää bittiä.
- **Käytä koherenttia muistia ohjausrakenteille ja virtauskuvausta
  datalle.** Koherentti muisti voi olla ARM:ssä välimuistiton ja siksi
  hidas CPU:lle.
- **Noudata omistusta.** Puskuria ei kosketa kuvauksen ja purun välillä,
  ellei omistusta siirretä `dma_sync_*`-funktioilla.
- **Tarkista `dma_mapping_error`.** Kuvaus voi epäonnistua, kun IOMMU:n
  tai välipuskurin tila loppuu.
- **Älä käytä pinon muistia DMA:han.** Pino voi olla `vmalloc`-muistia,
  jota ei voi kuvata, ja se jakaa välimuistirivejä muun datan kanssa.

## Itsearviointi

- Osaat selittää, miksi laite tarvitsee DMA-osoitteen eikä ytimen
  osoitinta, ja mitä IOMMU ja DMA-maski vaikuttavat siihen.
- Osaat varata koherentin puskurin ja käyttää virtauskuvausta oikealla
  suunnalla ja oikeassa järjestyksessä.
- Osaat selittää välimuistin koherenssin ARM64:ssä ja laitepuun
  `dma-coherent`-ominaisuuden merkityksen.
- Osaat kertoa, milloin ajuri käyttää `dmaengine`-palvelua oman
  DMA-koodin sijaan.
