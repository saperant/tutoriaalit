# Lineaariset yhtälöryhmät

Lineaarinen yhtälöryhmä $Ax = b$ on numeerisen laskennan työjuhta:
siihen päätyvät pienimmän neliösumman sovitus, Newtonin menetelmä
yhtälöryhmille, implisiittiset differentiaaliyhtälöiden ratkaisijat,
elementtimenetelmä ja piirisimulaattorit. Taidossa *Lineaarialgebra*
esiteltiin Gaussin eliminointi, LU-hajotelma ja ehtoluku. Tässä luvussa keskitytään numeriikkaan: miksi tuenta on
välttämätön, mitä hajotelmaa milloin käytetään ja miten ehtoluvusta ja
jäännöksestä saadaan virheelle raja.

## Tuenta

Gaussin eliminointi jakaa joka vaiheessa **tukialkiolla** eli
lävistäjän alkiolla. Jos se on nolla, algoritmi pysähtyy. Jos se on
lähes nolla, algoritmi ei pysähdy, vaan tuottaa väärän vastauksen.
**Osittainen tuenta** vaihtaa rivejä niin, että tukialkio on sarakkeen
itseisarvoltaan suurin.

```{.python tiedosto="esimerkit/06-tuenta.py" osa="gauss"}
```

```{.python tiedosto="esimerkit/06-tuenta.py" osa="kokeilu"}
```

```{.tuloste tiedosto="esimerkit/06-tuenta.odotettu"}
```

Matriisi on hyväkuntoinen, ja tarkka ratkaisu on hyvin lähellä
pistettä $(1, 1)$. Ilman tuentaa kerroin on $10^{20}$, ja toisen rivin
alkiot $1 - 10^{20}$ pyöristyvät arvoon $-10^{20}$: alkuperäisen rivin
tieto katoaa kokonaan. Tuennalla kertoimet ovat enintään 1, eikä
mitään katoa. Tuenta ei siis ole optimointi vaan oikeellisuuden ehto.
Osittaisella tuennalla Gaussin eliminointi on käytännössä taaksepäin
stabiili, ja kirjastot (LAPACK:n `getrf`) tekevät sen aina.

## Hajotelmat ja niiden valinta

Gaussin eliminointi on LU-hajotelma $PA = LU$, jossa $P$ on
permutaatiomatriisi, $L$ alakolmiomatriisi ja $U$ yläkolmiomatriisi.
Hajotelma maksaa noin $\tfrac23 n^3$ liukulukulaskua, mutta sen
jälkeen jokainen oikea puoli ratkeaa kahdella kolmiosysteemillä
hinnalla $2n^2$. Kun sama matriisi ratkaistaan monella oikealla
puolella (esimerkiksi Newtonin menetelmässä, jos Jacobin matriisi
pidetään kiinteänä), hajotelma tehdään kerran.

```{.python tiedosto="esimerkit/06-hajotelmat.py" osa="lu"}
```

Rakenteen hyödyntäminen säästää työtä ja parantaa tarkkuutta:

- **Cholesky** $A = LL^T$ symmetriselle positiivisesti definiitille
  matriisille maksaa puolet LU:sta eikä tarvitse tuentaa.
  Kovarianssimatriisit, elementtimenetelmän jäykkyysmatriisit ja
  normaaliyhtälöt ovat tällaisia. Jos Cholesky epäonnistuu, matriisi ei
  ole positiivisesti definiitti, mikä on hyödyllinen diagnoosi.
- **QR** $A = QR$ on noin kaksi kertaa LU:n hintainen, mutta
  taaksepäin stabiili ilman tuentaa ja toimii myös suorakulmaisille
  matriiseille (pienimmän neliösumman tehtävä, luku 4).
- **SVD** $A = U\Sigma V^T$ on kallein, mutta paljastaa kaiken:
  singulaariarvot kertovat asteen, ehtoluvun ja lähes singulaariset
  suunnat. Sitä käytetään huonokuntoisiin ja vajaa-asteisiin
  tehtäviin.
- **Nauha- ja kolmilävistäjämatriisit** ratkeavat hinnalla $O(n)$
  (`scipy.linalg.solve_banded`); harvat matriisit luvussa 7.

```{.python tiedosto="esimerkit/06-hajotelmat.py" osa="cholesky"}
```

```{.python tiedosto="esimerkit/06-hajotelmat.py" osa="svd"}
```

```{.tuloste tiedosto="esimerkit/06-hajotelmat.odotettu"}
```

**Käänteismatriisia ei muodosteta.** Lauseke `inv(A) @ b` on kolme
kertaa hitaampi kuin `solve(A, b)`, ja sen tulos on yleensä
epätarkempi. Jos lausekkeessa näkyy $A^{-1}$, se luetaan "ratkaise
yhtälöryhmä". Käänteismatriisia tarvitaan harvoin sellaisenaan
(esimerkiksi kovarianssimatriisin lävistäjäalkioita varten).

## Ehtoluku, jäännös ja virheraja

Matriisin ehtoluku $\kappa(A) = \|A\|\,\|A^{-1}\|$ (2-normissa suurimman
ja pienimmän singulaariarvon suhde) mittaa, kuinka herkkä ratkaisu on
datan muutoksille. Jos ratkaisija on taaksepäin stabiili, laskettu
$\hat x$ on tarkka ratkaisu hieman muutetulle tehtävälle, ja luvun 2
periaatteesta saadaan

$$\frac{\|\hat x - x\|}{\|x\|} \lesssim \kappa(A) \cdot
\frac{\|b - A\hat x\|}{\|A\|\,\|\hat x\|} \approx \kappa(A)\,\varepsilon.$$

**Hilbertin matriisi** $H_{ij} = 1/(i + j - 1)$ on tunnetusti
huonokuntoinen: sen ehtoluku kasvaa noin kertoimella 30 jokaista
rivin lisäystä kohden. Esimerkki ratkaisee yhtälöryhmän, jonka tarkka
ratkaisu on ykkösvektori, ja vertaa virhettä rajaan.

```{.python tiedosto="esimerkit/06-ehtoluku.py" osa="hilbert"}
```

```{.tuloste tiedosto="esimerkit/06-ehtoluku.odotettu"}
```

Tulos on tärkein yksittäinen opetus lineaarisista yhtälöryhmistä:

- **Jäännös on aina pieni**, koska ratkaisija on taaksepäin stabiili.
  Pieni jäännös ei siis kerro, että ratkaisu on tarkka.
- **Virhe pysyy rajan $\kappa\varepsilon$ alapuolella**, mutta raja
  itse kasvaa. Kun $n = 12$, ehtoluku on $2 \cdot 10^{16}$, eikä
  ratkaisussa ole yhtään luotettavaa numeroa.
- **Ratkaisija ei ole syyllinen.** Mikään algoritmi ei korjaa
  huonokuntoisuutta kaksoistarkkuudella; tehtävä on muotoiltava
  uudelleen (paremmat kantafunktiot, skaalaus, regularisointi) tai
  laskettava suuremmalla tarkkuudella.

SciPy varoittaa huonokuntoisesta matriisista (`LinAlgWarning`), ja
Octave tulostaa varoituksen "matrix singular to machine precision".
Esimerkki vaimentaa varoituksen, koska huonokuntoisuus on tässä
tiedossa, mutta tuotantokoodissa varoitus kertoo oikeasta ongelmasta.
Ehtoluvun arvio saadaan halvemmin kuin SVD:llä: LAPACK arvioi sen
LU-hajotelmasta (`scipy.linalg.solve` tekee tämän automaattisesti), ja
Octaven `rcond` palauttaa käänteisluvun arvion.

Myös **skaalaus** vaikuttaa: jos yksi yhtälö on megapascaleina ja
toinen pascaleina, ehtoluku kasvaa miljoonakertaiseksi ilman, että
fysikaalinen tehtävä muuttuu. Rivien ja sarakkeiden tasapainotus
(`scipy.linalg.matrix_balance`, LAPACK:n `geequ`) korjaa tämän.

## Sama Octavella

```{.octave tiedosto="esimerkit/octave/06-kenoviiva.m"}
```

```{.tuloste tiedosto="esimerkit/octave/06-kenoviiva.odotettu"}
```

Octaven ja MATLABin kenoviiva `A \ b` tutkii matriisin rakenteen ja
valitsee menetelmän itse: kolmiomatriisille takaisinsijoitus,
symmetriselle positiivisesti definiitille Cholesky, neliömatriisille LU
tuennalla ja suorakulmaiselle QR. Kenoviiva on siksi lähes aina oikea
valinta.

## Käytännössä

- **Käytä kirjaston ratkaisijaa.** `numpy.linalg.solve`,
  `scipy.linalg.solve` ja Octaven `\` kutsuvat LAPACKia, joka on
  tarkka, tuettu ja nopea. Oma eliminointi on opetusta varten.
- **Älä muodosta käänteismatriisia.** Ratkaise yhtälöryhmä tai käytä
  hajotelmaa uudelleen (`lu_factor` ja `lu_solve`, `cho_factor` ja
  `cho_solve`).
- **Valitse hajotelma rakenteen mukaan.** Symmetrinen ja positiivisesti
  definiitti: Cholesky. Suorakulmainen: QR. Huonokuntoinen tai
  vajaa-asteinen: SVD. Nauhamatriisi: `solve_banded`.
- **Tarkista jäännös ja ehtoluku yhdessä.** Jäännös kertoo, toimiko
  ratkaisija; ehtoluku kertoo, kuinka paljon tulokseen voi luottaa.
- **Skaalaa yksiköt** niin, että yhtälöt ja tuntemattomat ovat samaa
  suuruusluokkaa.
- **Suurille tehtäville** suorien menetelmien muisti ($n^2$) ja aika
  ($n^3$) loppuvat; silloin siirrytään harvoihin matriiseihin ja
  iteratiivisiin menetelmiin (luku 7). BLAS- ja LAPACK-toteutuksen
  (OpenBLAS, MKL) valinta vaikuttaa nopeuteen moninkertaisesti (taito
  *Suorituskyvyn analyysi ja optimointi*).

## Itsearviointi

- Osaat selittää, miksi Gaussin eliminointi ilman tuentaa voi antaa
  väärän tuloksen hyväkuntoisellekin matriisille.
- Osaat valita LU-, Cholesky-, QR- ja SVD-hajotelman välillä ja
  perustella valinnan hinnalla ja tarkkuudella.
- Osaat käyttää hajotelmaa uudelleen monelle oikealle puolelle.
- Osaat arvioida ratkaisun virheen ehtoluvusta ja selittää, miksi pieni
  jäännös ei takaa pientä virhettä.
- Osaat perustella, miksi käänteismatriisia ei muodosteta.
