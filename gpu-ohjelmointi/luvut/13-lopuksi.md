# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Validointi päälle kehityksessä**: OpenGL:n debug-viestit, Vulkanin
   validointikerros ja synkronoinnin validointi. Vulkan-ohjelma, joka
   toimii vain ilman ilmoituksia, toimii vahingossa.
2. **Varjostimet käännetään rakennuksessa** (SPIR-V) ja varoitukset
   ovat virheitä.
3. **C++-rakenne ja varjostimen lohko lukitaan toisiinsa**
   (`static_assert`, heijastus); vältä `vec3`:a puskureissa.
4. **Resurssit ja putket luodaan latauksessa**, ei ruudun aikana.
5. **Ajattele ryhmiä**: hajoava haarautuminen ja hajanaiset
   muistihaut maksavat koko ryhmälle.
6. **Läpinäkymättömät edestä taakse, läpinäkyvät takaa eteen.**
7. **Mip-tasot ja pakatut tekstuurit**; sRGB värikuville, lineaarinen
   datalle.
8. **Kaista on rajallinen**: laske muodot, ylipiirto ja koko ruudun
   vaiheet.
9. **Vähemmän piirtokutsuja**: instanssit, epäsuora piirto,
   lajittelu tilan mukaan.
10. **CPU ja GPU eivät odota toisiaan kesken ruudun**: limitetyt
    ruudut ja resurssi per ruutu.

## Jatkotaidot

- *GPU-laskenta*: laskentavarjostimet, jaettu muisti, reduktiot ja
  lajittelu sekä niiden käyttö grafiikassa (hiukkaset, valojen
  klusterointi, GPU-ohjattu renderöinti).
- *Säteenseuranta ja fysikaalinen valaistus*: fysikaalinen valon
  kulku ja polunseuranta.
  Laitteistokiihdytetty säteenseuranta (Vulkanin ray tracing
  -laajennukset) yhdistää sen rasterointiin.
- *Peliohjelmointi* ja *Reaaliaikaiset moninpelit*: renderöinnin
  paikka koko pelissä.
- *Suorituskyvyn analyysi ja optimointi* ja *C++:n suorituskyky*:
  CPU-puolen kustannukset, jotka rajoittavat piirtokutsuja.

## Lähteet ja jatkolukeminen

Määrittelyt ja viralliset aineistot:

- Khronos Group: *OpenGL 4.6 Core Profile Specification* ja *OpenGL
  Shading Language 4.60*. <https://registry.khronos.org/OpenGL/>
- Khronos Group: *Vulkan Specification* ja *Vulkan Guide*.
  <https://docs.vulkan.org/>
- Khronos Group: *SPIR-V Specification*.
  <https://registry.khronos.org/SPIR-V/>
- Khronos Group: *Synchronization Examples* (Vulkan-Docs wiki), esteiden
  oikeat vaiheet ja käytöt tyypillisiin tilanteisiin.
- Mesa: llvmpipe- ja lavapipe-dokumentaatio. <https://docs.mesa3d.org/>

Oppaat:

- Alexander Overvoorde ym.: *Vulkan Tutorial*. Lisenssi CC BY-SA 4.0.
  <https://vulkan-tutorial.com/>
- Victor Blanco: *Vulkan Guide* (vkguide.dev), nykyaikainen Vulkan
  dynaamisella renderöinnillä.
- Joey de Vries: *Learn OpenGL*. <https://learnopengl.com/>
- Sascha Willems: *Vulkan C++ examples* (MIT-lisenssi).
  <https://github.com/SaschaWillems/Vulkan>

Kirjat ja arkkitehtuuri:

- Tomas Akenine-Möller ym.: *Real-Time Rendering*, 4. painos. CRC
  Press 2018.
- Fabian Giesen: *A trip through the Graphics Pipeline* (blogisarja,
  2011): mitä laitteisto tekee jokaisessa vaiheessa.
- Emil Persson: *Depth in-depth* ja Nathan Reed: *Depth Precision
  Visualized*, syvyyden tarkkuus ja käänteinen syvyys.
- AMD GPUOpen ja NVIDIA Developer: arkkitehtuuri- ja
  optimointioppaat (RDNA, Ada) sekä Vulkan Memory Allocator.

Työkalut:

- RenderDoc <https://renderdoc.org/>, glslang, shaderc (glslc),
  SPIRV-Tools, SPIRV-Cross, Vulkan Memory Allocator.

Tämän tutoriaalin teksti ja esimerkit on kirjoitettu itse. Lähteistä
ei ole kopioitu tekstiä eikä koodia.

## Lisenssi

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0).
