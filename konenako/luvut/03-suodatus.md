# Suodatus

Taidossa *Signaalit ja järjestelmät* konvoluutio oli yksiulotteisen
jonon ja impulssivasteen summa. Kuvassa sama toimitus tehdään kahdessa
ulottuvuudessa: jokainen tulospikseli on painotettu summa naapuristaan,
ja painot ovat **ydin** (*kernel*). Ydin on kuvan impulssivaste, ja sen
2D-Fourier-muunnos on suotimen taajuusvaste. Tässä luvussa käydään läpi,
miten OpenCV suodattaa, mitä reunoilla tapahtuu, miksi erottuva ydin on
nopea, mitkä suotimet poistavat minkäkin kohinan ja miten aliasointi
näkyy kuvia pienennettäessä.

## 2D-konvoluutio ja korrelaatio

Konvoluutio kääntää ytimen ennen summausta:
$(I * k)(x, y) = \sum_{i,j} k(i, j)\, I(x - i, y - j)$. OpenCV:n
`filter2D` laskee kuitenkin **korrelaation**, eli se ei käännä ydintä.
Symmetrisillä ytimillä (keskiarvo, Gauss) ero ei näy, mutta
epäsymmetrisillä (derivaatat, liike-epäterävyys) se kääntää tuloksen
suunnan.

```{.python tiedosto="esimerkit/03-konvoluutio.py" osa="oma"}
```

```{.python tiedosto="esimerkit/03-konvoluutio.py" osa="vertailu"}
```

Kuvan reunalla ydin ulottuu kuvan ulkopuolelle, ja **reunakäsittely**
ratkaisee, mitä siellä on. OpenCV:n oletus `BORDER_REFLECT_101` peilaa
kuvaa reunapikseliä toistamatta. `BORDER_REPLICATE` toistaa reunapikseliä,
ja `BORDER_CONSTANT` täyttää vakiolla, joka tummentaa tai vaalentaa
reunat.

```{.python tiedosto="esimerkit/03-konvoluutio.py" osa="reunat"}
```

```{.tuloste tiedosto="esimerkit/03-konvoluutio.odotettu"}
```

Valinta ei ole kosmeettinen. Jos reunoilta mitataan jotain, kuten
reunoja tai kirkkautta, vakioreuna tuottaa vääriä reunoja kuvan laidoille.
Neuroverkkojen esikäsittely käyttää usein nollareunaa, mutta mittaavat
menetelmät peilausta.

## Erottuvat ytimet

$k \times k$ -ytimellä jokainen tulospikseli vaatii $k^2$
kertolaskua. Jos ydin on kahden 1D-ytimen ulkotulo
$k = g\,g^{\mathsf T}$, suodatus voidaan tehdä ensin riveittäin ja sitten
sarakkeittain, ja kustannus laskee $2k$:hon. Tällainen ydin on
**erottuva** (*separable*). Gaussin ydin on erottuva, ja sen matriisin
aste on 1.

```{.python tiedosto="esimerkit/03-erottuva.py" osa="ydin"}
```

```{.python tiedosto="esimerkit/03-erottuva.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/03-erottuva.odotettu"}
```

Ytimen koko valitaan $\sigma$:n mukaan: kolme $\sigma$:aa kumpaankin
suuntaan kattaa 99,7 % painosta. `GaussianBlur(kuva, (0, 0), sigma)`
laskee koon itse. Gaussin suodin on myös kohinan ja aliasoinnin kannalta
paras alipäästö pienelle ytimelle, koska sen taajuusvaste on taas Gaussin
käyrä ilman sivukeiloja.

## Kohinan poisto

Kohinan luonne ratkaisee suotimen. **Gaussin kohina** (anturin
lämpökohina) lisää jokaiseen pikseliin pientä satunnaisvaihtelua, ja
keskiarvoistava suodin vaimentaa sitä. **Suola ja pippuri** (viallisia
pikseleitä, siirtovirheitä) korvaa yksittäisiä pikseleitä ääriarvoilla.
Keskiarvo levittää ne naapureihin, mutta **mediaanisuodin** valitsee
ympäristön keskimmäisen arvon ja jättää ääriarvot kokonaan pois.

Kaikki tasoittavat suotimet sumentavat myös reunoja. **Bilateraalinen
suodin** painottaa naapureita sekä etäisyyden että kirkkauseron mukaan:
reunan toisella puolella olevat pikselit eroavat kirkkaudeltaan, joten
niiden paino on pieni, ja reuna säilyy.

```{.python tiedosto="esimerkit/03-kohina.py" osa="kuvat"}
```

Tulosta mitataan kahdella luvulla. **PSNR** (*peak signal-to-noise
ratio*) vertaa suodatettua kuvaa puhtaaseen: suurempi on parempi, ja
10 dB on kymmenkertainen ero virheen tehossa. **Reunan leveys** on niiden
sarakkeiden määrä, joissa kirkkaus on reunan 10 ja 90 prosentin
välissä.

```{.python tiedosto="esimerkit/03-kohina.py" osa="mittarit"}
```

```{.python tiedosto="esimerkit/03-kohina.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/03-kohina.odotettu"}
```

![Suola ja pippuri -kohina, Gaussin suodin ja mediaanisuodin. Gauss
levittää virheelliset pikselit läikiksi, mediaani poistaa
ne.](kuvat/kohina.png){width=100%}

Mediaani on ylivoimainen suola ja pippuri -kohinalle (49 dB), ja
bilateraalinen paras Gaussin kohinalle, mutta suolaan se ei tehoa:
ääriarvopikselit eroavat naapureistaan niin paljon, että suodin pitää
niitä reunoina ja säilyttää ne. Keskiarvo leventää reunaa eniten.

## Taajuustaso ja aliasointi

Kuvan 2D-DFT kertoo, mistä taajuuksista kuva koostuu. Kuvassa taajuudella
on suunta: raidat, joissa on 12 jaksoa vaakasuunnassa ja 5 pystysuunnassa,
näkyvät spektrissä huippuna kohdassa $(12, 5)$, ja huipun suunta on
raitojen normaali.

```{.python tiedosto="esimerkit/03-taajuus.py" osa="raidat"}
```

Taidon *Signaalit ja järjestelmät* näytteistysteoreema pätee kuviin
sellaisenaan. Kun kuvaa pienennetään, sen näytetaajuus pienenee, ja
Nyquistin rajan ylittävät yksityiskohdat **laskostuvat** matalammiksi
taajuuksiksi. Kuvassa ilmiö näkyy moiré-kuvioina ja porraskuvioina.
Pienennettäessä on siksi suodatettava ensin.

```{.python tiedosto="esimerkit/03-taajuus.py" osa="pienennys"}
```

```{.tuloste tiedosto="esimerkit/03-taajuus.odotettu"}
```

Neljäsosaan pienennetyssä kuvassa 40 jakson raidat laskostuvat kahdeksaksi
jaksoksi ($40 - 32$). `INTER_NEAREST` poimii näytteitä suodattamatta, ja
virheellinen kuvio näkyy täydellä voimakkuudella. `INTER_LINEAR` käyttää
vain kahta naapuria, joten se suodattaa hieman. `INTER_AREA` keskiarvoistaa
koko alueen, jonka pienennetty pikseli kattaa, ja vaimentaa laskostuneen
kuvion selvästi. Kokonaan sitä ei poista mikään yksinkertainen suodin:
signaalinkäsittelyn suodinsuunnittelu (taito *Digitaalinen
signaalinkäsittely*) koskee myös kuvia.

## Käytännössä

- **Muista, että `filter2D` korreloi.** Käännä ydin (`cv2.flip(k, -1)`),
  jos tarvitset konvoluution, ja testaa epäsymmetrinen suodin tunnetulla
  syötteellä.
- **Valitse reunakäsittely tietoisesti.** Mittaaville menetelmille
  `BORDER_REFLECT_101` tai `BORDER_REPLICATE`; vakioreuna vain, kun
  tiedät, mitä reunoille kuuluu.
- **Käytä erottuvia ytimiä.** `GaussianBlur` ja `sepFilter2D` ovat
  suurilla ytimillä moninkertaisesti nopeampia kuin `filter2D`.
  Suurilla mielivaltaisilla ytimillä OpenCV siirtyy itse
  DFT-pohjaiseen suodatukseen.
- **Valitse suodin kohinan mukaan.** Gaussin kohina: Gauss tai
  bilateraalinen. Impulssikohina: mediaani. Reunat tärkeitä:
  bilateraalinen tai mediaani. Älä suodata enempää kuin tarvitsee:
  jokainen suodatus hävittää yksityiskohtia.
- **Pienennä `INTER_AREA`:lla tai pyramidilla.** `pyrDown` suodattaa ja
  puolittaa. `INTER_NEAREST` vain, kun pikselit ovat nimiöitä (esim.
  segmentointimaskit), joita ei saa keskiarvoistaa.

## Itsearviointi

- Osaat selittää konvoluution ja korrelaation eron ja tarkistaa, kumpaa
  funktio laskee.
- Osaat valita reunakäsittelyn ja selittää, miten se vaikuttaa tulokseen
  kuvan reunoilla.
- Osaat tunnistaa erottuvan ytimen, suodattaa sillä kahdessa vaiheessa ja
  laskea säästön kertolaskuina.
- Osaat valita suotimen kohinatyypin mukaan ja mitata tuloksen PSNR:llä.
- Osaat selittää aliasoinnin kuvien pienentämisessä ja valita oikean
  interpolointitavan.
