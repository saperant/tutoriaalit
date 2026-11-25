# Ominaisarvot ja ominaisvektorit

Useimmat vektorit muuttavat suuntaansa, kun niihin sovelletaan
matriisia. Joillakin suunnilla matriisi vain venyttää tai kutistaa:

$$A v = \lambda v.$$

Tällainen $v \neq 0$ on **ominaisvektori** ja kerroin $\lambda$ sen
**ominaisarvo**. Ominaisvektorit ovat kuvauksen luonnolliset akselit.
Niiden kannassa matriisi on lävistäjämatriisi, ja monimutkainen
toistuva kuvaus hajoaa riippumattomiksi skaalauksiksi.

Ominaisarvot kertovat, mitä toistuvassa soveltamisessa tapahtuu:
värähtelyn ominaistaajuudet, Markovin ketjun tasapaino, dynaamisen
järjestelmän stabiilisuus ($|\lambda| < 1$ vaimenee, $|\lambda| > 1$
räjähtää) ja datan pääsuunnat.

![Kuvaus $A = \begin{pmatrix} 2 & 1 \\ 1 & 2 \end{pmatrix}$ vie
yksikköympyrän pisteet ellipsille (harmaat nuolet). Useimmat suunnat
kääntyvät, mutta kaksi ei: suunta $(1, 1)$ venyy kolminkertaiseksi ja
suunta $(-1, 1)$ pysyy paikallaan. Ne ovat ominaisvektorit, ja
venytyskertoimet 3 ja 1 ovat
ominaisarvot.](kuvat/ominaisvektorit.png){width=50%}

## Ominaisarvot käsin: karakteristinen yhtälö

Yhtälö $Av = \lambda v$ on sama kuin $(A - \lambda I)v = 0$. Sillä on
nollasta poikkeava ratkaisu $v$ täsmälleen silloin, kun matriisi
$A - \lambda I$ on singulaarinen eli sen determinantti on nolla (luku
*Determinantti ja käänteismatriisi*). Ominaisarvot ovat siis
**karakteristisen yhtälön**

$$\det(A - \lambda I) = 0$$

juuret. $2 \times 2$-matriisille yhtälö on toista astetta:

$$\lambda^2 - (a + d)\,\lambda + (ad - bc) = 0, \qquad
  A = \begin{pmatrix} a & b \\ c & d \end{pmatrix}.$$

Kerroin $a + d$ on matriisin **jälki** (lävistäjän summa) ja vakiotermi
sen determinantti. Kuvan matriisille yhtälö on
$\lambda^2 - 4\lambda + 3 = 0$, josta $\lambda = 3$ ja $\lambda = 1$.
Ominaisvektori saadaan sijoittamalla ominaisarvo takaisin:
$(A - 3I)v = 0$ antaa $v = (1, 1)$.

```{.python tiedosto="esimerkit/10-karakteristinen.py" osa="karakteristinen"}
```

```{.tuloste tiedosto="esimerkit/10-karakteristinen.odotettu" rivit="1-4"}
```

Neljä matriisia näyttävät neljä eri tilannetta. Symmetrisellä
matriisilla ominaisarvot ovat reaaliset. Fibonaccin matriisin
ominaisarvot ovat kultainen leikkaus $\varphi$ ja $-1/\varphi$, joihin
palataan osiossa *Diagonalisointi*. Leikkauksella on kaksinkertainen
ominaisarvo 1 mutta vain yksi ominaisvektorin suunta, joten sitä ei
voi diagonalisoida. Kierrolla ei ole reaalista ominaisvektoria, koska
se kääntää jokaisen suunnan: ominaisarvot ovat kompleksiluvut
$e^{\pm i\theta}$, joiden itseisarvo on 1 ja vaihekulma kiertokulma.
Kompleksiluvut käsitellään taidossa *Kompleksiluvut ja
Fourier-analyysi*.

```{.python tiedosto="esimerkit/10-karakteristinen.py" osa="jalki"}
```

```{.tuloste tiedosto="esimerkit/10-karakteristinen.odotettu" rivit="5-"}
```

Ominaisarvojen summa on aina jälki ja tulo determinantti. Tulo selittää
luvun *Determinantti ja käänteismatriisi* havainnon: matriisi on
singulaarinen täsmälleen silloin, kun jokin ominaisarvo on nolla.
Suuremmille matriiseille karakteristista polynomia ei käytetä
laskentaan, koska korkea-asteisen polynomin juuret ovat herkkiä
kertoimien pyöristysvirheille. Kirjastot käyttävät iteratiivisia
menetelmiä, joista yksinkertaisin on potenssimenetelmä.

## Potenssimenetelmä

Kun vektoria kerrotaan matriisilla yhä uudelleen, suurimman
ominaisarvon suuntainen komponentti kasvaa nopeimmin ja vie lopulta
voiton. Tämä on **potenssimenetelmä**: kerro, normalisoi, toista.
Lähestymisnopeuden määrää toiseksi suurimman ja suurimman ominaisarvon
suhde $|\lambda_2 / \lambda_1|$.

```{.python tiedosto="esimerkit/10-markov.py" osa="potenssi"}
```

## Esimerkki: Markovin ketju

Verkkokaupan kävijä siirtyy sivulta toiselle tietyin todennäköisyyksin.
Siirtymämatriisin sarake $j$ sisältää todennäköisyydet siirtyä sivulta
$j$ muille sivuille, joten sarakkeiden summa on 1. Jos $p$ on
todennäköisyysjakauma sivuilla nyt, $Pp$ on jakauma seuraavalla
askeleella. Pitkän ajan **tasapainojakauma** toteuttaa $Pp = p$: se
on ominaisarvoa 1 vastaava ominaisvektori.

```{.python tiedosto="esimerkit/10-markov.py" osa="ketju"}
```

```{.tuloste tiedosto="esimerkit/10-markov.odotettu" rivit="1-5"}
```

```{.python tiedosto="esimerkit/10-markov.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/10-markov.odotettu" rivit="6-"}
```

![Potenssimenetelmän virhe esimerkin Markovin ketjussa. Logaritmisella
asteikolla pisteet asettuvat suoralle, jonka kulmakertoimen määrää
toiseksi suurin ominaisarvo: joka kierros kertoo virheen luvulla
$\lvert\lambda_2\rvert = 0{,}251$.](kuvat/potenssi.png){width=58%}

Sama idea on Googlen alkuperäisen PageRank-algoritmin ytimessä:
verkkosivujen tärkeys on linkkimatriisin tasapainojakauma, ja se
lasketaan potenssimenetelmällä miljardien sivujen matriisille, koska
matriisi on harva ja kertolasku on halpa.

## Diagonalisointi

Jos $n \times n$-matriisilla on $n$ lineaarisesti riippumatonta
ominaisvektoria, se voidaan kirjoittaa muotoon

$$A = V D V^{-1},$$

missä $V$:n sarakkeet ovat ominaisvektoreita ja $D$ on
lävistäjämatriisi ominaisarvoista. Silloin $A^k = V D^k V^{-1}$, ja potenssi
lasketaan korottamalla lävistäjän alkiot potenssiin. Fibonaccin
lukujono on klassinen esimerkki: sen siirtymämatriisin ominaisarvot
ovat kultainen leikkaus $\varphi$ ja $-1/\varphi$, mistä seuraa
suljettu kaava (Binet'n kaava). Sama hajotelma ratkaisee lineaariset
differentiaaliyhtälöryhmät: ominaisarvot määräävät, vaimeneeko,
kasvaako vai värähteleekö ratkaisu (taito *Differentiaaliyhtälöt ja
Laplace-muunnos*).

```{.python tiedosto="esimerkit/10-fibonacci.py" osa="matriisi"}
```

```{.tuloste tiedosto="esimerkit/10-fibonacci.odotettu" rivit="1-1"}
```

```{.python tiedosto="esimerkit/10-fibonacci.py" osa="diagonalisointi"}
```

```{.tuloste tiedosto="esimerkit/10-fibonacci.odotettu" rivit="2-4"}
```

```{.python tiedosto="esimerkit/10-fibonacci.py" osa="raja"}
```

```{.tuloste tiedosto="esimerkit/10-fibonacci.odotettu" rivit="5-"}
```

Suljettu kaava on kaunis mutta käytännössä rajallinen: 64-bittisen
liukuluvun 53 bitin tarkkuus loppuu, kun luvut kasvavat. Tarkka
kokonaislukulaskenta on oikea työkalu, kun tulos on kokonaisluku.

## Symmetriset matriisit ja pääkomponentit

Symmetrisillä matriiseilla ($A = A^T$) on erityisen hyvät
ominaisuudet: ominaisarvot ovat reaalisia ja ominaisvektorit voidaan
valita kohtisuoriksi, joten $A = Q D Q^T$ ortogonaalisella $Q$:lla
(**spektraalilause**). Kovarianssimatriisit, jäykkyysmatriisit ja
etäisyyksiin perustuvat matriisit ovat symmetrisiä. NumPyssa niille on
oma, nopeampi ja tarkempi funktio `np.linalg.eigh`.

Symmetrinen matriisi on **positiivisesti definiitti**, jos
$x^T A x > 0$ kaikilla $x \neq 0$. Yhtäpitävä ehto on, että kaikki
ominaisarvot ovat positiivisia: ominaisvektorien kannassa
$x^T A x = \sum \lambda_i c_i^2$. Jos ominaisarvot ovat
ei-negatiivisia, matriisi on positiivisesti semidefiniitti.
Positiivisesti definiitille matriisille on olemassa Choleskyn
hajotelma $A = LL^T$ (luku *LU-hajotelma*), ja sen yritys on myös
nopein tapa testata definiittisyys.

**Pääkomponenttianalyysi** (PCA) etsii datan kovarianssimatriisin
ominaisvektorit. Kovarianssimatriisin lävistäjällä ovat muuttujien
varianssit ja muissa alkioissa niiden kovarianssit, jotka kertovat,
vaihtelevatko muuttujat yhdessä (taito *Todennäköisyys ja tilastot*).
Matriisi on symmetrinen ja positiivisesti semidefiniitti. Suurimman
ominaisarvon vektori on suunta, jossa data
vaihtelee eniten, ja ominaisarvo on vaihtelun määrä. PCA:ta käytetään
datan ulottuvuuksien vähentämiseen, kohinan suodatukseen ja
pääakselien löytämiseen.

```{.python tiedosto="esimerkit/10-pca.py" osa="data"}
```

```{.python tiedosto="esimerkit/10-pca.py" osa="pca"}
```

```{.tuloste tiedosto="esimerkit/10-pca.odotettu" rivit="1-4"}
```

![Anturidata ja kovarianssimatriisin ominaisvektorit. Nuolen pituus on
kaksi keskihajontaa eli $2\sqrt{\lambda}$. Ensimmäinen pääkomponentti
osoittaa värähtelyn suuntaan, toinen on sitä vastaan kohtisuorassa ja
kuvaa kohinaa.](kuvat/pca.png){width=60%}

Anturin värähtely löytyy kohinan keskeltä noin puolen asteen
tarkkuudella, ja yksi komponentti selittää lähes kaiken vaihtelun.
Kaksiulotteinen data voidaan siis tiivistää yhdeksi luvuksi
mittausta kohti. Kovarianssimatriisin definiittisyys näkyy samasta
datasta:

```{.python tiedosto="esimerkit/10-pca.py" osa="definiitti"}
```

```{.tuloste tiedosto="esimerkit/10-pca.odotettu" rivit="5-"}
```

## Käytännössä

- **Symmetriselle matriisille `eigh`, muille `eig`.** `eigh` on
  nopeampi, palauttaa reaaliset arvot nousevassa järjestyksessä ja
  ortonormaalit vektorit; `eig` voi palauttaa kompleksilukuja.
- **Ominaisvektorin etumerkki on vapaa.** Jos $v$ on ominaisvektori,
  myös $-v$ on. Kiinnitä etumerkki itse (esimerkiksi ensimmäinen alkio
  positiivinen), jos tulosta verrataan tai tallennetaan.
- **Laske ominaisarvot kirjastolla, älä karakteristisesta
  polynomista.** Polynomin juuret ovat herkkiä kertoimien virheille;
  käsin laskeminen kelpaa $2 \times 2$-matriisille ja ymmärtämiseen.
- **Suurille harvoille matriiseille iteratiivinen menetelmä.** Kun
  tarvitaan vain muutama ominaisarvo, `scipy.sparse.linalg.eigsh`
  (Lanczos) tai potenssimenetelmä on paljon halvempi kuin kaikkien
  arvojen laskeminen.
- **Keskitä data ennen PCA:ta.** Ilman keskitystä ensimmäinen
  "pääkomponentti" osoittaa datan keskiarvoon eikä vaihtelun suuntaan.
  Eri yksiköissä mitatut muuttujat skaalataan lisäksi yhtä suuriksi.
- **Stabiilisuus on ominaisarvo-ominaisuus.** Toistuva päivitys
  $x_{k+1} = A x_k$ (suodin, simulaatio, peli) pysyy rajoitettuna vain,
  jos kaikki $|\lambda| \leq 1$.

## Itsearviointi

- Osaat selittää ominaisarvon ja -vektorin geometrisesti ja
  tarkistaa yhtälön $Av = \lambda v$.
- Osaat laskea $2 \times 2$-matriisin ominaisarvot karakteristisesta
  yhtälöstä ja selittää, miksi kierron ominaisarvot ovat kompleksisia.
- Osaat määritellä positiivisesti definiitin matriisin ja testata
  definiittisyyden.
- Osaat toteuttaa potenssimenetelmän ja arvioida sen
  lähestymisnopeuden ominaisarvojen suhteesta.
- Osaat laskea Markovin ketjun tasapainojakauman ominaisvektorina.
- Osaat diagonalisoida matriisin ja käyttää sitä potenssien
  laskemiseen.
- Osaat tehdä pääkomponenttianalyysin kovarianssimatriisin
  ominaisvektoreilla ja tulkita tuloksen.
