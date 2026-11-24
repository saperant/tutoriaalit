# Piirteet ja sovittaminen

Monessa tehtävässä on löydettävä sama kohta kahdesta kuvasta: kun
panoraamaa kootaan, kun kameran liikettä arvioidaan tai kun tunnettu
kappale etsitään näkymästä. Pikseli itsessään ei kelpaa tunnisteeksi,
koska sama kirkkaus esiintyy kuvassa tuhansia kertoja. **Piirre**
(*feature*) on kohta, jonka ympäristö on erottuva ja löytyy uudelleen,
vaikka kuva kiertyy, skaalautuu tai valaistus muuttuu. Tässä luvussa
etsitään kulmia, kuvataan niiden ympäristö ja sovitetaan piirteet kahden
kuvan välillä.

## Kulmat

Tasaisella alueella ikkunaa voi siirtää mihin suuntaan tahansa kuvan
muuttumatta. Reunalla muutos näkyy vain reunaa vastaan kohtisuorassa
suunnassa. **Kulmassa** ikkunan siirto mihin tahansa suuntaan muuttaa
kuvaa. Tämä mitataan **rakennetensorilla**, ikkunan gradienttien
$2 \times 2$ -kovarianssimatriisilla

$$
M = \sum_{\text{ikkuna}} \begin{pmatrix} I_x^2 & I_x I_y \\
I_x I_y & I_y^2 \end{pmatrix}.
$$

Molemmat ominaisarvot ovat suuria vain kulmassa. **Harris** käyttää
vastetta $\det M - k\,(\operatorname{tr} M)^2$, ja **Shi–Tomasi**
pienempää ominaisarvoa $\min(\lambda_1, \lambda_2)$. Shi–Tomasi
(`goodFeaturesToTrack`) on hyvä oletus seurattaville pisteille.

Testikuva on shakkikuvio, jonka kulmat ovat tunnetuissa
**alipikselikohdissa**. Kuvio piirretään kahdeksankertaisena ja
pienennetään `INTER_AREA`:lla, jolloin reunapikselit saavat oikeat
väliarvot kuten oikeassa kamerassa.

```{.python tiedosto="esimerkit/05-kulmat.py" osa="kuva"}
```

```{.python tiedosto="esimerkit/05-kulmat.py" osa="harris"}
```

Ilmaisin antaa kulman kokonaislukupikselinä. **`cornerSubPix`** tarkentaa
sijaintia: kulman ympärillä jokaisen pikselin gradientti on kohtisuorassa
suoraa vastaan, joka kulkee kulman kautta, ja kulma ratkaistaan
pienimmän neliösumman tehtävänä.

```{.python tiedosto="esimerkit/05-kulmat.py" osa="shitomasi"}
```

```{.tuloste tiedosto="esimerkit/05-kulmat.odotettu"}
```

Tarkennus pienentää virheen kymmenesosaan. Loput noin 0,08 px on
systemaattista harhaa, joka johtuu ikkunan ja interpoloinnin
epäsymmetriasta. Kameran kalibroinnissa (luku 7) juuri alipikselitarkkuus
erottaa käyttökelpoisen tuloksen huonosta.

## Kuvaajat: ORB ja SIFT

Kulman sijainti ei vielä kerro, mikä kulma on kyseessä. **Kuvaaja**
(*descriptor*) on vektori, joka tiivistää piirteen ympäristön. Hyvä
kuvaaja on sama samalle kohdalle kierrosta, skaalasta ja valaistuksesta
riippumatta, ja eri kohdilla erilainen.

| Ominaisuus | SIFT | ORB |
|------------|------------------------------|------------------------------|
| ilmaisin | Gaussin erotukset skaala-avaruudessa | FAST-kulmat kuvapyramidissa |
| suunta | gradienttisuuntien histogrammi | intensiteettikeskiö |
| kuvaaja | 128 liukulukua (suuntahistogrammit) | 256 bittiä (kirkkausvertailut) |
| vertailu | euklidinen etäisyys | Hamming-etäisyys |
| nopeus | hitaampi | moninkertaisesti nopeampi |

SIFT:n patentti päättyi vuonna 2020, ja algoritmi on siitä lähtien ollut
OpenCV:n päämodulissa. ORB kehitettiin alun perin patenttivapaaksi ja
nopeaksi vaihtoehdoksi.

## Sovittaminen

Kahden kuvan kuvaajat sovitetaan etsimällä kullekin lähin vastine.
Raakahaku (`BFMatcher`) vertaa kaikkia pareja, ja se riittää tuhansille
piirteille. Lähin vastine ei aina ole oikea: toistuvassa tekstuurissa
monella piirteellä on lähes yhtä hyvä vastine. **Loween ratio-testi**
hyväksyy vastineen vain, jos se on selvästi parempi kuin toiseksi paras.

Väärät parit jäävät silti mukaan. **RANSAC** (*random sample consensus*)
arpoo pienen joukon pareja, laskee niistä muunnoksen ja laskee, kuinka
moni muu pari on muunnoksen kanssa samaa mieltä. Paras muunnos voittaa,
ja sen kanssa samaa mieltä olevat parit ovat **sisäpisteitä**
(*inliers*). Todennäköisyyslaskennan näkökulmasta tarvittavien arvontojen
määrä riippuu väärien parien osuudesta: kun osuus on $\varepsilon$ ja
otos on $s$ paria, onnistumiseen todennäköisyydellä $p$ tarvitaan
$\log(1-p)/\log(1-(1-\varepsilon)^s)$ arvontaa.

Testikuvana on satunnaisista kuvioista koottu näkymä ja sen kierretty,
pienennetty ja siirretty versio. Muunnos tunnetaan, joten jokaisen parin
oikeellisuus voidaan tarkistaa.

```{.python tiedosto="esimerkit/05-sovitus.py" osa="kuvat"}
```

```{.python tiedosto="esimerkit/05-sovitus.py" osa="sovitus"}
```

```{.tuloste tiedosto="esimerkit/05-sovitus.odotettu"}
```

![ORB-piirteiden 40 parasta paria näkymän ja sen kierretyn ja pienennetyn
version välillä.](kuvat/sovitus.png){width=100%}

Esimerkki ei tulosta piirteiden tai parien tarkkoja määriä, koska ne
vaihtelevat OpenCV:n version ja suorittimen käskykannan mukaan. Testi
tarkistaa sen, millä on merkitystä: pareja on riittävästi, valtaosa on
oikeita, ja RANSAC palauttaa tunnetun kierron ja skaalan. Kirjoittajan
koneella ORB löysi noin 800 ja SIFT noin 250 piirrettä, ja ratio-testin
jälkeen noin 90 prosenttia pareista oli oikeita.

## Käytännössä

- **Aloita ORB:lla, vaihda SIFT:iin tarvittaessa.** ORB on nopea ja
  riittää useimpiin kohdistus- ja seurantatehtäviin. SIFT on tarkempi
  suurissa skaalan ja näkökulman muutoksissa.
- **Käytä aina ratio-testiä ja RANSACia.** Ratio-testi karsii
  monitulkintaiset parit, RANSAC väärät. Pelkkä lähin vastine ilman
  kumpaakaan tuottaa käyttökelvottomia muunnoksia.
- **Hamming ORB:lle, L2 SIFT:lle.** Väärä etäisyysmitta toimii
  näennäisesti mutta huonosti.
- **Tarkenna alipikseleihin, kun mittaat.** `cornerSubPix` on halpa ja
  parantaa tarkkuutta kertaluokan.
- **Testaa tunnetulla muunnoksella.** Synteettinen kierto, skaalaus ja
  perspektiivi antavat oikean vastauksen, ja testi voi tarkistaa
  sisäpisteiden osuuden ja muunnoksen virheen.

## Itsearviointi

- Osaat selittää rakennetensorin avulla, miksi kulma on hyvä piirre ja
  reuna huono.
- Osaat etsiä kulmat Shi–Tomasilla ja tarkentaa ne alipikselitarkkuuteen.
- Osaat verrata ORB:n ja SIFT:n kuvaajia ja valita oikean etäisyysmitan.
- Osaat sovittaa piirteet ratio-testillä, arvioida muunnoksen RANSACilla
  ja tarkistaa tuloksen tunnettua muunnosta vasten.
