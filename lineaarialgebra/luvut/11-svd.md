# Singulaariarvohajotelma

Ominaisarvohajotelma kertoo kuvauksen luonnolliset akselit, mutta se on
olemassa vain neliömatriiseille, eikä niistäkään kaikille (leikkaus,
kierto). **Singulaariarvohajotelma** (SVD, *singular value
decomposition*) on olemassa jokaiselle matriisille, myös
suorakulmaiselle ja singulaariselle. Se kokoaa yhteen lähes kaiken
edellä opitun: ortogonaaliset matriisit, asteen, neljä aliavaruutta,
pienimmän neliösumman sovituksen, pääkomponentit ja ehtoluvun.

## Kierto, venytys, kierto

Jokainen $m \times n$-matriisi voidaan kirjoittaa tuloksi

$$A = U \Sigma V^T,$$

missä $U$ ($m \times m$) ja $V$ ($n \times n$) ovat ortogonaalisia ja
$\Sigma$ on lävistäjämatriisi, jonka lävistäjällä ovat
**singulaariarvot** $\sigma_1 \ge \sigma_2 \ge \dots \ge 0$.
Geometrisesti mikä tahansa lineaarikuvaus on siis kolmen
yksinkertaisen kuvauksen yhdistelmä: kierto (tai peilaus) $V^T$,
venytys koordinaattiakselien suuntaan $\Sigma$ ja toinen kierto $U$.

![Matriisi $A = \begin{pmatrix} 2 & 1 \\ 0{,}5 & 1{,}5 \end{pmatrix}$
vaiheittain. $V^T$ kiertää suunnat $v_1$ ja $v_2$ koordinaattiakseleille,
$\Sigma$ venyttää akseleita kertoimilla $\sigma_1 \approx 2{,}56$ ja
$\sigma_2 \approx 0{,}98$, ja $U$ kiertää tuloksen paikalleen.
Yksikköympyrästä tulee ellipsi, jonka puoliakselit ovat
singulaariarvot.](kuvat/svd.png){width=100%}

$V$:n sarakkeet $v_i$ ovat **oikeat singulaarivektorit** ja $U$:n
sarakkeet $u_i$ **vasemmat singulaarivektorit**. Hajotelma sanoo
sarake kerrallaan, että $A v_i = \sigma_i u_i$: kuvaus vie kohtisuorat
suunnat $v_i$ kohtisuoriksi suunniksi $u_i$ ja venyttää niitä
kertoimilla $\sigma_i$. Suurin singulaariarvo on suurin venytys, jonka
kuvaus tekee millekään vektorille, ja pienin on pienin venytys.

```{.python tiedosto="esimerkit/11-svd.py" osa="hajotelma"}
```

```{.tuloste tiedosto="esimerkit/11-svd.odotettu" rivit="1-7"}
```

Viimeinen rivi yhdistää hajotelman determinanttiin: kierrot eivät
muuta pinta-alaa, joten pinta-alan kerroin on singulaariarvojen tulo.
Singulaarivektorien etumerkit eivät ole yksikäsitteiset (pari
$u_i, v_i$ voidaan kääntää yhtä aikaa), joten tulosteissa verrataan
vain etumerkistä riippumattomia suureita.

## Yhteys ominaisarvoihin

Singulaariarvot saadaan symmetrisestä matriisista $A^T A$:

$$A^T A = (U \Sigma V^T)^T (U \Sigma V^T) = V \Sigma^T \Sigma\, V^T.$$

Tämä on $A^T A$:n ominaisarvohajotelma: $V$:n sarakkeet ovat sen
ominaisvektorit ja $\sigma_i^2$ ominaisarvot. Koska $A^T A$ on
symmetrinen ja positiivisesti semidefiniitti (luku *Ominaisarvot ja
ominaisvektorit*), ominaisarvot ovat ei-negatiivisia ja
ominaisvektorit kohtisuoria, ja siksi hajotelma on aina olemassa.
Vastaavasti $U$:n sarakkeet ovat matriisin $A A^T$ ominaisvektorit.

```{.python tiedosto="esimerkit/11-svd.py" osa="ominaisarvot"}
```

```{.tuloste tiedosto="esimerkit/11-svd.odotettu" rivit="8-9"}
```

Symmetriselle positiivisesti definiitille matriisille singulaariarvot
ovat samat kuin ominaisarvot. Yleiselle matriisille ne ovat eri asia:
ominaisarvot kertovat, mitä kuvauksen *toistaminen* tekee,
singulaariarvot, mitä *yksi* soveltaminen tekee pituuksille.
Kirjastot eivät muodosta matriisia $A^T A$, koska se neliöisi
ehtoluvun kuten normaaliyhtälöissä; ne laskevat hajotelman suoraan
$A$:sta ortogonaalisilla muunnoksilla.

## Aste, aliavaruudet ja ehtoluku

Nollasta poikkeavien singulaariarvojen määrä on matriisin aste $r$.
Singulaarivektorit antavat samalla ortonormaalit kannat luvun
*Aliavaruudet, kanta ja kannanvaihto* neljälle aliavaruudelle:

| Vektorit | Aliavaruus |
|----------|------------|
| $u_1, \dots, u_r$ | sarakeavaruus |
| $u_{r+1}, \dots, u_m$ | vasen nolla-avaruus |
| $v_1, \dots, v_r$ | riviavaruus |
| $v_{r+1}, \dots, v_n$ | nolla-avaruus |

Liukuluvuilla singulaariarvo on harvoin täsmälleen nolla, joten aste
on toleranssikysymys: `np.linalg.matrix_rank` laskee singulaariarvot ja
pitää nollina ne, jotka ovat pienempiä kuin suurin singulaariarvo
kertaa matriisin koko kertaa liukuluvun suhteellinen tarkkuus. Tämä on
luotettavin tapa määrittää aste numeerisesti.

```{.python tiedosto="esimerkit/11-svd.py" osa="aste"}
```

```{.tuloste tiedosto="esimerkit/11-svd.odotettu" rivit="10-12"}
```

Luvussa *Lineaariset yhtälöryhmät* ehtoluku esiteltiin herkkyytenä.
Singulaariarvot antavat sille täsmällisen määritelmän:

$$\kappa(A) = \lVert A \rVert \, \lVert A^{-1} \rVert
            = \frac{\sigma_{\max}}{\sigma_{\min}}.$$

Tässä $\lVert A \rVert = \sigma_{\max}$ on matriisin 2-normi eli suurin
venytys, ja käänteismatriisin suurin venytys on $1/\sigma_{\min}$.
Ehtoluku on siis ellipsin pisimmän ja lyhimmän puoliakselin suhde:
mitä litteämpi ellipsi, sitä huonokuntoisempi matriisi.
Ortogonaalisella matriisilla kaikki singulaariarvot ovat 1 ja ympyrä
pysyy ympyränä, singulaarisella $\sigma_{\min} = 0$ ja ellipsi litistyy
janaksi. Lähes yhdensuuntaisten suorien yhtälöpari on huonokuntoinen
samasta syystä: sen matriisi litistää tason lähes suoraksi, ja
kumoaminen venyttää virheet takaisin kertoimella $1/\sigma_{\min}$.

## Pseudoinverssi ja pienin neliösumma

Kun $A$ ei ole neliömatriisi tai on singulaarinen, käänteismatriisia
ei ole. **Pseudoinverssi** (Mooren–Penrosen käänteismatriisi) kumoaa
kuvauksen niin hyvin kuin mahdollista: kierrot kumotaan transpooseilla
ja venytykset käänteisluvuilla, mutta nollavenytykset jätetään
nolliksi,

$$A^+ = V \Sigma^+ U^T, \qquad
  \Sigma^+ = \operatorname{diag}(1/\sigma_1, \dots, 1/\sigma_r, 0, \dots, 0).$$

Vektori $x = A^+ b$ on pienimmän neliösumman ratkaisu. Kun $A$:n
sarakkeet ovat lineaarisesti riippumattomia, se on sama kuin
normaaliyhtälöiden ja QR-hajotelman antama ratkaisu:

```{.python tiedosto="esimerkit/11-pseudoinverssi.py" osa="pinv"}
```

```{.python tiedosto="esimerkit/11-pseudoinverssi.py" osa="sovitus"}
```

```{.tuloste tiedosto="esimerkit/11-pseudoinverssi.odotettu" rivit="1-2"}
```

Hajotelman hyöty näkyy, kun sarakkeet ovat riippuvia. Oletetaan, että
kalibrointimalliin lisätään huomaamatta sama lämpötila toisessa
yksikössä. Uusi sarake ei tuo tietoa, matriisin aste on vajaa,
normaaliyhtälöiden matriisi on singulaarinen ja ratkaisuja on
äärettömästi. Pseudoinverssi valitsee niistä lyhimmän:

```{.python tiedosto="esimerkit/11-pseudoinverssi.py" osa="vajaa"}
```

```{.tuloste tiedosto="esimerkit/11-pseudoinverssi.odotettu" rivit="3-"}
```

Ennusteet ovat samat kuin kahden sarakkeen mallilla, koska
sarakeavaruus ei muuttunut; vain kertoimien jako sarakkeiden kesken on
mielivaltainen. Raja `rcond` päättää, mikä singulaariarvo on "nolla".
Jos pieni mutta nollasta poikkeava singulaariarvo käännetään, sen
käänteisluku kertoo mittauskohinan valtavaksi; katkaisu on
yksinkertaisin regularisoinnin muoto (taito *Numeeriset menetelmät*).
NumPyn `np.linalg.lstsq` ja `np.linalg.pinv` toimivat juuri näin.

## Matala-asteinen approksimaatio

Hajotelma voidaan kirjoittaa summana astetta 1 olevia matriiseja,
tärkeimmästä vähiten tärkeään:

$$A = \sigma_1 u_1 v_1^T + \sigma_2 u_2 v_2^T + \dots +
      \sigma_r u_r v_r^T.$$

Kun summa katkaistaan $k$ termin jälkeen, saadaan matriisi $A_k$,
jonka aste on $k$. **Eckartin–Youngin lauseen** mukaan se on paras
mahdollinen: mikään muu asteen $k$ matriisi ei ole lähempänä $A$:ta,
ja virhe on pois jätettyjen singulaariarvojen neliösumman neliöjuuri.

Harmaasävykuva on matriisi, jonka alkiot ovat kuvapisteiden
kirkkauksia. $A_k$:n tallentamiseen riittää $k$ singulaariarvoa ja
$k$ vektoriparia eli $k(m + n + 1)$ lukua alkuperäisen $mn$:n sijaan:

```{.python tiedosto="esimerkit/11-kuva.py" osa="kuva"}
```

```{.python tiedosto="esimerkit/11-kuva.py" osa="pakkaus"}
```

```{.tuloste tiedosto="esimerkit/11-kuva.odotettu" rivit="1-7"}
```

![Esimerkin 64 × 64 -kuva ja sen approksimaatiot asteilla 1–16.
Ensimmäinen termi tavoittaa vain pysty- ja vaakasuuntaisen
kirkkausjakauman; neljällä termillä muodot erottuvat, ja
kuudellatoista eroa alkuperäiseen ei näe. Oikealla alhaalla
singulaariarvot logaritmisella asteikolla: muutama ensimmäinen kantaa
lähes kaiken.](kuvat/matala-aste.png){width=100%}

```{.python tiedosto="esimerkit/11-kuva.py" osa="virhe"}
```

```{.tuloste tiedosto="esimerkit/11-kuva.odotettu" rivit="8-"}
```

Koordinaattiakselien suuntaiset piirteet (liukuväri, suorakulmio)
tiivistyvät muutamaan termiin, pyöreä kiekko vaatii enemmän. Oikeat
kuvanpakkausmenetelmät, kuten JPEG, käyttävät kiinteää kantaa
(kosinimuunnos) eivätkä kuvakohtaista hajotelmaa, mutta idea on sama:
vaihdetaan kantaan, jossa suurin osa kertoimista on pieniä, ja
jätetään pienet pois.

Sama katkaisu on pääkomponenttianalyysin ydin. Kun keskitetyn datan
matriisi (rivit mittauksia) hajotetaan, oikeat singulaarivektorit
ovat pääkomponentit ja $\sigma_i^2 / (m - 1)$ niiden varianssit.
Kovarianssimatriisia ei tarvitse muodostaa, mikä on sekä nopeampaa
että tarkempaa:

```{.python tiedosto="esimerkit/11-svd.py" osa="pca"}
```

```{.tuloste tiedosto="esimerkit/11-svd.odotettu" rivit="13-"}
```

Tulos on sama kuin luvun *Ominaisarvot ja ominaisvektorit*
kovarianssimatriisista laskettu.

## Käytännössä

- **Käytä hajotelmaa diagnostiikkaan.** Singulaariarvot kertovat
  yhdellä silmäyksellä asteen, ehtoluvun ja sen, onko matriisissa
  lähes riippuvia sarakkeita. Tulosta ne, kun sovitus tai ratkaisu
  käyttäytyy oudosti.
- **Pyydä vain tarvitsemasi.** `np.linalg.svd(A, compute_uv=False)`
  laskee pelkät singulaariarvot ja `full_matrices=False` jättää pois
  ne $U$:n ja $V$:n sarakkeet, joita summa ei käytä. Suurille
  matriiseille, joista tarvitaan vain muutama suurin termi,
  `scipy.sparse.linalg.svds` on iteratiivinen ja paljon halvempi.
- **Älä muodosta matriisia $A^T A$.** Singulaariarvot sen
  ominaisarvoista menettävät puolet merkitsevistä numeroista.
- **Valitse katkaisuraja tietoisesti.** Aste, pseudoinverssi ja
  matala-asteinen approksimaatio riippuvat siitä, mikä tulkitaan
  nollaksi. Kirjaston oletus sopii pyöristysvirheelle; mittauskohinalle
  raja asetetaan kohinan tason mukaan.
- **Hajotelma on kalliimpi kuin LU ja QR.** Työmäärä on samaa
  kertaluokkaa $O(mn^2)$ mutta vakiokerroin on monikertainen.
  Tavalliseen yhtälöryhmään käytetään LU:ta ja hyväkuntoiseen
  sovitukseen QR:ää; SVD on työkalu vaikeisiin tapauksiin.

## Itsearviointi

- Osaat selittää hajotelman $A = U \Sigma V^T$ geometrisesti kiertona,
  venytyksenä ja kiertona ja kuvata, miksi yksikköympyrän kuva on
  ellipsi.
- Osaat johtaa singulaariarvot matriisin $A^T A$ ominaisarvoista ja
  kertoa, miten singulaariarvot ja ominaisarvot eroavat.
- Osaat määrittää asteen ja ehtoluvun singulaariarvoista ja selittää,
  miksi aste on liukuluvuilla toleranssikysymys.
- Osaat ratkaista pienimmän neliösumman tehtävän pseudoinverssillä
  myös silloin, kun sarakkeet ovat lineaarisesti riippuvia.
- Osaat muodostaa matala-asteisen approksimaation ja arvioida sen
  virheen ja tallennustilan.
