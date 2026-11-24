# Pienimmän neliösumman sovitus

Mittausdata ei koskaan osu malliin täsmälleen. Kun kalibroidaan
lämpötila-anturia seitsemässä pisteessä ja malli on suora, saadaan
seitsemän yhtälöä kahdelle tuntemattomalle, eikä mikään suora toteuta
niitä kaikkia. Ratkaisun sijaan haetaan paras likiratkaisu: se, jonka
virheiden neliösumma on pienin.

## Ylimääräytynyt yhtälöryhmä

Mallissa $u = a + bT$ jokainen mittaus $(T_i, u_i)$ antaa yhtälön
$a + b T_i = u_i$. Matriisimuodossa

$$\underbrace{\begin{pmatrix} 1 & T_1 \\ \vdots & \vdots \\ 1 & T_m
\end{pmatrix}}_{A}
\begin{pmatrix} a \\ b \end{pmatrix} \approx
\begin{pmatrix} u_1 \\ \vdots \\ u_m \end{pmatrix}.$$

Tavoite on minimoida $\lVert Ax - u \rVert^2$. Geometrisesti $Ax$
kulkee $A$:n sarakeavaruudessa, ja lähin piste $u$:ta on sen
**projektio** sarakeavaruudelle. Virhevektori $u - Ax$ on silloin
kohtisuorassa jokaista saraketta vastaan: $A^T (u - Ax) = 0$.

```{.python tiedosto="esimerkit/09-suora.py" osa="data"}
```

## Normaaliyhtälöt

Ortogonaalisuusehdosta saadaan **normaaliyhtälöt**

$$A^T A\, x = A^T u,$$

joka on tavallinen neliömatriisin yhtälöryhmä. Menetelmä on helppo ja
nopea, mutta sillä on numeerinen heikkous: $A^T A$:n kuntoluku on $A$:n
kuntoluvun **neliö**. Jos $A$ on vähänkin huonokuntoinen, normaali-
yhtälöt menettävät puolet tarkkuudesta.

```{.python tiedosto="esimerkit/09-suora.py" osa="normaali"}
```

## QR-hajotelmalla

QR-hajotelma $A = QR$ välttää $A^T A$:n muodostamisen. Koska $Q$:n
sarakkeet ovat ortonormaaleja, normaaliyhtälöt sievenevät muotoon
$Rx = Q^T u$, joka ratkeaa takaisinsijoituksella. Kirjastojen
`lstsq` käyttää QR:ää tai singulaariarvohajotelmaa.

```{.python tiedosto="esimerkit/09-suora.py" osa="qr"}
```

```{.python tiedosto="esimerkit/09-suora.py" osa="tulos"}
```

```{.tuloste tiedosto="esimerkit/09-suora.odotettu"}
```

Kalibroinnin tuloksena anturin jännite on noin 0,503 V nollassa
asteessa ja kasvaa 9,9 mV astetta kohti. Jäännös on kohtisuorassa
sarakkeita vastaan, kuten teoria lupaa. Kalibrointikäyrän avulla
mitattu jännite muunnetaan takaisin lämpötilaksi.

## Malli on lineaarinen kertoimissa

Pienimmän neliösumman menetelmä toimii kaikille malleille, jotka ovat
lineaarisia **kertoimissa**, vaikka ne eivät ole lineaarisia
muuttujissa. Polynomi $c_0 + c_1 x + c_2 x^2 + \dots$, eksponenttien
summa ja Fourier-sarja ovat kaikki sopivia: matriisin sarakkeet ovat
kantafunktioiden arvot mittauspisteissä. Polynomille matriisi on
Vandermonden matriisi.

Monimutkaisempi malli sovittuu dataan aina paremmin, mutta se ei
tarkoita parempaa mallia. Kun polynomin aste lähestyy pisteiden määrää,
käyrä alkaa seurata kohinaa (**ylisovitus**), ja ennuste uusissa
pisteissä huononee:

```{.python tiedosto="esimerkit/09-polynomi.py" osa="asteet"}
```

```{.python tiedosto="esimerkit/09-polynomi.py" osa="kuntoluku"}
```

```{.tuloste tiedosto="esimerkit/09-polynomi.odotettu"}
```

Asteella 11 käyrä kulkee kaikkien kahdentoista pisteen kautta
(opetusvirhe nolla), mutta uusissa pisteissä se on huonompi kuin
asteella 5. Toinen tulostus näyttää kuntoluvun neliöitymisen:
asteella 7 normaaliyhtälöiden kuntoluku on jo $10^{10}$, joten
kuudesta kymmenestä merkitsevästä numerosta on menetetty.

## Käytännössä

- **Käytä `np.linalg.lstsq`ia.** Se käsittelee myös huonokuntoiset ja
  vajaa-asteiset tapaukset. Normaaliyhtälöt kelpaavat vain hyvin
  kuntoisille pienille malleille.
- **Skaalaa ja keskitä muuttujat.** Polynomisovitus muuttujalla $x$
  välillä 2000–2030 (vuosiluvut) on hirvittävän huonokuntoinen;
  muuttujalla $x - 2015$ se on hyvä. `np.polynomial.Polynomial.fit`
  tekee skaalauksen automaattisesti.
- **Arvioi malli datalla, jota sovitus ei nähnyt.** Opetusvirhe
  pienenee aina mallia monimutkaistamalla. Pidä osa datasta erillään
  testausta varten.
- **Katso jäännöksiä.** Jos jäännöksissä on rakennetta (kaari,
  trendi), malli on väärä. Satunnaiselta näyttävät jäännökset ovat
  hyvän mallin merkki.
- **Painota epätarkat mittaukset.** Kun mittausten tarkkuus vaihtelee,
  kerro rivit tarkkuuden käänteisluvulla (painotettu sovitus).

## Itsearviointi

- Osaat muodostaa ylimääräytyneen yhtälöryhmän mallista, joka on
  lineaarinen kertoimissa.
- Osaat selittää pienimmän neliösumman ratkaisun projektiona ja
  perustella, miksi jäännös on kohtisuorassa sarakkeita vastaan.
- Osaat ratkaista sovituksen normaaliyhtälöillä ja QR-hajotelmalla ja
  perustella, miksi QR on tarkempi.
- Osaat tunnistaa ylisovituksen ja estää sen testidatalla.
