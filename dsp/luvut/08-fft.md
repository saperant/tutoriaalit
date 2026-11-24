# FFT ja spektrianalyysi

Taito *Kompleksiluvut ja Fourier-analyysi* esitteli DFT:n
kannanvaihtona ja FFT:n ideana, ja taito *Signaalit ja järjestelmät*
käytti `numpy.fft`-funktiota spektrin mittaamiseen. Tässä luvussa FFT
toteutetaan itse C:llä. Sitten sitä käytetään pitkän suotimen
laskemiseen lohkoittain, ja lopuksi katsotaan, milloin koko FFT on
tarpeeton.

## Radix-2: hajota ja hallitse

$N$-pisteinen DFT

$$X[k] = \sum_{n=0}^{N-1} x[n]\,W_N^{kn}, \qquad
W_N = e^{-2\pi i/N},$$

vaatii $N^2$ kompleksikertolaskua. Kun $N$ on kahden potenssi, summa
jaetaan parillisiin ja parittomiin indekseihin:

$$X[k] = E[k] + W_N^k\,O[k], \qquad
X[k + N/2] = E[k] - W_N^k\,O[k],$$

missä $E$ ja $O$ ovat puolikkaiden jonojen $N/2$-pisteisiä DFT:itä.
Yksi kertolasku $W_N^k O[k]$ tuottaa kaksi tulosta. Tätä kutsutaan
**perhoseksi**. Jako toistetaan, kunnes jäljellä on yhden pisteen
muunnoksia. Tasoja on $\log_2 N$, ja jokaisella tasolla on $N/2$
perhosta, joten kertolaskuja on $(N/2)\log_2 N$.

Iteratiivinen toteutus kääntää ensin syötteen indeksien bitit, jolloin
parilliset ja parittomat ovat valmiiksi vierekkäin, ja laskee sitten
perhoset alhaalta ylös.

```{.c tiedosto="esimerkit/08-fft/fft.c" osa="kaanto"}
```

```{.c tiedosto="esimerkit/08-fft/fft.c" osa="perhoset"}
```

Kiertokertoimet $W_N^k$ lasketaan kerran alustuksessa omaan taulukkoonsa.
Jokainen kerroin lasketaan suoraan sinistä ja kosinista. Rekursio
$W^{k+1} = W^k \cdot W$ olisi halvempi, mutta sen pyöristysvirhe kasvaa
lineaarisesti $k$:n mukana, ja pitkässä muunnoksessa viimeiset
kertoimet olisivat selvästi väärin.

```{.c tiedosto="esimerkit/08-fft/fft.h" osa="tyyppi"}
```

```{.c tiedosto="esimerkit/08-fft/fft.c" osa="alusta"}
```

## Testaus

FFT:llä on ominaisuuksia, jotka voi tarkistaa ilman referenssiä: sinin
on osuttava oikeaan taajuusbiniin, energian on säilyttävä (Parsevalin
lause), ja käänteismuunnoksen on palautettava syöte. Lisäksi tulosta
verrataan suoraan $O(N^2)$-DFT:hen muutamassa binissä.

```{.c tiedosto="esimerkit/08-fft/main.c" osa="testit"}
```

```{.tuloste tiedosto="esimerkit/08-fft.odotettu"}
```

Vertailuohjelma ja pytest tarkistavat lisäksi pituudet 2–4096 NumPyn
FFT:tä vastaan sekä sen, että muut kuin kahden potenssin pituudet
hylätään:

```{.python tiedosto="esimerkit/vertailu/test_vertailu.py" osa="fft"}
```

Tämä FFT on opetuksellinen. Tuotannossa käytetään valmista kirjastoa:
FFTW, KissFFT ja PocketFFT (NumPyn ja SciPyn moottori) osaavat myös
muut kuin kahden potenssin pituudet ja reaaliset syötteet. Reaalisen
signaalin muunnos maksaa noin puolet kompleksisesta, koska spektri on
symmetrinen (`numpy.fft.rfft`). Mikrokontrollereissa käytetään
valmistajan optimoituja kirjastoja, kuten Armin CMSIS-DSP:tä.

## Pitkä FIR: overlap-save

Signaalit ja järjestelmät -taidossa nähtiin, että konvoluutio on
pitkillä suotimilla nopeampi FFT:llä. Reaaliajassa signaali tulee
lohkoina, joten FFT-konvoluutiokin on tehtävä lohkoittain ja tilan on
säilyttävä. **Overlap-save** tekee sen näin:

1. Kehykseen otetaan $N$ näytettä: edellisen kehyksen viimeiset
   $M - 1$ näytettä ja $L = N - M + 1$ uutta.
2. Kehyksen FFT kerrotaan suotimen valmiiksi lasketulla FFT:llä.
3. Käänteismuunnoksen ensimmäiset $M - 1$ näytettä ovat syklisen
   konvoluution vääristämiä, ja ne heitetään pois. Loput $L$ ovat
   oikeita ulostuloja.

```{.python tiedosto="esimerkit/08-overlap.py" osa="overlap_save"}
```

```{.python tiedosto="esimerkit/08-overlap.py" osa="vertaa"}
```

Lohkon pituus valitaan laskennan ja viiveen kompromissina. Pieni FFT
tuottaa vähän ulostuloja muunnosta kohti, ja suuri FFT on kallis ja
lisää viivettä. Karkean laskentamallin mukaan 255 kertoimen suotimella
optimi on noin 2048 pisteen FFT:

```{.python tiedosto="esimerkit/08-overlap.py" osa="kustannus"}
```

```{.tuloste tiedosto="esimerkit/08-overlap.odotettu"}
```

Suoraan laskettuna 255 kertoimen suodin vaatii 255 kertolaskua
näytettä kohti, FFT:llä noin 52. Hinta on viive: ulostulo valmistuu
vasta, kun koko $L$:n näytteen lohko on kerätty. 48 kHz:n
näytetaajuudella 1794 näytettä on 37 ms, mikä on liikaa esimerkiksi
kuulokemonitorointiin. **Overlap-add** on toinen tapa: se laskee jokaisen
lohkon konvoluution erikseen ja summaa päällekkäiset hännät. Molempien
kustannus on sama. Pienen viiveen sovelluksissa, kuten
huonevasteiden konvoluutiossa, suodin jaetaan osiin, joista
ensimmäinen lasketaan suoraan tai lyhyellä FFT:llä ja loput pitkillä
(*partitioned convolution*).

## Yksi taajuus: Goertzel

Kun spektristä tarvitaan vain muutama bin, koko FFT on tuhlausta.
**Goertzelin algoritmi** laskee yhden DFT-arvon toisen asteen
resonaattorilla, jonka napa on yksikköympyrällä kohdassa
$e^{2\pi i k/N}$. Kertolaskuja on yksi reaalinen näytettä kohti, eikä
koko signaalia tarvitse tallentaa.

```{.python tiedosto="esimerkit/08-goertzel.py" osa="goertzel"}
```

Klassinen käyttökohde on puhelimen näppäinäänien (DTMF) tunnistus:
jokainen näppäin on kahden sinin summa, yksi neljästä rivitaajuudesta
ja yksi kolmesta saraketaajuudesta. Seitsemän Goertzel-suodinta riittää.

```{.python tiedosto="esimerkit/08-goertzel.py" osa="dtmf"}
```

```{.tuloste tiedosto="esimerkit/08-goertzel.odotettu"}
```

Seitsemän binin laskeminen Goertzelilla maksaa $7N \approx 1\,400$
reaalista kertolaskua. 256 pisteen FFT maksaa noin
$(N/2)\log_2 N = 1\,024$ kompleksista eli noin 4 000 reaalista
kertolaskua. Goertzel voittaa, kun binejä on vähemmän kuin noin
$2\log_2 N$. Lisäksi sen taajuuden ei tarvitse osua kahden potenssin
hilaan, ja $N = 205$ on valittu niin, että DTMF-taajuudet osuvat
lähelle binejä.

## Käytännössä

- **Käytä valmista FFT-kirjastoa** tuotannossa. Oma toteutus on
  opetuksellinen ja hyvä testikohde, mutta valmiit ovat nopeampia ja
  osaavat kaikki pituudet.
- **Testaa FFT ominaisuuksilla**: sini oikeaan biniin, Parseval,
  käänteismuunnoksen paluu ja vertailu suoraan DFT:hen.
- **Laske kiertokertoimet suoraan**, älä rekursiolla, kun muunnos on
  pitkä.
- **Valitse overlap-saven lohkopituus** laskennan ja viiveen
  kompromissina. Noin neljä kertaa suotimen pituus on hyvä lähtökohta.
- **Käytä Goertzelia**, kun tarvitset vain muutaman taajuuden, kuten
  äänitaajuuksien tunnistuksessa tai yksittäisen taajuuden
  valvonnassa.

## Itsearviointi

- Osaat johtaa radix-2-FFT:n perhosen ja laskea sen kertolaskujen
  määrän.
- Osaat toteuttaa iteratiivisen FFT:n bittien käännöllä ja testata sen
  ilman referenssiä.
- Osaat toteuttaa overlap-save-suodatuksen lohkoittain ja valita
  lohkopituuden laskennan ja viiveen perusteella.
- Osaat käyttää Goertzelin algoritmia yksittäisten taajuuksien
  tunnistukseen ja kertoa, milloin se on FFT:tä halvempi.
