# Johdanto {.runko-johdanto}

Näytönohjain (GPU) on tuhansien yksinkertaisten laskentayksiköiden
rinnakkaiskone, joka on suunniteltu tekemään samaa työtä valtavalle
määrälle dataa: miljoonalle pikselille, sadoilletuhansille
verteksille tai neuroverkon matriiseille. GPU-ohjelmointi tarkoittaa
kahta asiaa: *varjostimia* (shader), jotka ajetaan GPU:lla jokaiselle
verteksille tai pikselille, ja CPU:lla ajettavaa *isäntäkoodia*, joka
varaa muistin, lähettää datan ja komennot ja odottaa tuloksia.

Tämä tutoriaali opettaa molemmat kahdella rajapinnalla. **OpenGL**
on vanha ja korkean tason rajapinta, jossa ajuri hoitaa muistin,
synkronoinnin ja tilan. Se on hyvä tapa oppia grafiikkaputki ja GLSL.
**Vulkan** on matalan tason rajapinta, jossa sovellus tekee sen,
minkä OpenGL-ajuri teki sen puolesta. Työtä on enemmän, mutta
hinnat ja riippuvuudet näkyvät, ja ne ovat samat myös
Direct3D 12:ssa, Metalissa ja WebGPU:ssa.

Esitietoina ovat taidot *Renderöinnin perusteet* (koordinaatistot,
muunnosmatriisit, rasterointi ja valaistusmallit) ja
*Rinnakkaisohjelmointi*. Tarvittava renderöinnin teoria kerrataan
lyhyesti siellä, missä sitä käytetään. GPU:lla tehtävä
yleiskäyttöinen laskenta (laskentavarjostimet, reduktiot,
lajittelu) on taidon *GPU-laskenta* asia; tämä tutoriaali keskittyy
grafiikkaan.

## Rajapinnat

| Rajapinta | Taso | Alustat | Huomio |
|-----------|------|---------|--------|
| OpenGL 4.6 | korkea, ajuri hoitaa tilan | Windows, Linux | ei enää kehitetä; hyvä oppimiseen |
| OpenGL ES 3.2 / WebGL 2 | korkea | mobiili, selain | OpenGL:n osajoukko |
| Vulkan 1.3–1.4 | matala, eksplisiittinen | Windows, Linux, Android | Khronos-ryhmän nykyinen rajapinta |
| Direct3D 12 | matala | Windows, Xbox | rakenteeltaan lähellä Vulkania |
| Metal | keskitaso | Apple | MoltenVK kääntää Vulkanin Metaliksi |
| WebGPU | keskitaso | selain, natiivi (wgpu, Dawn) | Vulkanin, D3D12:n ja Metalin yhteinen nimittäjä |

Varjostinkielet: OpenGL ja Vulkan käyttävät **GLSL**:ää. Vulkan ei
kuitenkaan lue lähdekoodia vaan **SPIR-V**-välikieltä, johon GLSL
(tai HLSL tai Slang) käännetään etukäteen. Direct3D käyttää HLSL:ää,
Metal MSL:ää ja WebGPU WGSL:ää.

## Testaus ilman näytönohjainta

Tutoriaalin esimerkit on testattu ilman näytönohjainta ja näyttöä.
Mesa-ajurikirjastossa on kaksi ohjelmistototeutusta, jotka ajavat
varjostimet CPU:lla LLVM:n kääntäminä:

- **llvmpipe** toteuttaa OpenGL 4.5:n. Konteksti luodaan EGL:llä ilman
  ikkunaa (EGL_MESA_platform_surfaceless), ja piirto tehdään omaan
  kehyspuskuriin.
- **lavapipe** toteuttaa Vulkan 1.4:n. Ikkunaa ja swapchainia ei
  tarvita, koska piirretään kuvaan, joka kopioidaan CPU:lle.

Jokainen esimerkki tulostaa raportin: valittujen pikselien värit,
peitettyjen pikselien määrän tai laskureita. Tulostetta verrataan
odotettuun tulosteeseen, kuten muissakin tutoriaaleissa. Vulkan-
esimerkeissä on lisäksi päällä Khronosin **validointikerros**, joka
tarkistaa jokaisen kutsun määrittelyä vasten. Esimerkin on päätyttävä
ilman yhtään validointi-ilmoitusta.

Ohjelmistorenderöijä on hidas mutta deterministinen ja tarkka. Sama
koodi toimii oikealla näytönohjaimella. Pikseliarvot voivat
kuitenkin erota yhden tai kaksi yksikköä, koska laitteet pyöristävät
ja interpoloivat hieman eri tavoin.

## Työkalut

```text
apt install libegl-dev libopengl-dev libgl1-mesa-dri  # OpenGL + llvmpipe
apt install libvulkan-dev mesa-vulkan-drivers         # Vulkan + lavapipe
apt install vulkan-validationlayers vulkan-tools      # validointi, vulkaninfo
apt install glslc glslang-tools spirv-tools           # GLSL → SPIR-V
```

Kehityskontissa (`.devcontainer/gpu-ohjelmointi`) kaikki on valmiina.
Esimerkit käännetään ja testataan hakemistossa `esimerkit/`:

```text
make            # kääntää, ajaa kaikki ja vertaa tulosteet
make aja-03-kolmio
make kuvat      # ajojen kuvat PNG:ksi (../kuvat)
```

Oikean laitteen debuggaukseen käytetään **RenderDocia**, joka
tallentaa yhden ruudun kaikki kutsut, resurssit ja välitulokset.
Suorituskyvyn analyysiin on valmistajien omat työkalut (Nsight,
Radeon GPU Profiler).

## Ensimmäinen ohjelma

Ohjelma luo OpenGL-kontekstin ilman ikkunaa, tyhjentää 64×48-
kehyspuskurin sinertävällä värillä ja lukee tuloksen CPU:lle.
Konteksti, varjostinohjelmat ja kehyspuskuri on koottu apuluokkiin
tiedostossa `yhteinen/gl.hpp`; ne käydään läpi luvussa 3.

```{.cpp tiedosto="esimerkit/01-konteksti.cpp" osa="paa"}
```

```{.tuloste tiedosto="esimerkit/01-konteksti.odotettu"}
```

Väri annetaan liukulukuina väliltä 0–1, ja RGBA8-kehyspuskuri
tallentaa sen 8-bittisinä kokonaislukuina: 0,2 · 255 = 51.

## Tutoriaalin rakenne

Luku 2 kuvaa GPU:n arkkitehtuurin ja sen, miksi varjostinkoodi
käyttäytyy toisin kuin CPU-koodi. Luvut 3–6 opettavat grafiikkaputken
OpenGL:llä: puskurit, varjostimet, uniformit, tekstuurit, syvyys ja
sekoitus. Luvut 7–10 tekevät saman Vulkanilla ja lisäävät sen, minkä
OpenGL piilottaa: muistin, komentopuskurit, synkronoinnin ja
resurssien sidonnan. Luku 11 näyttää kaksi monivaiheista tekniikkaa
(varjokartat ja viivästetyn varjostuksen), ja luku 12 suorituskyvyn
mittaamisen ja tyypilliset pullonkaulat.
