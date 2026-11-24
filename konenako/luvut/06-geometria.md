# Geometriset muunnokset

Geometrinen muunnos siirtää pikseleitä paikasta toiseen: kiertää,
skaalaa, oikaisee perspektiivin tai kohdistaa kaksi kuvaa samaan
koordinaatistoon. Muunnokset esitetään homogeenisissa koordinaateissa
matriiseina (taito *Lineaarialgebra*), ja niiden ketjuttaminen on
matriisitulo. Tässä luvussa käydään läpi affiiniset muunnokset ja
homografia, homografian ratkaiseminen pisteistä, interpoloinnin
virheet ja panoraaman periaate.

## Muunnosten hierarkia

| Muunnos | Vapausasteet | Säilyttää | OpenCV |
|------------------------|-----------|------------------------|------------------------------|
| siirto | 2 | kaiken muun paitsi paikan | `warpAffine` |
| jäykkä (kierto + siirto) | 3 | pituudet, kulmat | `getRotationMatrix2D` |
| yhdenmuotoisuus (+ skaalaus) | 4 | kulmat, pituuksien suhteet | `estimateAffinePartial2D` |
| affiininen | 6 | yhdensuuntaisuus | `getAffineTransform`, `estimateAffine2D` |
| projektiivinen (homografia) | 8 | suorat viivat | `getPerspectiveTransform`, `findHomography` |

Affiininen muunnos on $2 \times 3$ -matriisi
$\begin{pmatrix} x' \\ y' \end{pmatrix} = A \begin{pmatrix} x \\ y \\ 1
\end{pmatrix}$, ja kolme pisteparia määrää sen yksikäsitteisesti.
Esimerkin muunnos on 30 asteen kierto ja siirto, ja sen
käänteismuunnos palauttaa pisteet.

```{.python tiedosto="esimerkit/06-muunnokset.py" osa="affiini"}
```

## Homografia

**Homografia** on $3 \times 3$ -matriisi $H$, joka kuvaa tason pisteet
toiselle tasolle: $(x', y', w')^{\mathsf T} = H\,(x, y, 1)^{\mathsf T}$,
ja kuvapiste on $(x'/w', y'/w')$. Jako $w'$:llä tekee muunnoksesta
epälineaarisen: kaukaiset asiat pienenevät, ja suorakaide näkyy vinossa
kuvassa puolisuunnikkaana. Homografia kuvaa kaksi tilannetta tarkasti:
**tasomaisen kohteen** eri suunnista otetut kuvat ja **paikallaan
kiertyvän kameran** kuvat. Siksi sillä oikaistaan dokumentteja ja
kootaan panoraamoja.

Neljä pisteparia riittää homografiaan. Seuraavassa A4-arkki on kuvattu
vinosti, ja sen neljästä kulmasta lasketaan muunnos, joka oikaisee arkin
millimetriasteikolle.

```{.python tiedosto="esimerkit/06-homografia.py" osa="oikaisu"}
```

### DLT: homografia lineaarisena yhtälönä

Jokainen pistepari $(x, y) \mapsto (u, v)$ antaa kaksi homografian
alkioille lineaarista yhtälöä, kun jakolasku kerrotaan pois:
$u\,(h_{31}x + h_{32}y + h_{33}) = h_{11}x + h_{12}y + h_{13}$ ja vastaavasti
$v$:lle. Yhtälöt kootaan matriisiksi $A$, ja ratkaisu on se yksikkövektori
$h$, joka minimoi $\lVert A h\rVert$: singulaariarvohajotelman pienintä
singulaariarvoa vastaava oikea singulaarivektori. Tämä on **suora
lineaarinen muunnos** (*direct linear transform*, DLT).

```{.python tiedosto="esimerkit/06-homografia.py" osa="dlt"}
```

Kun pisteitä on enemmän kuin neljä, DLT antaa pienimmän neliösumman
ratkaisun. Käytännön toteutukset normalisoivat pisteet ensin
(keskiarvo nollaan, keskietäisyys $\sqrt{2}$), koska muuten matriisin
$A$ alkiot ovat eri kertaluokkaa ja ratkaisu numeerisesti epätarkka.

### Väärät parit ja RANSAC

Piirteiden sovituksesta tulee aina myös vääriä pareja. Pienimmän
neliösumman ratkaisu yrittää sovittaa nekin, ja yksikin kaukainen väärä
pari voi vääristää tuloksen täysin. RANSAC (luku 5) etsii ensin
sisäpisteet ja ratkaisee muunnoksen vain niistä.

```{.python tiedosto="esimerkit/06-homografia.py" osa="ransac"}
```

```{.tuloste tiedosto="esimerkit/06-homografia.odotettu"}
```

Testi mittaa virhettä paperin kulmien siirtymänä pikseleinä eikä
matriisin alkioina. Homografian alkiot ovat eri yksiköissä, ja sama
geometrinen virhe voi näkyä niissä hyvin eri tavoin. Mittaa siksi aina
virhe siinä, mitä muunnoksella tehdään.

## Interpolointi

Kun kuvaa muunnetaan, tulospikselin lähde osuu yleensä lähdepikselien
väliin, ja arvo **interpoloidaan**. OpenCV laskee muunnoksen käänteisenä:
jokaiselle tulospikselille haetaan lähdekohta, ja sen arvo interpoloidaan.
Näin tulokseen ei jää aukkoja.

| Tapa | Naapureita | Ominaisuudet |
|------|------------|--------------|
| `INTER_NEAREST` | 1 | ei uusia arvoja; porrastus, sopii nimiökuville |
| `INTER_LINEAR` | 4 | nopea oletus; sumentaa hieman |
| `INTER_CUBIC` | 16 | terävämpi; voi ylittää alkuperäisen välin |
| `INTER_LANCZOS4` | 64 | terävin; hitain |
| `INTER_AREA` | alue | pienennykseen (luku 3) |

Jokainen interpolointi on pieni alipäästösuodatus, ja virhe kertyy, kun
kuvaa muunnetaan toistuvasti. Seuraavassa kuvaa kierretään kaksitoista
kertaa 30 astetta.

```{.python tiedosto="esimerkit/06-muunnokset.py" osa="kertyva"}
```

```{.tuloste tiedosto="esimerkit/06-muunnokset.odotettu"}
```

Bilineaarinen interpolointi sumentaa joka kierroksella, ja kahdentoista
kierroksen jälkeen se on jopa huonompi kuin lähin naapuri. Johtopäätös
ei ole valita aina Lanczosia, vaan välttää toistuvaa uudelleennäytteistystä:
**yhdistä muunnokset matriiseina ja näytteistä kerran**. Kaksitoista
kiertoa on yksi matriisitulo.

## Panoraaman periaate

Kun kamera kiertyy paikallaan, peräkkäisten kuvien välinen muunnos on
homografia. Panoraama kootaan sovittamalla piirteet, laskemalla
homografia RANSACilla ja muuntamalla kuva toisen koordinaatistoon.

```{.python tiedosto="esimerkit/06-panoraama.py" osa="kuvat"}
```

```{.python tiedosto="esimerkit/06-panoraama.py" osa="yhdistys"}
```

```{.tuloste tiedosto="esimerkit/06-panoraama.odotettu"}
```

Valmiit panoraamaohjelmat tekevät lisäksi kolme asiaa, jotka tästä
puuttuvat. Ne optimoivat kaikkien kuvien homografiat yhdessä (*bundle
adjustment*), jotta virhe ei kerry kuvasta toiseen. Ne projisoivat
kuvat sylinterille tai pallolle, koska taso ei kestä yli 180 asteen
näkökenttää. Ja ne häivyttävät saumat ja tasaavat valotuksen.
OpenCV:n `Stitcher` tekee nämä kaikki.

## Käytännössä

- **Valitse yksinkertaisin riittävä muunnos.** Mitä vähemmän
  vapausasteita, sitä vähemmän pisteitä tarvitaan ja sitä vähemmän
  kohina vääristää tulosta. Kamera, joka vain siirtyy, ei tarvitse
  homografiaa.
- **Yhdistä muunnokset ennen näytteistystä.** Kerro matriisit ja kutsu
  `warpAffine` tai `warpPerspective` kerran.
- **Interpoloi tehtävän mukaan.** Nimiökuvat ja maskit `INTER_NEAREST`,
  pienennys `INTER_AREA`, suurennus ja kierto `INTER_LINEAR` tai
  `INTER_CUBIC`.
- **Mittaa virhe geometrisesti.** Vertaa tunnettujen pisteiden sijaintia,
  älä matriisien alkioita.
- **Älä luota yhteen homografiaan väärien parien kanssa.** RANSAC aina,
  ja tarkista sisäpisteiden osuus: alle puolet tarkoittaa yleensä, että
  malli on väärä.

## Itsearviointi

- Osaat valita muunnostyypin vapausasteiden ja säilyvien ominaisuuksien
  perusteella.
- Osaat laskea homografian neljästä pisteestä ja johtaa DLT-ratkaisun
  SVD:llä.
- Osaat arvioida homografian väärien parien joukosta RANSACilla ja
  mitata sen virheen geometrisesti.
- Osaat valita interpolointitavan ja välttää toistuvan
  uudelleennäytteistyksen.
- Osaat selittää, miten panoraama kootaan piirteistä ja homografiasta.
