# Digitaalinen kuva

Ohjelman näkökulmasta kuva on taulukko lukuja. Harmaasävykuva on
kaksiulotteinen taulukko, jonka alkio on pikselin kirkkaus, ja värikuvassa
on lisäksi kolmas ulottuvuus kanaville. OpenCV:n Python-rajapinta
käyttää kuvina suoraan NumPy-taulukoita, joten kaikki taidon *Python
työkaluohjelmointiin* NumPy-tekniikat toimivat sellaisinaan. Tässä
luvussa käydään läpi taulukon rakenne ja sen sudenkuopat, väriavaruudet,
histogrammit ja kynnystys.

## Kuva taulukkona

Kuvan muoto on `(korkeus, leveys)` tai värikuvalla
`(korkeus, leveys, kanavat)`, ja tavallisin alkiotyyppi on `uint8`
(0–255). Indeksointi on rivi ensin, eli `kuva[y, x]`. OpenCV:n
piirtofunktiot ja muut pisteitä käsittelevät funktiot ottavat pisteet
sen sijaan muodossa `(x, y)`.

```{.python tiedosto="esimerkit/02-taulukko.py" osa="muoto"}
```

Viipale `kuva[20:50, 40:100]` on **näkymä**: se jakaa muistin kuvan
kanssa, joten sen muuttaminen muuttaa kuvaa. Näkymä on halpa tapa
käsitellä kuvan osaa (*region of interest*, ROI), mutta jos osaa
halutaan muokata koskematta alkuperäiseen, tarvitaan `copy()`.

```{.python tiedosto="esimerkit/02-taulukko.py" osa="nakyma"}
```

## Bittisyvyys ja ylivuoto

Kahdeksan bitin pikseli riittää näyttämiseen, mutta laskenta sillä on
vaarallista. NumPyn `uint8`-aritmetiikka kiertää modulo 256:
$200 + 100 = 44$. OpenCV:n funktiot `add` ja `subtract` **saturoivat**:
tulos leikataan välille 0–255, mikä on kuvalle yleensä oikea
käyttäytyminen.

```{.python tiedosto="esimerkit/02-taulukko.py" osa="ylivuoto"}
```

```{.tuloste tiedosto="esimerkit/02-taulukko.odotettu"}
```

Vähennyslasku näyttää ongelman pahimmillaan: $100 - 200$ antaa NumPylla
156 eli kirkkaan pikselin, vaikka tulos on negatiivinen. Kuvien erotus,
gradientti ja kaikki muu, mikä voi mennä negatiiviseksi, lasketaan
etumerkillisillä kokonaisluvuilla tai liukuluvuilla (`float32`).
Luvussa 4 sama virhe tulee vastaan Sobel-suotimen tulostyypissä.

Kamerat tuottavat myös 10-, 12- ja 16-bittisiä kuvia (`uint16`), ja
lääketieteessä ja tähtitieteessä käytetään liukulukukuvia. OpenCV:n
funktiot tukevat useimpia tyyppejä, mutta eivät kaikkia: dokumentaatio
kertoo funktiokohtaisesti, mitkä syvyydet kelpaavat.

## Värit ja väriavaruudet

OpenCV tallentaa värikuvan kanavat järjestyksessä **B, G, R**. Järjestys
on historiallinen jäänne, mutta se on edelleen oletus kaikkialla
OpenCV:ssä. Matplotlib, kuvatiedostokirjastot ja neuroverkot odottavat
yleensä järjestystä R, G, B. Kun RGB-taulukko annetaan OpenCV:lle
BGR:nä, punainen tulkitaan siniseksi.

```{.python tiedosto="esimerkit/02-varit.py" osa="bgr"}
```

Sävy 120 on OpenCV:n HSV:ssä sininen ja 0 punainen. OpenCV tallentaa
8-bittisen kuvan sävyn välille 0–179 eli puoliksi asteina, jotta se
mahtuu tavuun.

**HSV** (*hue, saturation, value*) erottaa sävyn kirkkaudesta. Siksi
värin perusteella tehty kynnystys toimii HSV:ssä myös silloin, kun
valaistus vaihtelee. Seuraavassa kuvassa varjo tummentaa oikeaa reunaa.
HSV-rajat löytävät molemmat punaiset kappaleet, kiinteät BGR-rajat vain
valoisan puolen kappaleen. Punainen on sävyasteikon molemmissa päissä,
joten se tarvitsee kaksi väliä.

```{.python tiedosto="esimerkit/02-varit.py" osa="hsv"}
```

**Lab** (CIELAB) on suunniteltu niin, että euklidinen etäisyys vastaa
suunnilleen havaittua värieroa. Kaksi väriparia, joiden BGR-etäisyys on
sama, voivat näyttää silmälle eri tavoin erilaisilta. Lab on oikea
avaruus, kun värejä verrataan, ryhmitellään tai kun värien eron pitää
olla havaittavissa.

```{.python tiedosto="esimerkit/02-varit.py" osa="lab"}
```

```{.tuloste tiedosto="esimerkit/02-varit.odotettu"}
```

## Histogrammit ja kontrasti

Histogrammi kertoo, kuinka monta pikseliä kullakin harmaasävyllä on.
Matalakontrastisessa kuvassa arvot ovat kapealla välillä, ja kuva
näyttää harmaalta sumulta. Seuraavassa kuvassa arvot ovat välillä
82–154.

```{.python tiedosto="esimerkit/02-histogrammi.py" osa="kuva"}
```

Kontrastia parannetaan kolmella tavalla. **Venytys** (`normalize`)
kuvaa pienimmän arvon nollaksi ja suurimman 255:ksi lineaarisesti.
**Histogrammin tasoitus** (`equalizeHist`) levittää arvot niin, että
histogrammista tulee mahdollisimman tasainen; se korostaa kontrastia
voimakkaasti ja voi yhdistää lähekkäisiä tasoja. **CLAHE** (*contrast
limited adaptive histogram equalization*) tasoittaa histogrammin
paikallisesti pienissä ruuduissa ja rajoittaa vahvistusta, jotta kohina
ei korostu. Se on hyvä oletus, kun valaistus vaihtelee kuvan eri osissa.

```{.python tiedosto="esimerkit/02-histogrammi.py" osa="venytys"}
```

**Gammakorjaus** muuttaa arvoja epälineaarisesti:
$I' = 255\,(I/255)^{1/\gamma}$. Kun $\gamma > 1$, tummat sävyt
vaalenevat. Näyttöjen ja kuvatiedostojen sRGB-koodaus on lähes
gammakorjaus kertoimella 2,2. Siksi pikseliarvot eivät ole
lineaarisessa suhteessa valon määrään. Valon fysiikkaa laskettaessa
(esimerkiksi kuvien keskiarvoa tai sumennusta) arvot pitäisi ensin
muuntaa lineaarisiksi. Taito *Renderöinnin perusteet* käsittelee
sRGB:n tarkemmin.

Kaikkia pikseleitä koskeva muunnos tehdään nopeimmin
**hakutaulukolla**: 256 tulosta lasketaan kerran, ja `LUT` hakee jokaisen
pikselin tuloksen taulukosta.

```{.python tiedosto="esimerkit/02-histogrammi.py" osa="gamma"}
```

```{.tuloste tiedosto="esimerkit/02-histogrammi.odotettu"}
```

Venytys ei muuta tasojen määrää (71), koska se vain siirtää arvoja.
Tasoitus yhdistää osan tasoista (62). CLAHE nostaa paikallista kontrastia
mutta pitää kokonaisvaihtelun maltillisena.

## Kynnystys

Kynnystys jakaa pikselit kahteen luokkaan: kohteeseen ja taustaan.
Kiinteä kynnys toimii vain, jos valaistus on tasainen ja tunnettu.
**Otsun menetelmä** valitsee kynnyksen histogrammista niin, että
luokkien sisäinen varianssi on pienin. Se toimii, kun histogrammissa on
kaksi selvää huippua.

Kun valaistus vaihtelee kuvan sisällä, yksikään yhteinen kynnys ei toimi.
Seuraavassa kuvassa valaistus heikkenee oikealle niin paljon, että
oikean reunan paperi on tummempaa kuin vasemman reunan teksti.
**Adaptiivinen kynnystys** laskee jokaiselle pikselille oman kynnyksen
sen ympäristön painotetusta keskiarvosta.

```{.python tiedosto="esimerkit/02-kynnystys.py" osa="kuva"}
```

```{.python tiedosto="esimerkit/02-kynnystys.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/02-kynnystys.odotettu"}
```

![Epätasaisesti valaistu teksti, Otsun kynnystys ja adaptiivinen
kynnystys. Otsu valitsee yhden kynnyksen koko kuvalle, ja oikea reuna
peittyy.](kuvat/kynnystys.png){width=100%}

Koska kuva on synteettinen, oikea tulos tunnetaan pikseleittäin, ja
menetelmät voidaan asettaa järjestykseen yhdellä luvulla. Oikeassa
sovelluksessa samaan päästään käsin merkityillä testikuvilla: muutama
huolella merkitty kuva on arvokkaampi kuin sata silmämääräistä
tarkistusta.

## Käytännössä

- **Pidä koordinaattijärjestys mielessä.** NumPy indeksoi `[y, x]`,
  OpenCV:n pisteet ovat `(x, y)`, ja kuvan koko annetaan OpenCV:lle
  muodossa `(leveys, korkeus)` mutta NumPyn `shape` on
  `(korkeus, leveys)`. Nimeä muuttujat niin, että järjestys näkyy.
- **Muunna värijärjestys rajapinnassa.** Kun kuva tulee OpenCV:stä
  muualle tai muualta OpenCV:hen, tee muunnos heti rajalla
  (`cvtColor(..., COLOR_BGR2RGB)`) ja kirjaa järjestys funktion
  dokumentaatioon.
- **Laske liukuluvuilla, tallenna kokonaisluvuin.** Muunna
  `float32`:ksi ennen aritmetiikkaa ja takaisin `uint8`:ksi
  `np.clip`:n kautta. Kiertävä ylivuoto on hiljainen virhe, joka
  näkyy vain kuvassa.
- **Kynnystä HSV:ssä, vertaa Labissa.** Värin perusteella tehty
  rajaus kestää valaistuksen vaihtelua HSV:ssä, ja Lab antaa värieroille
  havaintoa vastaavan mitan.
- **Valitse kynnystys valaistuksen mukaan.** Tasainen valaistus:
  Otsu. Vaihteleva valaistus: adaptiivinen kynnystys tai valaistuksen
  korjaus ennen kynnystystä. Kiinteä kynnys vain hallituissa
  olosuhteissa, kuten teollisuuden taustavalossa.

## Itsearviointi

- Osaat indeksoida kuvaa NumPylla, erottaa näkymän kopiosta ja selittää,
  miksi `(x, y)` ja `[y, x]` sekoittuvat.
- Osaat selittää, miten NumPyn ja OpenCV:n `uint8`-aritmetiikka eroavat,
  ja laskea kuvia turvallisesti liukuluvuilla.
- Osaat muuntaa kuvan BGR-, RGB-, HSV- ja Lab-avaruuksien välillä ja
  valita avaruuden tehtävän mukaan.
- Osaat parantaa kontrastia venytyksellä, histogrammin tasoituksella,
  CLAHE:lla ja gammakorjauksella hakutaulukon avulla.
- Osaat valita kiinteän, Otsun ja adaptiivisen kynnystyksen välillä ja
  mitata kynnystyksen virheen tunnettua tulosta vasten.
