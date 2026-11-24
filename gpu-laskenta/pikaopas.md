---
title: GPU-laskenta
subtitle: Pikaopas · laskentavarjostimet, aliryhmät, primitiivit, muisti ja synkronointi
---

# Laskentavarjostin

```{.glsl tiedosto="esimerkit/varjostimet/saxpy.comp" osa="saxpy"}
```

| Muuttuja | Merkitys |
|----------|----------|
| `gl_GlobalInvocationID` | paikka koko ajossa |
| `gl_LocalInvocationID`, `gl_LocalInvocationIndex` | paikka työryhmässä |
| `gl_WorkGroupID`, `gl_NumWorkGroups` | työryhmä ja niiden määrä |
| `gl_SubgroupSize`, `gl_SubgroupID`, `gl_SubgroupInvocationID` | aliryhmä |

- Puskurit std430, `readonly` ja `writeonly`; push-vakiot vähintään
  128 t; erikoistusvakiot `constant_id`, `local_size_x_id`
  (vaatii `maintenance4`).
- Rajat: `maxComputeWorkGroupInvocations` (väh. 128),
  `maxComputeWorkGroupCount` (väh. 65 535), `maxComputeSharedMemorySize`
  (väh. 16 KiB).

# Isäntä

```{.cpp tiedosto="esimerkit/yhteinen/laskenta.hpp" osa="ryhmia"}
```

- **Putki:** SPIR-V-moduuli ja `VkComputePipelineCreateInfo` (yksi
  vaihe); asettelu = kuvaajajoukkojen asettelut + push-vakioiden alue.
- **Ajo:** `vkCmdBindPipeline`, `vkCmdBindDescriptorSets`,
  `vkCmdPushConstants`, `vkCmdDispatch(ryhmia(n, 256), 1, 1)`.
- **Ajojen väliin** `vkCmdPipelineBarrier2`: `COMPUTE_SHADER` +
  `SHADER_STORAGE_WRITE` → `COMPUTE_SHADER` + `SHADER_STORAGE_READ`.
- **Tulos CPU:lle:** aita, sitten luku kuvatusta muistista
  (ei-koherentti: `vkInvalidateMappedMemoryRanges`).

```text
glslc --target-env=vulkan1.3 -Werror -O x.comp -o x.spv
spirv-val --target-env vulkan1.3 x.spv
VK_DRIVER_FILES=/usr/share/vulkan/icd.d/lvp_icd.json ./ohjelma
LP_NATIVE_VECTOR_WIDTH=256      # lavapipe: aliryhmä 8 kaistaa
vulkaninfo | grep -i subgroup
```

# Aliryhmät

| Laite | Leveys |
|-------|--------|
| NVIDIA, Apple | 32 |
| AMD | 32 tai 64 |
| Intel | 8, 16, 32 |
| lavapipe | vektorileveys / 32 |

| Operaatio | Tulos |
|-----------|-------|
| `subgroupAny`, `subgroupAll` | ehto koko aliryhmälle |
| `subgroupAdd`, `subgroupMax` | reduktio |
| `subgroupInclusiveAdd`, `subgroupExclusiveAdd` | skannaus |
| `subgroupBallot`, `subgroupBallotExclusiveBitCount` | maski, sija |
| `subgroupShuffle`, `subgroupShuffleXor` | toisen kaistan arvo |
| `subgroupElect` | yksi kaista tekee |

```{.glsl tiedosto="esimerkit/varjostimet/reduktio_aliryhma.comp" osa="aliryhma"}
```

# Primitiivit

| Primitiivi | Rakenne | Ajoja | Huomio |
|------------|---------|-------|--------|
| reduktio | puu tai aliryhmä + uusi ajo | $\log_{512} n$ | liukuluvuissa järjestys vaikuttaa |
| skannaus (Blelloch) | ylös, alas, lisäys | $2 \log_{512} n - 1$ | $O(n)$ työtä |
| skannaus (Hillis–Steele) | $\log n$ kierrosta | 1 lohkolle | $O(n \log n)$ työtä |
| tiivistys | liput, skannaus, hajautus | 2 + skannaus | vakaa |
| histogrammi | jaettu muisti + globaali | 1 | vino data kilpailee |
| bitoninen lajittelu | $(k, j)$-askeleet | $\log n (\log n + 1) / 2$ | $n$ kahden potenssi |
| kantalukulajittelu | laskenta, skannaus, hajautus | 5 kierrosta kohden | vakaa, $O(n)$ kierrosta kohden |

# Muisti

- Aalto lukee 128 t:n segmenttejä: naapurikaistat naapuriosoitteisiin.
- Jaettu muisti 32 pankkia; sarakehaku `t[lx][c]` = 32-kertainen
  konflikti, täyte `[32][33]` poistaa sen.
- Laatoitus nostaa intensiteettiä: matriisitulo 16 × 16 laatoilla
  0,25 → 4 laskua/tavu.
- Roofline: $\min(P, B \cdot I)$; GPU:n harjanne 10–100 laskua/tavu.

# Synkronointi

| Tilanne | Väline |
|---------|--------|
| jaettu muisti työryhmässä | `barrier()` tasaisessa ohjausvuossa |
| kirjoitus → luku ajojen välillä (RAW) | muistieste `SHADER_WRITE` → `SHADER_READ` |
| luku → kirjoitus (WAR) | suoritusriippuvuus riittää |
| GPU → CPU | aita, sitten luku |
| ajon koko GPU:lta | `vkCmdDispatchIndirect` |

# Mittaus

- `vkCmdResetQueryPool`, `vkCmdWriteTimestamp2` ennen ja jälkeen,
  `vkGetQueryPoolResults(... WAIT_BIT)`; lämmittely, toistot, mediaani.
- Leima × `timestampPeriod` = ns; `timestampValidBits` > 0; nollaa
  kysely ennen jokaista kirjoitusta.
- PCIe 4.0 x16 ≈ 25 Gt/s: pidä data laitteella, siirrä isoina paloina.

# Sudenkuopat

| Virhe | Oire |
|-------|------|
| ryhmät `n / koko` | lopun alkiot laskematta |
| ei reunatarkistusta | puskurin yli, laitteen menetys |
| `barrier()` haarassa | jumi tai satunnainen tulos |
| este puuttuu ajojen välistä | vanha data; `SYNC-HAZARD-*` |
| kiinteä aliryhmän leveys | väärä tulos toisella laitteella |
| atominen float-summa | tulos vaihtelee ajosta toiseen |
| ryhmiä yli 65 535 | validointivirhe, kaatuminen |
