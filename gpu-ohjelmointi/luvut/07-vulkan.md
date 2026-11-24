# Vulkan: instanssi, laite ja muisti

OpenGL-ajuri tekee sovelluksen puolesta paljon: se seuraa tilaa,
päättää, missä muistissa resurssit ovat, lisää tarvittavat
synkronoinnit ja kääntää varjostimet. Työ on näkymätöntä mutta ei
ilmaista. Ajuri ei tiedä sovelluksen aikeita, joten sen on oltava
varovainen, ja varovaisuus näkyy CPU-kuormana ja ennustamattomina
pysähdyksinä.

Vulkan siirtää nämä päätökset sovellukselle. Kaikki on eksplisiittistä:

- **muisti** varataan itse ja liitetään resursseihin,
- **komennot** tallennetaan komentopuskureihin ja lähetetään jonoon,
- **synkronointi** on sovelluksen vastuulla (luku 9),
- **tila** kootaan etukäteen muuttumattomiin putkiolioihin (luku 8).

Hinta on koodin määrä: tämän tutoriaalin kolmio on Vulkanilla noin
kolme kertaa pidempi kuin OpenGL:llä. Siksi oikeissa projekteissa
toistuva koodi kootaan apukirjastoon, kuten tässä `yhteinen/vk.hpp`.

## Oliot

| Olio | Tehtävä |
|------|---------|
| `VkInstance` | yhteys Vulkan-lataajaan; kerrokset ja laajennukset |
| `VkPhysicalDevice` | yksi GPU (tai lavapipe); ominaisuuksien ja rajojen kysely |
| `VkDevice` | looginen laite: sovelluksen yhteys GPU:hun |
| `VkQueue` | jono, johon komentopuskurit lähetetään |
| `VkCommandPool`, `VkCommandBuffer` | komentojen tallennus |
| `VkBuffer`, `VkImage` + `VkDeviceMemory` | resurssi ja sen muisti erikseen |
| `VkPipeline` | koko putken tila: varjostimet, rasterointi, sekoitus |
| `VkFence`, `VkSemaphore`, esteet | synkronointi |

Rakenteet välitetään `…CreateInfo`-tietueina, joiden ensimmäinen kenttä
`sType` kertoo tyypin ja `pNext` mahdollistaa laajennusrakenteiden
ketjuttamisen. Esimerkeissä rakenteet alustetaan C++20:n nimetyillä
kentillä, ja puuttuvat kentät nollautuvat.

## Instanssi ja validointikerros

```{.cpp tiedosto="esimerkit/yhteinen/vk.hpp" osa="instanssi"}
```

**Validointikerros** (`VK_LAYER_KHRONOS_validation`) on Vulkan-
kehityksen tärkein työkalu. Vulkan-ajuri ei tarkista kutsuja, joten
virheellinen kutsu voi toimia yhdellä laitteella ja kaataa toisen.
Kerros tarkistaa jokaisen kutsun määrittelyä vasten ja ilmoittaa
rikkeet viestinä, jossa on yksilöivä tunniste (VUID) ja viittaus
määrittelyn kohtaan. Viestit kerätään takaisinkutsulla:

```{.cpp tiedosto="esimerkit/yhteinen/vk.hpp" osa="viestit"}
```

Kerros otetaan käyttöön vain kehityksessä; julkaistussa ohjelmassa se
hidastaisi kaikkia kutsuja.

Virhekoodit tarkistetaan jokaisesta kutsusta, joka palauttaa
`VkResult`-arvon:

```{.cpp tiedosto="esimerkit/yhteinen/vk.hpp" osa="tarkista"}
```

## Laite ja jonot

Fyysinen laite valitaan ominaisuuksien perusteella (tässä ainoa),
ja siltä haetaan jonoperhe, joka tukee grafiikkaa. Looginen laite
luodaan pyytäen ne ominaisuudet, joita sovellus käyttää: tässä
Vulkan 1.3:n dynaaminen renderöinti, synchronization2 ja 1.2:n
aikajanasemaforit.

```{.cpp tiedosto="esimerkit/yhteinen/vk.hpp" osa="laite"}
```

```{.cpp tiedosto="esimerkit/07-vk-laite.cpp" osa="paa"}
```

```{.tuloste tiedosto="esimerkit/07-vk-laite.odotettu"}
```

Lavapipellä on yksi jonoperhe ja yksi muistityyppi, koska CPU:lla
kaikki muisti on samaa. Erillisellä näytönohjaimella tilanne on
toinen: tyypillisesti kaksi kekoa (VRAM ja järjestelmämuisti) ja
useita muistityyppejä sekä erilliset jonoperheet grafiikalle,
asynkroniselle laskennalle ja siirroille (DMA-moottori).

## Muisti

Vulkanissa resurssi ja sen muisti ovat eri olioita. Resurssi kertoo
vaatimuksensa (koko, tasaus, sallitut muistityypit), ja sovellus valitsee
muistityypin tarpeen mukaan:

```{.cpp tiedosto="esimerkit/yhteinen/vk.hpp" osa="muistityyppi"}
```

| Ominaisuus | Merkitys | Käyttö |
|------------|----------|--------|
| `DEVICE_LOCAL` | GPU:n oma muisti (VRAM) | tekstuurit, verteksipuskurit, piirtokohteet |
| `HOST_VISIBLE` | CPU voi kuvata muistin osoiteavaruuteensa | siirtopuskurit, usein päivittyvä data |
| `HOST_COHERENT` | CPU:n kirjoitukset näkyvät ilman erillistä huuhtelua | yksinkertaisuus |
| `HOST_CACHED` | CPU:n luku on välimuistissa | GPU:n tulosten luku CPU:lle |

Puskuri, jonka muisti on CPU:lle näkyvää ja pysyvästi kuvattu:

```{.cpp tiedosto="esimerkit/yhteinen/vk.hpp" osa="puskuri"}
```

Erillisellä näytönohjaimella iso staattinen data (meshit, tekstuurit)
ladataan **siirtopuskurin** kautta: data kopioidaan CPU:lle näkyvään
puskuriin, ja siirtokomento kopioi sen `DEVICE_LOCAL`-muistiin.
Nykyisissä laitteissa on usein myös pieni alue (Resizable BAR), joka
on sekä `DEVICE_LOCAL` että `HOST_VISIBLE`; siihen CPU voi kirjoittaa
suoraan.

Vulkan-toteutus saa rajoittaa muistivarausten määrän (usein 4 096).
Jokaiselle resurssille ei siis tehdä omaa varausta, vaan isosta
varauksesta jaetaan osia. Tähän käytetään lähes aina valmista
kirjastoa, **Vulkan Memory Allocatoria** (VMA). Tämän tutoriaalin
esimerkit varaavat resurssikohtaisesti, koska resursseja on vähän.

## Käytännössä

- **Validointikerros aina päälle kehityksessä**, myös
  synkronoinnin tarkistus (luku 9). Koodi, joka "toimii" ilman
  validointivirheitä vain yhdellä laitteella, ei toimi.
- **Pyydä vain tarvitsemasi ominaisuudet ja laajennukset**, ja
  tarkista niiden tuki ennen pyyntöä. Ominaisuuden käyttö ilman
  pyyntöä on määrittelemätöntä, vaikka se toimisi.
- **Käytä VMA:ta**. Muistityypin valinta, alivaraus ja tasaus ovat
  rutiinia, jossa virheet ovat vaikeita löytää.
- **Tuhoa oliot käänteisessä järjestyksessä** (RAII-kääreet kuten
  tässä tai vulkan.hpp:n `vk::raii`). Validointikerros ilmoittaa
  vuotaneista olioista instanssia tuhottaessa.
- **Vulkan kannattaa vasta, kun OpenGL:n hinta näkyy**: paljon
  piirtokutsuja, monisäikeinen komentojen tallennus, asynkroninen
  laskenta tai tarkka muistinhallinta. Pieneen visualisointiin OpenGL
  tai WebGPU on usein parempi valinta.

## Itsearviointi

- Osaat luoda instanssin validointikerroksineen ja kerätä sen
  ilmoitukset.
- Osaat valita fyysisen laitteen ja jonoperheen ja luoda loogisen
  laitteen tarvittavine ominaisuuksineen.
- Osaat varata muistin resurssille sen vaatimusten ja halutun
  muistityypin perusteella.
- Osaat selittää, milloin data kulkee siirtopuskurin kautta ja miksi
  muistia ei varata resurssikohtaisesti oikeissa sovelluksissa.
