# Renderöintitekniikat: varjokartat ja viivästetty varjostus

Lähes kaikki nykyiset renderöintitekniikat ovat monivaiheisia: yksi
vaihe piirtää tekstuuriin, ja seuraava lukee sitä. Tämä luku näyttää
kaksi keskeistä esimerkkiä OpenGL:llä, koska ne ovat sillä
lyhyempiä. Vulkanilla vaiheiden väliin tarvitaan lisäksi esteet ja
asettelun vaihdot (luku 9).

Esimerkkien matriisit tulevat pienestä apukirjastosta
`yhteinen/matriisi.hpp` (kamera, perspektiivi ja ortografinen
projektio). Oikeissa projekteissa käytetään GLM:ää tai vastaavaa.

## Varjokartat

Piste on varjossa, jos valolta katsottuna sen edessä on jotain.
Varjokartta ratkaisee tämän kahdessa vaiheessa:

1. Kohtaus piirretään **valon näkökulmasta** pelkkään syvyyspuskuriin.
   Jokainen kartan teksel tallentaa valoa lähimmän pinnan syvyyden.
2. Kohtaus piirretään **kameran näkökulmasta**. Jokainen pikseli
   muunnetaan valon koordinaatteihin, ja sen syvyyttä verrataan
   karttaan: jos kartassa on lähempi pinta, pikseli on varjossa.

```{.cpp tiedosto="esimerkit/11-varjokartta.cpp" osa="kartta"}
```

```{.cpp tiedosto="esimerkit/11-varjokartta.cpp" osa="kamera"}
```

Vertailu tehdään laitteistossa *vertailunäytteistimellä*
(`sampler2DShadow`, `GL_COMPARE_REF_TO_TEXTURE`). Lineaarisella
suodatuksella se vertaa neljää tekseliä ja palauttaa osuuden, mikä
pehmentää reunoja hieman ilmaiseksi.

```{.cpp tiedosto="esimerkit/11-varjokartta.cpp" osa="glsl"}
```

```{.cpp tiedosto="esimerkit/11-varjokartta.cpp" osa="raportti"}
```

```{.tuloste tiedosto="esimerkit/11-varjokartta.odotettu"}
```

![Varjokartta: levyn varjo lattialla.](kuvat/11-varjokartta.png){width=40%}

Varjokarttojen tyypilliset virheet ja korjaukset:

- **Varjoakne** (shadow acne): pinta varjostaa itseään raidoittain,
  koska kartan tarkkuus on rajallinen. Korjaus on pieni siirtymä
  (bias), kuten esimerkin 0,002, tai kaltevuuden mukaan kasvava
  siirtymä (`glPolygonOffset`).
- **Peter Panning**: liian suuri siirtymä irrottaa varjon kohteesta.
- **Portaat**: kartan tekselit näkyvät reunoissa. Korjauksia ovat
  isompi kartta, PCF-suodatus (useita vertailuja) ja porrastetut
  kaskadit (cascaded shadow maps), joissa lähialueella on oma
  tarkempi karttansa.

## Viivästetty varjostus

Tavallisessa (*forward*) renderöinnissä jokainen piirretty fragmentti
lasketaan kaikilla valoilla, myös ne, jotka myöhemmin peittyvät.
Kustannus on (fragmentit, myös peittyvät) × (valot).

Viivästetty varjostus (*deferred shading*) erottaa geometrian ja
valaistuksen:

1. **Geometriavaihe** piirtää kohtauksen ja kirjoittaa jokaisen
   näkyvän pikselin pinnan tiedot **G-puskuriin**: väri, normaali,
   sijainti (tai syvyys, josta sijainti lasketaan) ja materiaali.
   Kirjoitus tehdään useaan väriliitäntään kerralla (*MRT*, multiple
   render targets).
2. **Valaistusvaihe** käy jokaisen pikselin läpi kerran ja laskee
   valot G-puskurin tiedoilla.

```{.cpp tiedosto="esimerkit/11-viivastetty.cpp" osa="gpuskuri"}
```

```{.cpp tiedosto="esimerkit/11-viivastetty.cpp" osa="geometria"}
```

```{.cpp tiedosto="esimerkit/11-viivastetty.cpp" osa="valaistus"}
```

```{.cpp tiedosto="esimerkit/11-viivastetty.cpp" osa="vaiheet"}
```

```{.cpp tiedosto="esimerkit/11-viivastetty.cpp" osa="raportti"}
```

```{.tuloste tiedosto="esimerkit/11-viivastetty.odotettu"}
```

![G-puskurin kolme liitäntää geometriavaiheen jälkeen: pinnan väri,
normaali ja sijainti maailmassa (koordinaatit väreinä). Valaistusvaihe
lukee vain näitä kuvia eikä piirrä geometriaa
uudelleen.](kuvat/11-gpuskuri.png){width=95%}

![Viivästetty varjostus: kolme pistevaloa lattialla ja seinällä.](kuvat/11-viivastetty.png){width=40%}

Valaistuksen kustannus on nyt (näkyvät pikselit) × (valot), eikä se
riipu geometrian määrästä. Satoja valoja varten pikselit jaetaan
lisäksi ruutuihin tai klustereihin, ja kullekin lasketaan vain siihen
vaikuttavat valot (tiled tai clustered shading).

Hinta on **kaista ja muisti**: G-puskuri on esimerkissä 23 tavua
pikseliä kohden, eli 45 Mt 1080p-ruudulla, ja se kirjoitetaan ja
luetaan joka ruudussa. Lisäksi viivästetty varjostus ei sovi
läpinäkyville pinnoille (G-puskuriin mahtuu yksi pinta pikseliä
kohden), eikä se toimi suoraan MSAA-reunanpehmennyksen kanssa.
Siksi monet moottorit käyttävät *forward+*-mallia: valot
klusteroidaan, mutta varjostus tehdään yhdessä vaiheessa.

## Käytännössä

- **Monivaiheinen renderöinti on normaalia.** Varjot, syvyyden
  esipiirto, G-puskuri, valaistus, läpinäkyvät, jälkikäsittely ja
  käyttöliittymä ovat kukin oma vaiheensa. Niiden riippuvuudet
  kannattaa kuvata renderöintigraafina.
- **Valitse G-puskurin muodot tarkasti.** Normaali mahtuu kahteen
  komponenttiin (oktaedrikoodaus) ja sijainti lasketaan syvyydestä;
  jokainen säästetty tavu säästää kaistaa koko ruudulta.
- **Varjojen laatu on kompromissi.** Kaskadit, PCF ja siirtymä
  säädetään kohtauksen mittakaavan mukaan; yksi asetus ei sovi
  kaikkeen.
- **Forward vai deferred?** Vähän valoja ja paljon läpinäkyvyyttä tai
  MSAA: forward(+). Paljon valoja ja monimutkainen geometria:
  deferred tai clustered.

## Itsearviointi

- Osaat toteuttaa varjokartan kahdessa vaiheessa ja selittää
  vertailunäytteistimen.
- Osaat tunnistaa varjoaknen, Peter Panningin ja porrastuksen sekä
  niiden korjaukset.
- Osaat rakentaa G-puskurin usealla väriliitännällä ja toteuttaa
  valaistusvaiheen.
- Osaat vertailla forward- ja deferred-varjostusta kustannuksen,
  kaistan ja läpinäkyvyyden kannalta.
