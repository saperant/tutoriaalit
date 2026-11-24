# Aliavaruudet, kanta ja kannanvaihto

Koordinaatit eivät ole vektorin ominaisuus vaan valinta. Sama nuoli
voidaan kuvata itä–pohjoinen-koordinaatistossa, kadun suuntaisessa
koordinaatistossa tai kameran koordinaatistossa. Sama väri voidaan
kuvata punaisen, vihreän ja sinisen määrinä tai kirkkautena ja
kahtena värierona. Hyvin valittu koordinaatisto tekee monimutkaisesta
tehtävästä yksinkertaisen, ja tämän luvun käsitteet kertovat, milloin
valinta on mahdollinen.

## Virittäminen ja lineaarinen riippumattomuus

Vektorien $v_1, \dots, v_k$ kaikki lineaarikombinaatiot muodostavat
niiden **virittämän aliavaruuden**. Kaksi eri suuntiin osoittavaa
tason vektoria virittää koko tason; kaksi samansuuntaista vain suoran.

Vektorit ovat **lineaarisesti riippumattomia**, jos mikään niistä ei
ole muiden lineaarikombinaatio. Silloin jokaisella virittämän
aliavaruuden vektorilla on täsmälleen yksi esitys niiden avulla.
Riippumattomuuden voi tarkistaa asteesta: kun vektorit kootaan
matriisin sarakkeiksi, ne ovat riippumattomia täsmälleen silloin, kun
aste on vektorien määrä.

```{.python tiedosto="esimerkit/07-kanta.py" osa="riippumattomuus"}
```

**Kanta** on joukko lineaarisesti riippumattomia vektoreita, jotka
virittävät koko avaruuden. Kannan koko on avaruuden **ulottuvuus**:
tasossa kanta on aina kaksi vektoria, avaruudessa kolme.

## Koordinaatit toisessa kannassa

Kun kantavektorit $b_1, \dots, b_n$ kootaan matriisin $B$ sarakkeiksi,
vektorin $v$ koordinaatit $c$ tässä kannassa toteuttavat
$Bc = v$. Koordinaattien laskeminen on siis yhtälöryhmän
ratkaisemista, ja takaisin pääsee kertomalla $B$:llä.

```{.python tiedosto="esimerkit/07-kanta.py" osa="koordinaatit"}
```

## Esimerkki: värikoordinaatit

Kuvanpakkaus vaihtaa värit RGB-kannasta kantaan, jossa ensimmäinen
koordinaatti on kirkkaus ja kaksi muuta värieroja. Ihmissilmä on
tarkempi kirkkaudelle kuin värille, joten värierot voidaan tallentaa
pienemmällä tarkkuudella ilman, että kuva näyttää huonommalta.
YCoCg-muunnos on lineaarinen ja tarkasti käännettävä:

```{.python tiedosto="esimerkit/07-kanta.py" osa="vari"}
```

```{.tuloste tiedosto="esimerkit/07-kanta.odotettu"}
```

Harmaasävyissä (valkoinen) värierot ovat nollia, joten kaikki tieto on
kirkkaudessa. Takaisinmuunnoksen kertoimet ovat kokonaislukuja, mikä
tekee muunnoksesta halvan laitteistossa.

## Nolla-avaruus

Matriisin $A$ **nolla-avaruus** on niiden vektorien $x$ joukko, joille
$Ax = 0$. Se on aliavaruus, jonka ulottuvuus on $n - r$, missä $r$ on
aste. Nolla-avaruus kertoo, mitkä syötteen muutokset kuvaus "ei näe".
Jos $x_0$ on yhtälön $Ax = b$ jokin ratkaisu, kaikki ratkaisut ovat
muotoa $x_0 + z$, missä $z$ on nolla-avaruudessa.

Kauniin esimerkin tarjoaa kemia. Reaktioyhtälön tasapainotuksessa
jokaisen alkuaineen atomimäärä on sama molemmilla puolilla. Kertoimet
ovat tuntemattomat, ja jokainen alkuaine antaa yhden homogeenisen
yhtälön, jossa tuotteet ovat negatiivisina. Tasapainotetut kertoimet
ovat nolla-avaruuden vektori:

```{.python tiedosto="esimerkit/07-nolla-avaruus.py" osa="nolla-avaruus"}
```

```{.python tiedosto="esimerkit/07-nolla-avaruus.py" osa="reaktio"}
```

```{.tuloste tiedosto="esimerkit/07-nolla-avaruus.odotettu"}
```

Nolla-avaruus on yksiulotteinen, joten tasapainotus on yksikäsitteinen
kerrointa vaille. Pienin kokonaislukuratkaisu saadaan kertomalla
nimittäjien pienimmällä yhteisellä jaettavalla. Jos nolla-avaruus olisi
kaksiulotteinen, reaktio olisi kahden itsenäisen reaktion yhdistelmä.

## Neljä perusaliavaruutta

Matriisiin liittyy neljä aliavaruutta, jotka kertovat kuvauksesta
kaiken olennaisen:

| Aliavaruus | Merkitys | Ulottuvuus |
|------------|----------|------------|
| sarakeavaruus | kaikki mahdolliset tulokset $Ax$ | $r$ |
| nolla-avaruus | syötteet, jotka kuvautuvat nollaksi | $n - r$ |
| riviavaruus | syötteiden osa, jonka kuvaus "näkee" | $r$ |
| vasen nolla-avaruus | tulosavaruuden suunnat, joihin $Ax$ ei koskaan osoita | $m - r$ |

Yhtälöllä $Ax = b$ on ratkaisu täsmälleen silloin, kun $b$ on
sarakeavaruudessa. Pienimmän neliösumman sovitus (luku 9) etsii
sarakeavaruuden pisteen, joka on lähimpänä $b$:tä.

## Käytännössä

- **Valitse koordinaatisto tehtävän mukaan.** Fysiikka on usein
  yksinkertaisinta kappaleen omissa koordinaateissa, grafiikka kameran
  koordinaateissa ja tilastot pääkomponenttien kannassa (luku 10).
  Muunna sisään, laske, muunna ulos.
- **Nimeä koordinaatistot koodissa.** `p_maailma`, `p_kamera` ja
  `p_kappale` estävät sekoittamasta koordinaatistoja, joka on yleinen
  ja vaikeasti löydettävä virhe.
- **Tarkista riippumattomuus asteella, ei determinantilla.**
  `np.linalg.matrix_rank` käyttää singulaariarvoja ja kohtuullista
  toleranssia; determinantin arvo riippuu skaalauksesta.
- **Tarkat luvut, kun rakenne on diskreetti.** Stoikiometria,
  verkkojen yhtenäisyys ja kombinatoriset ehdot kannattaa laskea
  murtoluvuilla tai kokonaisluvuilla.

## Itsearviointi

- Osaat tarkistaa vektorien lineaarisen riippumattomuuden asteen avulla
  ja selittää, mitä kanta ja ulottuvuus tarkoittavat.
- Osaat laskea vektorin koordinaatit toisessa kannassa ja muuntaa ne
  takaisin.
- Osaat määrittää nolla-avaruuden kannan porrasmuodosta ja käyttää
  sitä homogeenisen yhtälöryhmän, kuten reaktioyhtälön, ratkaisemiseen.
- Osaat selittää, milloin yhtälöllä $Ax = b$ on ratkaisu
  sarakeavaruuden avulla.
