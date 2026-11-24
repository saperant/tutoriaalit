# Matriisit ja tensorit muistissa

Muisti on yksiulotteinen jono tavuja. Matriisi, kuva tai neljän
ulottuvuuden tensori on tallennettava siihen jossakin järjestyksessä,
ja järjestys ratkaisee, kuinka nopeasti dataa voi lukea. Prosessori ei
lue muistia tavu kerrallaan vaan 64 tavun *välimuistirivi* kerrallaan
ja ennakoi peräkkäisiä lukuja. Peräkkäisten osoitteiden läpikäynti on
siksi moninkertaisesti nopeampaa kuin hyppiminen.

## Rivi- ja sarakejärjestys

C, C++, Python ja NumPy tallentavat matriisit oletuksena
*rivijärjestyksessä* (row-major): rivin alkiot ovat peräkkäin, ja
alkion $(i, j)$ paikka $n$-sarakkeisessa matriisissa on $i \cdot n + j$.
Fortran, MATLAB, Julia, R ja monet BLAS-rutiinit käyttävät
*sarakejärjestystä* (column-major), jossa sarake on peräkkäin.

```{.c tiedosto="esimerkit/09-jarjestys.c" osa="indeksi"}
```

Sama summa lasketaan kahdella silmukkajärjestyksellä. Riveittäin
kulkiessa jokainen välimuistirivi käytetään kokonaan. Sarakkeittain
jokainen alkio on eri välimuistirivillä ja usein eri muistisivulla:

```{.c tiedosto="esimerkit/09-jarjestys.c" osa="lapikaynti"}
```

Ohjelma tarkistaa testeissä vain, että summat ovat samat. Mittaus on
mielekäs vain optimoituna, joten Makefile kääntää sen valitsimella
`-O2` ja ajaa 4096 × 4096 -matriisilla (`make mittaa`). Sarakkeittainen
läpikäynti on tyypillisesti 5–10 kertaa hitaampi. Raja on kirjoitettu
väljäksi, jotta tulos ei riipu koneesta:

```{.tuloste tiedosto="esimerkit/09-jarjestys-mittaus.odotettu"}
```

## Askeleet

NumPy-taulukko on muistialue ja kuvaus siitä, miten indeksit
muunnetaan osoitteiksi. Kuvaus koostuu muodosta (`shape`) ja
askeleista (`strides`): askel kertoo, montako tavua siirrytään, kun
indeksi kasvaa yhdellä kyseisessä ulottuvuudessa. Rivijärjestyksessä
3 × 4 -matriisin `float64`-alkioilla askeleet ovat (32, 8).

Monet operaatiot muuttavat pelkkiä askeleita ja palauttavat *näkymän*
samaan muistiin. Transpoosi vaihtaa askelten järjestyksen, ja viipale
`[:, 1::2]` kaksinkertaistaa sarakeaskeleen. Kumpikaan ei kopioi
dataa:

```{.python tiedosto="esimerkit/09-askeleet.py" osa="askeleet"}
```

Näkymät ovat tehokkaita mutta yllättäviä. Näkymän kautta tehty
muutos näkyy alkuperäisessä taulukossa. Jotkin operaatiot taas
palauttavat kopion, jos tulosta ei voi esittää askelilla: transpoosin
`reshape` vaatii, että alkiot luetaan eri järjestyksessä kuin ne ovat
muistissa:

```{.python tiedosto="esimerkit/09-askeleet.py" osa="kopio"}
```

```{.tuloste tiedosto="esimerkit/09-askeleet.odotettu"}
```

Monet kirjastot, kuten C-laajennukset ja GPU-siirrot, vaativat yhtenäisen
(*contiguous*) taulukon. `np.ascontiguousarray` tekee kopion vain
tarvittaessa.

## Kuvat ja tensorit

Värikuva on kolmiulotteinen taulukko: korkeus, leveys ja kanavat. Kuvien
käsittelyssä (Pillow, OpenCV) kanavat ovat yleensä viimeisenä (*HWC*),
jolloin yhden pikselin värit ovat peräkkäin. Monet neuroverkkokirjastot
(PyTorch) haluavat kanavat ensin (*CHW*), jolloin kukin kanava on oma
yhtenäinen kuvansa. Neljäntenä ulottuvuutena on erä (*batch*): NCHW tai
NHWC.

Pikselit ovat yleensä `uint8`-arvoja, joten kirkastus kiertää kuten
luvussa 3. Laskenta tehdään leveämmässä tyypissä ja rajataan:

```{.python tiedosto="esimerkit/09-kuva.py" osa="kirkastus"}
```

Kanavien siirto on transpoosi eli pelkkä näkymä. Harmaasävymuunnos on
painotettu summa kanavien yli, joten se on matriisitulo:

```{.python tiedosto="esimerkit/09-kuva.py" osa="kanavat"}
```

```{.tuloste tiedosto="esimerkit/09-kuva.odotettu"}
```

Väärä järjestys on hidas tai väärä. Jos CHW-näkymä annetaan
kirjastolle, joka olettaa yhtenäisen taulukon, tulos on joko kopio tai
sekoittunut kuva. Järjestys kannattaa siksi nimetä muuttujiin tai
tyyppeihin.

## Käytännössä

- **Sisin silmukka kulkee peräkkäisiä osoitteita.** Rivijärjestyksessä
  sisin silmukka käy sarakeindeksin läpi. Sama sääntö pätee
  rakenteiden taulukoihin: kentät, joita käsitellään yhdessä, sijoitetaan
  vierekkäin.
- **Tunne kirjaston järjestys.** NumPy on rivijärjestyksessä, BLAS ja
  LAPACK usein sarakejärjestyksessä, PyTorch NCHW ja TensorFlow NHWC.
  Rajapinnalla tehdään tarvittaessa yksi tietoinen muunnos.
- **Tiedä, palauttaako operaatio näkymän vai kopion.** Viipaleet ja
  transpoosit ovat näkymiä, joten niiden kautta tehty muutos näkyy
  alkuperäisessä. `np.shares_memory` kertoo totuuden. Kopioi
  tarkoituksella (`.copy()`), jos tarvitset itsenäisen taulukon.
- **Yhtenäisyys ennen raskasta laskentaa.** Jos samaa ei-yhtenäistä
  näkymää luetaan monta kertaa, kertakopio yhtenäiseksi on halvempi
  kuin toistuvat hypyt.
- **Mittaa optimoituna.** Välimuistikokeet ja muut suorituskykymittaukset
  tehdään optimoidulla käännöksellä ilman sanitoijia. Taito
  *Suorituskyvyn analyysi ja optimointi* käsittelee mittaamista tarkemmin.

## Itsearviointi

- Osaat laskea alkion osoitteen rivi- ja sarakejärjestyksessä ja
  valita silmukkajärjestyksen välimuistin kannalta oikein.
- Osaat selittää NumPy-taulukon muodon ja askeleet ja ennustaa, onko
  operaation tulos näkymä vai kopio.
- Osaat muuntaa kuvan HWC- ja CHW-järjestyksen välillä ja käsitellä
  `uint8`-pikseleitä kiertymättä.
