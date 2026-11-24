# Johdanto {.runko-johdanto}

Konenäkö on kuvien tulkintaa ohjelmalla. Kamera mittaa jokaiseen
pikseliin tulevan valon määrän, ja ohjelman tehtävä on päätellä
mittauksista jotain maailmasta: montako kolikkoa pöydällä on, missä
kohdassa kuvaa on paperin kulma, kuinka kaukana este on tai mihin
suuntaan auto liikkuu. Teollisuudessa konenäkö tarkastaa tuotteita
liukuhihnalla, lukee viivakoodeja ja ohjaa robotteja. Autoissa se
tunnistaa kaistaviivat ja jalankulkijat, puhelimissa se kohdistaa
panoraamakuvat ja mittaa etäisyyksiä.

Tämä tutoriaali opettaa konenäön klassiset menetelmät OpenCV-kirjastolla:
kuvien käsittelyn, suodatuksen, piirteet, geometriset muunnokset,
kameramallin ja kalibroinnin, stereonäön, segmentoinnin ja seurannan. Ne
ovat edelleen tarpeen, vaikka monet tunnistustehtävät tehdään nykyään
neuroverkoilla. Syväoppiva malli tarvitsee esikäsitellyn syötteen, sen
tulokset sijoitetaan maailmaan kameramallin avulla, ja monet mittaus- ja
tarkastustehtävät ratkeavat klassisilla menetelmillä nopeammin,
selitettävämmin ja ilman opetusaineistoa.

## Ensimmäinen esimerkki: kolikoiden laskeminen

Pöydällä on kuusi kolikkoa: kolme pientä ja kolme isoa. Kuva on
synteettinen: ohjelma piirtää kolikot itse ja lisää kohinaa kiinteällä
siemenellä. Siksi oikea vastaus tunnetaan, ja tulosta voi verrata siihen.

```{.python tiedosto="esimerkit/01-kolikot.py" osa="kuva"}
```

Analyysi on kolmen vaiheen ketju, joka toistuu koko tutoriaalissa:
esikäsittely (tasoitus vaimentaa kohinaa), päätös pikseleistä
(kynnystys erottaa kolikot pöydästä) ja tulkinta (yhtenäiset alueet ovat
kolikoita, ja niiden pinta-alat kertovat koon).

```{.python tiedosto="esimerkit/01-kolikot.py" osa="analyysi"}
```

Lopuksi mitattuja pinta-aloja verrataan piirrettyjen ympyröiden
pinta-aloihin $\pi r^2$.

```{.python tiedosto="esimerkit/01-kolikot.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/01-kolikot.odotettu"}
```

Kuusi kolikkoa löytyi, ja koot erottuvat selvästi. Kynnyksen valitsi
Otsun menetelmä kuvan histogrammista, joten mitään lukua ei tarvinnut
säätää käsin. Esimerkki on pieni, mutta siinä on jo tutoriaalin
työtapa: tunnettu syöte, menetelmä ja tarkistus tunnettua vastausta
vasten.

## Kenelle ja mitä tarvitaan

Lukija osaa Pythonin ja NumPyn (taito *Python työkaluohjelmointiin*)
sekä signaalinkäsittelyn perusteet: konvoluution, näytteistyksen,
aliasoinnin ja DFT:n yhdessä ulottuvuudessa (taito *Signaalit ja
järjestelmät*). Kuva on kaksiulotteinen signaali, ja tämä tutoriaali
laajentaa ne käsitteet kahteen ulottuvuuteen eikä toista niitä.
Lineaarialgebrasta tarvitaan matriisit, homogeeniset koordinaatit ja
singulaariarvohajotelma (taito *Lineaarialgebra*), ja taidon
*Renderöinnin perusteet* kamera- ja projektiomalli on tämän tutoriaalin
kameraluvun käänteinen tehtävä.

| Luku | Kysymys |
|------|---------|
| Digitaalinen kuva | Mitä kuvataulukossa on, ja miten väri ja kontrasti käsitellään? |
| Suodatus | Miten kohinaa poistetaan, ja mitä taajuustaso kertoo kuvasta? |
| Reunat, morfologia ja muodot | Miten kuvasta löydetään reunat, alueet ja muodot? |
| Piirteet ja sovittaminen | Miten kahdesta kuvasta löydetään samat kohdat? |
| Geometriset muunnokset | Miten kuvia käännetään, oikaistaan ja yhdistetään? |
| Kameramalli ja kalibrointi | Miten pikseli liittyy pisteeseen maailmassa? |
| Stereonäkö | Miten kahdesta kuvasta mitataan syvyys? |
| Segmentointi ja seuranta | Miten kappaleet erotellaan ja niiden liike seurataan? |
| Suorituskyky ja C++ | Mikä on kallista, ja miltä sama koodi näyttää C++:lla? |
| Koneoppimisen rajapinta | Miten klassinen ja oppiva konenäkö kohtaavat? |

## Merkinnät ja koordinaatit

| Merkintä | Tarkoitus |
|----------|-----------|
| $I(x, y)$ | kuvan arvo sarakkeessa $x$ ja rivillä $y$ |
| `kuva[y, x]` | sama NumPy-taulukossa: ensin rivi, sitten sarake |
| `(x, y)` | OpenCV:n piste: ensin sarake, sitten rivi |
| $K$ | kameran sisäiset parametrit, $3 \times 3$ |
| $R$, $t$ | kameran asento: kierto ja siirto |
| $H$ | homografia, $3 \times 3$ |
| $d$ | dispariteetti pikseleinä |

Pikselin $(x, y)$ keskikohta on kokonaislukukoordinaatissa, ja pikseli
kattaa välin $x - 0{,}5 \ldots x + 0{,}5$. Y-akseli osoittaa alaspäin,
joten positiivinen kulma kääntää kuvassa vastapäivään. NumPyn
indeksijärjestys `[y, x]` ja OpenCV:n pistejärjestys `(x, y)` ovat
alkeellisin mutta yleisin virhelähde, ja siihen palataan seuraavassa
luvussa.

## Työkalut ja versiot

Esimerkit ovat Python 3.12 -ohjelmia, jotka käyttävät NumPya ja
OpenCV:n Python-pakettia `opencv-python-headless` (versio 5.1, ilman
käyttöliittymämoduleja). Paketissa on tyyppitiedot, joten ruff ja mypy
(`--strict`) tarkistavat jokaisen esimerkin. Testaaja ajaa esimerkin ja
vertaa tulostetta tallennettuun. Luvun 7 kalibrointiesimerkki on
hakemisto, jonka renderöijä testataan pytestillä.

Luvun 10 C++-esimerkki käyttää Ubuntun pakettia `libopencv-dev`, jonka
versio on 4.6. Python-paketti tulee PyPI:stä ja on uudempi. Versioero on
tarkoituksellinen valinta: Python-esimerkit seuraavat OpenCV:n nykyistä
linjaa, ja C++-esimerkki näyttää, miten sama ohjelma rakennetaan
jakelun paketista ilman omaa käännöstä. Kirjastojen rajapinta on tässä
käytetyiltä osin sama. Suurin ero näkyy luvussa 11: OpenCV 5 siirsi
vanhan koneoppimismodulin `ml` lisämoduleihin.

Kaikki kuvat ovat synteettisiä: ohjelma piirtää ne itse kiinteillä
siemenillä. Näin oikea vastaus tunnetaan, tulokset toistuvat joka
koneella, eikä tutoriaali tarvitse ladattavia kuvia tai lisensoitavia
aineistoja. Tuloksia verrataan tunnettuihin arvoihin toleranssilla, ja
algoritmit, joiden tarkka tulos voi vaihdella version tai suorittimen
käskykannan mukaan, kuten piirteiden määrät, testataan väljillä
ehdoilla ("yli 100 piirrettä"). Kehityskontissa
(`.devcontainer/konenako`) on kaikki tarvittava.

Tutoriaalin kuvat piirtää skripti `kuvat/piirra.py` (`make kuvat`). Se
ajaa testatut esimerkit ja kuvittaa niiden muuttujat, joten kuva näyttää
täsmälleen sen, minkä esimerkki laskee.

## Mitä tutoriaali ei kata

Neuroverkkojen opettaminen on oma alansa. Luku 11 näyttää, miten
klassinen konenäkö ja opetettu malli kohtaavat: esikäsittely,
tulosten jälkikäsittely ja arviointi. Kolmiulotteinen rekonstruktio
monesta kuvasta (*structure from motion*) ja SLAM mainitaan vain
stereonäön jatkona. Grafiikkasuorittimella kiihdyttäminen on taidon
*GPU-laskenta* aihe.
