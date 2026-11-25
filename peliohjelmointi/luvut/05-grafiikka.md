# 2D-grafiikka

Tähän asti peli on ollut lukuja: aikaa, syötettä ja tiloja. Nyt tila
piirretään näkyviin. Grafiikkakirjasto (SDL, SFML, raylib tai
pelimoottori) hoitaa ikkunan
ja kuvien siirron näytönohjaimelle, mutta 2D-pelin piirron käsitteet
ovat samat kaikissa: kuvapuskuri, spritet, atlas, animaatio, kamera ja
karsinta. Tässä luvussa ne toteutetaan ohjelmistona omaan
kuvapuskuriin, jotta jokainen pikseli on näkyvissä ja testattavissa.
SDL2:lla näytölle vienti on luvussa *Kipinä*.

## Kuvapuskuri

Kuvapuskuri on taulukko pikseleitä rivi kerrallaan. Pikselin paikka
on `y * leveys + x`. Tallennettu kuva ja sen tarkistussumma tekevät
piirrosta testattavan: muutos piirtokoodissa näkyy summassa.

```{.cpp tiedosto="esimerkit/05-piirto/kuva.hpp" osa="kuva"}
```

Kaikki piirto *leikataan* (clipping) kuvan rajoihin: ruudun reunan yli
menevä sprite piirretään osittain, eikä kirjoita muistin ohi.

```{.cpp tiedosto="esimerkit/05-piirto/kuva.cpp" osa="piirra"}
```

Esimerkin sprite on joko täysin peittävä tai läpinäkyvä
(*väriavain*). Puoliläpinäkyvyys vaatisi *alfasekoituksen*:
`kohde = lähde · a + kohde · (1 − a)`, jolloin piirtojärjestyksellä on
väliä ja läpinäkyvät kappaleet piirretään takaa eteen.

## Spritet, atlas ja animaatio

*Sprite* on pieni kuva, joka piirretään maailmaan. Spritet kootaan
*atlakseen* (sprite sheet): yhteen suureen kuvaan, josta kukin sprite
on alue. Näytönohjaimella atlas on merkittävä optimointi, koska
tekstuurin vaihtaminen piirtokutsujen välillä on kallista: saman atlaksen
spritet voidaan piirtää yhdellä kutsulla (batching).

```{.cpp tiedosto="esimerkit/05-piirto/main.cpp" osa="atlas"}
```

Esimerkin atlas on kirjoitettu ASCII-taiteena, jotta se näkyy
tekstissä; oikeassa pelissä se ladataan kuvatiedostosta. Animaatio on
lista atlaksen alueita ja kuvan kesto.

```{.cpp tiedosto="esimerkit/05-piirto/atlas.hpp" osa="animaatio"}
```

Animaatiokuva valitaan pelin ajasta. Jos kuva vaihdettaisiin joka
piirrolla, animaatio pyörisi 144 Hz:n näytöllä yli kaksi kertaa
nopeammin kuin 60 Hz:n näytöllä.

## Kamera ja koordinaatit

Pelin tila on *maailman koordinaateissa* (esimerkiksi pikseleinä tai
metreinä tason alusta). Kamera muuntaa ne *ruudun koordinaateiksi*.
2D-kamerassa muunnos on vähennyslasku; zoomaus ja kierto tekevät siitä
matriisin.

```{.cpp tiedosto="esimerkit/05-piirto/kamera.hpp" osa="kamera"}
```

Kamera seuraa pelaajaa vasta, kun tämä poistuu näkymän keskialueelta
(*kuollut alue*, dead zone). Pienet liikkeet eivät heiluta näkymää, mikä
on miellyttävämpää katsoa. Kamera ei myöskään näytä maailman
ulkopuolta. Pyöristys kokonaisiin pikseleihin tehdään vasta
muunnoksessa: jos kameran paikka pyöristettäisiin ensin, hidas liike
nytkähtelisi.

![Kamera ja pelaaja, joka juoksee oikealle ja kääntyy välillä takaisin.
Kamera pysyy paikallaan niin kauan kuin pelaaja on kuolleella alueella
ja liikkuu vasta, kun pelaaja työntää alueen reunaa. Alussa kamera ei
näytä maailman vasemman reunan ohi.](kuvat/kamera.png){width=75%}

Taustan voi piirtää useana *kerroksena*, joista kukin käyttää kameran
paikkaa eri kertoimella: kaukainen vuoristo liikkuu esimerkiksi
neljäsosan kameran matkasta ja pilvet kymmenesosan. Tämä
*parallaksivieritys* luo syvyysvaikutelman pelkällä
vähennyslaskulla, koska vain piirron muunnos muuttuu.

## Piirto ja karsinta

Näkymään piirretään vain ruudut, jotka ovat kameran alueella
(*karsinta*, culling). Ruutukartassa näkyvät ruudut lasketaan suoraan
kameran paikasta.

```{.cpp tiedosto="esimerkit/05-piirto/main.cpp" osa="piirto"}
```

```{.tuloste tiedosto="esimerkit/05-piirto.odotettu"}
```

Kartan 140 ruudusta piirretään 13. Tulosteen merkkikuvassa näkyy joka
toinen pikselirivi: kolikko, osa tasannetta, hahmo ja lattia. Sama
kuva tallentuu tiedostoon `ruutu.ppm` ja atlas tiedostoon `atlas.ppm`.

![Esimerkin tallentamat kuvat suurennettuina. Atlaksessa on neljä
kahdeksan pikselin spriteä: tiili, kolikko ja kaksi kävelyanimaation
kuvaa. Ruudussa näkyy kameran rajaama osa
maailmasta.](kuvat/piirto.png){width=95%}

## Käytännössä

- **Maailma ja ruutu erikseen.** Pelilogiikka ei tunne pikseleitä
  ruudulla; kamera ja piirto tekevät muunnoksen. Silloin
  resoluution vaihto tai jaettu ruutu ei muuta pelilogiikkaa.
- **Pikselitaide:** piirrä matalaan resoluutioon (esim. 320 × 180) ja
  skaalaa kokonaisluvulla näytölle. Muuten pikselit ovat erikokoisia.
- **Atlas ja eräpiirto.** Näytönohjaimella piirtokutsujen määrä ja
  tekstuurin vaihdot rajoittavat useammin kuin pikselimäärä.
- **Karsinta ennen piirtoa.** Suurissa maailmoissa myös päivitys
  rajataan aktiiviseen alueeseen.
- **Piirtojärjestys** (z-järjestys): tausta, ruudut, oliot, efektit,
  käyttöliittymä. Isometrisessa tai ylhäältä kuvatussa pelissä oliot
  lajitellaan y-koordinaatin mukaan.

## Itsearviointi

- Osaat piirtää spriten kuvapuskuriin leikkauksen ja väriavaimen kanssa
  ja kertoa, miten alfasekoitus muuttaa piirtojärjestystä.
- Osaat koota spritet atlakseen ja valita animaatiokuvan pelin ajasta.
- Osaat toteuttaa kameran, joka seuraa pelaajaa kuolleen alueen kanssa
  ja pysyy maailman rajoissa.
- Osaat karsia näkymän ulkopuoliset ruudut ennen piirtoa.
