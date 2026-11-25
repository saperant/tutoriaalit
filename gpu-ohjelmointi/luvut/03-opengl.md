# OpenGL: konteksti, puskurit ja ensimmäinen kolmio

OpenGL on tilakone. Kutsut kuten `glUseProgram` tai `glBindVertexArray`
muuttavat *kontekstin* nykyistä tilaa, ja piirtokutsu käyttää sitä
tilaa, joka on voimassa kutsuhetkellä. Tämä on OpenGL:n helppous ja
sen suurin sudenkuoppa: unohtunut sidonta toisesta koodin osasta
muuttaa piirtoa hiljaa.

Tutoriaali käyttää OpenGL 4.5:n **suoraa tilankäsittelyä** (DSA,
direct state access): oliota muokataan sen nimellä (`glNamedBuffer…`,
`glTexture…`), eikä sitä tarvitse sitoa ensin. Vanhemmissa ohjeissa
näkyvä `glBindBuffer` + `glBufferData` -pari tekee saman mutta
muuttaa sivuvaikutuksena kontekstin tilaa.

## Konteksti ilman ikkunaa

Tavallisesti konteksti luodaan ikkunakirjastolla (GLFW, SDL), joka
liittää kontekstiin ikkunan pinnan. Ilman ikkunaa konteksti luodaan
suoraan EGL:llä ja piirretään omaan kehyspuskuriin:

```{.cpp tiedosto="esimerkit/yhteinen/gl.hpp" osa="konteksti"}
```

Kolme yksityiskohtaa:

- **Ydinprofiili** (core profile) jättää pois vanhentuneet
  ominaisuudet, kuten kiinteän toiminnon putken (`glBegin`/`glEnd`).
  Vanhoista oppaista kopioitu koodi ei siksi toimi, mikä on hyvä asia.
- **Debug-konteksti ja `glDebugMessageCallback`** saavat ajurin
  kertomaan virheistä viesteinä. Ilman niitä virhe näkyy vain
  `glGetError`-kutsulla, jota kukaan ei muista kutsua oikeassa
  kohdassa. Synkroninen tila takaa, että viesti tulee virheen
  aiheuttaneen kutsun aikana.
- **Takaisinkutsusta ei heitetä poikkeusta**, koska se kulkisi ajurin
  C-koodin läpi. Viesti tallennetaan, ja `tarkista()` heittää sen
  myöhemmin.

## Varjostinohjelma

Varjostimet käännetään ajonaikaisesti ajurin kääntäjällä.
Käännös- ja linkitysvirheet on aina luettava lokista; muuten tuloksena
on vain musta ruutu.

```{.cpp tiedosto="esimerkit/yhteinen/gl.hpp" osa="ohjelma"}
```

## Verteksidata ja verteksitaulukko

Kolmion kärjet ovat C++-taulukossa. Koordinaatit ovat *normalisoituja
laitekoordinaatteja* (NDC): kuvan vasen alakulma on (−1, −1) ja oikea
yläkulma (1, 1).

```{.cpp tiedosto="esimerkit/03-kolmio.cpp" osa="data"}
```

Data kopioidaan GPU:n puskuriin, ja *verteksitaulukko-olio* (VAO)
kuvaa, miten puskuria luetaan: mistä sidontapisteestä, millä
askeleella (stride) ja mistä siirtymästä kukin attribuutti alkaa.

```{.cpp tiedosto="esimerkit/03-kolmio.cpp" osa="puskurit"}
```

`glNamedBufferStorage` luo muuttumattoman kokoisen puskurin. Lippu 0
kertoo, ettei CPU kirjoita puskuriin enää; ajuri voi sijoittaa sen
nopeimpaan muistiin. Usein päivitettävälle datalle annetaan liput
kuten `GL_DYNAMIC_STORAGE_BIT` tai `GL_MAP_WRITE_BIT`.

## Varjostimet

```{.cpp tiedosto="esimerkit/03-kolmio.cpp" osa="varjostimet"}
```

Verteksivarjostin ajetaan kerran jokaiselle verteksille. Sen
pakollinen tulos on `gl_Position`, sijainti *leikkausavaruudessa*
(clip space). Kiinteä vaihe jakaa sen w-komponentilla, jolloin saadaan
NDC-koordinaatit. Tässä w on 1, joten jako ei muuta mitään;
perspektiiviprojektiossa w on syvyys, ja jako tekee kaukaisista
kohteista pienempiä.

`out`-muuttujat interpoloidaan rasteroinnissa kolmion yli ja
luetaan fragmenttivarjostimessa samannimisinä `in`-muuttujina.
Fragmenttivarjostin ajetaan kerran jokaiselle peitetylle pikselille.

## Piirto ja tulos

```{.cpp tiedosto="esimerkit/03-kolmio.cpp" osa="piirto"}
```

```{.cpp tiedosto="esimerkit/03-kolmio.cpp" osa="raportti"}
```

```{.tuloste tiedosto="esimerkit/03-kolmio.odotettu"}
```

![Kolmio, jonka kärkien värit on interpoloitu.](kuvat/03-kolmio.png){width=30%}

Keskikohdan väri on kärkivärien painotettu keskiarvo (barysentriset
koordinaatit). Kolmion pinta-ala on noin 77 · 77 / 2 ≈ 2 950
pikseliä; rasteroija laskee pikselin peitetyksi, jos pikselin
*keskipiste* on kolmion sisällä, joten luku on hieman pienempi.

Kehyspuskurin luku CPU:lle näkyy tiedostossa `gl.hpp`:

```{.cpp tiedosto="esimerkit/yhteinen/gl.hpp" osa="kehys"}
```

`glGetTextureImage` pysäyttää CPU:n, kunnes GPU on piirtänyt kaiken
edeltävän. Oikeassa sovelluksessa tulos luetaan vain testeissä tai
kuvakaappauksissa; muuten luku tehdään asynkronisesti
pikselipuskuriin (PBO), jotta CPU ja GPU eivät odota toisiaan.

## Indeksoitu piirto

Useimmissa malleissa sama kärki kuuluu moneen kolmioon: kuution kulma
kolmeen sivuun ja sileän pinnan kärki keskimäärin kuuteen kolmioon.
**Indeksipuskuri** (element buffer) tallentaa kärjet kerran ja kolmiot
kärkien numeroina. Nelikulmio on pienin esimerkki:

```{.cpp tiedosto="esimerkit/03-indeksit.cpp" osa="data"}
```

Indeksipuskuri on tavallinen puskuri, joka liitetään
verteksitaulukkoon. Piirtokutsu on `glDrawElements`, jolle kerrotaan
indeksien määrä ja tyyppi:

```{.cpp tiedosto="esimerkit/03-indeksit.cpp" osa="indeksoitu"}
```

Vertailuksi sama nelikulmio puretaan kuudeksi kärjeksi ja piirretään
`glDrawArrays`-kutsulla:

```{.cpp tiedosto="esimerkit/03-indeksit.cpp" osa="purettu"}
```

```{.cpp tiedosto="esimerkit/03-indeksit.cpp" osa="raportti"}
```

```{.tuloste tiedosto="esimerkit/03-indeksit.odotettu"}
```

Kuvat ovat pikselilleen samat. Indeksoitu versio vie vähemmän muistia,
ja verteksivarjostin ajettiin neljästi kuuden sijaan (putken
tilastokysely `GL_VERTEX_SHADER_INVOCATIONS`). Laite saa ajaa
varjostimen samalle kärjelle uudelleen, jos kärki on ehtinyt poistua
sen välimuistista, joten neljä on alaraja eikä takuu. Oikeissa
malleissa säästö on suurempi: kärki vie kymmeniä tavuja (sijainti,
normaali, tekstuurikoordinaatit) ja indeksi kaksi tai neljä.
16-bittinen indeksi riittää 65 536 kärjelle, ja suuremmat mallit
käyttävät 32-bittisiä indeksejä.

## Käytännössä

- **Käytä DSA:ta ja debug-kontekstia.** Ne poistavat kaksi yleisintä
  virhelähdettä: väärään olioon kohdistuvan sidonnan ja huomaamatta
  jääneen virheen. Kehitysversiossa debug-viestit ovat aina päällä.
- **Tarkista varjostimien käännös ja linkitys aina.** Ajurit eroavat
  siinä, mitä ne hyväksyvät. Koodi, joka kääntyy yhdellä valmistajalla,
  voi hylkääntyä toisella. `glslangValidator` (luku 8) tarkistaa
  GLSL:n määrittelyä vasten ilman ajuria.
- **Indeksoi mallit.** Jaetut kärjet tallennetaan ja varjostetaan
  kerran. Mallien tiedostomuodot ja työkalut tuottavat indeksoitua
  dataa valmiiksi.
- **Puskurit kerralla ja harvoin.** Puskurin luonti on kallis; luo ne
  käynnistyksessä ja päivitä sisältöä. `glNamedBufferStorage` kertoo
  ajurille etukäteen, miten puskuria käytetään.
- **Älä lue GPU:n tuloksia synkronisesti ruudunpiirron aikana.**
  `glReadPixels`, `glGetTextureImage` ja kyselyjen tulokset
  pysäyttävät putken. Käytä PBO:ta tai lue tulos vasta seuraavalla
  ruudulla.
- **Kirjoita koodi niin, että tila asetetaan ennen jokaista piirtoa.**
  Älä luota siihen, että joku muu jätti oikean ohjelman tai VAO:n
  sidotuksi.

## Itsearviointi

- Osaat luoda OpenGL-kontekstin ilman ikkunaa ja ottaa debug-viestit
  käyttöön.
- Osaat kääntää ja linkittää varjostinohjelman ja lukea virhelokin.
- Osaat kuvata verteksidatan puskuriin ja verteksitaulukkoon DSA:lla:
  sidontapiste, askel, siirtymä ja attribuutin muoto.
- Osaat selittää leikkausavaruuden, perspektiivijaon ja NDC:n sekä
  sen, miten `out`-muuttujat interpoloidaan fragmenteille.
- Osaat piirtää indeksoidun mallin ja kertoa, mitä indeksipuskuri
  säästää.
- Osaat piirtää omaan kehyspuskuriin ja lukea tuloksen CPU:lle sekä
  kertoa, miksi luku on kallis.
