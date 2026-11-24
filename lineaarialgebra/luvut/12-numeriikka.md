# Numeeriset näkökohdat

Liukuluvuilla laskettu tulos on aina likiarvo. Useimmiten virhe on
viimeisessä desimaalissa ja täysin merkityksetön, mutta lineaarialgebrassa
on tilanteita, joissa pienet virheet kasvavat ja tuhoavat tuloksen.
Tämä luku kokoaa ne yhteen. Liukulukujen esitys ja pyöristys
käsitellään taidossa *Miten tietokone laskee*; tässä katsotaan, mitä
niistä seuraa matriisilaskennassa.

## Kuntoluku

Ongelman **kuntoluku** kertoo, kuinka paljon syötteen suhteellinen
virhe voi pahimmillaan kasvaa tuloksessa. Matriisille

$$\kappa(A) = \lVert A \rVert \, \lVert A^{-1} \rVert,$$

joka on suurimman ja pienimmän singulaariarvon suhde. Ortogonaalisella
matriisilla $\kappa = 1$ (paras mahdollinen), singulaarisella
$\kappa = \infty$. Nyrkkisääntö: kun $\kappa \approx 10^k$, ratkaisusta
menetetään noin $k$ merkitsevää numeroa. 64-bittisessä liukuluvussa
numeroita on noin 16.

Kuntoluku on ongelman ominaisuus, ei algoritmin. Huonokuntoista
yhtälöryhmää ei voi ratkaista tarkasti millään menetelmällä, koska jo
syötteen pyöristys tai mittausvirhe muuttaa oikeaa ratkaisua paljon.
Geometrisesti kaksi lähes yhdensuuntaista suoraa leikkaavat kaukana,
ja pieni siirto toisessa siirtää leikkauspistettä paljon:

```{.python tiedosto="esimerkit/12-kuntoluku.py" osa="herkkyys"}
```

Hilbertin matriisi on tunnettu esimerkki huonokuntoisuudesta. Kun
ratkaisu tunnetaan etukäteen, menetettyjen numeroiden määrän näkee
suoraan:

```{.python tiedosto="esimerkit/12-kuntoluku.py" osa="hilbert"}
```

```{.tuloste tiedosto="esimerkit/12-kuntoluku.odotettu"}
```

Kymmenen tuntemattoman Hilbertin matriisilla tarkkuudesta on jäljellä
vain muutama numero, vaikka ratkaisija on moitteeton.

## Vakaat ja epävakaat algoritmit

Hyväkuntoinen ongelma voidaan silti ratkaista huonosti. **Vakaa**
algoritmi tuottaa tuloksen, joka on täsmälleen oikea hieman
häirityille syötteille; silloin virhe on kuntoluvun ja
pyöristysvirheen tulon luokkaa, eikä parempaa voi odottaa.
Epävakaa algoritmi tuottaa ylimääräistä virhettä.

Gaussin eliminointi ilman tuentaa on epävakaa. Pieni tukialkio
tuottaa valtavan kertoimen, ja ykkösen suuruinen tieto häviää
pyöristyksessä:

```{.python tiedosto="esimerkit/12-tuenta.py" osa="ilman"}
```

```{.python tiedosto="esimerkit/12-tuenta.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/12-tuenta.odotettu"}
```

Matriisi on hyväkuntoinen, ja oikea ratkaisu on käytännössä $(1, 1)$.
Pelkkä rivien järjestyksen vaihto korjaa tuloksen. Muita esimerkkejä
epävakaista menetelmistä ovat klassinen Gram–Schmidt (luku 8) ja
normaaliyhtälöt huonokuntoisessa sovituksessa (luku 9).

## Käänteismatriisi ja jäännös

Luvussa 6 todettiin, että yhtälöryhmää ei ratkaista käänteismatriisin
avulla. Huonokuntoisella matriisilla ero näkyy jäännöksessä
$\lVert Ax - b \rVert$: LU-ratkaisun jäännös on pyöristysvirheen
luokkaa, käänteismatriisin kautta lasketun selvästi suurempi.

```{.python tiedosto="esimerkit/12-kaanteis.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/12-kaanteis.odotettu"}
```

Kumpikaan ei tuota tarkkaa ratkaisua, koska kuntoluku on
$10^{10}$. Mutta `solve` antaa ratkaisun, joka toteuttaa yhtälön
pyöristysvirheen tarkkuudella, eli vastaa parhaiten saatavilla olevaa
tietoa.

## Käytännössä

- **Laske kuntoluku epäilyttävissä tilanteissa.** `np.linalg.cond`
  on halpa pienille matriiseille. Jos se on yli $10^{12}$, tulokseen
  ei voi luottaa, ja ongelma pitää muotoilla uudelleen.
- **Paranna mallia, älä algoritmia.** Huonokuntoisuus johtuu usein
  huonosta mallinnuksesta: lähes riippuvista muuttujista,
  skaalaamattomista yksiköistä tai liian korkeasta polynomin asteesta.
  Skaalaus, keskitys ja turhien muuttujien poisto auttavat eniten.
- **Käytä vakaita menetelmiä.** Osittaistuenta, Householderin QR,
  `lstsq` ja `eigh` ovat vakaita. Kirjastofunktiot valitsevat ne
  automaattisesti.
- **Vertaa toleranssilla.** `np.allclose` ja `np.isclose`
  vertaavat suhteellisella ja absoluuttisella toleranssilla. Yhtäsuuruus
  `==` liukuluvuilla on lähes aina virhe.
- **Varo float32:ta.** Grafiikan ja koneoppimisen 32-bittiset
  luvut antavat noin seitsemän numeroa. Kuntoluku $10^4$ jättää
  niistä kolme.

## Itsearviointi

- Osaat selittää kuntoluvun ja arvioida sen avulla, montako
  merkitsevää numeroa ratkaisusta menetetään.
- Osaat erottaa huonokuntoisen ongelman ja epävakaan algoritmin.
- Osaat näyttää esimerkillä, miksi osittaistuenta tarvitaan.
- Osaat perustella, miksi `solve` on parempi kuin käänteismatriisi
  myös tarkkuuden kannalta.
