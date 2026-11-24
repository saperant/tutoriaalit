# SPIR-V, kuvaajat ja push-vakiot

## Varjostimien kääntäminen etukäteen

Vulkan ei lue GLSL:ää vaan **SPIR-V**:tä, binääristä välikieltä.
Varjostimet käännetään rakennusvaiheessa samalla tavalla kuin muukin
koodi. Tämän tutoriaalin Makefile tekee sen glslc-kääntäjällä:

```{.makefile tiedosto="esimerkit/Makefile" osa="spirv"}
```

Etukäteen kääntämisellä on kolme etua: virheet löytyvät
rakennuksessa eivätkä ajurissa käyttäjän koneella, ajurin ei tarvitse
jäsentää lähdekoodia, ja sama SPIR-V kelpaa kaikille valmistajille.
Ajuri kääntää SPIR-V:n edelleen laitteen konekielelle putkea
luotaessa (luku 8).

SPIR-V:n voi tuottaa myös HLSL:stä (DXC) tai Slangista, mikä
mahdollistaa saman varjostinkoodin käytön Direct3D:n ja Vulkanin
välillä. Työkaluja:

| Työkalu | Tehtävä |
|---------|---------|
| `glslc`, `glslangValidator` | GLSL → SPIR-V ja GLSL:n tarkistus |
| `spirv-dis`, `spirv-val` | SPIR-V tekstiksi ja tarkistus |
| `spirv-opt` | optimointi ja koon pienennys |
| `spirv-cross` | SPIR-V → GLSL, HLSL, MSL; heijastustieto |

## Resurssit varjostimelle

OpenGL:ssä resurssit sidotaan numeroituihin sidontapisteisiin
kontekstiin. Vulkanissa ne kootaan **kuvaajajoukkoihin**
(descriptor set). Kuvaaja kertoo varjostimelle, missä resurssi on:
uniform-puskuri, varastopuskuri, kuva tai näytteistin. Joukko vastaa
varjostimen `set`-numeroa ja kuvaaja `binding`-numeroa:

```{.glsl tiedosto="esimerkit/varjostimet/kuvaajat.vert"}
```

Pientä, piirtokohtaista dataa varten on **push-vakiot**: enintään
128 tavua (useimmilla laitteilla 256), jotka kirjoitetaan suoraan
komentopuskuriin ilman puskuria tai kuvaajaa. Ne ovat oikea paikka
esimerkiksi mallimatriisille tai materiaalin indeksille.

C++-rakenteiden on vastattava asettelua (luku 4): uniform-puskuri
std140, push-vakiot std430.

```{.cpp tiedosto="esimerkit/10-vk-kuvaajat.cpp" osa="rakenteet"}
```

### Asettelu, allas ja joukko

Kuvaajajoukon asettelu (`VkDescriptorSetLayout`) ja push-vakioiden
alue kootaan **putken asetteluksi** (`VkPipelineLayout`), joka on putken
osa:

```{.cpp tiedosto="esimerkit/10-vk-kuvaajat.cpp" osa="asettelu"}
```

Joukot varataan altaasta, ja niihin kirjoitetaan resurssien osoitteet:

```{.cpp tiedosto="esimerkit/10-vk-kuvaajat.cpp" osa="joukko"}
```

Piirrossa joukko sidotaan kerran ja push-vakiot vaihdetaan piirtojen
välissä. Kuvan renderöinti ja luku on koottu apufunktioon
`renderoi` (`yhteinen/vk.hpp`), joka tekee luvun 8 vaiheet:

```{.cpp tiedosto="esimerkit/10-vk-kuvaajat.cpp" osa="piirto"}
```

```{.tuloste tiedosto="esimerkit/10-vk-kuvaajat.odotettu"}
```

Värit ovat puolet täydestä, koska yhteinen kirkkaus 0,5 tuli
uniform-puskurista ja värit push-vakioista.

### Joukot päivitystiheyden mukaan

Tavallinen jako on neljä joukkoa: 0 ruudun data (kamera, valot),
1 vaiheen data, 2 materiaali ja 3 piirto. Joukko sidotaan uudelleen vain,
kun sen data vaihtuu, ja korkeamman numeron joukon vaihto ei mitätöi
alempia. Uudempi tapa on **bindless**: kaikki tekstuurit yhteen
isoon taulukkoon (descriptor indexing), ja varjostin valitsee
tekstuurin indeksillä, joka tulee push-vakioista tai puskurista.
Silloin piirtojen välillä ei vaihdeta kuvaajia lainkaan.

## Käytännössä

- **Käännä varjostimet rakennuksessa ja varoitukset virheiksi**
  (`glslc -Werror`). Ajonaikainen käännös on vain työkaluille ja
  kokeiluille.
- **Pidä varjostimet ja C++-rakenteet synkronissa** heijastuksella
  (SPIRV-Reflect, spirv-cross) tai generoimalla rakenteet; käsin
  ylläpidetyt asettelut ajautuvat eroon.
- **Push-vakiot pienelle piirtokohtaiselle datalle**, uniform-
  puskurit jaetulle datalle, varastopuskurit isoille taulukoille.
- **Kuvaajajoukot päivitystiheyden mukaan** tai bindless-malli. Molemmat
  vähentävät sidontoja, jotka ovat CPU-kuorman yleisin lähde.
- **Älä varaa joukkoja jokaisessa ruudussa** uudelleen altaasta ilman
  syytä; varaa kerran, kirjoita tarvittaessa, tai nollaa allas ruudun
  alussa (`vkResetDescriptorPool`).

## Itsearviointi

- Osaat kääntää GLSL:n SPIR-V:ksi rakennuksessa ja ladata sen
  varjostinmoduuliksi.
- Osaat luoda kuvaajajoukon asettelun, putken asettelun, altaan ja
  joukon sekä kirjoittaa joukkoon puskurin.
- Osaat käyttää push-vakioita ja tiedät niiden kokorajan.
- Osaat jakaa resurssit joukkoihin päivitystiheyden mukaan ja
  selittää bindless-mallin idean.
