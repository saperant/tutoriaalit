# GPU:n arkkitehtuuri

CPU on suunniteltu suorittamaan yksi säie mahdollisimman nopeasti:
isot välimuistit, haarautumisen ennustus ja käskyjen uudelleenjärjestely
piilottavat muistin viiveen. GPU on suunniteltu suorittamaan
valtava määrä säikeitä mahdollisimman suurella läpäisyllä. Yksittäinen
säie on hidas, mutta niitä on kymmeniätuhansia yhtä aikaa, ja kun
yksi odottaa muistia, toinen laskee.

## SIMT: sama käsky monelle säikeelle

GPU:n laskentayksikkö (NVIDIA: SM, AMD: CU, Intel: Xe-ydin) suorittaa
säikeitä ryhminä. Ryhmän nimi on NVIDIAlla *warp* (32 säiettä) ja
AMD:llä *aalto* (wavefront, 32 tai 64). Ryhmän kaikki säikeet
suorittavat samaa käskyä samaan aikaan omilla datoillaan. Mallin nimi
on SIMT (single instruction, multiple threads).

Varjostin kirjoitetaan yhden säikeen näkökulmasta, ja laitteisto
niputtaa säikeet ryhmiksi. Esimerkiksi fragmenttivarjostimessa
naapuripikselit (2×2-ryhmät) päätyvät samaan warppiin.

Ehtolause on ongelma: jos osa ryhmän säikeistä menee then-haaraan ja
osa else-haaraan, ryhmä suorittaa *molemmat* haarat peräkkäin ja
maskaa tulokset. Seuraava malli simuloi tätä CPU:lla:

```{.cpp tiedosto="esimerkit/02-simt.cpp" osa="malli"}
```

```{.cpp tiedosto="esimerkit/02-simt.cpp" osa="kokeet"}
```

```{.tuloste tiedosto="esimerkit/02-simt.odotettu"}
```

Kun ehto noudattaa ryhmän rajaa (`i < 32`), kumpikin ryhmä suorittaa
vain toisen haaran. Kun yksikin säie poikkeaa (`i != 7`), koko ryhmä
maksaa molemmat haarat. Haarautuminen ei siis ole sinänsä kallista;
kallista on *hajoava* haarautuminen (divergence) ryhmän sisällä.

## Muistihierarkia

| Taso | Koko (suuruusluokka) | Viive | Näkyy |
|------|----------------------|-------|-------|
| rekisterit | 64–256 kt / laskentayksikkö | 1 sykli | säikeelle |
| jaettu muisti / LDS | 64–228 kt / laskentayksikkö | ~20–30 sykliä | työryhmälle (laskentavarjostimet) |
| L1 ja tekstuurivälimuisti | 64–256 kt / laskentayksikkö | ~30–100 sykliä | laskentayksikölle |
| L2 | 4–100 Mt | ~200 sykliä | koko piirille |
| VRAM (GDDR, HBM) | 8–192 Gt | 400–800 sykliä | koko piirille ja CPU:lle siirtojen kautta |

Viive piilotetaan *rinnakkaisuudella*: laskentayksikössä on samaan
aikaan elossa kymmeniä warppeja, ja kun yksi odottaa muistia,
ajoitin vaihtaa toiseen ilman kustannusta. Siksi rekisterien määrä
varjostinta kohden on tärkeä: mitä enemmän rekisterejä yksi säie
käyttää, sitä vähemmän warppeja mahtuu yksikköön (occupancy) ja sitä
huonommin viive piiloutuu.

Muistin kaistanleveys (satoja gigatavuja tai teratavuja sekunnissa)
on silti usein pullonkaula. Grafiikassa kaistaa kuluttavat
tekstuurien luku, kehyspuskurin kirjoitus ja sekoitus. Luku 12
palaa tähän, ja taito *GPU-laskenta* käsittelee muistihierarkian
tarkemmin laskennan kannalta.

## Kiinteät yksiköt ja grafiikkaputki

Kaikki ei ole ohjelmoitavaa. Grafiikkaputken vaiheet kulkevat
laitteistossa seuraavasti:

1. **Syötteen kokoaminen** (kiinteä) lukee verteksit ja indeksit
   puskureista.
2. **Verteksivarjostin** (ohjelmoitava) muuntaa jokaisen verteksin
   leikkausavaruuteen ja laskee interpoloitavat arvot.
3. **Primitiivien kokoaminen, leikkaus ja perspektiivijako**
   (kiinteä).
4. **Rasterointi** (kiinteä) päättää, mitkä pikselit kolmio peittää,
   ja interpoloi verteksien arvot niille.
5. **Aikainen syvyystesti** (kiinteä, jos mahdollista) hylkää
   piilossa olevat fragmentit ennen varjostusta.
6. **Fragmenttivarjostin** (ohjelmoitava) laskee värin. Tekstuurit
   luetaan *tekstuuriyksiköllä*, joka tekee osoitteenlaskun ja
   suodatuksen laitteistossa.
7. **Syvyys- ja sapluunatesti, sekoitus ja kirjoitus** (kiinteä,
   ROP) kehyspuskuriin.

```{.dot otsikko="Grafiikkaputki laitteistossa. Tummemmat vaiheet ovat ohjelmoitavia varjostimia, muut kiinteitä yksiköitä, joita ohjataan asetuksilla."}
digraph {
  rankdir=LR; nodesep=0.2; ranksep=0.28;
  node [shape=box, style="rounded,filled", fillcolor="#EEF0F2"];
  ia [label="syötteen\nkokoaminen"];
  vs [label="verteksi-\nvarjostin", fillcolor="#C9CEEE"];
  pa [label="kokoaminen,\nleikkaus, jako"];
  ra [label="rasterointi"];
  ez [label="aikainen\nsyvyystesti"];
  fs [label="fragmentti-\nvarjostin", fillcolor="#C9CEEE"];
  rop [label="testit, sekoitus,\nkirjoitus"];
  tex [label="tekstuuri-\nyksikkö", shape=ellipse, fillcolor="#F4E6DA"];
  ia -> vs -> pa -> ra -> ez -> fs -> rop;
  tex -> fs [style=dashed];
}
```

Mobiili-GPU:t (ja osin työpöydänkin) renderöivät ruudun pieninä
*ruutuina* (tile-based): ruudun kolmiot lajitellaan ensin ruuduille,
ja kunkin ruudun väri- ja syvyyspuskuri pysyy piirin sisäisessä
muistissa. Silloin kaistaa säästää se, ettei välituloksia kirjoiteta
VRAMiin turhaan. Vulkanin `loadOp`- ja `storeOp`-asetukset (luku 8)
ovat olemassa juuri tätä varten.

## Käytännössä

- **Ajattele ryhmiä, älä säikeitä.** Haarautuminen säikeen datan
  perusteella hajottaa ryhmän. Jos ehto on sama koko piirrolle (esim.
  uniform-muuttuja), haarautuminen on halpaa, koska kaikki säikeet
  menevät samaan haaraan. Laskennassa data kannattaa järjestää niin,
  että samaa käsittelyä tarvitsevat alkiot ovat vierekkäin.
- **Viive piiloutuu vain, jos työtä on tarpeeksi.** Pieni piirto tai
  pieni laskenta ei täytä GPU:ta, ja silloin yksittäisen säikeen hitaus
  näkyy. GPU kannattaa vasta, kun rinnakkaista työtä on tuhansia
  yksiköitä.
- **Muistia luetaan yhtenäisinä lohkoina.** Kun ryhmän säikeet lukevat
  vierekkäisiä osoitteita, laitteisto yhdistää luvut (coalescing).
  Hajanaiset luvut kuluttavat kaistaa moninkertaisesti.
- **Kiinteät yksiköt ovat ilmaisia, kunhan niitä ei ohiteta.**
  Esimerkiksi `discard` tai syvyyden kirjoitus fragmenttivarjostimessa
  voi estää aikaisen syvyystestin (luku 12).

## Itsearviointi

- Osaat selittää SIMT-mallin ja sen, miksi hajoava haarautuminen
  ryhmän sisällä maksaa molemmat haarat.
- Osaat kuvata GPU:n muistihierarkian ja sen, miten viive piilotetaan
  rinnakkaisuudella ja miksi rekisterien määrä vaikuttaa siihen.
- Osaat luetella grafiikkaputken vaiheet ja kertoa, mitkä niistä ovat
  ohjelmoitavia ja mitkä kiinteitä.
- Osaat selittää ruutupohjaisen renderöinnin idean ja sen yhteyden
  kaistanleveyteen.
