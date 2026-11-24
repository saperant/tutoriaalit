# Epipolaarigeometria ja stereonäkö

Yksi kuva ei kerro etäisyyttä. Kaksi kuvaa eri paikoista kertoo, kuten
ihmisen kaksi silmää: lähellä oleva kohde siirtyy kuvien välillä
enemmän kuin kaukainen. Tässä luvussa käydään läpi kahden kameran
geometria, kameran liikkeen ratkaiseminen pisteistä ja syvyyden
mittaaminen rektifioidusta kuvaparista.

## Epipolaarirajoite

Kun sama piste $X$ näkyy kahdessa kuvassa, sen kuvapisteet $x_1$ ja
$x_2$ eivät ole riippumattomia. Piste $X$ ja kameroiden projektiokeskukset
määräävät tason, ja tämä taso leikkaa kummankin kuvan suorana,
**epipolaarisuorana**. Kuvan 1 pisteen vastine kuvassa 2 on välttämättä
tällä suoralla. Rajoite on bilineaarinen yhtälö

$$
x_2^{\mathsf T} F\, x_1 = 0,
$$

jossa $F$ on $3 \times 3$ -**perusmatriisi** (*fundamental matrix*).
Kalibroiduilla kameroilla käytetään **essentiaalimatriisia**
$E = K^{\mathsf T} F K = [t]_\times R$, joka sisältää kameroiden välisen
kierron $R$ ja siirron $t$ suunnan. Rajoite on käytännössä tärkeä
kahdesta syystä: vastineen haku supistuu kaksiulotteisesta
yksiulotteiseksi, ja vääriä pareja voi karsia tarkistamalla rajoitteen.

## Kameran liike pisteistä

Kun kahden kuvan välillä on riittävästi vastinpareja, `findEssentialMat`
ratkaisee $E$:n RANSACilla, ja `recoverPose` purkaa sen kierroksi ja
siirroksi. Siirron pituutta ei saa: mittakaava katoaa samasta syystä kuin
yhden kuvan projektiossa, ja kahden kuvan perusteella ei voi erottaa
suurta maailmaa pienestä. Siirto palautuu yksikkövektorina.

Testissä 3D-pisteet projisoidaan kahdelle kameralle, joiden välinen
liike tunnetaan, ja kuvapisteisiin lisätään kohinaa.

```{.python tiedosto="esimerkit/08-epipolaari.py" osa="pisteet"}
```

```{.python tiedosto="esimerkit/08-epipolaari.py" osa="essentiaali"}
```

```{.python tiedosto="esimerkit/08-epipolaari.py" osa="rajoite"}
```

```{.tuloste tiedosto="esimerkit/08-epipolaari.odotettu"}
```

Pisteiden syvyyden vaihtelu on tärkeää. Kun kaikki pisteet ovat lähes
samalla etäisyydellä, pieni kierto ja pieni sivuttaissiirto näyttävät
kuvissa lähes samalta, ja estimointi sekoittaa ne. Ensimmäisessä
kokeilussa pisteet olivat 3–6 metrin päässä, ja kiertovirhe oli lähes kaksi
astetta. Kun syvyys vaihtelee 1,5–8 metrin välillä, virhe putoaa alle
puoleen asteeseen. Sama ilmiö rajoittaa oikeita järjestelmiä:
tasaisesta seinästä kameran liikettä on vaikea mitata.

Tästä jatketaan *structure from motion* -menetelmiin, joissa monesta
kuvasta ratkaistaan sekä kameroiden asennot että näkymän pisteet
yhdessä, ja SLAMiin (*simultaneous localization and mapping*), jossa
liikkuva kamera rakentaa karttaa reaaliajassa.

## Rektifiointi ja dispariteetti

Stereokamerassa kaksi kalibroitua kameraa on kiinnitetty vierekkäin.
**Rektifiointi** (`stereoRectify`, `initUndistortRectifyMap`) kiertää
kuvat virtuaalisesti niin, että epipolaarisuorat ovat vaakasuoria ja
samalla rivillä kummassakin kuvassa. Silloin vastine haetaan samalta
riviltä, ja kohta, joka vasemmassa kuvassa on sarakkeessa $x$, on
oikeassa sarakkeessa $x - d$. Siirtymä $d$ on **dispariteetti**, ja
syvyys saadaan yhdenmuotoisista kolmioista:

$$
Z = \frac{f\,B}{d},
$$

jossa $f$ on polttoväli pikseleinä ja $B$ kameroiden välinen etäisyys,
**kantaväli**. Syvyyden virhe kasvaa etäisyyden neliössä: yhden
pikselin dispariteettivirhe on lähellä pieni ja kaukana suuri.

Synteettisessä kuvaparissa on kolme tasoa tunnetuilla
dispariteeteilla. Jokainen taso on täynnä satunnaista tekstuuria, koska
vastineen haku tarvitsee tekstuuria: tasaiselta seinältä dispariteettia
ei voi mitata.

```{.python tiedosto="esimerkit/08-stereo.py" osa="kuvat"}
```

**SGBM** (*semi-global block matching*) vertaa pikselien ympäristöjä
ja suosii tasaista dispariteettia naapuripikseleiden välillä
rangaistuksilla `P1` (pieni muutos) ja `P2` (suuri muutos). Näin
tekstuuriton tai toistuva alue saa arvonsa naapureiltaan.

```{.python tiedosto="esimerkit/08-stereo.py" osa="sgbm"}
```

```{.tuloste tiedosto="esimerkit/08-stereo.odotettu"}
```

![Synteettinen stereopari ja SGBM:n dispariteettikartta. Vasen reuna jää
ilman arvoa, koska oikea kamera ei näe sitä, ja kappaleiden vasemmalla
puolella on peittyvä alue.](kuvat/stereo.png){width=100%}

Kartassa näkyy kaksi stereonäön perusongelmaa. Vasemman kuvan vasen
reuna ei näy oikeassa kuvassa lainkaan, joten sille ei ole vastinetta.
Kappaleen reunan toisella puolella on **peittyvä alue** (*occlusion*),
jonka vain toinen kamera näkee. Hyvä stereoalgoritmi merkitsee
tällaiset pikselit epävarmoiksi eikä keksi niille arvoa.

## Käytännössä

- **Kalibroi stereopari yhdessä.** `stereoCalibrate` ratkaisee
  kameroiden keskinäisen asennon. Pienikin kiertovirhe siirtää
  epipolaarisuoria, ja vastineen haku samalta riviltä epäonnistuu.
- **Valitse kantaväli mittausetäisyyden mukaan.** Leveä kantaväli
  parantaa syvyystarkkuutta kaukana mutta kasvattaa peittyviä alueita
  ja vähimmäisetäisyyttä.
- **Tekstuuri ratkaisee.** Passiivinen stereo ei näe tasaisia pintoja.
  Aktiiviset järjestelmät heijastavat kohteeseen pistekuvion.
- **Mittaa liike pisteistä, joiden syvyys vaihtelee.** Essentiaalimatriisin
  estimointi on epävakaa, kun näkymä on lähes tasomainen; silloin
  homografia on parempi malli.
- **Muista mittakaava.** Kahdesta kuvasta saa siirron vain suuntana.
  Mittakaava tulee tunnetusta kantavälistä, kappaleen koosta tai muusta
  anturista.

## Itsearviointi

- Osaat selittää epipolaarirajoitteen ja sen, miten se rajaa vastineen
  haun suoralle.
- Osaat ratkaista kameran liikkeen vastinpisteistä essentiaalimatriisilla
  ja selittää, miksi siirron pituus jää tuntemattomaksi.
- Osaat laskea syvyyden dispariteetista ja arvioida, miten virhe kasvaa
  etäisyyden mukana.
- Osaat laskea dispariteettikartan SGBM:llä ja tunnistaa peittyvät alueet
  ja tekstuurittomat pinnat ongelmakohdiksi.
