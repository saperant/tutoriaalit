# GPU:n suoritusmalli

Taito *GPU-ohjelmointi: OpenGL ja Vulkan* esitteli SIMT-mallin: säikeet ajetaan
ryhminä, jotka suorittavat saman käskyn kerrallaan, ja hajoava
haarautuminen ajaa molemmat haarat maskattuina. Tässä luvussa sama
malli nähdään laskentavarjostimen kannalta. Laskennassa ryhmä on
ohjelmoijalle näkyvä yksikkö, jolla on omat operaationsa, ja sen
leveys vaikuttaa sekä tulokseen että nopeuteen.

## Aliryhmät

Vulkan kutsuu laitteiston säieryhmää **aliryhmäksi** (subgroup).
CUDA:ssa sama on *warp*, AMD:lla ja Direct3D:ssä *wave*. Työryhmä
jaetaan aliryhmiin, ja jokainen aliryhmä suoritetaan yhtenä
käskyvirtana: yksi käskyn haku ja purku, ja käskyn operandit ovat
vektorirekistereitä, joissa on yksi kaista jokaiselle säikeelle.

| Laite | Aliryhmän leveys |
|-------|------------------|
| NVIDIA | 32 |
| AMD GCN | 64 |
| AMD RDNA | 32 tai 64 (kääntäjä valitsee) |
| Intel Xe | 8, 16 tai 32 |
| Apple | 32 |
| Arm Mali (Valhall) | 16 |
| lavapipe | CPU:n vektorileveys / 32 bittiä: SSE 4, AVX2 8, AVX-512 16 |

Leveyttä ei pidä kiinnittää koodiin. Varjostin lukee sen muuttujasta
`gl_SubgroupSize`, ja isäntä voi kysyä sen laitteen ominaisuuksista
(`VkPhysicalDeviceSubgroupProperties`). Jos algoritmi vaatii tietyn
leveyden, Vulkan 1.3:ssa voi pyytää sitä putkea luotaessa
(`requiredSubgroupSize`), jos laite sallii leveyden valinnan.
Esimerkkien Makefile kiinnittää lavapipen leveyden kahdeksaan
(luku 1), joten tulosteet ovat samat kaikilla koneilla.

![Sama 32 säikeen työryhmä kolmella aliryhmän leveydellä. Aliryhmät
ovat tässä työryhmän peräkkäisiä säikeitä; määrittely ei takaa sitä,
ja esimerkki tarkistaa sen
lavapipelle.](kuvat/03-aliryhmat.png){width=90%}

Esimerkki tarkistaa kolme asiaa: aliryhmän koon, sen, että aliryhmät
ovat työryhmän peräkkäisiä säikeitä, ja aliryhmän summan. Tulokset
kerätään yhteen puskuriin:

```{.glsl tiedosto="esimerkit/varjostimet/aliryhmat.comp" osa="tulos"}
```

```{.glsl tiedosto="esimerkit/varjostimet/aliryhmat.comp" osa="jarjestys"}
```

Määrittely ei lupaa, että aliryhmä $k$ sisältää säikeet
$kS, \dots, kS + S - 1$, vaikka käytännössä kaikki toteutukset tekevät
niin yksiulotteisille ryhmille. Algoritmit, jotka olettavat tämän
(esimerkiksi luvun 7 vakaa kantalukulajittelu), kannattaa testata
juuri tällä tavalla. Vulkan 1.3:n piirre `computeFullSubgroups`
lupaa lisäksi, ettei aliryhmä ole vajaa, kun työryhmän koko on
aliryhmän monikerta.

## Aliryhmäoperaatiot

Aliryhmän kaistat voivat vaihtaa dataa suoraan rekisterien kautta,
ilman jaettua muistia ja ilman `barrier()`-kutsua. Operaatiot ovat
GLSL:n laajennuksissa `GL_KHR_shader_subgroup_*`, ja laite kertoo
tukemansa ryhmät kentässä `subgroupSupportedOperations`:

| Ryhmä | Esimerkkejä | Käyttö |
|-------|-------------|--------|
| basic | `subgroupElect`, `subgroupBarrier` | yksi kaista tekee työn |
| vote | `subgroupAny`, `subgroupAll` | koko aliryhmän ehto |
| arithmetic | `subgroupAdd`, `subgroupInclusiveAdd`, `subgroupMax` | reduktio ja skannaus |
| ballot | `subgroupBallot`, `subgroupBallotBitCount` | bittimaski kaistoista |
| shuffle | `subgroupShuffle`, `subgroupShuffleXor` | toisen kaistan arvo |
| clustered | `subgroupClusteredAdd` | reduktio osaryhmissä |

`subgroupAdd(paikka)` palauttaa jokaiselle kaistalle koko aliryhmän
summan yhdellä operaatiolla. Laitteistossa se on muutama
kaistojen välinen siirto ja yhteenlasku. Luvun 4 reduktio ja luvun 7
lajittelu käyttävät näitä operaatioita jaetun muistin sijaan.

## Haarautumisen hajaantuminen

Kun aliryhmän kaistat päätyvät ehtolauseessa eri haaroihin, aliryhmä
on **hajaantunut** (divergent), ja molemmat haarat suoritetaan
peräkkäin. Esimerkki mittaa hajaantumisen suoraan: jokainen aliryhmä
kysyy äänestyksellä, onko ehto tosi joillakin mutta ei kaikilla
kaistoilla.

```{.glsl tiedosto="esimerkit/varjostimet/aliryhmat.comp" osa="ehdot"}
```

```{.glsl tiedosto="esimerkit/varjostimet/aliryhmat.comp" osa="hajaantuminen"}
```

Sama lasketaan CPU:lla mallilla, joka jakaa säikeet minkä tahansa
leveyden aliryhmiin. GPU:n tulos varmistaa, että malli vastaa
todellista suoritusta, ja malli näyttää, mitä tapahtuisi leveämmillä
aliryhmillä:

```{.cpp tiedosto="esimerkit/03-aliryhmat.cpp" osa="malli"}
```

```{.tuloste tiedosto="esimerkit/03-aliryhmat.odotettu"}
```

Taulukon rivit kertovat, milloin haarautuminen maksaa:

- **64 säikeen lohkot** eivät hajaannu millään leveydellä, koska ehto
  vaihtuu vain aliryhmän rajalla. Kun data voidaan järjestää niin,
  että samaa käsittelyä tarvitsevat alkiot ovat vierekkäin, ehto on
  ilmainen.
- **8 säikeen lohkot** ovat lavapipelle ilmaisia, mutta 32 ja 64
  kaistan laitteilla jokainen aliryhmä hajaantuu. Koodi, joka on
  viritetty yhden laitteen leveydelle, voi olla toisella hidas.
- **Parilliset ja parittomat** hajaantuvat aina: puolet kaistoista
  tekee then-haaraa ja puolet else-haaraa, joten kumpikin haara maksaa
  koko aliryhmälle.
- **Yksi säie työryhmästä** hajauttaa täsmälleen yhden aliryhmän
  jokaisessa työryhmässä. Harvinainen poikkeustapaus on halpa, jos se
  on lyhyt.

NVIDIA:n Volta-arkkitehtuurista alkaen hajaantuneet kaistat voivat
edetä itsenäisesti (*independent thread scheduling*). Hinta on
kuitenkin sama, sillä haarat suoritetaan edelleen eri aikaan.
Itsenäinen eteneminen estää lähinnä lukkiutumisen silloin, kun kaistat
odottavat toisiaan.

## Viiveen piilotus ja käyttöaste

Globaalin muistin luku kestää satoja kellojaksoja. GPU ei piilota
viivettä välimuisteilla ja spekulatiivisella suorituksella kuten CPU,
vaan rinnakkaisuudella. Laskentayksikössä on samanaikaisesti useita
aliryhmiä, ja kun yksi odottaa muistia, toinen suorittaa. Vaihto on
ilmainen, koska jokaisen aliryhmän rekisterit ovat koko ajan
rekisteritiedostossa.

Kuinka monta aliryhmää laskentayksikköön mahtuu, riippuu siitä
resurssista, joka loppuu ensin: rekistereistä, jaetusta muistista vai
aliryhmä- ja työryhmäpaikoista. Suhdetta laitteen enimmäismäärään
kutsutaan **käyttöasteeksi** (occupancy). Esimerkin laskuri käyttää
kuvitteellista esimerkkilaitetta, jonka luvut ovat tyypillistä
suuruusluokkaa:

```{.cpp tiedosto="esimerkit/03-aliryhmat.cpp" osa="kayttoaste"}
```

Tulosteen alaosa näyttää neljä tyypillistä tilannetta. 64 rekisteriä
säiettä kohden puolittaa rekistereihin mahtuvien ryhmien määrän. 16
KiB jaettua muistia työryhmää kohden rajoittaa ryhmiä neljään. Yksi
1 024 säikeen ryhmä vie 32 aaltopaikkaa, eikä toinen mahdu jäljellä
oleviin 16:een. Pieni 64 säikeen ryhmä, joka käyttää 128 rekisteriä,
jää kolmannekseen.

Käyttöaste ei ole tavoite sinänsä. Ydin, jolla on paljon
käskytason rinnakkaisuutta (useita riippumattomia latauksia säiettä
kohden), voi saavuttaa täyden kaistan pienelläkin käyttöasteella.
Rekisterien lisääminen voi silloin nopeuttaa, vaikka käyttöaste
laskee. Käyttöasteen tärkein käyttö on selittää, miksi ydin on hidas:
jos se on muistisidonnainen ja käyttöaste on matala, viivettä ei ole
millä piilottaa.

Kääntäjä kertoo rekisterien määrän (NVIDIA: `--resource-usage`, AMD:
Radeon GPU Analyzer), ja profiloijat näyttävät saavutetun
käyttöasteen. Vulkanissa samat tiedot saa laajennuksella
`VK_KHR_pipeline_executable_properties`.

## Lavapipe suoritusmallina

Lavapipe toteuttaa saman mallin CPU:lla. Aliryhmä on yksi
AVX2-vektori, jossa on 8 kaistaa, ja työryhmä ajetaan yhdellä
CPU-säikeellä silmukkana aliryhmien yli. Eri työryhmät jaetaan
CPU:n ytimille. `barrier()` toteutetaan vaihtamalla työryhmän sisällä
seuraavaan aliryhmään. Se on CPU:lla kallis operaatio, koska jokaisen
aliryhmän tila on tallennettava ja palautettava. Siksi lavapipellä
jaettua muistia ja esteitä käyttävät versiot ovat usein *hitaampia*
kuin suorat versiot (luvut 4, 7 ja 8), vaikka oikealla GPU:lla
tilanne on päinvastainen. Tämä on hyvä muistutus siitä, että nopeus
on aina mitattava kohdelaitteella.

## Käytännössä

- **Älä kiinnitä aliryhmän leveyttä.** Käytä `gl_SubgroupSize`-
  muuttujaa ja testaa vähintään kahdella leveydellä. Lavapipellä sen
  voi vaihtaa ympäristömuuttujalla `LP_NATIVE_VECTOR_WIDTH` (128, 256
  tai 512 bittiä).
- **Järjestä data haarojen mukaan.** Jos osa alkioista tarvitsee
  kallista käsittelyä, erottele ne ensin omaan jonoonsa (virran
  tiivistys, luku 5) ja käsittele jono omalla ajollaan.
- **Aliryhmäoperaatiot ovat nopeampia kuin jaettu muisti.** Ne eivät
  tarvitse estettä, eivätkä ne kuluta jaettua muistia, joka rajoittaa
  käyttöastetta.
- **Käyttöaste selittää, ei määrää.** Mittaa ensin, onko ydin muisti-
  vai laskentasidonnainen (luku 10), ja katso käyttöastetta vasta, kun
  muistisidonnainen ydin ei saavuta kaistaa.

## Itsearviointi

- Osaat selittää, mikä aliryhmä on, miten sen leveys vaihtelee
  laitteittain ja miksi koodi ei saa olettaa tiettyä leveyttä.
- Osaat käyttää aliryhmäoperaatioita (äänestys, summa, ballot) ja
  kertoa, mitä hyötyä niistä on jaettuun muistiin verrattuna.
- Osaat ennustaa, milloin ehtolause hajauttaa aliryhmän, ja
  järjestää datan niin, ettei niin käy.
- Osaat laskea työryhmän käyttöasteen rekisterien, jaetun muistin ja
  aliryhmäpaikkojen perusteella ja kertoa, miksi korkea käyttöaste ei
  aina ole tavoite.
