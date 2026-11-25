# Vulkan: putki, komentopuskurit ja piirto

Luvun 3 kolmio piirretään nyt Vulkanilla. Kuva ja raportti ovat samat
kuin OpenGL:llä, mutta jokainen vaihe on näkyvissä. Ensimmäinen ero
tulee vastaan jo ennen putkea: varjostimet eivät ole enää
merkkijonoja ohjelman sisällä.

## Varjostimet SPIR-V:nä

Vulkan ei lue GLSL:ää vaan **SPIR-V**:tä, binääristä välikieltä.
Varjostimet käännetään rakennusvaiheessa samalla tavalla kuin muukin
koodi. Tämän tutoriaalin Makefile tekee sen glslc-kääntäjällä:

```{.makefile tiedosto="esimerkit/Makefile" osa="spirv"}
```

Etukäteen kääntämisellä on kolme etua: virheet löytyvät
rakennuksessa eivätkä ajurissa käyttäjän koneella, ajurin ei tarvitse
jäsentää lähdekoodia, ja sama SPIR-V kelpaa kaikille valmistajille.
Ajuri kääntää SPIR-V:n edelleen laitteen konekielelle, kun putki
luodaan.

SPIR-V:n voi tuottaa myös HLSL:stä (DXC) tai Slangista, mikä
mahdollistaa saman varjostinkoodin käytön Direct3D:n ja Vulkanin
välillä. Työkaluja:

| Työkalu | Tehtävä |
|---------|---------|
| `glslc`, `glslangValidator` | GLSL → SPIR-V ja GLSL:n tarkistus |
| `spirv-dis`, `spirv-val` | SPIR-V tekstiksi ja tarkistus |
| `spirv-opt` | optimointi ja koon pienennys |
| `spirv-cross` | SPIR-V → GLSL, HLSL, MSL; heijastustieto |

## Putki on muuttumaton

OpenGL:ssä putken tila (varjostimet, verteksien muoto, rasterointi,
sekoitus) kootaan piirtohetkellä kontekstin nykyisestä tilasta, ja
ajuri voi joutua kääntämään varjostimet uudelleen kesken ruudun, kun
jokin tila muuttuu. Vulkanissa koko tila kootaan etukäteen
**putkiolioon** (`VkPipeline`), joka käännetään kerran:

```{.cpp tiedosto="esimerkit/yhteinen/vk.hpp" osa="putki"}
```

Verteksien muoto on putken osa, ja se annetaan tässä erikseen:

```{.cpp tiedosto="esimerkit/08-vk-kolmio.cpp" osa="syote"}
```

Putkien määrä kasvaa nopeasti: jokainen varjostin-, muoto- ja
tilayhdistelmä on oma putkensa. Pelimoottorit luovat ne latausvaiheessa
ja tallentavat käännökset **putkivälimuistiin**
(`VkPipelineCache`), jotta seuraava käynnistys on nopeampi. Osa
tilasta voidaan merkitä *dynaamiseksi* (esim. näkymäalue ja leikkaus),
jolloin se asetetaan komennolla eikä vaadi uutta putkea.

Vulkanin leikkausavaruuden y-akseli osoittaa alaspäin, toisin kuin
OpenGL:ssä, joten verteksivarjostin kääntää y:n:

```{.glsl tiedosto="esimerkit/varjostimet/kolmio.vert"}
```

## Resurssit

```{.cpp tiedosto="esimerkit/08-vk-kolmio.cpp" osa="resurssit"}
```

Kuva luodaan `VkKuva`-apuluokalla. Kuvan *käyttötarkoitus* (usage)
kerrotaan luonnissa: piirtokohde ja kopioinnin lähde. Ajuri voi
valita tallennusmuodon (tiling) sen mukaan, ja käyttö muuhun
tarkoitukseen on virhe.

```{.cpp tiedosto="esimerkit/yhteinen/vk.hpp" osa="kuva"}
```

## Komentopuskurit

Komennot tallennetaan komentopuskuriin ja lähetetään jonoon. Tallennus
ei tee vielä mitään GPU:lla; se on halpaa ja onnistuu useasta säikeestä
yhtä aikaa omiin puskureihinsa. Tämä on Vulkanin suurin
suorituskykyetu OpenGL:ään nähden.

```{.cpp tiedosto="esimerkit/yhteinen/vk.hpp" osa="komennot"}
```

Esimerkki käyttää kertakäyttöisiä komentopuskureita ja odottaa aidalla
(fence) jokaisen lähetyksen valmistumista. Oikeassa sovelluksessa
CPU tallentaa seuraavaa ruutua sillä aikaa, kun GPU piirtää edellistä,
ja komentopuskurit kierrätetään (luku 9).

## Kuvan asettelu ja dynaaminen renderöinti

Kuvalla on aina **asettelu** (layout), joka kertoo, missä
käyttötarkoituksessa se on: piirtokohteena, varjostimen luettavana,
kopioinnin lähteenä. Laite voi tallentaa kuvan eri tavalla eri
käyttöä varten (esim. pakattuna), joten asettelu vaihdetaan esteellä
ennen käyttöä. Este kertoo samalla, mitkä aiemmat kirjoitukset on
saatava valmiiksi:

```{.cpp tiedosto="esimerkit/yhteinen/vk.hpp" osa="siirtyma"}
```

```{.dot otsikko="Esimerkin kohdekuvan asettelut. Jokainen nuoli on este komentopuskurissa."}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.45;
  node [shape=box, style="rounded,filled", fillcolor="#EEF0F2"];
  u [label="UNDEFINED\n(luotu, sisältö\nmäärittelemätön)"];
  c [label="COLOR_ATTACHMENT_\nOPTIMAL\n(piirtokohde)", fillcolor="#C9CEEE"];
  t [label="TRANSFER_SRC_\nOPTIMAL\n(kopioinnin lähde)", fillcolor="#F4E6DA"];
  u -> c [label="ennen piirtoa"];
  c -> t [label="ennen lukua\nCPU:lle"];
}
```

Piirto tapahtuu **dynaamisen renderöinnin** (Vulkan 1.3) sisällä.
Liitännät annetaan suoraan `vkCmdBeginRendering`-kutsulle. Vanhempi
tapa, render pass ja framebuffer -oliot, on edelleen tuettu, ja se on
hyödyllinen mobiililaitteilla, joissa monivaiheisen renderöinnin
välitulokset voivat pysyä piirin sisäisessä muistissa.

```{.cpp tiedosto="esimerkit/08-vk-kolmio.cpp" osa="komennot"}
```

`loadOp = CLEAR` ja `storeOp = STORE` kertovat, mitä liitännälle
tehdään renderöinnin alussa ja lopussa. Ruutupohjaisella GPU:lla
(luku 2) ne ovat suorituskyvyn kannalta tärkeitä: `DONT_CARE`
syvyyspuskurin tallennukselle säästää koko ruudun kirjoituksen
VRAMiin, jos syvyyttä ei tarvita myöhemmin.

```{.tuloste tiedosto="esimerkit/08-vk-kolmio.odotettu"}
```

Tulos on sama kuin OpenGL:llä (sama kuva kuin luvussa 3), ja
validointikerros ei löytänyt virheitä.

Indeksoitu piirto toimii kuten OpenGL:ssä: indeksipuskuri sidotaan
komennolla `vkCmdBindIndexBuffer`, ja piirtokomento on
`vkCmdDrawIndexed`.

## Ikkuna ja swapchain

Ikkunaan piirtävä sovellus pyytää ikkunajärjestelmältä pinnan
(`VkSurfaceKHR`) ja sen kuvat *swapchainina*. Jokaisessa ruudussa
sovellus pyytää seuraavan vapaan kuvan (`vkAcquireNextImageKHR`),
piirtää siihen semaforilla odottaen ja palauttaa sen esitettäväksi
(`vkQueuePresentKHR`). Rakenne on sama kuin tässä luvussa; vain
kohdekuva tulee swapchainista. Tämän tutoriaalin esimerkit ajetaan
ilman näyttöä, joten swapchain ohitetaan.

## Käytännössä

- **Käännä varjostimet rakennuksessa ja varoitukset virheiksi**
  (`glslc -Werror`). Ajonaikainen käännös on vain työkaluille ja
  kokeiluille.
- **Kokoa toistuvat rakenteet apukoodiksi heti**, mutta näe ensin
  koko ketju kerran. Vulkan-koodin virheet ovat lähes aina
  unohtuneita kenttiä tai väärää järjestystä.
- **Putket käännetään latauksessa, ei piirtäessä.** Uuden putken
  luonti kesken pelin aiheuttaa nykäyksen (shader compilation
  stutter). Käytä putkivälimuistia ja kerää tarvittavat putket
  etukäteen.
- **Asettelun siirtymät ovat pakollisia**, vaikka tietyllä laitteella
  ne eivät tekisi mitään. `UNDEFINED`-asettelusta siirrytään, kun
  vanhaa sisältöä ei tarvita; se on halvin siirtymä.
- **Valitse `loadOp` ja `storeOp` tietoisesti.** `LOAD` lukee koko
  liitännän muistista ja `STORE` kirjoittaa sen takaisin; tarpeettomat
  maksavat kaistaa.
- **Dynaaminen renderöinti** on yksinkertaisin tapa uudessa koodissa;
  render pass -olioita kannattaa harkita mobiilissa ja monivaiheisissa
  tekniikoissa.

## Itsearviointi

- Osaat kääntää GLSL:n SPIR-V:ksi rakennuksessa ja ladata sen
  varjostinmoduuliksi.
- Osaat luoda grafiikkaputken ja selittää, miksi putki on muuttumaton
  ja mitä dynaaminen tila tarkoittaa.
- Osaat tallentaa komentopuskurin, lähettää sen jonoon ja odottaa sen
  valmistumista aidalla.
- Osaat vaihtaa kuvan asettelun esteellä ja piirtää dynaamisella
  renderöinnillä.
- Osaat valita `loadOp`- ja `storeOp`-arvot ja selittää niiden
  vaikutuksen kaistanleveyteen.
- Osaat kuvata, miten sama rakenne toimii ikkunaan piirrettäessä
  swapchainin kanssa.
