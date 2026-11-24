# GLSL, uniformit ja muistiasettelu

GLSL on C:n kaltainen kieli vektoreille ja matriiseille. Siinä ei ole
osoittimia, rekursiota eikä dynaamista muistia, mutta siinä on
vektorityypit (`vec2`–`vec4`, `ivec`, `uvec`), matriisit
(`mat2`–`mat4`, sarakkeittain), sisäänrakennetut funktiot (`dot`,
`cross`, `normalize`, `mix`, `clamp`, `smoothstep`) ja *swizzle*-
merkintä, jolla komponentteja valitaan ja järjestetään: `v.xyz`,
`v.zyx`, `c.rgb`.

Varjostin saa dataa neljää reittiä:

| Reitti | Muuttuu | Esimerkki |
|--------|---------|-----------|
| verteksiattribuutti (`in` verteksivarjostimessa) | verteksistä toiseen | sijainti, normaali, UV |
| interpoloitu arvo (`out` → `in`) | pikselistä toiseen | väri, UV, normaali |
| uniform tai uniform-puskuri (UBO) | piirtokutsujen välillä | muunnosmatriisi, valot |
| tekstuuri tai varastopuskuri (SSBO) | mielivaltainen haku indeksillä | kuvat, instanssien data |

## Uniform-puskuri ja std140

Yksittäiset uniformit (`layout(location = 0) uniform mat4 m;`)
riittävät pienille määrille. Isompi data, jota moni ohjelma jakaa,
kuten kameran matriisit ja valot, kootaan *uniform-puskuriin* (UBO).
Puskuri on tavallinen GPU-puskuri, ja sen tavujen on vastattava GLSL:n
lohkon asettelua täsmälleen. Asettelusääntö `std140` määrittelee sen:

```{.cpp tiedosto="esimerkit/04-uniformit.cpp" osa="glsl"}
```

std140:n säännöt, jotka yllättävät:

- `vec3` tasataan 16 tavuun kuten `vec4`, mutta sen perään mahtuu
  `float` (tässä `kirkkaus` siirtymässä 76).
- Taulukon *jokainen alkio* vie vähintään 16 tavua. `float[3]` on 48
  tavua, ei 12.
- `mat4` on neljä `vec4`-saraketta. GLSL:n matriisit ovat
  sarakkeittain, joten C++-taulukon on oltava samassa järjestyksessä.

C++-rakenne kirjoitetaan vastaamaan lohkoa, ja `static_assert` pitää
huolen, ettei kukaan riko vastaavuutta huomaamattaan:

```{.cpp tiedosto="esimerkit/04-uniformit.cpp" osa="cpp"}
```

Asettelu voidaan myös kysyä ajurilta. Se on hyvä tapa varmistaa
oletus:

```{.cpp tiedosto="esimerkit/04-uniformit.cpp" osa="kysely"}
```

Puskuri täytetään ja sidotaan sidontapisteeseen 0, johon lohkon
`binding = 0` viittaa:

```{.cpp tiedosto="esimerkit/04-uniformit.cpp" osa="paivitys"}
```

```{.tuloste tiedosto="esimerkit/04-uniformit.odotettu"}
```

Väri on (1, 0,5, 0) · 0,8 · (0,5 + 0,25 + 0,25) = (0,8, 0,4, 0), eli
(204, 102, 0). Jos `painot` olisi C++:ssa tiivis `float[3]`, toinen ja
kolmas paino luettaisiin täytetavuista ja väri olisi väärä mutta
uskottava. Tämä on yleisin UBO-virhe.

**std430** on tiiviimpi asettelu, jota käytetään varastopuskureissa
(SSBO) ja Vulkanin push-vakioissa: taulukon `float`-alkiot vievät
4 tavua. `vec3` tasataan kuitenkin edelleen 16 tavuun, minkä vuoksi
moni välttää `vec3`-tyyppiä puskureissa kokonaan ja käyttää `vec4`:ää.

## Piirto ilman verteksipuskuria

Esimerkin neliö piirretään ilman verteksidataa: verteksivarjostin
valitsee kulman sisäänrakennetusta muuttujasta `gl_VertexID`, joka
on piirtokutsun verteksin järjestysnumero. Ydinprofiili vaatii
silti sidotun (tyhjän) VAO:n. Sama tekniikka on tavallinen koko ruudun
kattaville jälkikäsittelyvaiheille (luvut 5 ja 11).

## Tarkkuus ja liukuluvut varjostimissa

Varjostimen `float` on 32-bittinen. Mobiililaitteilla GLSL ES:n
tarkkuusmääreet (`mediump`, `lowp`) voivat pudottaa sen 16 bittiin,
mikä näkyy esimerkiksi isojen UV-koordinaattien tai sijaintien
värinänä. Liukulukujen ominaisuuksista kertoo taito *Miten tietokone
laskee*.

## Käytännössä

- **Kirjoita C++-rakenne ja GLSL-lohko yhdessä ja lukitse vastaavuus
  `static_assert`illa.** Vielä parempi on generoida toinen toisesta
  tai käyttää heijastusta (reflection, esim. SPIRV-Reflect).
- **Vältä `vec3`:a puskureissa.** Käytä `vec4`:ää tai kahta erillistä
  kenttää, niin std140/std430-tasauksen yllätykset poistuvat.
- **Ryhmittele uniformit päivitystiheyden mukaan.** Ruudun data
  (kamera), materiaalin data ja piirron data omiin lohkoihinsa. Silloin
  ruudun data päivitetään kerran ruudussa, ei kerran piirrossa.
- **Hajoava haarautuminen ja silmukat datan mukaan ovat kalliita**
  (luku 2). Uniform-muuttujan mukaan haarautuminen on halpaa, koska
  kaikki säikeet menevät samaan haaraan.

## Itsearviointi

- Osaat valita oikean reitin datalle varjostimeen: attribuutti,
  interpoloitu arvo, uniform tai UBO, tekstuuri tai SSBO.
- Osaat laskea std140-asettelun siirtymät ja kirjoittaa sitä
  vastaavan C++-rakenteen.
- Osaat kysyä lohkon asettelun ajurilta ja tunnistaa
  asettelueroista johtuvat virheet.
- Osaat piirtää ilman verteksipuskuria `gl_VertexID`:n avulla.
