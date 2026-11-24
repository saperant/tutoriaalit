# Kuvat ja pikselit

Renderöijän tulos on **kuvapuskuri** (framebuffer): suorakulmainen
taulukko pikseleitä. Ennen kuin piirretään mitään, on sovittava kaksi
asiaa: miten pikselit ovat muistissa ja mitä pikselin numero
tarkoittaa. Ensimmäinen on helppo, toinen on yllättävän monen
grafiikkavirheen syy.

## Kuvapuskuri

Pikselit tallennetaan rivi kerrallaan ylhäältä alas, joten pikselin
$(x, y)$ indeksi on $y \cdot \text{leveys} + x$. Tämä on sama järjestys
kuin näytöllä ja useimmissa kuvatiedostoissa. Ruudun koordinaatistossa
$y$ kasvaa siis alaspäin, toisin kuin matematiikassa. Ristiriita
ratkaistaan yhdessä paikassa, näkymäporttimuunnoksessa (luku
*Muunnokset*); muualla putki käyttää tavallista $y$ ylös -suuntaa.

```{.cpp tiedosto="esimerkit/yhteinen/kuva.hpp" osa="kuva"}
```

`aseta` tarkistaa rajat ja jättää ulkopuoliset pikselit piirtämättä.
Viivoissa ja testeissä se on kätevä, mutta varsinainen rasteroija
leikkaa työalueen ruudun kokoiseksi etukäteen eikä tarkista jokaista
pikseliä erikseen.

## Väri on valon määrä

Näytön pikseli lähettää valoa kolmella päävärillä: punaisella,
vihreällä ja sinisellä. Renderöijän laskut (valaistus, sekoitus,
suodatus, keskiarvot) koskevat valon määrää, joka on **lineaarinen**:
kaksi lamppua antaa kaksinkertaisen määrän valoa. Siksi renderöijä
laskee liukuluvuilla, joissa 0 on pimeä ja 1 näytön maksimi:

```{.cpp tiedosto="esimerkit/yhteinen/kuva.hpp" osa="vari"}
```

Tallennettu pikseli on kuitenkin kolme tavua, ja tavut eivät ole
lineaarisia valon suhteen. Ihmisen näkö erottaa tummia sävyjä paljon
tarkemmin kuin kirkkaita, joten 256 tasoa kannattaa jakaa niin, että
tummille sävyille annetaan enemmän tasoja. Tätä koodausta kutsutaan
**gammaksi**, ja sen nykyinen standardi on **sRGB**.

## sRGB-siirtofunktio

sRGB:n siirtofunktio on likimain potenssifunktio
$s = v^{1/2.2}$, tarkemmin potenssi $1/2.4$ ja pienillä arvoilla
lineaarinen osa, jotta derivaatta ei kasva nollan lähellä äärettömäksi:

```{.cpp tiedosto="esimerkit/yhteinen/kuva.hpp" osa="srgb"}
```

Kuvan tallentaminen tarkoittaa siis koodausta (`koodaa`) ja
tekstuurin lukeminen purkua (`pura`). Taulukko näyttää, mitä tämä
tarkoittaa käytännössä:

```{.cpp tiedosto="esimerkit/02-gamma.cpp" osa="taulukko"}
```

```{.tuloste tiedosto="esimerkit/02-gamma.odotettu"}
```

Puolet näytön valosta on tavu 188, ei 128. Tavu 128 vastaa noin 22
prosenttia valosta. Jos renderöijä kirjoittaa lineaarisen arvon
suoraan tavuksi (sarake *naiivi tavu*), kuva on liian tumma ja
kontrastinen, ja valaistus näyttää väärältä: pallon reunat tummuvat
liian nopeasti ja valon ja varjon raja on terävä.

Tulosteen keskimmäinen osa näyttää toisen tyypillisen virheen.
Punaisen ja vihreän keskiarvo tavuista laskettuna on tumma
(128, 128, 0), oikea keskiarvo valona on (188, 188, 0). Sama virhe
tapahtuu aina, kun pikseleitä sekoitetaan koodatussa muodossa:
kuvan pienennyksessä, läpinäkyvyydessä ja suodatuksessa. Tummat
reunat pienennetyissä kuvissa ja likaiset värisiirtymät johtuvat
yleensä tästä.

```{.cpp tiedosto="esimerkit/02-gamma.cpp" osa="sekoitus"}
```

![Ylhäällä tavut kasvavat tasaisesti, keskellä vasemmalla
mustavalkoinen shakkiruutu ja oikealla lineaarinen 0,5 koodattuna,
alhaalla valo kasvaa tasaisesti.](kuvat/02-gamma.png){width=55%}

Kuvan keskimmäinen raita on hyvä testi omalle näytölle. Vasemmalla
puolella on vuorotellen mustia ja valkoisia pikseleitä, joiden
keskiarvo on täsmälleen puolet valosta. Oikea puoli on lineaarinen 0,5
sRGB-koodattuna eli tavu 188. Kauempaa katsottuna puoliskojen pitäisi
näyttää yhtä kirkkailta. Tavu 128 näyttäisi selvästi tummemmalta.

## Missä muodossa mikin on

| Data | Muoto | Syy |
|------|-------|-----|
| renderöijän laskut | lineaarinen liukuluku | valo summautuu |
| tallennettu kuva, näyttö | sRGB-tavut | tasot tummiin sävyihin |
| värikuva tekstuurina | sRGB, puretaan luettaessa | piirretty silmälle |
| normaali-, syvyys- ja maskikartat | lineaarinen | eivät ole valoa |
| välipuskurit (HDR) | 16 tai 32 bitin liukuluku | yli 1:n arvot |

Näytönohjaimissa koodaus ja purku tehdään laitteistossa:
tekstuuri- ja kehyspuskurimuodoilla on sRGB-versiot (esimerkiksi
`R8G8B8A8_SRGB`), jotka purkavat luettaessa ja koodaavat
kirjoitettaessa. Ohjelmoijan tehtävä on valita oikea muoto. Väri
1,0 ei myöskään ole yläraja: kirkas taivas tai lamppu voi olla
satoja kertoja valkoista paperia kirkkaampi. Tällaiset **HDR**-arvot
pakataan näytettäviksi **sävykartoituksella** (tone mapping) ennen
sRGB-koodausta. Tämän tutoriaalin kohtaukset pysyvät välillä 0–1, ja
`koodaa` vain leikkaa ylimenevät arvot.

## PPM-tiedostomuoto

Yksinkertaisin tapa saada kuva levylle on binäärinen **PPM** (P6):
tekstimuotoinen otsikko, jossa ovat tunniste, leveys, korkeus ja
suurin arvo, ja sen perään RGB-tavut rivi kerrallaan. Pakkausta tai
metatietoja ei ole, joten kirjoittaja mahtuu kymmeneen riviin (ks.
`tallenna_ppm` yllä):

```{.cpp tiedosto="esimerkit/02-gamma.cpp" osa="liuku"}
```

Tiedoston koko on otsikko ja $3 \cdot 64 \cdot 24$ tavua. PNG olisi
pienempi mutta vaatisi pakkauskirjaston. Kuvatiedostojen värit ovat
sovinnaisesti sRGB:tä, ellei tiedostossa toisin kerrota.

## Tarkistussumma testinä

Kuvan oikeellisuutta on vaikea testata katsomalla. Siksi esimerkit
tulostavat kuvasta tarkistussumman ja tilastoja:

```{.cpp tiedosto="esimerkit/yhteinen/kuva.hpp" osa="summa"}
```

FNV-1a sekoittaa jokaisen tavun tilaan, joten yksikin muuttunut
pikseli muuttaa summan. Summa ei kerro, *mikä* muuttui, joten sen
rinnalla tulostetaan peitto (montako pikseliä poikkeaa taustasta) ja
keskikirkkaus, jotka kertovat muutoksen suunnan. Kirkkaus lasketaan
tavuista Rec. 709 -painoilla; se ei ole tarkka valon määrä vaan
karkea luku vertailuun. Isommissa projekteissa kuvia verrataan
vertailukuviin pikseleittäin ja sallitaan pieni toleranssi, koska eri
laitteet pyöristävät eri tavoin. Tässä tutoriaalissa toleranssia ei
tarvita, koska kaikki lasketaan samoilla IEEE 754 -operaatioilla.

Lisäksi `ascii` tulostaa kuvasta pienen esikatselun merkkeinä, jotta
tulosteesta näkee kuvan muodon:

```{.cpp tiedosto="esimerkit/yhteinen/kuva.hpp" osa="ascii"}
```

## Käytännössä

- **Laske lineaarisesti, tallenna sRGB:nä.** Pura tekstuurit ennen
  käyttöä ja koodaa tulos vasta lopuksi. Jokainen keskiarvo,
  summa tai interpolointi koodatuilla arvoilla on virhe.
- **Pidä ruudun $y$-suunta yhdessä paikassa.** Kuvatiedostot ja näytöt
  aloittavat ylhäältä, OpenGL:n tekstuurit alhaalta, Vulkanin NDC
  ylhäältä. Muunna yhdessä kohdassa ja kirjoita se näkyviin.
- **Tee kuvista testattavia.** Tarkistussumma, tilastot ja
  vertailukuva tekevät renderöijästä regressiotestattavan.
  Satunnaisuus (kohina, näytekuviot) tarvitsee kiinteän siemenen.
- **PPM on hyvä välimuoto.** Sen voi kirjoittaa ilman kirjastoja ja
  muuntaa muihin muotoihin työkaluilla.

## Itsearviointi

- Osaat selittää, miksi renderöijä laskee lineaarisella valolla ja
  miksi tallennettu kuva on sRGB-koodattu.
- Osaat muuntaa arvon sRGB-koodaukseen ja takaisin sekä kertoa, mikä
  tavu vastaa puolta valosta.
- Osaat tunnistaa virheet, jotka syntyvät, kun koodattuja arvoja
  sekoitetaan tai suodatetaan.
- Osaat kirjoittaa kuvan PPM-tiedostoksi ja testata kuvaa
  tarkistussummalla.
