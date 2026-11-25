# Suorituskyvyn mittaaminen

Taito *Suorituskyvyn analyysi ja optimointi* käsitteli mittaamisen
periaatteet:
toistot, lämmittely, mediaani ja kohinan lähteet. Ne pätevät GPU:lla
sellaisinaan, mutta kello on eri. CPU:n kello ei näe, milloin GPU
aloittaa ja lopettaa, koska komennot vain lähetetään jonoon. Kun
CPU mittaa aikaa lähetyksestä aidan odotuksen loppuun, mukana ovat
lähetyksen, ajurin ja herätyksen viiveet. Lyhyillä ajoilla ne voivat
olla suurempia kuin itse työ. GPU:n työ mitataan siksi GPU:n omalla
kellolla, **aikaleimakyselyillä**.

## Aikaleimat

Aikaleima kirjoitetaan komentopuskuriin kuten mikä tahansa komento.
`vkCmdWriteTimestamp2` kirjoittaa kyselyyn laitteen kellon arvon, kun
kaikki sitä ennen tallennetut komennot ovat edenneet annettuun
vaiheeseen asti. Kahden leiman erotus on niiden välisten komentojen
kesto. Apukirjaston ajastin:

```{.cpp tiedosto="esimerkit/yhteinen/laskenta.hpp" osa="ajastin"}
```

Kolme yksityiskohtaa:

- **Leiman yksikkö on laitteen jakso.** Kellon arvo kerrotaan
  laitteen rajalla `timestampPeriod`, joka on nanosekunteja jaksoa
  kohden. Lavapipellä se on 1, mutta oikeilla laitteilla esimerkiksi
  10 tai 40.
- **Kaikki jonot eivät tue aikaleimoja.** Jonoperheen kenttä
  `timestampValidBits` kertoo kellon bittien määrän. Arvo 0 tarkoittaa,
  ettei aikaleimoja ole. Apukirjasto tallentaa sen laitetta
  valittaessa (luku 2).
- **Kysely on nollattava ennen jokaista käyttöä.** Kyselyä ei saa
  kirjoittaa uudelleen ennen nollausta. Ensimmäinen versio nollasi
  kyselyt vain luettaessa, ja ohjelmat, jotka eivät mittaustilan
  ulkopuolella lukeneet aikoja, saivat validointivirheen
  `VUID-vkCmdWriteTimestamp2-None-03864`. Nyt nollaus tallennetaan
  komentopuskuriin ennen ensimmäistä leimaa.

Esimerkin testitila tarkistaa vain, että aikaleimat toimivat. Ajat
vaihtelevat koneittain eikä niitä verrata:

```{.tuloste tiedosto="esimerkit/10-mittaus.odotettu"}
```

## Toistot ja mediaani

Yksittäinen GPU-ajo vaihtelee kellotaajuuden, lämpötilan, muiden
prosessien ja välimuistin tilan mukaan. Ensimmäinen ajo on usein
hitaampi, koska ajuri valmistelee resursseja tai laite herää
virransäästötilasta. Mittaus ajetaan siksi useasti, ensimmäinen ajo
hylätään, ja tuloksena raportoidaan mediaani:

```{.cpp tiedosto="esimerkit/10-mittaus.cpp" osa="mediaani"}
```

Oikealla GPU:lla kellotaajuus nousee kuormassa ja laskee lämmetessä.
Toistettavia vertailuja varten taajuuden voi lukita
valmistajan työkaluilla (`nvidia-smi --lock-gpu-clocks`, AMD:n
`rocm-smi --setperfdeterminism`). Lavapipellä mittaus on yhtä
herkkä kuin mikä tahansa CPU-ohjelma muiden prosessien kuormalle.
Kirjoittajan kone oli tätä kirjoitettaessa raskaasti kuormitettu, joten
tekstin luvut ovat suuntaa-antavia.

## Siirtojen hinta

Erillisellä näytönohjaimella data kulkee isännän muistista laitteen
muistiin PCIe-väylää pitkin. PCIe 4.0 x16 siirtää käytännössä noin 25
Gt/s ja PCIe 5.0 noin 50 Gt/s, kun laitteen oma muisti on kymmeniä
kertoja nopeampi. Siirto on usein koko laskennan kallein osa:

```{.cpp tiedosto="esimerkit/10-mittaus.cpp" osa="siirto"}
```

Lavapipellä molemmat puskurit ovat samaa keskusmuistia, ja kopion
nopeus oli mittaustilassa 4–7 Gt/s, eli CPU:n muistikopion luokkaa.
Oikealla laitteella sama mittaus näyttää väylän nopeuden. Kolme
sääntöä:

1. **Pidä data laitteella.** Siirrä syöte kerran, tee kaikki vaiheet
   GPU:lla ja siirrä vain lopputulos takaisin. Esimerkin lajittelu ja
   skannaus eivät lue välituloksia CPU:lle.
2. **Siirrä suuria paloja.** Jokaisella siirrolla on kiinteä
   aloitushinta, joten monta pientä siirtoa on hitaampi kuin yksi suuri.
3. **Limitä siirto ja laskenta.** Erillinen siirtojono
   (`VK_QUEUE_TRANSFER_BIT`) kopioi seuraavan erän samalla, kun
   laskentajono käsittelee nykyistä.

Amdahlin laki pätee: jos siirto vie puolet ajasta, laskennan
nopeuttaminen ei voi nopeuttaa kokonaisuutta yli kaksinkertaisesti.
GPU kannattaa vain, jos laskentaa on tarpeeksi siirrettyä dataa kohden
tai jos data on jo valmiiksi laitteella.

## Roofline GPU:lla

Roofline-mallin kaksi rajaa ovat muistin kaista ja laskentateho. Ne
voi mitata omalle laitteelle ytimellä, jonka laskentaintensiteettiä
voi säätää. Jokainen säie lukee yhden luvun, laskee sille toistot
kertaa $x \leftarrow ax + b$ ja kirjoittaa tuloksen:

```{.glsl tiedosto="esimerkit/varjostimet/kuorma.comp" osa="kuorma"}
```

```{.cpp tiedosto="esimerkit/10-mittaus.cpp" osa="roofline"}
```

Mittaustilassa lavapipe antoi seuraavanlaisia tuloksia (kuormitettu
kone, suuntaa-antavia):

| Toistot | Laskut/tavu | Glaskua/s | Gt/s |
|---------|-------------|-----------|------|
| 1 | 0,25 | 1,1 | 4,3 |
| 4 | 1 | 1,9 | 1,9 |
| 16 | 4 | 3,8 | 1,0 |
| 64 | 16 | 4,5 | 0,3 |
| 256 | 64 | 4,4 | 0,1 |

![Sama taulukko roofline-kuvaajana. Mallin kaksi rajaa on otettu
taulukon suurimmasta kaistasta (4,3 Gt/s) ja suurimmasta
laskunopeudesta (4,5 Glaskua/s). Mittaus seuraa rajoja päistään, ja
siirtymä niiden välillä on pehmeä.](kuvat/10-roofline.png){width=68%}

Pienellä intensiteetillä ydin on muistisidonnainen, ja laskunopeus
kasvaa intensiteetin mukana. Rajojen leikkauspiste eli harjanne on
tällä laitteella noin yhden laskun kohdalla tavua kohden, mutta
siirtymä on pehmeä: laskunopeus saavuttaa kattonsa vasta noin 16
laskulla tavua kohden, minkä jälkeen ydin on selvästi
laskentasidonnainen. Oikealla GPU:lla molemmat rajat ovat
satoja kertoja korkeammalla, mutta käyrän muoto on sama. Harjanne on
yleensä 10–100 laskua tavua kohden, joten useimmat ytimet ovat
muistisidonnaisia. Tämän ytimen laskuja ei voi laskea rinnakkain,
koska jokainen toisto riippuu edellisestä, joten se ei saavuta
laitteen todellista huippua. Mittaus kertoo silti, millä
intensiteetillä tämän tyyppinen ydin muuttuu laskentasidonnaiseksi.

## Profiloijat

Aikaleimat kertovat, kuinka kauan ajo kesti, mutta eivät sitä, miksi.
Valmistajien profiloijat lukevat laitteen laskureita: saavutettu kaista,
välimuistien osumat, käyttöaste, hajaantuminen, pankkikonfliktit ja
syyt, miksi aliryhmät odottivat.

| Työkalu | Laitteet | Huomio |
|---------|----------|--------|
| NVIDIA Nsight Compute ja Nsight Graphics | NVIDIA | ydinkohtainen analyysi, roofline |
| Radeon GPU Profiler | AMD | aaltojen aikajana, käskytason ajoitus |
| Intel GPA, VTune | Intel | aliryhmä- ja muistianalyysi |
| RenderDoc | kaikki | komentojen ja resurssien tarkastelu, ei laskureita |
| `VK_KHR_performance_query` | laitteet, jotka tukevat | laskurit Vulkanin kautta |

## Vulkan, CUDA, OpenCL ja SYCL

Tämän tutoriaalin käsitteet ovat samat kaikissa
GPU-laskennan rajapinnoissa. Nimet vaihtelevat:

| Vulkan / GLSL | CUDA | OpenCL | SYCL |
|---------------|------|--------|------|
| säie (invocation) | thread | work-item | work-item |
| aliryhmä (subgroup) | warp | sub-group | sub-group |
| työryhmä (workgroup) | block | work-group | work-group |
| ajo (dispatch) | grid, kernel launch | NDRange | `parallel_for` |
| `shared` | `__shared__` | `__local` | `local_accessor` |
| `barrier()` | `__syncthreads()` | `barrier()` | `group_barrier()` |
| `subgroupAdd` | `__reduce_add_sync`, CUB | `sub_group_reduce_add` | `reduce_over_group` |
| putken este | virran järjestys | tapahtumat | riippuvuudet |

CUDA on suosituin, koska sen ympärillä on laajin kirjastojen valikoima
(cuBLAS, cuDNN, CUB, Thrust) ja työkalut. Se toimii kuitenkin vain
NVIDIA:n laitteilla. AMD:n HIP kääntää lähes saman koodin AMD:lle.
SYCL ja OpenCL ovat avoimia standardeja, ja SYCL:ssä isännän ja
laitteen koodi kirjoitetaan samaan C++-lähteeseen. Vulkan on näistä
eksplisiittisin: muisti, synkronointi ja putket ovat ohjelmoijan
vastuulla. Se on luonteva valinta, kun laskenta on osa
grafiikkasovellusta (hiukkaset, fysiikka, kuvankäsittely,
GPU-ohjattu renderöinti) tai kun ohjelman on toimittava kaikkien
valmistajien laitteilla.

## Käytännössä

- **Mittaa GPU:n kellolla.** Aikaleimat ajon ympärillä kertovat
  GPU:n työn keston. CPU:n kello mittaa lisäksi ajurin ja odotuksen.
- **Toista, hylkää ensimmäinen, raportoi mediaani.** Lukitse kellot,
  jos vertaat kahta toteutusta.
- **Raportoi kaista ja laskunopeus, ei pelkkää aikaa.** Gt/s ja
  Glaskua/s suhteessa laitteen huippuun kertovat, onko optimoitavaa
  jäljellä. Muistisidonnainen ydin, joka saavuttaa 80 % kaistasta,
  on valmis.
- **Siirrot kuuluvat mittaukseen.** Ilmoita GPU:n nopeutus koko
  työstä siirtoineen, ei pelkästä ytimestä.
- **Lavapipe testaa oikeellisuutta, ei nopeutta.** Tämän tutoriaalin
  mittaukset näyttivät useita tapauksia, joissa lavapipellä hitaampi
  versio on oikealla GPU:lla nopeampi.

## Itsearviointi

- Osaat mitata GPU:n työn keston aikaleimakyselyillä ja muuntaa
  leimat nanosekunneiksi.
- Osaat suunnitella toistettavan mittauksen: lämmittely, toistot,
  mediaani ja kellojen lukitus.
- Osaat arvioida siirtojen osuuden kokonaisajasta ja vähentää sitä.
- Osaat mitata roofline-mallin rajat omalle laitteelle ja vertailla
  Vulkanin, CUDA:n, OpenCL:n ja SYCL:n vastaavia käsitteitä.
