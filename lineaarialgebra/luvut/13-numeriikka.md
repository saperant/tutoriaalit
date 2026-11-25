# Numeeriset näkökohdat

Liukuluvuilla laskettu tulos on aina likiarvo. Useimmiten virhe on
viimeisessä desimaalissa ja täysin merkityksetön, mutta lineaarialgebrassa
on tilanteita, joissa pienet virheet kasvavat ja tuhoavat tuloksen.
Aiemmat luvut ovat varoittaneet niistä yksi kerrallaan; tämä luku
kokoaa ne yhteen ja mittaa ne. Liukulukujen esitys ja pyöristys
käsitellään taidossa *Miten tietokone laskee*; tässä katsotaan, mitä
niistä seuraa matriisilaskennassa. Virheanalyysi jatkuu taidossa
*Numeeriset menetelmät*.

## Ehtoluku käytännössä

Luku *Lineaariset yhtälöryhmät* esitteli ehtoluvun herkkyytenä ja luku
*Singulaariarvohajotelma* antoi sille määritelmän
$\kappa(A) = \sigma_{\max} / \sigma_{\min}$. Nyrkkisääntö oli: kun
$\kappa \approx 10^k$, ratkaisusta menetetään noin $k$ merkitsevää
numeroa 64-bittisen liukuluvun noin 16:sta.

Hilbertin matriisi on tunnettu esimerkki huonokuntoisuudesta. Kun
ratkaisu tunnetaan etukäteen, menetettyjen numeroiden määrän näkee
suoraan:

```{.python tiedosto="esimerkit/13-ehtoluku.py" osa="hilbert"}
```

```{.tuloste tiedosto="esimerkit/13-ehtoluku.odotettu" rivit="1-4"}
```

Kymmenen tuntemattoman Hilbertin matriisilla tarkkuudesta on jäljellä
vain muutama numero, vaikka ratkaisija on moitteeton. Ehtoluku on
ongelman ominaisuus, eikä parempi algoritmi auta.

```{.python tiedosto="esimerkit/13-ehtoluku.py" osa="singulaariarvot"}
```

```{.tuloste tiedosto="esimerkit/13-ehtoluku.odotettu" rivit="5-"}
```

## Stabiilit ja epästabiilit algoritmit

Hyväkuntoinen ongelma voidaan silti ratkaista huonosti. **Stabiili**
(vakaa) algoritmi tuottaa tuloksen, joka on täsmälleen oikea hieman
häirityille syötteille; silloin virhe on ehtoluvun ja
pyöristysvirheen tulon luokkaa, eikä parempaa voi odottaa.
**Epästabiili** algoritmi tuottaa ylimääräistä virhettä.

Gaussin eliminointi ilman tuentaa on epästabiili. Pieni tukialkio
tuottaa valtavan kertoimen, ja ykkösen suuruinen tieto häviää
pyöristyksessä:

```{.python tiedosto="esimerkit/13-tuenta.py" osa="ilman"}
```

```{.python tiedosto="esimerkit/13-tuenta.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/13-tuenta.odotettu"}
```

Matriisi on hyväkuntoinen, ja oikea ratkaisu on käytännössä $(1, 1)$.
Pelkkä rivien järjestyksen vaihto korjaa tuloksen. Muita esimerkkejä
epästabiileista menetelmistä ovat klassinen Gram–Schmidt (luku
*Ortogonaalisuus*) ja normaaliyhtälöt huonokuntoisessa sovituksessa
(luku *Pienimmän neliösumman sovitus*).

## Käänteismatriisi ja jäännös

Luvussa *Determinantti ja käänteismatriisi* todettiin, että
yhtälöryhmää ei ratkaista käänteismatriisin avulla. Nyt väite mitataan. Huonokuntoisella matriisilla ero näkyy jäännöksessä
$\lVert Ax - b \rVert$: LU-ratkaisun jäännös on pyöristysvirheen
luokkaa, käänteismatriisin kautta lasketun selvästi suurempi.

```{.python tiedosto="esimerkit/13-kaanteis.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/13-kaanteis.odotettu"}
```

Kumpikaan ei tuota tarkkaa ratkaisua, koska ehtoluku on
$10^{10}$. Mutta `solve` antaa ratkaisun, joka toteuttaa yhtälön
pyöristysvirheen tarkkuudella, eli vastaa parhaiten saatavilla olevaa
tietoa. Jäännöksestä ja ehtoluvusta saadaan myös raja ratkaisun
virheelle; se johdetaan taidossa *Numeeriset menetelmät*, jossa
käsitellään myös iteratiivinen tarkennus ja harvojen matriisien
ratkaisijat.

## Käytännössä

- **Laske ehtoluku epäilyttävissä tilanteissa.** `np.linalg.cond`
  on halpa pienille matriiseille. Jos se on yli $10^{12}$, tulokseen
  ei voi luottaa, ja ongelma pitää muotoilla uudelleen.
- **Paranna mallia, älä algoritmia.** Huonokuntoisuus johtuu usein
  huonosta mallinnuksesta: lähes riippuvista muuttujista,
  skaalaamattomista yksiköistä tai liian korkeasta polynomin asteesta.
  Skaalaus, keskitys ja turhien muuttujien poisto auttavat eniten.
- **Käytä stabiileja menetelmiä.** Osittaistuenta, Householderin QR,
  `lstsq` ja `eigh` ovat stabiileja. Kirjastofunktiot valitsevat ne
  automaattisesti.
- **Vertaa toleranssilla.** `np.allclose` ja `np.isclose`
  vertaavat suhteellisella ja absoluuttisella toleranssilla. Yhtäsuuruus
  `==` liukuluvuilla on lähes aina virhe.
- **Varo float32:ta.** Grafiikan ja koneoppimisen 32-bittiset
  luvut antavat noin seitsemän numeroa. Ehtoluku $10^4$ jättää
  niistä kolme.

## Itsearviointi

- Osaat arvioida ehtoluvusta, montako merkitsevää numeroa ratkaisusta
  menetetään, ja tarkistaa arvion kokeella.
- Osaat erottaa huonokuntoisen ongelman ja epästabiilin algoritmin.
- Osaat näyttää esimerkillä, miksi osittaistuenta tarvitaan.
- Osaat perustella, miksi `solve` on parempi kuin käänteismatriisi
  myös tarkkuuden kannalta.
