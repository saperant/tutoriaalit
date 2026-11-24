# GPU-ohjelmointi: OpenGL ja Vulkan

Grafiikkaohjelmointi GPU:lla: arkkitehtuuri (SIMT, muisti, kiinteät
yksiköt), OpenGL 4.5 ja GLSL (puskurit, uniformit ja std140,
tekstuurit, kehyspuskurit, syvyys ja sekoitus), Vulkan (laite ja
muisti, putki ja komentopuskurit, synkronointi, SPIR-V ja kuvaajat),
varjokartat, viivästetty varjostus ja suorituskyvyn analyysi.
Valmis dokumentti:
[gpu-ohjelmointi.pdf](https://saperant.github.io/tutoriaalit/materiaalit/gpu-ohjelmointi.pdf),
pikaopas:
[gpu-ohjelmointi-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/gpu-ohjelmointi-pikaopas.pdf).

Esitiedot: taidot *Renderöinnin perusteet* ja *Rinnakkaisohjelmointi*.

## Esimerkit

`esimerkit/` sisältää 14 C++23-ohjelmaa (GCC 14), apuotsakkeet
(`yhteinen/`) ja Vulkanin varjostimet (`varjostimet/`). Ne ajetaan
ilman näytönohjainta Mesan ohjelmistorenderöijillä: OpenGL
llvmpipellä EGL:n kautta ilman ikkunaa ja Vulkan lavapipellä
validointikerroksen kanssa. Jokainen ohjelma tulostaa raportin
(pikselien värit, laskurit), jota verrataan tiedostoon
`<nimi>.odotettu`.

```text
cd esimerkit
make              # varjostimet, ohjelmat, ajot ja vertailu
make aja-08-vk-kolmio
make kuvat        # kuvitukset ../kuvat/*.png
```

Tarvittavat paketit (Ubuntu 24.04): `libegl-dev libopengl-dev
libgl1-mesa-dri libvulkan-dev mesa-vulkan-drivers
vulkan-validationlayers glslc`. Kehityskontissa
(`.devcontainer/gpu-ohjelmointi`) ne ovat valmiina.

## Rakentaminen

`make testaa` tarkistaa rakenteen ja ajaa esimerkit, `make pdf`
rakentaa PDF:t.

Lisenssi: CC BY-SA 4.0.
