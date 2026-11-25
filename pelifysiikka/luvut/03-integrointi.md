# Voimat ja integrointi

Edellinen luku määritteli tilan. Tässä luvussa tila pannaan liikkeelle:
voimat ja vääntömomentit muuttavat nopeuksia, ja nopeudet muuttavat
paikkaa ja asentoa. Siirtymäliike on tuttu kaksiulotteisesta pelistä.
Pyöriminen kolmessa ulottuvuudessa ei ole, ja sen integrointi
huolimattomasti on yleinen syy siihen, että kappaleet alkavat pyöriä
itsestään yhä nopeammin.

## Voima ja vääntömomentti

Massakeskipisteen liikkeelle pätee $\mathbf F = m\mathbf a$,
kohdistui voima mihin tahansa kappaleen kohtaan. Pyörimiseen vaikuttaa
*vääntömomentti*

$$\boldsymbol\tau = \mathbf r \times \mathbf F,$$

missä $\mathbf r$ on voiman vaikutuspisteen paikka massakeskipisteestä.
Massakeskipisteeseen osuva voima ei väännä, ja mitä pidempi varsi, sitä
suurempi vääntö. Painovoima vaikuttaa massakeskipisteeseen, joten se ei
pyöritä vapaasti putoavaa kappaletta.

Moottorissa voimat kerätään askeleen aikana kahteen summaan, voimaan ja
vääntöön, ja ne nollataan, kun ne on käytetty:

```{.cpp tiedosto="esimerkit/yhteinen/kappale.hpp" osa="integroi-nopeus"}
```

Tämä on puoli-implisiittinen Euler taidosta *Peliohjelmointi*: ensin
nopeudet, sitten paikka uusilla nopeuksilla. Esimerkissä lankun päähän
kiinnitetty rakettimoottori työntää sivulle sekunnin ajan:

```{.cpp tiedosto="esimerkit/03-integrointi.cpp" osa="voima"}
```

```{.tuloste tiedosto="esimerkit/03-integrointi.odotettu" alkaen="moottori 1 s"}
```

Lankku sekä etenee että kääntyy, ja koska moottori kääntyy lankun
mukana, työntösuunta muuttuu matkalla. Kulmanopeus 1,41 rad/s on
täsmälleen $\tau t / I$: vääntö 2 N · 1 m sekunnin ajan jaettuna
pystyakselin hitausmomentilla 1,417 kg m².

## Asennon päivitys

Sijainnin päivitys on yhteenlasku. Asento on kvaternio, ja sen
aikaderivaatta on

$$\dot q = \tfrac12\,(0, \boldsymbol\omega)\,q,$$

missä $(0, \boldsymbol\omega)$ on kvaternio, jonka skalaariosa on nolla
ja vektoriosa kulmanopeus.

```{.cpp tiedosto="esimerkit/yhteinen/kvaternio.hpp" osa="asennon-askel"}
```

Askel on likiarvo, joka venyttää kvaterniota hieman, joten tulos
normalisoidaan aina.

Heitetyn kappaleen massakeskipiste lentää paraabelia, vaikka kappale
pyörii matkalla:

```{.cpp tiedosto="esimerkit/03-integrointi.cpp" osa="heitto"}
```

```{.tuloste tiedosto="esimerkit/03-integrointi.odotettu" alkaen="heitto 0,5 s" asti="tarkka"}
```

Vaakasuunta on tarkka. Pystysuunnassa simuloitu kappale on neljä
senttimetriä tarkan ratkaisun alapuolella, koska puoli-implisiittinen
Euler käyttää koko askeleen ajan askeleen lopun nopeutta. Virhe on
$\tfrac12 g\,t\,\Delta t$ ja sama jokaisella ajokerralla, joten peli voi
ottaa sen huomioon. Menetelmän kertaluku ja stabiilisuus ovat taidon
*Numeeriset menetelmät* aiheita.

## Vapaa pyöriminen

Pyörimisen liikeyhtälö on Eulerin yhtälö

$$I\,\dot{\boldsymbol\omega} = \boldsymbol\tau -
  \boldsymbol\omega \times (I\boldsymbol\omega).$$

Jälkimmäinen termi on *gyroskooppinen termi*. Se on nolla, kun kappale
pyörii jonkin pääakselinsa ympäri tai kun kaikki hitausmomentit ovat
samat, kuten pallolla. Muulloin kulmanopeus muuttuu, vaikka mikään ei
väännä kappaletta: liikemäärämomentti $\mathbf L$ pysyy paikallaan,
mutta kappale kääntyy sen ympärillä, ja $\boldsymbol\omega = I^{-1}
\mathbf L$ muuttuu hitaustensorin mukana.

Termin voi käsitellä neljällä tavalla. Esimerkki vertaa niitä kirjan
muotoisella kappaleella, jolla on kolme eri hitausmomenttia ja joka
pyörii keskimmäisen akselinsa ympäri:

```{.cpp tiedosto="esimerkit/03-integrointi.cpp" osa="kappale"}
```

```{.cpp tiedosto="esimerkit/03-integrointi.cpp" osa="tavat"}
```

```{.tuloste tiedosto="esimerkit/03-integrointi.odotettu" rivit="1-6"}
```

![Vapaa pyöriminen neljällä tavalla integroituna. Oikeassa ruudussa on
pyörimisakseliksi valitun kappaleen akselin suunta moottorin omalla
tavalla: akseli kääntyy ympäri muutaman sekunnin
välein.](kuvat/integrointi.png){width=100%}

- **Vakio kulmanopeus** jättää termin pois. Energia säilyy, mutta
  liikemäärämomentti heiluu ja kappale pyörii jäykästi yhden akselin
  ympäri. Moni fysiikkamoottori tekee oletuksena näin, koska tapa on
  ehdottoman stabiili, ja pelaaja huomaa eron harvoin.
- **Eksplisiittinen askel** laskee termin askeleen alun tilasta.
  Energia kasvaa portaittain, lopulta rajatta. Tämä on se tapa, joka
  saa kappaleet pyörimään itsestään yhä nopeammin.
- **Liikemäärämomentin säilyttäminen** laskee $\mathbf L$:n ennen
  asennon päivitystä ja kulmanopeuden siitä uudessa asennossa.
  $\mathbf L$ säilyy tarkasti, mutta energia kasvaa silti, kunnes
  kappale pyörii pienimmän hitausmomenttinsa ympäri. Yhden suureen
  säilyttäminen ei takaa toista.
- **Keskipistemenetelmä** tekee saman, mutta päivittää asennon
  askeleen puolivälin kulmanopeudella. Sekä liikemäärämomentti että
  energia säilyvät taulukon tarkkuudella. Moottori käyttää tätä:

```{.cpp tiedosto="esimerkit/yhteinen/kappale.hpp" osa="integroi-paikka"}
```

Viimeisen sarakkeen "käännöt" ovat todellinen ilmiö. Kappale, joka
pyörii keskimmäisen pääakselinsa ympäri, ei pysy asennossaan vaan
kääntyy säännöllisin välein ympäri (*välimmäisen akselin lause*, myös
tennismailailmiö). Pyöriminen suurimman tai pienimmän hitausmomentin
akselin ympäri on vakaata. Oikein integroiva simulaatio toistaa
ilmiön, ja tavoista kaksi antaa saman kääntöjen määrän kuin tarkempi
laskenta lyhyemmällä askeleella.

![Sama kappale kerran kierroksessa kuvattuna. Pyörimisakseli osoittaa
aluksi katsojaa kohti, kääntyy ympäri ja palaa
takaisin.](kuvat/kaanto.png){width=100%}

## Käytännössä

- **Puoli-implisiittinen Euler ja kiinteä askel** ovat oletus myös
  kolmessa ulottuvuudessa. Tarkempi integraattori ei auta, koska
  virheen hallitseva osa tulee kosketuksista, ei vapaasta lennosta.
- **Gyroskooppinen termi joko pois tai stabiilisti.** Eksplisiittinen
  toteutus on virhe. Jos pyörivät kappaleet ovat pelin kannalta
  tärkeitä (hyrrät, heitettävät esineet), termi lasketaan
  liikemäärämomentin kautta tai implisiittisesti; muuten sen voi
  jättää pois.
- **Kulmanopeudelle katto.** Moottorit rajaavat kulmanopeuden
  suurimman arvon, koska hyvin nopeasti pyörivä kappale kääntyy
  askeleessa niin paljon, ettei törmäystunnistus pysy mukana.
- **Vaimennus** (`nopeus *= 1 - c * dt`) poistaa energiaa, jota
  ilmanvastus ja muut mallintamattomat häviöt todellisuudessa
  poistaisivat. Pieni kulmavaimennus peittää integroinnin virheitä,
  mutta suuri saa kappaleet näyttämään siltä kuin ne liikkuisivat
  siirapissa.
- **Voimat kootaan, impulssit annetaan heti.** Jatkuva vaikutus
  (painovoima, moottori, jousi) lisätään voimasummaan. Hetkellinen
  (osuma, räjähdys) annetaan impulssina suoraan nopeuteen.

## Itsearviointi

- Osaat laskea voiman aiheuttaman vääntömomentin ja kertoa, milloin
  voima ei pyöritä kappaletta.
- Osaat päivittää asennon kvaterniona kulmanopeudesta.
- Osaat selittää, mikä gyroskooppinen termi on ja miksi sen
  eksplisiittinen integrointi lisää energiaa.
- Osaat kertoa, mitä liikemäärämomentin säilyttävä päivitys tekee ja
  miksi se ei yksin riitä.
- Osaat arvioida, milloin termin voi jättää pois.
