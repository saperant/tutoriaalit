# Kuvaajat ja push-vakiot

Luvun 8 kolmio ei tarvinnut varjostimeen muuta dataa kuin kärjet.
Tavallinen varjostin lukee lisäksi puskureita ja tekstuureja: kameran
matriisin, valot ja materiaalin. Tässä luvussa kerrotaan, miten
Vulkanissa resurssit annetaan varjostimelle ja miten pieni
piirtokohtainen data kulkee ilman puskuria.

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

```{.dot otsikko="Kuvaajien oliot. Asettelu kuvaa joukon muodon, allas antaa muistin, ja joukkoon kirjoitetaan viittaukset resursseihin. Putki tuntee vain asettelun, joten saman putken kanssa voi käyttää eri joukkoja."}
digraph {
  rankdir=LR; nodesep=0.22; ranksep=0.4;
  node [shape=box, style="rounded,filled", fillcolor="#EEF0F2"];
  dsl [label="VkDescriptorSetLayout\n(sidonta 0: uniform-puskuri)"];
  pl [label="VkPipelineLayout\n(joukkojen asettelut +\npush-vakioiden alue)"];
  pipe [label="VkPipeline"];
  pool [label="VkDescriptorPool"];
  set [label="VkDescriptorSet", fillcolor="#C9CEEE"];
  ubo [label="VkBuffer\n(uniform-data)", fillcolor="#F4E6DA"];
  sh [label="varjostin:\nset = 0, binding = 0", shape=ellipse];
  dsl -> pl -> pipe;
  dsl -> set [label="muoto"];
  pool -> set [label="varataan"];
  set -> ubo [label="viittaa", style=dashed];
  set -> sh [label="sidotaan\npiirrossa", style=dashed];
}
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

- Osaat pitää C++-rakenteet ja varjostimen lohkot samassa asettelussa
  (std140 uniform-puskurille, std430 push-vakioille).
- Osaat luoda kuvaajajoukon asettelun, putken asettelun, altaan ja
  joukon sekä kirjoittaa joukkoon puskurin.
- Osaat käyttää push-vakioita ja tiedät niiden kokorajan.
- Osaat jakaa resurssit joukkoihin päivitystiheyden mukaan ja
  selittää bindless-mallin idean.
