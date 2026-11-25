# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Radianssi säteitä pitkin, koodaus vasta lopuksi.** Liukulukupuskuri,
   valotus, sävykuvaus ja sRGB tässä järjestyksessä.
2. **Paino on $f\cos\theta/p$**, ja $p$:n on vastattava poimintaa
   täsmälleen, samassa mitassa (avaruuskulma tai pinta-ala).
3. **Suora valo valon näytteellä**, epäsuora BRDF:n näytteellä, ja
   MIS yhdistämään ne kiiltävillä pinnoilla.
4. **Venäläinen ruletti kiinteän syvyyden sijaan.**
5. **Siirrä toisen säteen lähtöpistettä normaalin suuntaan**
   oikealle puolelle, ja suhteuta siirto koordinaattien suuruuteen.
6. **BVH ja SAH**, testattuna raakahakua vastaan.
7. **Toistettava satunnaisuus**: oma generaattori, oma virta
   pikselille, yksi satunnaisluku lausetta kohden.
8. **Testaa tunnetuilla arvoilla**: leikkaukset tapauksilla,
   integraalit analyyttisillä arvoilla, BRDF:t albedolla ja
   renderöijä valkoisella uunilla.
9. **Mittaa virhe RMSE:nä harhatonta vertailukuvaa vastaan**, ja
   laskureilla aikojen sijaan.
10. **Harha on valinta**: kohinan poisto ja leikkaus ovat hyviä
    työkaluja, kun niiden vaikutus tiedetään.

## Mitä tuotantorenderöijä tekee toisin

Tämän tutoriaalin renderöijä on kirjoitettu luettavaksi. Tuotannossa
sama algoritmi on tyypillisesti sata kertaa nopeampi ja paljon
laajempi:

- **Rinnakkaisuus.** Pikselit ovat riippumattomia, ja oma
  satunnaislukuvirta pikseliä kohden tekee rinnakkaistamisesta
  suoraviivaista: ruudut säikeille, SIMD-käskyt usealle säteelle
  kerralla (taito *Rinnakkaisohjelmointi*).
- **Näytönohjain.** Säteenseurantayksiköt käyvät BVH:n läpi ja
  testaavat kolmiot laitteistossa; ohjelmoija kirjoittaa varjostimet
  osumille ja ohituksille (Vulkan Ray Tracing, DirectX Raytracing,
  OptiX). Taito *GPU-ohjelmointi: OpenGL ja Vulkan* käsittelee rajapinnat.
- **Liukuluvut.** Yksinkertainen tarkkuus (`float`) puolittaa
  muistin ja kaksinkertaistaa SIMD-leveyden, mutta tekee
  itseleikkauksesta vakavamman ongelman.
- **Kaksitasoinen BVH**, instanssit ja liikesumennus.
- **Spektrinen renderöinti**: aallonpituudet näytteinä RGB:n sijaan,
  mikä tekee dispersiosta ja tarkoista väreistä mahdollisia.
- **Kaksisuuntaiset menetelmät**: polut sekä kamerasta että valosta
  (bidirectional path tracing, Metropolis, fotonikartat), jotka
  löytävät kaustiikat ja vaikeat valopolut.
- **Osallistuvat aineet**: savu, sumu ja iho, joissa valo siroaa
  aineen sisällä.
- **Ympäristövalaistus kuvasta**: taivas tai studio valaisee
  kohtauksen suuren dynamiikan panoraamakuvana, jonka kirkkaita
  kohtia näytteistetään tärkeyden mukaan.
- **Matalan diskrepanssin jonot** kaikille ulottuvuuksille ja
  neuroverkkopohjainen kohinan poisto.

## Jatkotaidot

- *GPU-ohjelmointi: OpenGL ja Vulkan*: rasterointiputki ja säteenseurannan
  laajennukset näytönohjaimella.
- *Rinnakkaisohjelmointi*: säikeet, tehtävät ja SIMD, joilla
  renderöijä saadaan käyttämään koko prosessoria.
- *Suorituskyvyn analyysi ja optimointi*: välimuistit, haarautumat
  ja vektorointi BVH:n läpikäynnissä.
- *Peliohjelmointi*: renderöinnin paikka pelisilmukassa.

Hyviä harjoituksia tämän toteutuksen jatkoksi ovat MIS polunseurannan
suoraan valaistukseen, Sobolin jono, syväterävyys linssillä,
tekstuurit barysentrisillä koordinaateilla, instanssit muunnoksilla,
monisirontakorjaus mikrofasettimalliin ja rinnakkaistus säikeillä.
Jokaiselle löytyy testi tämän tutoriaalin tekniikoilla: vertailu
analyyttiseen arvoon, valkoinen uuni tai harhaton vertailukuva.

## Lähteet ja jatkolukeminen

Kirjat:

- Matt Pharr, Wenzel Jakob, Greg Humphreys: *Physically Based
  Rendering: From Theory to Implementation*, 4. painos. MIT Press
  2023. Verkossa vapaasti: <https://pbr-book.org/>
- Peter Shirley ym.: *Ray Tracing in One Weekend* -kirjasarja.
  <https://raytracing.github.io/>
- Eric Haines, Tomas Akenine-Möller (toim.): *Ray Tracing Gems*.
  Apress 2019. Verkossa vapaasti.
- Adam Marrs, Peter Shirley, Ingo Wald (toim.): *Ray Tracing Gems
  II*. Apress 2021. Verkossa vapaasti.
- Philip Dutré, Kavita Bala, Philippe Bekaert: *Advanced Global
  Illumination*, 2. painos. A K Peters 2006.
- Eric Veach: *Robust Monte Carlo Methods for Light Transport
  Simulation*. Väitöskirja, Stanford University 1997.

Alkuperäiset artikkelit:

- Turner Whitted: An Improved Illumination Model for Shaded Display.
  *Communications of the ACM* 23(6), 1980.
- Robert L. Cook, Thomas Porter, Loren Carpenter: Distributed Ray
  Tracing. *SIGGRAPH* 1984.
- Cindy M. Goral ym.: Modeling the Interaction of Light Between
  Diffuse Surfaces. *SIGGRAPH* 1984 (Cornellin laatikko).
- James T. Kajiya: The Rendering Equation. *SIGGRAPH* 1986.
- Tomas Möller, Ben Trumbore: Fast, Minimum Storage Ray-Triangle
  Intersection. *Journal of Graphics Tools* 2(1), 1997.
- Eric Veach, Leonidas Guibas: Optimally Combining Sampling
  Techniques for Monte Carlo Rendering. *SIGGRAPH* 1995.
- Robert L. Cook, Kenneth E. Torrance: A Reflectance Model for
  Computer Graphics. *ACM Transactions on Graphics* 1(1), 1982.
- Bruce Walter ym.: Microfacet Models for Refraction through Rough
  Surfaces. *Eurographics Symposium on Rendering* 2007 (GGX).
- Brent Burley: Physically-Based Shading at Disney. *SIGGRAPH* 2012
  -kurssimateriaali.
- Christophe Schlick: An Inexpensive BRDF Model for Physically-based
  Rendering. *Computer Graphics Forum* 13(3), 1994.
- Ingo Wald: On fast Construction of SAH-based Bounding Volume
  Hierarchies. *IEEE Symposium on Interactive Ray Tracing* 2007.
- Melissa E. O'Neill: *PCG: A Family of Simple Fast Space-Efficient
  Statistically Good Algorithms for Random Number Generation*.
  Tekninen raportti, Harvey Mudd College 2014.
- Tom Duff ym.: Building an Orthonormal Basis, Revisited. *Journal of
  Computer Graphics Techniques* 6(1), 2017.
- Christopher Kulla, Alejandro Conty: Revisiting Physically Based
  Shading at Imageworks. *SIGGRAPH* 2017 -kurssimateriaali.
- Christoph Schied ym.: Spatiotemporal Variance-Guided Filtering.
  *High Performance Graphics* 2017.
- Krzysztof Narkowicz: ACES Filmic Tone Mapping Curve. Blogi 2016.

Ray Tracing Gemsin luvut, joihin viitattiin: Eric Haines ym.,
*Precision Improvements for Ray/Sphere Intersection* (luku 7), ja
Carsten Wächter, Nikolaus Binder, *A Fast and Robust Method for
Avoiding Self-Intersection* (luku 6).
