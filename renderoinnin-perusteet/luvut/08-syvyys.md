# Syvyys ja näkyvyys

Kun kaksi kolmiota peittää saman pikselin, näkyviin pitää jäädä
lähempi. Varhaiset renderöijät lajittelivat kolmiot takaa eteen ja
piirsivät lähimmät viimeisinä (**maalarin algoritmi**). Lajittelu ei
kuitenkaan toimi, kun kolmiot leikkaavat toisiaan tai peittävät
toisiaan ristiin, ja se maksaa joka ruudulla. Nykyään näkyvyys
ratkaistaan pikseleittäin **syvyyspuskurilla** (z-puskuri, Catmull
1974): jokaiselle pikselille tallennetaan lähimmän tähän mennessä
piirretyn pinnan syvyys.

## Syvyystesti

Syvyyspuskuri alustetaan arvoon 1 (kaukotaso). Jokaiselle
fragmentille interpoloidaan syvyys, ja fragmentti piirretään vain, jos
se on lähempänä kuin puskurissa oleva arvo. Silloin myös puskuri
päivitetään:

```{.cpp tiedosto="esimerkit/yhteinen/putki.hpp" osa="kolmio"}
```

Testi tehdään ennen fragmenttivarjostinta. Peitetyn pikselin
varjostaminen olisi turhaa työtä, joten näytönohjaimetkin tekevät
testin etukäteen (**early-z**), aina kun varjostin ei itse muuta
syvyyttä tai hylkää pikseleitä. Läpinäkymättömät kappaleet kannattaa
siksi piirtää edestä taakse: takimmaisten fragmentit hylätään ennen
varjostusta.

Syvyyspuskurilla piirtojärjestyksellä ei ole väliä tulokselle (paitsi
täsmälleen yhtä syvillä pinnoilla). Poikkeus ovat läpinäkyvät pinnat,
joiden väri sekoitetaan taustaan. Ne piirretään läpinäkymättömien
jälkeen takaa eteen lajiteltuina, ja syvyyspuskuriin niitä ei
kirjoiteta. Sekoitus toteutetaan taidossa *GPU-ohjelmointi: OpenGL ja Vulkan*.

## Syvyyden jakauma

Puskuriin tallennetaan $d = (z/w + 1)/2$, joka on perspektiivijaon
jälkeen lineaarinen ruudulla (luku *Perspektiivi*). Projektiomatriisin
kolmannesta rivistä seuraa, että se on muotoa

$$d = A - \frac{B}{e}, \qquad
B = \frac{\text{kauka} \cdot \text{lähi}}{\text{kauka} - \text{lähi}},$$

missä $e$ on etäisyys kamerasta. Syvyys on siis lineaarinen $1/w$:n
eikä etäisyyden suhteen. Taulukko näyttää, mitä se tarkoittaa
lähitasolla 0,1 ja kaukotasolla 100:

```{.cpp tiedosto="esimerkit/08-syvyys.cpp" osa="jakauma"}
```

```{.tuloste tiedosto="esimerkit/08-syvyys.odotettu" rivit="1-10"}
```

![Syvyyspuskurin arvo etäisyyden funktiona (etäisyysakseli on
logaritminen). Lähitasolla 0,1 puolet arvoista kuluu etäisyyksiin
alle 0,2. Lähitaso 1 siirtää saman käyrän kymmenkertaiselle
etäisyydelle.](kuvat/08-syvyysjakauma.png){width=62%}

Puolet koko syvyysalueesta kuluu etäisyyksiin 0,1–0,2, ja 90
prosenttia etäisyyksiin alle yhden. Sarakkeet oikealla kertovat, kuinka
suuri etäisyysero vastaa yhtä puskurin porrasta: 24 bitillä 100
yksikön päässä porras on 6 millimetriä (jos yksikkö on metri), 16
bitillä puolitoista metriä. Porras kasvaa etäisyyden neliönä ja on
kääntäen verrannollinen lähitason etäisyyteen. Lähitason siirtäminen
0,1:stä 1:een parantaa tarkkuutta kymmenkertaisesti; kaukotason
siirtäminen vaikuttaa vähän.

## Z-taistelu

Kun kaksi pintaa on lähempänä toisiaan kuin syvyyden porras, niiden
syvyydet pyöristyvät samoiksi, ja testi ratkeaa sattumanvaraisesti:
pinnat välkkyvät kameran liikkuessa (**z-taistelu**, z-fighting).
Esimerkin toinen osa piirtää kaksi lattiaa millimetrin päähän
toisistaan. Alempi (punainen) piirretään ensin, ja ylempi (sininen)
sen päälle, joten oikeassa kuvassa punaista ei näy lainkaan:

```{.cpp tiedosto="esimerkit/08-syvyys.cpp" osa="piirto"}
```

```{.tuloste tiedosto="esimerkit/08-syvyys.odotettu" rivit="12-21"}
```

![Sama kohtaus suuremmalla tarkkuudella: vasemmalla 16-bittinen ja
oikealla 24-bittinen syvyyspuskuri. Punainen kaista horisontin
tuntumassa on alempi lattia, jonka ylemmän olisi pitänyt
peittää.](kuvat/08-syvyys.png){width=85%}

16-bittisellä puskurilla kaukaiset rivit (tulosteessa `#`) jäävät punaisiksi:
ylemmän lattian syvyys pyöristyy samaksi kuin alemman, ja testi
`z < puskuri` hylkää sen. 24 bittiä ja liukuluku selviävät tästä
kohtauksesta. Viistossa kulmassa katsottu pinta on pahin tapaus,
koska säteen suuntainen ero kahden pinnan välillä on silloin
pieni suhteessa etäisyyteen.

Z-taistelua torjutaan näin:

- **Lähitaso niin kauas kuin mahdollista.** Tämä on tehokkain keino.
- **Käänteinen syvyys** (reversed-Z): syvyysväli $0 \ldots 1$
  käännetään niin, että kaukotaso on 0, ja puskuri on 32-bittinen
  liukuluku. Liukuluvun tarkkuus on suurimmillaan nollan lähellä, ja
  se kumoaa $1/w$-jakauman epätasaisuuden lähes kokonaan.
- **Syvyyssiirtymä** (polygon offset) siirtää tarkoituksella
  samassa tasossa olevia pintoja, kuten tarroja ja varjokarttojen
  syvyyksiä.
- **Mallinnus**: kaksi pintaa ei saa olla samassa tasossa, jos
  molempien on tarkoitus näkyä.

## Takapintojen karsinta

Suljetun kappaleen, kuten kuution tai pallon, takapuolen kolmiot eivät
voi koskaan näkyä: etupuoli peittää ne aina. Kolmion kiertosuunta
ruudulla kertoo, kumpi puoli on kameraan päin. Mallin kolmiot ovat
ulkoa katsottuna vastapäivään (luku *Muunnokset*), joten ruudulla
myötäpäivään kiertävä kolmio on kääntynyt kamerasta poispäin ja
voidaan hylätä ennen rasterointia. Tämä on **takapintojen karsinta**
(back-face culling), ja sen testi on sama ristitulo kuin
reunafunktiossa.

```{.cpp tiedosto="esimerkit/08-karsinta.cpp" osa="karsinta"}
```

```{.tuloste tiedosto="esimerkit/08-karsinta.odotettu"}
```

Kuva on molemmilla kerroilla sama (sama tarkistussumma), mutta
karsinnan kanssa puolet kolmioista hylätään ennen rasterointia, eikä
yhtään fragmenttia hylätä syvyystestissä. Ilman karsintaa rasteroija
käsittelee 670 fragmenttia, joista 170 hylätään syvyystestissä. Kun
kuution kolmiot piirretään eri järjestyksessä, osa takapinnoista
piirretään ensin ja peitetään myöhemmin, mikä on täysin turhaa työtä.

Karsinta toimii vain suljetuille, oikein suunnatuille malleille. Ohut
seinä, lehti tai kangas näkyy molemmilta puolilta, joten sille karsinta
kytketään pois ja valaistuksessa normaali käännetään kameraan päin.
Väärin päin mallinnettu kolmio katoaa karsinnassa, mikä on tavallinen
virhe tuoduissa malleissa.

## Käytännössä

- **Alusta syvyyspuskuri ja käytä testiä aina** läpinäkymättömille
  pinnoille. Piirtojärjestys on silloin vain suorituskykykysymys.
- **Piirrä edestä taakse** läpinäkymättömät kappaleet, jotta
  early-z hylkää peitetyt fragmentit ennen varjostusta.
- **Valitse lähitaso huolella** ja käytä käänteistä syvyyttä, jos
  näkymä on laaja (maasto, avaruus).
- **Karsi takapinnat suljetuilta malleilta** ja tarkista mallien
  kiertosuunta tuonnissa.

## Itsearviointi

- Osaat selittää syvyyspuskurin toiminnan ja sen, miksi se korvasi
  maalarin algoritmin.
- Osaat kertoa, miksi syvyys on lineaarinen $1/w$:n eikä etäisyyden
  suhteen, ja mitä se tarkoittaa tarkkuudelle.
- Osaat selittää z-taistelun ja luetella keinot sen torjumiseksi.
- Osaat kertoa, miten takapintojen karsinta toimii ja milloin se
  pitää kytkeä pois.
