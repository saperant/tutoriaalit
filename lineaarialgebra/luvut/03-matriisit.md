# Matriisit ja lineaarikuvaukset

Matriisi on lukutaulukko, mutta hyödyllisempää on ajatella sitä
**kuvauksena**: $m \times n$-matriisi $A$ vie $n$-ulotteisen vektorin
$x$ $m$-ulotteiseksi vektoriksi $Ax$. Kuvaus on **lineaarinen**: se
säilyttää summat ja skalaarimonikerrat,

$$A(u + v) = Au + Av, \qquad A(k u) = k\,Au.$$

Geometrisesti lineaarikuvaus pitää suorat suorina, yhdensuuntaiset
yhdensuuntaisina ja origon paikallaan. Kierrot, skaalaukset,
leikkaukset, peilaukset ja projektiot ovat lineaarikuvauksia; siirto ei
ole (se liikuttaa origoa), ja siihen palataan luvussa 11.

## Matriisi ja vektori

Tulossa $y = Ax$ alkio $y_i$ on $A$:n rivin $i$ ja vektorin $x$
pistetulo. Saman tuloksen saa toisinkin päin luettuna: $Ax$ on $A$:n
sarakkeiden lineaarikombinaatio, jonka kertoimet ovat $x$:n alkiot.

$$Ax = x_1 a_1 + x_2 a_2 + \dots + x_n a_n,$$

missä $a_j$ on $A$:n sarake $j$. Jälkimmäinen tulkinta kertoo, mitä
matriisi tekee: **sarakkeet ovat kantavektorien kuvat**. Ensimmäinen
sarake on se, mihin $e_1 = (1, 0, \dots)$ kuvautuu, toinen se, mihin
$e_2$ kuvautuu, ja niin edelleen. Kun tiedät, mihin kuvaus vie
kantavektorit, tiedät matriisin.

## Tason peruskuvaukset

Tason kierto kulman $\theta$ verran vastapäivään vie $e_1$:n pisteeseen
$(\cos\theta, \sin\theta)$ ja $e_2$:n pisteeseen
$(-\sin\theta, \cos\theta)$. Nämä ovat kiertomatriisin sarakkeet:

$$R(\theta) = \begin{pmatrix} \cos\theta & -\sin\theta \\
                              \sin\theta & \cos\theta \end{pmatrix}.$$

Skaalaus on lävistäjämatriisi, ja leikkaus siirtää pisteitä
vaakasuunnassa sitä enemmän, mitä korkeammalla ne ovat (kursivointi).

```{.python tiedosto="esimerkit/03-kuvaukset.py" osa="kuvaukset"}
```

```{.python tiedosto="esimerkit/03-kuvaukset.py" osa="sarakkeet"}
```

## Yhdistetty kuvaus on matriisitulo

Kun ensin tehdään kuvaus $B$ ja sitten kuvaus $A$, tulos on
$A(Bx) = (AB)x$. Yhdistetyn kuvauksen matriisi on siis matriisitulo
$AB$, ja **oikeanpuoleisin tehdään ensin**. Matriisitulo ei yleensä ole
vaihdannainen: skaalaus ja kierto eri järjestyksessä tuottavat eri
kuvion.

```{.python tiedosto="esimerkit/03-kuvaukset.py" osa="yhdistaminen"}
```

```{.tuloste tiedosto="esimerkit/03-kuvaukset.odotettu"}
```

Tason kierrot ovat poikkeus: ne vaihtuvat keskenään, koska kaksi
kiertoa on vain kulmien summa. Kolmiulotteiset kierrot eri akselien
ympäri eivät vaihdu, mikä on yksi syy siihen, miksi 3D-kierrot ovat
hankalia (luku 8).

## Matriisitulo itse toteutettuna

Matriisitulossa $C = AB$ alkio $c_{ij}$ on $A$:n rivin $i$ ja $B$:n
sarakkeen $j$ pistetulo. Tulo on määritelty, kun $A$:ssa on yhtä monta
saraketta kuin $B$:ssä rivejä: $(m \times n)(n \times p) = m \times p$.
**Transpoosi** $A^T$ vaihtaa rivit ja sarakkeet, ja tulon transpoosi on
transpoosien tulo käänteisessä järjestyksessä: $(AB)^T = B^T A^T$.

```{.python tiedosto="esimerkit/03-matriisitulo.py" osa="tulo"}
```

```{.python tiedosto="esimerkit/03-matriisitulo.py" osa="tarkistus"}
```

```{.python tiedosto="esimerkit/03-matriisitulo.py" osa="hinta"}
```

```{.tuloste tiedosto="esimerkit/03-matriisitulo.odotettu"}
```

Matriisitulon työmäärä kasvaa kuutiollisesti. Siksi suurten matriisien
tulo lasketaan aina optimoidulla kirjastolla (BLAS), joka hyödyntää
välimuistia, vektorikäskyjä ja ytimiä. Taito *Miten tietokone laskee*
näyttää, miten silmukkajärjestys ja lohkominen vaikuttavat nopeuteen;
puhtaan Pythonin silmukka on satoja kertoja hitaampi kuin NumPyn `@`.

## Käytännössä

- **Lue matriisi sarakkeittain.** Kun haluat tietää, mitä matriisi
  tekee, katso sarakkeita: ne ovat kantavektorien kuvat. Kun rakennat
  matriisia, kirjoita sarakkeiksi se, mihin akselien haluat päätyvän.
- **Kirjoita kuvausten järjestys koodiin näkyviin.** `M = T @ R @ S`
  tarkoittaa: ensin skaalaus, sitten kierto, sitten siirto. Väärä
  järjestys on yleisin grafiikkavirhe, ja se näkyy vasta, kun
  kuvaukset eivät vaihdu keskenään.
- **Yhdistä kuvaukset ennen kuin sovellat niitä.** Tuhannen pisteen
  kuvaaminen kolmella matriisilla erikseen maksaa kolme kertaa
  enemmän kuin yhdellä esilasketulla tulolla.
- **Tarkista muodot.** NumPy `@` kaatuu, jos muodot eivät sovi, mutta
  yksiulotteinen taulukko tulkitaan tilanteen mukaan riviksi tai
  sarakkeeksi. Pidä muodot eksplisiittisinä (`(3,)`, `(3, 1)` vai
  `(1, 3)`) ja tarkista `shape` epäselvissä kohdissa.
- **Älä toteuta matriisituloa itse tuotantokoodissa.** Oma toteutus on
  opetusväline. BLAS-kirjastot ovat vuosikymmenten optimoinnin tulos.

## Itsearviointi

- Osaat tulkita matriisin ja vektorin tulon sekä rivien pistetuloina
  että sarakkeiden lineaarikombinaationa.
- Osaat muodostaa tason kierto-, skaalaus- ja leikkausmatriisin
  kantavektorien kuvista.
- Osaat yhdistää kuvaukset matriisituloksi oikeassa järjestyksessä ja
  perustella, miksi järjestyksellä on väliä.
- Osaat toteuttaa matriisitulon ja transpoosin sekä arvioida
  matriisitulon työmäärän.
