# Kuvat, grafiikka ja taulukot

Edellisessä luvussa sivu jäsennettiin tekstielementeillä. Tässä
luvussa sisältöön lisätään se, mikä ei ole juoksevaa tekstiä: kuvat,
vektorigrafiikka, taulukot, video ja muilta sivuilta upotettu
sisältö. Kaikille on yhteistä, että sisällön on välityttävä myös
silloin, kun sitä ei näe tai se ei lataudu. Siksi luku alkaa
vaihtoehtoisesta tekstistä.

## Vaihtoehtoinen teksti

Jokaisella `<img>`-elementillä on `alt`-attribuutti. Se korvaa kuvan,
kun kuvaa ei näe: ruudunlukijassa, hakukoneessa, hitaalla yhteydellä
tai kun kuva ei lataudu. Kirjoitettava teksti riippuu kuvan
tehtävästä:

| Kuvan tehtävä | `alt` |
|---------------|-------|
| Informatiivinen: kuva kertoo jotain | sama tieto lyhyesti tekstinä |
| Toiminnallinen: kuva on linkki tai painike | mitä linkki tai painike tekee |
| Koriste tai toistaa viereisen tekstin | tyhjä: `alt=""` |
| Monimutkainen: kaavio, kartta | lyhyt kuvaus, tiedot tekstinä tai taulukkona |

Tyhjä `alt=""` ja puuttuva `alt` ovat eri asioita. Tyhjä kertoo, että
kuva on koriste, ja ruudunlukija ohittaa sen. Puuttuvan tilalla
ruudunlukija lukee usein tiedostonimen, kuten "IMG_4021 jpg".

```{.html tiedosto="esimerkit/03-alt.ei-kaanny.html" osa="kuvat"}
```

```text
11:8  error  <img> is missing required "alt" attribute  wcag/h37
```

```{.tuloste tiedosto="esimerkit/03-alt.odotettu"}
```

Kuvatekstin (`<figcaption>`) kanssa kuva saa tyhjän `alt`-tekstin, kun
kuvateksti jo kertoo saman; muuten ruudunlukija lukisi nimen kahdesti.
Esimerkin kuvat ovat yhden pikselin paikkamerkkejä, jotta esimerkki ei
tarvitse kuvatiedostoja.

Hyvä vaihtoehtoinen teksti on lyhyt (noin 100 merkkiä), ei ala sanoilla
"kuva, jossa" (ruudunlukija kertoo roolin itse) ja kertoo sen, minkä
vuoksi kuva on sivulla. Saman kuvan `alt` voi olla eri sivuilla eri.

## Kuvat, kaaviot ja koristeet

```{.html tiedosto="esimerkit/03-kuvat/index.html" osa="linkkikuva"}
```

Logo on linkki etusivulle, joten sen teksti kertoo linkin kohteen.

```{.html tiedosto="esimerkit/03-kuvat/index.html" osa="kaavio"}
```

Upotetulle SVG:lle annetaan rooli `img` ja nimi sen `<title>`-
elementistä. Kaavion tiedot ovat nimessä; laajemmat tiedot kuuluvat
taulukkoon kaavion viereen.

```{.html tiedosto="esimerkit/03-kuvat/index.html" osa="koriste"}
```

```{.tuloste tiedosto="esimerkit/03-kuvat.odotettu"}
```

Koristekuva puuttuu saavutettavuuspuusta kokonaan, kuten pitääkin.
Raportin alku kertoo maisemakuvan koon kahdella leveydellä: 360 pikselin
näkymässä 640 pikselin kuva on kutistunut sivun levyiseksi, ja korkeus
on pysynyt kuvasuhteessa 16:9.

## Responsiiviset kuvat

```{.html tiedosto="esimerkit/03-kuvat/index.html" osa="kuva"}
```

```{.css tiedosto="esimerkit/03-kuvat/tyyli.css" osa="kuvat"}
```

- `width` ja `height` ovat kuvan luontaiset mitat. Niistä selain
  laskee kuvasuhteen ja varaa tilan ennen latausta, joten sivu ei
  hypi kuvan saapuessa (*Cumulative Layout Shift*, CLS). CSS:n
  `block-size: auto` ja `max-inline-size: 100%` antavat kuvan
  kutistua säilyttäen suhteen.
- `srcset` luettelee saman kuvan eri kokoiset versiot leveyksineen ja
  `sizes` kertoo, kuinka leveänä kuva näytetään. Selain valitsee
  pienimmän riittävän version näytön tiheyden mukaan. Puhelin ei lataa
  työpöydän kuvaa.
- `<picture>`-elementti ja sen `<source>`-lapset valitsevat eri
  *tiedostomuodon* (AVIF, WebP, JPEG) tai eri rajauksen kapealle ja
  leveälle näkymälle.
- `loading="lazy"` lykkää näkymän ulkopuolisten kuvien latausta. Sitä
  ei käytetä sivun pääkuvalle, joka näkyy heti.

## Taulukot

Taulukko on taulukkomuotoista tietoa varten, ei asetteluun.
Ruudunlukija lukee solun yhteydessä sen rivi- ja sarakeotsikot, kun
otsikot on merkitty:

```{.html tiedosto="esimerkit/03-taulukko.html" osa="taulukko"}
```

```{.css tiedosto="esimerkit/03-taulukko.html" osa="tyyli"}
```

```{.tuloste tiedosto="esimerkit/03-taulukko.odotettu"}
```

![Taulukko selaimessa: luvut on tasattu oikealle ja otsikkosolut
lihavoitu.](kuvat/03-taulukko-1024.png){width=35%}

- `<caption>` on taulukon nimi; se näkyy saavutettavuuspuussa taulukon
  nimenä.
- `<th scope="col">` on sarakeotsikko, `<th scope="row">`
  riviotsikko. Ruudunlukija lukee solun "Q2, A, 2 380".
- `<thead>`, `<tbody>` ja `<tfoot>` jäsentävät rivit; tulostettaessa
  `<thead>` toistuu jokaisella sivulla.
- Luvut tasataan oikealle ja tasalevyisillä numeroilla
  (`font-variant-numeric: tabular-nums`), jotta suuruusluokat näkyvät.
- Kapealla näytöllä leveä taulukko vieritetään vaakasuunnassa omassa
  kehyksessään (`overflow-x: auto`). Taulukkoa ei pilkota
  `<div>`-elementeiksi, koska rakenne katoaisi.

## Avattava sisältö, video ja upotukset

Kolme elementtiä tuo sivulle toiminnallisuutta, joka muuten
vaatisi JavaScriptiä.

`<details>` on avattava osio, jonka otsikko on `<summary>`. Se sopii
usein kysyttyihin kysymyksiin ja lisätietoihin:

```{.html tiedosto="esimerkit/03-upotukset.html" osa="details"}
```

Selain hoitaa avaamisen, näppäimistökäytön ja tilan ilmoittamisen
ruudunlukijalle. Suljetun osion sisältö löytyy silti sivun sisäisellä
haulla. Attribuutti `open` avaa osion valmiiksi, ja sama
`name`-attribuutti usealla `<details>`-elementillä tekee niistä
ryhmän, josta vain yksi on kerrallaan auki.

`<video>` ja `<audio>` toistavat mediaa selaimen omilla säätimillä:

```{.html tiedosto="esimerkit/03-upotukset.html" osa="video"}
```

- `controls` näyttää säätimet. Ilman sitä käyttäjä ei voi pysäyttää
  toistoa.
- `<track kind="captions">` liittää tekstityksen (WebVTT-tiedosto).
  Tekstitys on videon vaihtoehtoinen teksti: WCAG edellyttää sitä
  tallenteilta, ja moni katsoo videot ilman ääntä.
- `preload="none"` jättää videon lataamatta, kunnes käyttäjä
  käynnistää sen. Esimerkin testi nojaa tähän: videotiedostoa ei ole,
  eikä selain yritä hakea sitä.
- Elementin sisältö (latauslinkki) näytetään vain, jos selain ei tue
  elementtiä.
- Itsestään käynnistyvä ääni on saavutettavuusvirhe. `autoplay`
  toimii selaimissa yleensä vain mykistettynä (`muted`).

`<iframe>` upottaa toisen sivun: kartan, videopalvelun soittimen tai
maksulomakkeen.

```{.html tiedosto="esimerkit/03-upotukset.html" osa="iframe"}
```

```{.tuloste tiedosto="esimerkit/03-upotukset.odotettu"}
```

![Avattavat osiot (ensimmäinen suljettu, toinen auki), video
säätimineen ja upotettu sivu.](kuvat/03-upotukset-560.png){width=55%}

- `title` on kehyksen nimi ruudunlukijalle ja pakollinen samasta
  syystä kuin kuvan `alt`.
- `loading="lazy"` lataa kehyksen vasta, kun se on tulossa näkyviin.
  Sama attribuutti toimii kuvissa.
- Upotettu sivu on toisen osapuolen koodia. `sandbox`-attribuutti
  rajaa, mitä se saa tehdä (esimerkiksi `sandbox="allow-scripts"`), ja
  kolmannen osapuolen upotus voi seurata kävijää, mikä on otettava
  huomioon evästesuostumuksessa.

Raportissa videon leveys on 322 pikseliä: 320 pikselin sisältö ja
yhden pikselin reunus kummallakin puolella (laatikkomalli, luku 7).

Modaalinen ikkuna tehdään `<dialog>`-elementillä. Se esitellään
luvussa 11, koska siihen liittyy sivun kerrosten pinoutuminen.

## Käytännössä

- **Kirjoita `alt` silloin, kun kuva lisätään.** Jälkikäteen tekstejä ei
  enää kirjoiteta. Sisällönhallintajärjestelmässä `alt` on pakollinen
  kenttä, jossa on myös "koriste"-valinta.
- **Optimoi kuvat rakennusvaiheessa.** Kuvat ovat tyypillisesti suurin
  osa sivun siirtomäärästä. Kuvaputki (esimerkiksi sivustogeneraattorin
  kuvakomponentti tai `sharp`) tuottaa `srcset`-versiot ja modernit
  tiedostomuodot automaattisesti.
- **Mitat aina.** `width` ja `height` jokaiseen kuvaan ja upotukseen;
  ilman niitä sivu hyppii latautuessaan.
- **SVG ikoneihin ja kaavioihin.** Vektorigrafiikka skaalautuu ja on
  pieni. Koristeikonit merkitään `aria-hidden="true"`, ja painikkeen tai
  linkin nimi tulee tekstistä (luku 5).
- **Taulukolle otsikot.** Jokaisessa datataulukossa on `<caption>` ja
  `<th>`-solut. Monitasoiset otsikot kannattaa välttää: kaksi
  yksinkertaista taulukkoa on helpompi lukea kuin yksi monimutkainen.

## Itsearviointi

- Osaat kirjoittaa vaihtoehtoisen tekstin informatiiviselle,
  toiminnalliselle ja koristekuvalle ja perustella valinnan.
- Osaat tehdä responsiivisen kuvan `srcset`- ja `sizes`-attribuuteilla
  ja estää sivun hyppimisen kuvan latautuessa.
- Osaat tehdä saavutettavan SVG-kaavion.
- Osaat merkitä datataulukon otsikot niin, että ruudunlukija yhdistää
  solun otsikoihinsa.
- Osaat tehdä avattavan osion `<details>`-elementillä ja upottaa
  videon ja toisen sivun niin, että niillä on tekstitys ja nimi.
