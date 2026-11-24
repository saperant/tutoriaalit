# Harvat matriisit ja iteratiiviset menetelmät

Osittaisdifferentiaaliyhtälöiden diskretoinnit, piirit, verkostot ja
graafit tuottavat yhtälöryhmiä, joissa on miljoonia tuntemattomia mutta
jokainen yhtälö riippuu vain muutamasta naapurista. Tällainen matriisi
on **harva**: lähes kaikki alkiot ovat nollia. Tiheänä se ei mahdu
muistiin, eikä $n^3$-algoritmi valmistu. Tässä luvussa katsotaan,
miten harva matriisi tallennetaan, milloin suora harva ratkaisija riittää
ja miten iteratiiviset menetelmät ratkaisevat suuret tehtävät.

## Harva tallennus

Esimerkkinä on Poissonin yhtälö $-\nabla^2 u = f$ neliössä. Kun
neliö jaetaan $m \times m$ -hilaan ja toinen derivaatta korvataan
erotusosamäärällä, jokainen yhtälö sitoo hilapisteen neljään
naapuriinsa. Matriisi kootaan **Kroneckerin tulolla** yksiulotteisesta
kolmilävistäjämatriisista $T = \mathrm{tridiag}(-1, 2, -1)$.

```{.python tiedosto="esimerkit/07-harva.py" osa="poisson"}
```

**CSR-muoto** (compressed sparse row) tallentaa vain nollasta poikkeavat
alkiot, niiden sarakeindeksit ja rivien alkukohdat. Matriisi-vektoritulo
maksaa silloin nollasta poikkeavien alkioiden määrän verran.

```{.python tiedosto="esimerkit/07-harva.py" osa="koko"}
```

```{.python tiedosto="esimerkit/07-harva.py" osa="ratkaisu"}
```

```{.tuloste tiedosto="esimerkit/07-harva.odotettu"}
```

300 × 300 -hilan matriisi veisi tiheänä 65 gigatavua, harvana kuusi
megatavua. Kokoamiseen käytetään yleensä COO- tai LIL-muotoa, ja
laskentaan CSR- tai CSC-muotoa. SciPyn uudet `sparse.*_array`-luokat
noudattavat NumPyn taulukkosemantiikkaa: `@` on matriisitulo ja `*`
alkioittainen tulo.

**Suora harva ratkaisija** (`spsolve`, SuperLU tai UMFPACK) tekee
LU-hajotelman ja järjestää rivit ja sarakkeet niin, että
**täyttyminen** (fill-in) eli hajotelmaan syntyvät uudet nollasta
poikkeavat alkiot jää pieneksi. Kaksiulotteisille tehtäville se on
usein paras valinta satoihin tuhansiin tuntemattomiin asti. Kolmessa
ulottuvuudessa täyttyminen kasvaa nopeasti, ja iteratiiviset menetelmät
voittavat.

## Klassiset iteraatiot: Jacobi ja Gauss–Seidel

Iteratiivinen menetelmä parantaa arvausta $x_k$ askel kerrallaan ja
tarvitsee matriisista vain tulon $Ax$. **Jacobin menetelmä** ratkaisee
jokaisesta yhtälöstä lävistäjätuntemattoman muiden vanhoilla arvoilla.
**Gauss–Seidel** käyttää uusia arvoja heti, kun ne on laskettu.

```{.python tiedosto="esimerkit/07-iteraatiot.py" osa="jacobi"}
```

Molemmat ovat kiintopisteiteraatioita $x_{k+1} = Gx_k + c$ (luku 3),
ja ne suppenevat, jos iteraatiomatriisin $G$ **spektrisäde**
$\rho(G)$ eli itseisarvoltaan suurin ominaisarvo on alle 1. Virhe
pienenee joka kierroksella noin kertoimella $\rho(G)$. Poissonin
matriisille Jacobin spektrisäde on $\cos\bigl(\pi/(n+1)\bigr)$, joka on
hyvin lähellä ykköstä, ja Gauss–Seidelin spektrisäde on sen neliö:
Gauss–Seidel on kaksi kertaa nopeampi, mutta yhtä toivoton suurilla
$n$.

## Liittogradienttimenetelmä

Symmetriselle positiivisesti definiitille matriisille
**liittogradienttimenetelmä** (CG, conjugate gradient) on
paljon tehokkaampi. Se minimoi neliömuotoa
$\tfrac12 x^TAx - b^Tx$, jonka minimi on yhtälön $Ax = b$ ratkaisu, ja
valitsee hakusuunnat niin, että ne ovat keskenään $A$-ortogonaalisia.
Silloin jokainen askel minimoi virheen koko tähänastisessa aliavaruudessa.

```{.python tiedosto="esimerkit/07-iteraatiot.py" osa="cg"}
```

```{.python tiedosto="esimerkit/07-iteraatiot.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/07-iteraatiot.odotettu"}
```

![Suhteellinen jäännös kierroksen funktiona 30 tuntemattoman
Poissonin tehtävälle. Pisteviiva on lopetusraja.](kuvat/iteraatiot.png){width=62%}

Jacobi ja Gauss–Seidel tarvitsevat tuhansia kierroksia, ja määrät
vastaavat spektrisäteestä laskettua ennustetta (ennuste on hieman
varovainen, koska se olettaa pahimman alkuvirheen). Liittogradientti
ratkaisee tehtävän 15 kierroksessa. Tarkoilla luvuilla se löytäisi
ratkaisun enintään $n = 30$ kierroksessa, ja vielä vähemmässä, kun
oikea puoli sisältää vain osan ominaisvektoreista: tässä symmetrinen
oikea puoli herättää vain puolet ominaisvektoreista. Kuvasta näkyy myös
CG:n erikoisuus: jäännös ei pienene tasaisesti, koska menetelmä
minimoi virheen $A$-normissa eikä jäännöstä.

Liittogradientin kierrosten määrä on suunnilleen verrannollinen
neliöjuureen ehtoluvusta, $\sqrt{\kappa(A)}$. Poissonin matriisin
ehtoluku kasvaa kuten $n^2$ yhdessä ulottuvuudessa, joten CG skaalautuu
paljon paremmin kuin klassiset iteraatiot. Epäsymmetrisille
matriiseille vastaavat menetelmät ovat **GMRES** ja **BiCGSTAB**
(`scipy.sparse.linalg.gmres`, `bicgstab`).

## Esiehdostus

Kierrosten määrä riippuu ehtoluvusta, joten tehtävä kannattaa muuttaa
hyväkuntoisemmaksi. **Esiehdostin** $M \approx A$ on matriisi, jonka
yhtälöryhmä ratkeaa halvalla, ja iteraatio ratkaisee tehtävän
$M^{-1}Ax = M^{-1}b$. Hyvä esiehdostin on kompromissi: $M = A$
ratkaisisi tehtävän yhdellä kierroksella mutta olisi yhtä kallis kuin
alkuperäinen tehtävä, ja $M = I$ ei auta lainkaan.

Tavallisia esiehdostimia ovat lävistäjä (Jacobi), **epätäydellinen
LU tai Cholesky** (ILU, IC), jossa hajotelma lasketaan, mutta
täyttymistä ei sallita, sekä **monihilamenetelmät** (multigrid), jotka
ratkaisevat tehtävän karkeammilla hiloilla ja saavuttavat
osittaisdifferentiaaliyhtälöille kierrosmäärän, joka ei kasva hilan
tihentyessä. SciPyssä `spilu` tuottaa epätäydellisen LU:n, ja
PyAMG-kirjasto toteuttaa algebrallisen monihilan.

## Sama Octavella

```{.octave tiedosto="esimerkit/octave/07-pcg.m"}
```

```{.tuloste tiedosto="esimerkit/octave/07-pcg.odotettu"}
```

Octavessa `spdiags`, `speye` ja `kron` kokoavat harvan matriisin,
`pcg` on esiehdostettu liittogradientti ja `ichol` epätäydellinen
Cholesky. Esiehdostettu iteraatio suppenee tässä yli kaksi kertaa
vähemmillä kierroksilla.

## Käytännössä

- **Tallenna harva matriisi harvana alusta asti.** Tiheän matriisin
  muodostaminen ja muuntaminen voi jo kuluttaa koko muistin.
- **Kokeile ensin suoraa harvaa ratkaisijaa.** `spsolve` ei tarvitse
  parametreja, ja kaksiulotteisille tehtäville se on usein nopein.
- **Symmetriselle positiivisesti definiitille matriisille CG,
  muille GMRES tai BiCGSTAB.** Jacobi ja Gauss–Seidel ovat nykyään
  lähinnä monihilan tasoittimia.
- **Esiehdostus ratkaisee iteratiivisen menetelmän tehon.** Ilman sitä
  iteratiivinen menetelmä on harvoin kilpailukykyinen.
- **Lopetusehto on suhteellinen jäännös**, ja sen kannattaa suhteuttaa
  diskretointivirheeseen: yhtälöryhmää ei kannata ratkaista tarkemmin
  kuin malli on tarkka.
- **Matriisivapaa ratkaisu**: iteratiiviset menetelmät tarvitsevat vain
  tulon $Ax$. `scipy.sparse.linalg.LinearOperator` sallii matriisin
  korvaamisen funktiolla, jolloin suurtakaan matriisia ei tallenneta.

## Itsearviointi

- Osaat koota harvan matriisin ja selittää CSR-muodon edut.
- Osaat valita suoran harvan ratkaisijan ja iteratiivisen menetelmän
  välillä tehtävän koon ja ulottuvuuden perusteella.
- Osaat toteuttaa Jacobin, Gauss–Seidelin ja liittogradientin ja
  selittää niiden suppenemisen spektrisäteen ja ehtoluvun avulla.
- Osaat selittää esiehdostuksen idean ja nimetä tavallisimmat
  esiehdostimet.
- Osaat ratkaista suuren harvan tehtävän SciPyllä ja Octavella.
