# Matriisitulo ja BLAS

Matriisitulo $C = AB$ on numeerisen laskennan ja koneoppimisen
tärkein yksittäinen operaatio. $n \times n$ -matriiseilla se vaatii
$2n^3$ liukulukuoperaatiota ja käyttää $3n^2$ lukua, joten jokaista
lukua käytetään $n$ kertaa. Hyvä toteutus pitää luvut välimuistissa
käyttökertojen välillä. Huono toteutus hakee ne joka kerta muistista
ja on kymmeniä kertoja hitaampi.

## Silmukkajärjestys

Oppikirjan toteutus laskee jokaisen tuloalkion pistetulona: rivi
$A$:sta ja sarake $B$:stä. Sarake on rivijärjestyksessä hajallaan,
joten sisin silmukka hyppii $B$:n riviltä toiselle:

```{.c tiedosto="esimerkit/10-matriisitulo.c" osa="ijk"}
```

Kun silmukat vaihdetaan järjestykseen *ikj*, sisin silmukka kulkee
$B$:n ja $C$:n rivejä peräkkäin. Laskutoimitukset ovat samat, vain
summausjärjestys muuttuu. Kääntäjä voi lisäksi vektoroida sisimmän
silmukan SIMD-käskyiksi, koska sen iteraatiot ovat riippumattomia:

```{.c tiedosto="esimerkit/10-matriisitulo.c" osa="ikj"}
```

## Lohkominen

Suurilla matriiseilla $B$:n rivit eivät mahdu välimuistiin, joten
ikj-järjestyskin hakee ne muistista $n$ kertaa. *Lohkominen* (tiling)
jakaa matriisit pieniin osamatriiseihin, jotka mahtuvat välimuistiin, ja
laskee tulon osamatriisi kerrallaan. Jokainen lohko käytetään moneen
kertaan ennen kuin seuraava haetaan:

```{.c tiedosto="esimerkit/10-matriisitulo.c" osa="lohkottu"}
```

Testeissä ohjelma tarkistaa, että kaikki toteutukset antavat saman
tuloksen pyöristysvirheen tarkkuudella. Tulokset eivät ole bittitarkasti
samat, koska summausjärjestys eroaa. `make mittaa` vertaa nopeutta
512 × 512 -matriiseilla:

```{.tuloste tiedosto="esimerkit/10-matriisitulo-mittaus.odotettu"}
```

Tyypillisesti ikj ja lohkottu versio ovat 4–10 kertaa nopeampia kuin
ijk. Ero kasvaa matriisien koon mukana, kun data ei enää mahdu
välimuistiin.

## BLAS

Ammattimainen matriisitulo on vielä kymmeniä kertoja nopeampi kuin
lohkottu C-silmukka. BLAS-kirjastot (*Basic Linear Algebra
Subprograms*), kuten OpenBLAS, Intel oneMKL, Apple Accelerate ja BLIS,
käyttävät käsin optimoituja ytimiä. Ne lohkovat jokaiselle
välimuistitasolle erikseen, järjestävät lohkot uudelleen yhtenäisiksi
(*packing*), pitävät osan tuloksesta rekistereissä ja käyttävät
prosessorin leveimpiä SIMD- ja FMA-käskyjä sekä kaikkia ytimiä.

NumPyn `@`-operaattori kutsuu BLAS-kirjaston rutiinia `dgemm`.
Pythonin silmukoihin verrattuna ero on valtava, koska jokainen
Python-tason kertolasku on oliokäsittelyä:

```{.python tiedosto="esimerkit/10-blas.py" osa="silmukat"}
```

```{.python tiedosto="esimerkit/10-blas.py" osa="blas"}
```

Tarkkuuden ja muistin välillä tehdään sama valinta kuin luvussa 8:
`float32` puolittaa muistin ja tuplaa SIMD-leveyden, mutta tulos on
tarkka vain noin seitsemällä numerolla:

```{.python tiedosto="esimerkit/10-blas.py" osa="tyyppi"}
```

```{.tuloste tiedosto="esimerkit/10-blas.odotettu"}
```

## Mittasuhteet

Laskennan nopeus mitataan liukulukuoperaatioina sekunnissa (FLOPS).
Kannettavan tietokoneen ydin laskee FMA-käskyillä useita kymmeniä
miljardeja `double`-operaatioita sekunnissa, ja koko prosessori satoja.
Muistista saadaan samassa ajassa vain muutama miljardi lukua. Laskenta,
joka käyttää jokaista luettua lukua vain kerran (vektorien summa), on
siksi muistin rajoittamaa. Matriisitulo käyttää jokaista lukua $n$
kertaa ja voi saavuttaa laskentayksikön huippunopeuden. Taito
*Suorituskyvyn analyysi ja optimointi* esittelee tähän perustuvan roofline-mallin.

## Käytännössä

- **Älä kirjoita omaa matriisituloa tuotantoon.** BLAS-kirjasto on
  nopeampi, testatumpi ja hyödyntää kaikki ytimet. NumPy, Eigen,
  PyTorch ja muut kutsuvat sitä automaattisesti.
- **Muotoile laskenta matriisituloiksi.** Monta pientä
  matriisi-vektoritulona tehtyä laskua on usein nopeampi koota
  yhdeksi matriisituloksi, koska silloin dataa käytetään uudelleen.
  Koneoppimisen erät (*batch*) perustuvat tähän.
- **Kun oma silmukka on välttämätön, järjestä se.** Sisin silmukka
  peräkkäisiin osoitteisiin, lohkominen suurilla matriiseilla ja
  optimoitu käännös. Tarkista tulos toleranssilla vertailutoteutusta
  vastaan.
- **Säikeiden määrä on päätös.** BLAS käyttää oletuksena kaikkia ytimiä.
  Jos sovellus rinnakkaistaa itse, BLAS-säikeet rajataan
  (`OPENBLAS_NUM_THREADS=1`), ettei säikeitä ole liikaa.

## Itsearviointi

- Osaat selittää, miksi ijk-järjestyksen matriisitulo on hidas ja miten
  ikj-järjestys ja lohkominen korjaavat sen.
- Osaat laskea matriisitulon operaatiomäärän ja datan uudelleenkäytön.
- Osaat kertoa, mitä BLAS-kirjasto tekee ja miksi se on nopeampi kuin
  oma silmukka.
- Osaat arvioida, onko laskenta muistin vai laskentayksikön
  rajoittamaa.
