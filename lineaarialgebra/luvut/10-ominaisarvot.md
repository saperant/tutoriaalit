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

```{.python tiedosto="esimerkit/10-markov.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/10-markov.odotettu"}
```

Sama idea on Googlen alkuperäisen PageRank-algoritmin ytimessä:
verkkosivujen tärkeys on linkkimatriisin tasapainojakauma, ja se
lasketaan potenssimenetelmällä miljardien sivujen matriisille, koska
matriisi on harva ja kertolasku on halpa.

## Diagonalisointi

Jos $n \times n$-matriisilla on $n$ lineaarisesti riippumatonta
ominaisvektoria, se voidaan kirjoittaa muotoon

$$A = V D V^{-1},$$

missä $V$:n sarakkeet ovat ominaisvektoreita ja $D$ on lävistäjä-
matriisi ominaisarvoista. Silloin $A^k = V D^k V^{-1}$, ja potenssi
lasketaan korottamalla lävistäjän alkiot potenssiin. Fibonaccin
lukujono on klassinen esimerkki: sen siirtymämatriisin ominaisarvot
ovat kultainen leikkaus $\varphi$ ja $-1/\varphi$, mistä seuraa
suljettu kaava (Binet'n kaava).

```{.python tiedosto="esimerkit/10-fibonacci.py" osa="matriisi"}
```

```{.python tiedosto="esimerkit/10-fibonacci.py" osa="diagonalisointi"}
```

```{.python tiedosto="esimerkit/10-fibonacci.py" osa="raja"}
```

```{.tuloste tiedosto="esimerkit/10-fibonacci.odotettu"}
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

**Pääkomponenttianalyysi** (PCA) etsii datan kovarianssimatriisin
ominaisvektorit. Suurimman ominaisarvon vektori on suunta, jossa data
vaihtelee eniten, ja ominaisarvo on vaihtelun määrä. PCA:ta käytetään
datan ulottuvuuksien vähentämiseen, kohinan suodatukseen ja
pääakselien löytämiseen.

```{.python tiedosto="esimerkit/10-pca.py" osa="data"}
```

```{.python tiedosto="esimerkit/10-pca.py" osa="pca"}
```

```{.tuloste tiedosto="esimerkit/10-pca.odotettu"}
```

Anturin värähtely löytyy kohinan keskeltä noin puolen asteen
tarkkuudella, ja yksi komponentti selittää lähes kaiken vaihtelun.
Kaksiulotteinen data voidaan siis tiivistää yhdeksi luvuksi
mittausta kohti.

## Käytännössä

- **Symmetriselle matriisille `eigh`, muille `eig`.** `eigh` on
  nopeampi, palauttaa reaaliset arvot nousevassa järjestyksessä ja
  ortonormaalit vektorit; `eig` voi palauttaa kompleksilukuja.
- **Ominaisvektorin etumerkki on vapaa.** Jos $v$ on ominaisvektori,
  myös $-v$ on. Kiinnitä etumerkki itse (esimerkiksi ensimmäinen alkio
  positiivinen), jos tulosta verrataan tai tallennetaan.
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
- Osaat toteuttaa potenssimenetelmän ja arvioida sen
  lähestymisnopeuden ominaisarvojen suhteesta.
- Osaat laskea Markovin ketjun tasapainojakauman ominaisvektorina.
- Osaat diagonalisoida matriisin ja käyttää sitä potenssien
  laskemiseen.
- Osaat tehdä pääkomponenttianalyysin kovarianssimatriisin
  ominaisvektoreilla ja tulkita tuloksen.
