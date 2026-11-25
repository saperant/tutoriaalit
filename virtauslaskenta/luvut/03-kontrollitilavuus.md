# Kontrollitilavuusmenetelmä

Lähes kaikki virtauslaskentaohjelmat diskretoivat yhtälönsä
**kontrollitilavuusmenetelmällä** (*finite volume method*). Sen ajatus on
tuttu: alue jaetaan ruutuihin ja jokaiselle ruudulle kirjoitetaan tase.
Tässä luvussa menetelmä muotoillaan suureelle, jota virtaus kuljettaa,
ja nähdään, miksi juuri säilyvyys tekee siitä virtauslaskennan
perusmenetelmän. Virtaus on tässä ja kahdessa seuraavassa luvussa
annettu; sen ratkaisemiseen päästään luvussa 6.

## Ruudun tase

Olkoon $c$ jonkin aineen pitoisuus: savua ilmassa, väriainetta vedessä,
tai yhtä hyvin lämpötila. Virtaus kuljettaa sitä nopeudella
$\mathbf u$, diffuusio levittää sitä kertoimella $D$, ja lähde $s$
tuottaa sitä. Ruudun sisältämä määrä muuttuu sen verran kuin pintojen
läpi kulkee ja sisällä syntyy:

$$\frac{d}{dt}\int_V c\,dV
  = -\oint_{\partial V} (\mathbf u\,c - D\nabla c)\cdot\mathbf n\,dA
  + \int_V s\,dV.$$

Sulkeissa on **vuo**: advektio vie määrän $\mathbf u c$ ja diffuusio
määrän $-D\nabla c$ pinta-alayksikön läpi aikayksikössä. Kun ruutu
kutistetaan pisteeksi, taseesta tulee **kuljetusyhtälö**

$$\frac{\partial c}{\partial t} + \nabla\cdot(\mathbf u\,c)
  = \nabla\cdot(D\nabla c) + s.$$

Kontrollitilavuusmenetelmä ei kuitenkaan tee tätä rajankäyntiä. Se
pitää ruudut äärellisinä ja tallentaa jokaiselle yhden luvun, ruudun
keskiarvon. Diskretoitavaksi jäävät vain pintojen vuot.

![Kontrollitilavuus ja sen naapurit. Tuntematon on ruudun keskiarvo;
kaikki likiarvot tehdään pintojen voissa.](kuvat/tilavuus.png){width=85%}

Liikemäärän yhtälö on samaa muotoa. Kun $c$:n paikalle kirjoitetaan
nopeuskomponentti $u$, diffuusiokertoimeksi $\nu$ ja lähteeksi
painegradientti, saadaan Navier–Stokesin yhtälön $x$-komponentti. Kaikki,
mitä kuljetusyhtälöstä opitaan, pätee siis liikemäärään.

## Säilyvyys on rakennettu sisään

Pinnan vuo lasketaan kerran. Se vähennetään siitä ruudusta, josta
pinta katsoo ulos, ja lisätään naapuriin. Kun kaikkien ruutujen taseet
lasketaan yhteen, sisäpintojen vuot kumoutuvat pareittain ja jäljelle
jäävät vain alueen reunan vuot:

- jokaisen ruudun tase toteutuu täsmälleen (**paikallinen säilyvyys**),
- koko alueen tase toteutuu täsmälleen (**globaali säilyvyys**),
- kumpikaan ei riipu siitä, kuinka karkea hila on tai kuinka huonosti
  pinnan vuo on arvioitu.

Virhe näkyy siis väärässä paikassa olevana aineena, ei kadonneena tai
tyhjästä syntyneenä. Virtauksessa tämä on tärkeämpää kuin
lämmönjohtumisessa, koska massan tase on se ehto, josta paine
määräytyy.

Esimerkissä pulssi kulkee kanavassa, jossa virtaus hidastuu kolmasosaan.
Ensimmäinen kaavio on taseen suora diskretointi.

```{.python tiedosto="esimerkit/03-sailyvyys.py" osa="tehtava"}
```

```{.python tiedosto="esimerkit/03-sailyvyys.py" osa="sailyva"}
```

Toinen kaavio diskretoi saman yhtälön tulon derivaatan säännöllä auki
kerrottuna. Kumpikin derivaatta on korvattu järkevällä erotusosamäärällä,
ja kaavio suppenee hilaa tihennettäessä oikeaan ratkaisuun.

```{.python tiedosto="esimerkit/03-sailyvyys.py" osa="sailymaton"}
```

```{.tuloste tiedosto="esimerkit/03-sailyvyys.odotettu"}
```

![Vasemmalla pulssi alussa ja lopussa sekä virtausnopeus. Hidastuvassa
virtauksessa pulssi kasaantuu kapeammaksi. Oikealla aineen kokonaismäärä:
säilyvässä muodossa se pysyy, auki kerrotussa se heilahtelee
prosentteja.](kuvat/sailyvyys.png){width=95%}

Säilyvä muoto pitää määrän tarkasti. Auki kerrotussa muodossa aineen
määrä ensin vähenee lähes kolme prosenttia ja kasvaa sitten neljä
prosenttia alkuperäistä suuremmaksi, vaikka mitään ei tule sisään eikä
mene ulos. Virhe pienenee hilaa tihentämällä, mutta pitkässä laskussa
tai suljetussa kierrossa se kertautuu.

## Kaksi ulottuvuutta: savuvana tuulessa

Tasossa ruudulla on neljä pintaa, ja tase on sama. Rakennetaan pieni
kirjasto `kuljetus`, joka ratkaisee kuljetusyhtälön tasapainotilan
tunnetussa virtauksessa. Pitoisuus on ruutujen keskipisteissä ja nopeus
pinnoilla, eli siellä, missä vuo lasketaan.

```{.python tiedosto="esimerkit/03-kuljetus/kuljetus.py" osa="hila"}
```

Jokaisen sisäpinnan vuo kirjoitetaan kahden viereisen ruudun arvojen
avulla. Diffuusiovuo on erotusosamäärä. Advektiovuo tarvitsee
pitoisuuden *pinnalla*, vaikka se tunnetaan vain ruutujen keskellä, ja
sen arvioimiseen on kaksi luontevaa tapaa: naapurien keskiarvo tai
tulosuunnan ruudun arvo. Valinta osoittautuu virtauslaskennan
keskeiseksi kysymykseksi, ja luvut 4 ja 5 käsittelevät sitä. Tässä
luvussa käytetään tulosuunnan arvoa.

```{.python tiedosto="esimerkit/03-kuljetus/kuljetus.py" osa="pinta"}
```

Kokoaminen käy pinnat läpi ja lisää jokaisen vuon kahden ruudun
yhtälöihin vastakkaisin merkein. Reunapinnoilla virtauksen suunta
ratkaisee ehdon: sisään tulevan virtauksen pitoisuus tunnetaan, ulos
lähtevä virtaus vie mukanaan ruudun oman pitoisuuden.

```{.python tiedosto="esimerkit/03-kuljetus/kuljetus.py" osa="kokoa"}
```

Tase tarkistetaan laskemalla, kuinka paljon ainetta reunojen läpi
poistuu:

```{.python tiedosto="esimerkit/03-kuljetus/kuljetus.py" osa="tase"}
```

Koetehtävä on savupiippu tasaisessa tuulessa. Pistemäinen lähde
päästää ainetta vakionopeudella, tuuli kuljettaa sen oikealle ja
diffuusio levittää vanaa sivusuunnassa.

```{.python tiedosto="esimerkit/03-kuljetus/main.py" osa="tehtava"}
```

Tehtävälle on yksinkertainen teoria. Aine, joka on kulkenut matkan
$x - x_0$, on ollut ilmassa ajan $(x - x_0)/U$, ja sinä aikana
diffuusio on kasvattanut vanan varianssia määrällä $2Dt$. Vanan
poikkileikkaus on siis normaalijakauma, jonka keskihajonta on
$\sigma = \sqrt{2D(x - x_0)/U}$. Arvio pätee, kun tuuli kuljettaa paljon
nopeammin kuin diffuusio levittää.

```{.python tiedosto="esimerkit/03-kuljetus/main.py" osa="leveys"}
```

```{.tuloste tiedosto="esimerkit/03-kuljetus.odotettu"}
```

![Savuvanan pitoisuus hilalla 160 × 80 ja teorian ennustama
leveys.](kuvat/savuvana.png){width=95%}

Tase toteutuu jokaisella hilalla: reunoilta poistuu täsmälleen se, mitä
lähde tuottaa. Vanan leveys on karkeimmallakin hilalla noin kolmen
prosentin päässä teoriasta ja lähestyy sitä hilaa tihennettäessä. Pitoisuus ei
ole missään negatiivinen. Tulos näyttää siltä, että menetelmä on
valmis. Luku 5 kääntää tuulen vinoon ja näyttää, ettei ole.

## Miksi juuri tämä menetelmä

Differenssimenetelmä ja kontrollitilavuusmenetelmä antavat tasaisella
suorakulmaisella hilalla usein täsmälleen saman kaavan. Ero on
ajattelutavassa ja siinä, mihin se yleistyy.

- Tase ei vaadi ruuduilta muotoa. Sama periaate toimii kolmioilla,
  monikulmioilla ja kolmiulotteisilla monitahokkailla, joten hilan voi
  sovittaa auton tai putkiston pintaan (luku 12).
- Säilyvyys ei riipu tarkkuudesta. Karkea hila antaa epätarkan mutta
  taseeltaan oikean tuloksen.
- Reunaehdot ovat voita, ja vuolla on fysikaalinen merkitys: massavirta,
  lämpöteho, voima.

Elementtimenetelmääkin käytetään virtauksille, mutta
kontrollitilavuusmenetelmä on alan valtamenetelmä juuri säilyvyyden ja
yksinkertaisuutensa vuoksi.

## Käytännössä

- **Tallenna vuot pinnoille, älä derivaattoja pisteisiin.** Jos ohjelma
  laskee pinnan vuon kahdesti eri kaavalla, säilyvyys on menetetty.
- **Tarkista tase jokaisesta ajosta.** Sisään miinus ulos on kertymä.
  Valmiit ohjelmat raportoivat massataseen virheen; sen pitää olla
  pyöristysvirheen tai ratkaisijan toleranssin luokkaa.
- **Pidä nopeus lähteettömänä.** Kuljetusyhtälön säilyvä muoto olettaa,
  että ruutuun tuleva tilavuusvirta on sama kuin lähtevä. Jos
  nopeuskenttä vuotaa, pitoisuuteen syntyy lähteitä tyhjästä.
- **Reunalla virtauksen suunta määrää ehdon.** Sisäänvirtausreunalle
  annetaan arvo, ulosvirtausreunalle ei. Arvon pakottaminen
  ulosvirtausreunalle tuottaa ohuen keinotekoisen rajakerroksen.
- **Tuntematon on keskiarvo.** Ruudun arvo ei ole pistearvo ruudun
  keskellä vaan keskiarvo koko ruudussa. Ero näkyy, kun tuloksia
  verrataan mittauksiin tai tarkkaan ratkaisuun.

## Itsearviointi

- Osaat kirjoittaa ruudun taseen kuljetettavalle suureelle ja nimetä
  vuon advektio- ja diffuusio-osan.
- Osaat selittää, miksi kontrollitilavuusmenetelmä säilyttää suureen
  täsmälleen hilasta riippumatta, ja erotat paikallisen ja globaalin
  säilyvyyden.
- Osaat koota tasapainotilan yhtälöryhmän pintojen kertoimista ja
  käsitellä sisään- ja ulosvirtausreunan.
- Osaat tarkistaa lasketun pitoisuuskentän taseen.
- Osaat arvioida savuvanan leveyden kulkuajan ja diffuusiokertoimen
  avulla.
