# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Laske valolla, tallenna sRGB:nä.** Kaikki summat, keskiarvot,
   interpoloinnit ja suodatukset lineaarisilla arvoilla.
2. **Pikselin keskipiste on $(x + 0{,}5, y + 0{,}5)$**, ja reunoilla
   noudatetaan vasen-ylä-sääntöä.
3. **Kärjet kiinteään pilkkuun ennen peittotestiä**, jotta yhteiset
   reunat päätetään samoin molemmille kolmioille.
4. **Tiedä, missä koordinaatistossa kukin arvo on.** Malli, maailma,
   kamera, leikkausavaruus, NDC, ruutu.
5. **Leikkaa lähitasoa vastaan ennen jakoa $w$:llä**; muut tasot
   hoitaa suojakaista.
6. **Interpoloi perspektiivikorjatusti**, paitsi syvyys.
7. **Lähitaso kauas, tai käänteinen syvyys liukulukuna.**
8. **Normaalit käänteismatriisin transpoosilla, ja interpoloitu
   normaali normalisoidaan.**
9. **Mipmapit ja trilineaarinen tai anisotrooppinen suodatus**
   kaikille pienentyville tekstuureille.
10. **Tee kuvista testattavia**: deterministinen laskenta,
    tarkistussummat ja vaihekohtaiset tilastot.

## Jatkotaidot

- *GPU-ohjelmointi: OpenGL ja Vulkan*: sama putki OpenGL:llä ja Vulkanilla, varjostimet
  GLSL:nä, puskurit, synkronointi ja tekniikat kuten varjokartat ja
  viivästetty varjostus.
- *Säteenseuranta ja fysikaalinen valaistus*: näkyvyys säteillä
  rasteroinnin sijaan, varjot, heijastukset, epäsuora valo ja
  fysikaalisesti perustellut materiaalit (BRDF).
- *Peliohjelmointi* ja *3D-peliohjelmointi*: renderöinnin paikka
  pelisilmukassa; kolmiulotteisen pelin kamerat, näkymägraafi,
  törmäykset ja animaatio.
- *Kompleksiluvut ja Fourier-analyysi*: näytteenottoteoreema, suodattimet ja
  aliasointi yleisesti; tekstuurien ja reunanpehmennyksen teoria.

Hyviä harjoituksia tämän toteutuksen jatkoksi ovat varjokartta (syvyys
valosta katsottuna ja vertailu fragmenttivarjostimessa),
läpinäkyvyys ja sekoitus, normaalikartat tangenttiavaruudessa,
inkrementaaliset reunafunktiot lohkoittain sekä säikeistetty
ruutuihin perustuva rasterointi.

## Lähteet ja jatkolukeminen

Kirjat:

- Tomas Akenine-Möller, Eric Haines, Naty Hoffman ym.: *Real-Time
  Rendering*, 4. painos. CRC Press 2018.
- Steve Marschner, Peter Shirley: *Fundamentals of Computer Graphics*,
  5. painos. CRC Press 2021.
- Matt Pharr, Wenzel Jakob, Greg Humphreys: *Physically Based
  Rendering*, 4. painos. MIT Press 2023. <https://pbr-book.org/>
- John F. Hughes ym.: *Computer Graphics: Principles and Practice*,
  3. painos. Addison-Wesley 2013.

Alkuperäiset artikkelit:

- J. E. Bresenham: Algorithm for computer control of a digital
  plotter. *IBM Systems Journal* 4(1), 1965.
- Juan Pineda: A Parallel Algorithm for Polygon Rasterization.
  *SIGGRAPH* 1988.
- Ivan Sutherland, Gary Hodgman: Reentrant Polygon Clipping.
  *Communications of the ACM* 17(1), 1974.
- Edwin Catmull: *A Subdivision Algorithm for Computer Display of
  Curved Surfaces*. Väitöskirja, University of Utah 1974.
- Henri Gouraud: Continuous Shading of Curved Surfaces. *IEEE
  Transactions on Computers* C-20(6), 1971.
- Bui Tuong Phong: Illumination for Computer Generated Pictures.
  *Communications of the ACM* 18(6), 1975.
- James F. Blinn: Models of Light Reflection for Computer Synthesized
  Pictures. *SIGGRAPH* 1977.
- Lance Williams: Pyramidal Parametrics. *SIGGRAPH* 1983.

Artikkelit ja verkkoaineistot:

- Fabian Giesen: *A trip through the Graphics Pipeline 2011* ja
  *Optimizing the basic rasterizer* (blogisarjat): laitteiston ja
  ohjelmistorasteroijan toteutuksen yksityiskohdat.
- Nathan Reed: *Depth Precision Visualized* (2015): syvyyden
  jakauma ja käänteinen syvyys.
- Khronos Group: *Vulkan Specification*, luvut rasteroinnista,
  leikkauksesta ja näytteenotosta. <https://docs.vulkan.org/>
- Microsoft: *Direct3D 11 Rasterization Rules* (vasen-ylä-sääntö ja
  alipikselitarkkuus).
- IEC 61966-2-1: sRGB-väriavaruuden määrittely.
- Mesa: llvmpipe-dokumentaatio. <https://docs.mesa3d.org/>

Tämän tutoriaalin teksti ja esimerkit on kirjoitettu itse. Lähteistä
ei ole kopioitu tekstiä eikä koodia.

## Lisenssi

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0).
