---
title: "GPU-ohjelmointi: OpenGL ja Vulkan"
subtitle: Pikaopas · grafiikkaputki, varjostimet, Vulkanin oliot ja synkronointi
---

# Grafiikkaputki

| Vaihe | Ohjelmoitava? | Huomio |
|-------|---------------|--------|
| syötteen kokoaminen | ei | verteksi- ja indeksipuskurit |
| verteksivarjostin | kyllä | tulos `gl_Position` leikkausavaruudessa |
| leikkaus, jako w:llä | ei | NDC −1…1; Vulkanissa y alaspäin |
| rasterointi | ei | pikselin keskipiste kolmion sisällä |
| aikainen syvyystesti | ei | estyy: `discard`, `gl_FragDepth` |
| fragmenttivarjostin | kyllä | 2×2-ryhminä (derivaatat, mip) |
| syvyys, sapluuna, sekoitus | ei | ROP; sekoitus lukee kohteen |

# OpenGL 4.5 (DSA)

- **Puskuri:** `glCreateBuffers`, `glNamedBufferStorage`.
- **Verteksimuoto:** `glCreateVertexArrays`,
  `glVertexArrayVertexBuffer`, `glVertexArrayAttribFormat`,
  `glVertexArrayAttribBinding`.
- **Indeksit:** `glVertexArrayElementBuffer`, `glDrawElements`;
  Vulkanissa `vkCmdBindIndexBuffer`, `vkCmdDrawIndexed`.
- **Ohjelma:** `glCreateShader`, `glCompileShader`, `glLinkProgram`;
  lue aina lokit.
- **Uniformit:** `glProgramUniform*`; UBO:
  `glBindBufferBase(GL_UNIFORM_BUFFER, n, puskuri)`.
- **Tekstuuri:** `glCreateTextures`, `glTextureStorage2D`,
  `glGenerateTextureMipmap`, `glBindTextureUnit`.
- **Kehyspuskuri:** `glCreateFramebuffers`,
  `glNamedFramebufferTexture`, `glCheckNamedFramebufferStatus`.
- **Virheet:** debug-konteksti ja `glDebugMessageCallback`.

```{.cpp tiedosto="esimerkit/yhteinen/gl.hpp" osa="ohjelma"}
```

# std140 (UBO) ja std430 (SSBO, push-vakiot)

| Tyyppi | std140 | std430 |
|--------|--------|--------|
| `float`, `int` | 4 / tasaus 4 | sama |
| `vec2` | 8 / 8 | sama |
| `vec3` | 12 / **16** (float mahtuu perään) | sama |
| `vec4` | 16 / 16 | sama |
| `float[n]` | **16 · n** | 4 · n |
| `mat4` | 4 saraketta à 16 | sama |

```{.cpp tiedosto="esimerkit/04-uniformit.cpp" osa="cpp"}
```

# Vulkanin oliot

instanssi (+ validointi) → fyysinen laite → looginen laite + jono →
komentoallas → komentopuskuri. Resurssi (`VkBuffer`, `VkImage`) +
muisti (`VkDeviceMemory`, VMA) + näkymä. Putki = varjostimet + kiinteä
tila + putken asettelu (kuvaajajoukkojen asettelut + push-vakiot).

| Muisti | Käyttö |
|--------|--------|
| `DEVICE_LOCAL` | tekstuurit, meshit, piirtokohteet |
| `HOST_VISIBLE \| COHERENT` | siirtopuskurit, ruudun data |
| `HOST_CACHED` | tulosten luku CPU:lle |

# Synkronointi

| Väline | Välillä |
|--------|---------|
| este (`vkCmdPipelineBarrier2`) | saman jonon komennot; asettelut |
| binäärinen semafori | jonolähetykset, swapchain |
| aikajanasemafori | GPU–GPU, GPU–CPU, ruutunumerot |
| aita | GPU → CPU |

Asettelun vaihto ja muistiriippuvuus tehdään yhdellä
`VkImageMemoryBarrier2`-esteellä. Tavalliset siirtymät:

| Vanha → uusi | src-vaihe / käyttö | dst-vaihe / käyttö |
|--------------|--------------------|--------------------|
| UNDEFINED → COLOR_ATTACHMENT | NONE / NONE | COLOR_ATTACHMENT_OUTPUT / WRITE |
| COLOR_ATTACHMENT → SHADER_READ_ONLY | COLOR_ATTACHMENT_OUTPUT / WRITE | FRAGMENT_SHADER / SHADER_SAMPLED_READ |
| COLOR_ATTACHMENT → TRANSFER_SRC | COLOR_ATTACHMENT_OUTPUT / WRITE | COPY / TRANSFER_READ |
| UNDEFINED → TRANSFER_DST (lataus) | NONE / NONE | COPY / TRANSFER_WRITE |

# Työkalut

| Komento | Tehtävä |
|---------|---------|
| `glslc -Werror -O x.vert -o x.vert.spv` | GLSL → SPIR-V |
| `glslangValidator x.frag` | GLSL:n tarkistus |
| `spirv-dis`, `spirv-val`, `spirv-cross` | SPIR-V tekstiksi, tarkistus, heijastus |
| `vulkaninfo --summary` | laitteet ja versiot |
| `VK_DRIVER_FILES=…/lvp_icd.json` | lavapipe käyttöön |
| `EGL_PLATFORM=surfaceless` | OpenGL ilman ikkunaa |
| RenderDoc, Nsight, RGP | ruudun analyysi, laskurit |

# Suorituskyky

- Pullonkaula ensin: resoluutio pienemmäksi → nopeutuuko?
- Edestä taakse, syvyyden esipiirto; ei turhaa `discard`ia.
- Instanssit ja epäsuora piirto; lajittelu putken ja materiaalin
  mukaan.
- Kaista: mip-tasot, pakatut muodot, pienet välimuodot,
  `loadOp`/`storeOp`.
- Ei synkronista lukua kesken ruudun; 2–3 limitettyä ruutua.
