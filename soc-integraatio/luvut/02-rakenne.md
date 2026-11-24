# SoC:n rakenne

Järjestelmäpiirin lohkot jaetaan kahteen rooliin. *Isäntä* (manager,
vanhemmissa dokumenteissa master) aloittaa siirtoja: suoritinydin hakee
käskyjä ja lukee dataa, DMA-ohjain kopioi muistia, näytönohjain lukee
kehyspuskuria. *Orja* (subordinate, vanhemmin slave) vastaa siirtoihin:
muistit ja oheislaitteiden rekisterit. Väylä tai kytkentäverkko kuljettaa
siirrot isännältä oikealle orjalle osoitteen perusteella.

## Pikku-SoC:n lohkokaavio

```{.dot otsikko="Pikku-SoC:n lohkokaavio. Yhtenäiset nuolet ovat väyliä isännältä orjalle, katkoviivat keskeytysjohtoja."}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.4;
  ydin; silta; dma_m [label="DMA\n(AXI-isäntä)"];
  kytkin [label="kytkin\n(AXI4-Lite)"];
  ram [label="RAM\n16 KiB"]; apb [label="APB-silta"];
  uart [label="UART"]; syscon [label="SYSCON"]; gpio [label="GPIO"];
  dma_r [label="DMA:n\nrekisterit"]; clint [label="CLINT"]; plic [label="PLIC"];
  ydin -> silta; silta -> kytkin [label="AXI4-Lite"]; dma_m -> kytkin;
  kytkin -> ram; kytkin -> apb;
  apb -> uart; apb -> syscon; apb -> gpio; apb -> dma_r; apb -> clint;
  apb -> plic [label="APB"];
  edge [style=dashed, constraint=false];
  gpio -> plic; dma_r -> plic;
  clint -> ydin [label="MTIP"]; plic -> ydin [label="MEIP"];
}
```

Kaaviossa näkyy kolme järjestelmäpiirien yleistä piirrettä:

- **Väylähierarkia.** Nopea väylä (AXI) yhdistää isännät ja muistin;
  hitaat oheislaitteet ovat yksinkertaisemman väylän (APB) takana
  sillan kautta. Oheislaitteen ei tarvitse toteuttaa nopean väylän
  monimutkaista protokollaa, ja sillan takana oleva logiikka voi käydä
  hitaammalla kellolla.
- **Sama lohko on sekä isäntä että orja.** DMA-ohjain on APB-orja, kun
  ohjelmisto ohjelmoi sen rekisterit, ja AXI-isäntä, kun se kopioi
  dataa.
- **Keskeytykset kulkevat väylien ohi.** Ne ovat erillisiä johtoja
  oheislaitteilta keskeytysohjaimelle ja siitä ytimelle.

## Muistikartta

Kaikki ohjelmiston näkemät resurssit ovat yhdessä 32-bittisessä
osoiteavaruudessa. Ohjelmiston näkökulmasta muistikartta on sopimus,
joka kirjoitetaan otsakkeeseen:

```{.c tiedosto="esimerkit/sw/soc.h" osa="kartta"}
```

| Alue | Koko | Väylä | Sisältö |
|------|------|-------|---------|
| `0x0000_0000` | 16 KiB | AXI | RAM: käynnistysosoite 0 |
| `0x1000_0000` | 4 KiB | APB | UART |
| `0x1000_1000` | 4 KiB | APB | SYSCON |
| `0x1000_2000` | 4 KiB | APB | GPIO |
| `0x1000_3000` | 4 KiB | APB | DMA:n rekisterit |
| `0x1000_4000` | 4 KiB | APB | CLINT |
| `0x1000_5000` | 4 KiB | APB | PLIC |
| muu | – | – | väylävirhe (DECERR) |

Jokaiselle oheislaitteelle on varattu 4 KiB:n ikkuna, vaikka se
käyttäisi vain muutaman rekisterin. Tasakokoiset ja tasattuihin
osoitteisiin sijoitetut ikkunat tekevät dekoodauksesta halvan
(osoitteen ylimmät bitit valitsevat laitteen) ja sopivat
muistinsuojaukseen: MMU:n ja PMP:n pienin suojattava yksikkö on
tyypillisesti 4 KiB:n sivu, joten jokaisen laitteen voi antaa eri
ohjelmalle.

RISC-V-järjestelmissä CLINT on usein osoitteessa `0x0200_0000` ja PLIC
osoitteessa `0x0C00_0000`, koska QEMU:n `virt`-kone ja monet
SiFive-piirit käyttävät niitä. Osoitteet eivät kuitenkaan ole
standardin määräämiä: ohjelmisto saa ne laitepuusta (device tree) tai
otsakkeesta. Pikku-SoC kokoaa kaikki oheislaitteet yhdelle APB-alueelle,
jotta väylärakenne pysyy yksinkertaisena.

## Kokoaminen ylimmällä tasolla

Ylimmän tason moduuli `soc.sv` sisältää vain kytkentöjä. Väylät ovat
rakennetyyppejä (luku 4), joten jokainen liitäntä on kaksi signaalia:
isännältä orjalle ja orjalta isännälle.

```{.systemverilog tiedosto="esimerkit/rtl/soc.sv" osa="kytkenta"}
```

Kytkimen parametrit `KANTA` ja `MASKI` ovat laitteiston puolen
muistikartta: orja *i* vastaa osoitteeseen, jolle
`(osoite & MASKI[i]) == KANTA[i]`. Ohjelmiston otsakkeen ja laitteiston
parametrien on oltava yhtäpitäviä. Pienessä piirissä ne pidetään
yhtäpitävinä käsin; suuressa molemmat generoidaan samasta kuvauksesta
(luku 8).

Oheislaitteet kytketään APB-sillan liitäntöihin. Keskeytyslähdöt
kootaan PLICin lähdevektoriin:

```{.systemverilog tiedosto="esimerkit/rtl/soc.sv" osa="oheislaitteet"}
```

## Kellot ja nollaukset

Pikku-SoC:ssa on yksi kello ja yksi nollaus, joten kaikki lohkot ovat
samassa kellotus- ja nollausalueessa. Oikeassa SoC:ssa on lähes aina
*kello- ja nollausyksikkö* (clock and reset unit, CRU):

- **Kellot.** Vaihelukittu silmukka (PLL) tuottaa nopeat kellot
  kidekellosta. Jakajat ja kellojen portitus tuottavat hitaammat ja
  sammutettavat kellot. Ohjelmisto valitsee taajuudet rekistereillä.
- **Nollaukset.** Ulkoinen nollausnasta, virransyötön valvonta
  (power-on reset, brown-out) ja vahtikoira (watchdog) tuottavat
  nollauksia, jotka tahdistetaan jokaiseen kellotusalueeseen ja
  vapautetaan sovitussa järjestyksessä.

Luku 11 käsittelee kello-, nollaus- ja tehoalueet.

## Käynnistys

Nollauksen jälkeen ydin hakee ensimmäisen käskyn *nollausvektorista*.
Pikku-SoC:ssa se on osoite 0 eli RAMin alku, ja testipenkki lataa
ohjelman RAMiin ennen nollauksen vapauttamista. Oikeassa piirissä RAM
on käynnistyksessä tyhjä, joten nollausvektori osoittaa *käynnistys-ROMiin*
(boot ROM). Sen koodi alustaa kellot ja muistiohjaimen ja lataa
seuraavan vaiheen flash-muistista, SD-kortilta tai sarjaportista. Monen
piirin käynnistys-ROM myös tarkistaa ladattavan koodin allekirjoituksen
(*Sulautettujen järjestelmien tietoturva*).

## Käytännössä

- **Muistikartta on rajapinta.** Se kirjoitetaan, katselmoidaan ja
  versioidaan kuten ohjelmointirajapinta. Osoitteen muuttaminen
  julkaisun jälkeen rikkoo ajurit, käynnistyskoodin ja laitepuut, joten
  ikkunoihin jätetään tilaa kasvulle.
- **Tyhjä osoite antaa virheen.** Kartoittamaton osoite vastaa
  väylävirheellä eikä palauta nollaa tai jonkin toisen laitteen arvoa.
  Ohjelmointivirhe paljastuu silloin heti eikä viikkoja myöhemmin
  outona käytöksenä (luku 12).
- **Hitaat laitteet sillan taakse.** Nopean väylän kaistaa ja
  ajoitusta ei tuhlata rekistereihin, joita luetaan harvoin. Sillan
  hinta on muutaman jakson lisäviive, joka rekisterikäytössä ei
  merkitse mitään.
- **Ylin taso on vain kytkentöjä.** Kun `soc.sv` sisältää pelkät
  instanssit ja johdot, sen voi generoida kuvauksesta, ja
  integrointivirheet (väärä keskeytyslinja, väärä osoite) on helppo
  tarkistaa katselmoinnissa.
- **Laskelma ennen kokoamista.** Muistikartan, väylien kaistan ja
  keskeytysten määrän voi arvioida taulukkolaskelmalla ennen yhtään
  RTL-riviä. Integrointivaiheessa korjattu virhe maksaa vähän, piissä
  korjattu paljon.

## Itsearviointi

- Osaat selittää isännän ja orjan roolit ja nimetä kummastakin
  esimerkkejä.
- Osaat perustella väylähierarkian: miksi oheislaitteet ovat sillan
  takana.
- Osaat lukea muistikartan ja kertoa, mihin laitteeseen annettu
  osoite kuuluu.
- Osaat kertoa, mistä ydin hakee ensimmäisen käskyn ja mitä
  käynnistys-ROM tekee.
- Osaat selittää, miksi kartoittamattomaan osoitteeseen pitää vastata
  virheellä.
