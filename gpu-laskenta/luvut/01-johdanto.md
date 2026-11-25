# Johdanto {.runko-johdanto}

Näytönohjain on rinnakkaiskone, jossa on tuhansia yksinkertaisia
laskentakaistoja ja satojen gigatavujen sekuntinopeus omaan muistiin.
Grafiikassa sen työ on varjostaa miljoonia pikseleitä. Samaa konetta
voi käyttää mihin tahansa laskentaan, jossa samaa työtä tehdään
suurelle datamäärälle: kuvankäsittelyyn, fysiikkasimulaatioihin,
lajitteluun, tietokantaoperaatioihin ja neuroverkkojen
matriisilaskentaan. Tätä kutsutaan **GPU-laskennaksi** (GPGPU,
*general-purpose computing on GPUs*).

GPU-laskenta ei ole tavallisen ohjelman siirtämistä toiselle
suorittimelle. Algoritmi on usein kirjoitettava uudestaan. Silmukka,
joka summaa taulukon CPU:lla, muuttuu GPU:lla puuksi, jossa tuhannet
säikeet summaavat pareja ja tahdistuvat tasojen välissä. Lajittelu
muuttuu lajitteluverkoksi tai prefiksisummiin perustuvaksi
kantalukulajitteluksi. Tämä tutoriaali opettaa nämä *rinnakkaiset
primitiivit*: reduktion, prefiksisumman, histogrammin ja lajittelun.
Niistä rakennetaan lähes kaikki muu GPU-laskenta.

## Esitiedot ja rajaus

Esitietoina ovat taidot *GPU-ohjelmointi: OpenGL ja Vulkan* ja *Suorituskyvyn analyysi
ja optimointi*. Ensimmäisestä tarvitaan Vulkanin perusteet: instanssi,
laite ja jonot, muisti ja puskurit, komentopuskurit, kuvaajajoukot,
push-vakiot, SPIR-V ja esteet. Niitä ei selitetä tässä uudestaan,
vaan viitataan taitoon *GPU-ohjelmointi: OpenGL ja Vulkan*. Jälkimmäisestä tarvitaan
roofline-malli, muistihierarkia ja mittaamisen periaatteet, joita
sovelletaan tässä GPU:hun. Taito *Rinnakkaisohjelmointi* käsittelee
samoja primitiivejä CPU:n säikeillä ja muistimallin kannalta.

Tutoriaali käyttää Vulkanin laskentavarjostimia ja pysyy
primitiiveissä. Valmistajakohtaiset rajapinnat (CUDA, HIP, SYCL)
esitellään vain vertailuna luvussa 10. Koneoppimisen kehykset,
usean GPU:n laskenta ja kokonaiset sovellukset, kuten
hiukkassimulaatio, rajataan pois. Luvun 7 lopussa kuvataan
esimerkkinä, miten naapurihaku kootaan primitiiveistä.

## Rajapinnat

GPU-laskentaan on useita rajapintoja. Tämä tutoriaali käyttää
**Vulkanin laskentavarjostimia** (compute shader), koska Vulkan toimii
kaikkien valmistajien laitteilla ja sille on avoin
ohjelmistototeutus, jolla esimerkit voidaan testata ilman
näytönohjainta. Käsitteet ovat samat kaikissa rajapinnoissa; vain
nimet vaihtelevat (luku 10).

| Rajapinta | Kieli | Laitteet | Huomio |
|----------------|----------------------|----------------|------------------------------|
| Vulkan-laskenta | GLSL, HLSL, Slang → SPIR-V | kaikki valmistajat | eksplisiittinen, sama kuin grafiikka |
| CUDA | C++-laajennus | NVIDIA | laajin ekosysteemi ja kirjastot |
| HIP (ROCm) | C++-laajennus | AMD, NVIDIA | CUDA:n kaltainen |
| OpenCL | C-pohjainen | useimmat | vanhempi, avoin standardi |
| SYCL | standardi-C++ | Intel, NVIDIA, AMD | yksi lähde isännälle ja laitteelle |
| Metal, WebGPU | MSL, WGSL | Apple, selain | grafiikkarajapintojen laskenta |

## Testaus ilman näytönohjainta

Esimerkit ajetaan Mesan **lavapipe**-ajurilla. Se toteuttaa Vulkan
1.4:n CPU:lla: varjostimet käännetään LLVM:llä CPU:n
vektorikäskyiksi, ja työryhmät jaetaan CPU:n ytimille. Samaa ajuria
käytti GPU-ohjelmoinnin tutoriaali piirtämiseen. Laskennassa se on
vielä luontevampi, koska ikkunaa, kuvia tai rasterointia ei tarvita.

Jokainen esimerkki tekee saman työn kahdesti: GPU:lla ja
yksinkertaisella CPU-toteutuksella, *referenssillä*. Ohjelma vertaa
tuloksia ja tulostaa raportin, jota verrataan odotettuun tulosteeseen
kuten muissakin tutoriaaleissa. Vertailu tehdään tarkasti, kun tulos
on kokonaislukuja. Liukuluvuissa vertaillaan toleranssilla, koska
rinnakkainen summa laskee yhteenlaskut eri järjestyksessä kuin
peräkkäinen silmukka (luku 4).

Lisäksi Khronosin **validointikerros** tarkistaa jokaisen
Vulkan-kutsun, ja esimerkin on päätyttävä ilman yhtään ilmoitusta.
Luvun 9 esimerkki käyttää myös synkronoinnin validointia, joka löytää
puuttuvat esteet.

Aliryhmän leveys (luku 3) riippuu lavapipellä CPU:n vektorileveydestä.
Esimerkkien Makefile kiinnittää sen, jotta tulosteet ovat samat
kaikilla koneilla:

```{.makefile tiedosto="esimerkit/Makefile" osa="ymparisto"}
```

Lavapipe ei kerro mitään oikean GPU:n nopeudesta. Se on oikeellisuuden
testaamiseen. Aikoja ei verrata testeissä, mutta jokaisen esimerkin voi
ajaa valitsimella `--mittaa`, jolloin se tulostaa GPU:n aikaleimoilla
mitatut ajat (luku 10). Tekstissä mainitut ajat on mitattu
kirjoittajan koneella lavapipellä, ja ne ovat suuntaa-antavia. Usein
ne osoittavat, mikä optimointi *ei* auta CPU-emuloinnissa, vaikka
auttaa oikealla GPU:lla. Tämä ero selitetään aina.

## Ensimmäinen laskenta

Klassinen ensimmäinen GPU-laskenta on SAXPY, $y \leftarrow a x + y$.
Jokainen säie laskee yhden alkion:

```{.glsl tiedosto="esimerkit/varjostimet/saxpy.comp" osa="saxpy"}
```

```{.tuloste tiedosto="esimerkit/01-saxpy.odotettu"}
```

Miljoona alkiota jaetaan 3 907 työryhmään, joissa kussakin on 256
säiettä. Viimeinen ryhmä on vajaa, joten 189 säiettä palaa heti
tarkistettuaan indeksinsä. Kolmas rivi näyttää yleisen virheen:
ryhmien määrä on pyöristetty alaspäin, ja 67 viimeistä alkiota jää
laskematta. Luku 2 käy esimerkin läpi.

## Työkalut

| Työkalu | Tehtävä |
|---------|---------|
| `glslc` (shaderc) | GLSL → SPIR-V, varoitukset virheinä |
| `spirv-val`, `spirv-dis` | SPIR-V:n tarkistus ja tekstimuoto |
| `vulkaninfo` | laitteen rajat ja ominaisuudet |
| validointikerros | kutsujen ja synkronoinnin tarkistus |
| RenderDoc, Nsight, Radeon GPU Profiler | oikean GPU:n analyysi |

Esimerkkien hakemistossa `make` kääntää varjostimet ja ohjelmat, ajaa
ne ja vertaa tulosteet. `make aja-04-reduktio` ajaa yhden esimerkin, ja
`make mittaa` ajaa kaikki mittaustilassa. Kehityskontissa
(`.devcontainer/gpu-laskenta`) kaikki tarvittava on valmiina.
Esimerkkitiedoston numero on sen luvun numero, jossa esimerkki
käsitellään. Algoritmien periaatekuvat piirtää `kuvat/piirra.py`
(`make kuvat` paketin juuressa); niitä ei tarvita esimerkkien
ajamiseen.

## Tutoriaalin rakenne

Luku 2 rakentaa laskentaputken ja pienen apukirjaston, jota kaikki
esimerkit käyttävät. Luku 3 kuvaa GPU:n suoritusmallin: aliryhmät,
haarautumisen hajaantumisen ja käyttöasteen. Luvut 4–7 käsittelevät
rinnakkaiset primitiivit: reduktion, prefiksisumman, atomiset
operaatiot ja histogrammin sekä lajittelun. Luku 8 käsittelee GPU:n
muistihierarkiaa matriisin transpoosin ja matriisitulon avulla, luku 9
synkronointia ja luku 10 suorituskyvyn mittaamista.
