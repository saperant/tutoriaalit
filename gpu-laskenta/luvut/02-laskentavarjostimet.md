# Laskentavarjostimet

Laskentavarjostin on GPU:lla ajettava ohjelma, jolla ei ole paikkaa
grafiikkaputkessa. Sillä ei ole verteksejä eikä pikseleitä, vain
*säikeitä* (invocation), jotka lukevat ja kirjoittavat puskureita.
Isäntä käynnistää varjostimen komennolla `vkCmdDispatch(x, y, z)`,
joka luo $x \cdot y \cdot z$ **työryhmää** (workgroup). Työryhmän koko
kiinnitetään varjostimessa, esimerkiksi 256 säiettä.

Työryhmä on GPU-laskennan tärkein käsite. Saman työryhmän säikeet
ajetaan samalla laskentayksiköllä, ne voivat jakaa nopean **jaetun
muistin** (shared memory) ja tahdistua keskenään `barrier()`-kutsulla.
Eri työryhmät ovat toisistaan riippumattomia. Niiden suoritusjärjestystä
ei taata, eikä niiden välillä ole tahdistusta saman ajon aikana. Tästä
seuraa koko tutoriaalin perussääntö: **riippuvuus työryhmien välillä
vaatii uuden ajon** (luku 9).

## Varjostimen rakenne

SAXPY-varjostimessa (luku 1) on kaikki laskentavarjostimen osat.
`layout(local_size_x = 256) in` kiinnittää työryhmän koon. Puskurit
esitellään `buffer`-lohkoina, joilla on sidontapiste
(`set`, `binding`), ja push-vakiot `push_constant`-lohkona. Funktio
`main` ajetaan kerran jokaiselle säikeelle. Säie tunnistaa itsensä
sisäänrakennetuista muuttujista:

| Muuttuja | Tyyppi | Merkitys |
|----------|--------|----------|
| `gl_GlobalInvocationID` | `uvec3` | säikeen paikka koko ajossa |
| `gl_LocalInvocationID` | `uvec3` | säikeen paikka työryhmässä |
| `gl_LocalInvocationIndex` | `uint` | sama yhtenä lukuna |
| `gl_WorkGroupID` | `uvec3` | työryhmän paikka ajossa |
| `gl_WorkGroupSize` | `uvec3` | työryhmän koko (vakio) |
| `gl_NumWorkGroups` | `uvec3` | ajon työryhmien määrä |

Globaali indeksi on `gl_WorkGroupID * gl_WorkGroupSize +
gl_LocalInvocationID`. Yksiulotteinen data käyttää vain x-akselia;
kuvat ja matriisit käyttävät x- ja y-akselia.

Varastopuskurit (storage buffer) noudattavat **std430**-asettelua,
jossa `float`- ja `uint`-taulukot ovat tiiviitä kuten C++:ssa. Rakenteet
ja `vec3` saavat täytettä (GPU-ohjelmoinnin luku 4). Määreet
`readonly` ja `writeonly` kertovat kääntäjälle ja lukijalle, mihin
puskuria käytetään. Ne myös auttavat synkronoinnin validointia (luku 9).

## Putki ja kuvaajat isännällä

Laskentaputki on paljon yksinkertaisempi kuin grafiikkaputki: siinä on
yksi varjostinvaihe ja asettelu (pipeline layout), joka kertoo
kuvaajajoukot ja push-vakioiden koon. Kaikki tutoriaalin varjostimet
lukevat ja kirjoittavat vain varastopuskureita, joten apukirjaston
`Putki`-luokka olettaa, että sidontapisteet 0, 1, 2, … ovat puskureita
joukossa 0. Luokka luo kuvaajajoukon asettelun, putken asettelun ja
kuvaaja-altaan, ja sen käyttö näyttää tältä:

```{.cpp tiedosto="esimerkit/01-saxpy.cpp" osa="ajo"}
```

Kuvaajajoukko (descriptor set) sitoo putken sidontapisteisiin
konkreettiset puskurit. Samalla putkella voi olla useita joukkoja: luvun
7 kantalukulajittelu ajaa samaa varjostinta vuorotellen puskureista
A → B ja B → A. Ajo tallentaa komentopuskuriin kolme komentoa:
putken ja joukon sidonnan, push-vakiot ja `vkCmdDispatch`:

```{.cpp tiedosto="esimerkit/yhteinen/laskenta.hpp" osa="aja"}
```

```{.cpp tiedosto="esimerkit/yhteinen/laskenta.hpp" osa="ryhmat"}
```

Ajon kaksi muotoa ovat erillään tarkoituksella. Ensimmäinen versio
otti ryhmien määrän kolmena kokonaislukuna, ja kutsu
`aja(kp, joukko, n, ryhmat)` valitsi ilman push-vakioita olevan
muodon: `n` tulkittiin x-suunnan ryhmien määräksi ja `ryhmat`
y-suunnan määräksi. Miljoonan alkion skannaus käynnisti siis lähes
kaksi miljardia työryhmää, ja ohjelma näytti jumittuvan. Oikealla
GPU:lla ajuri olisi lopulta katkaissut työn (TDR, *timeout detection
and recovery*). Erillinen `Ryhmat`-tyyppi tekee tällaisesta kutsusta
käännösvirheen, ja muoto ilman vakioita tarkistaa, ettei putki odota
niitä.

Puskurit ovat apukirjastossa tyypitettyjä. Oletuksena ne varataan
CPU:lle näkyvästä, koherentista muistista ja kuvataan pysyvästi, joten
isäntä lukee ja kirjoittaa alkioita suoraan `std::span`-näkymän
kautta:

```{.cpp tiedosto="esimerkit/yhteinen/vk.hpp" osa="puskuri"}
```

Erillisellä näytönohjaimella CPU:lle näkyvä muisti on hidasta GPU:lle,
koska se on isännän keskusmuistissa PCIe-väylän takana. Oikeassa
ohjelmassa suuret puskurit varataan laitteen omasta muistista
(`DEVICE_LOCAL`), ja data kopioidaan sinne välipuskurin kautta.
Lavapipellä ja integroiduilla näytönohjaimilla muisti on samaa, joten
esimerkit käyttävät yksinkertaisempaa tapaa. Siirron hinta mitataan
luvussa 10.

## Työryhmien määrä ja reunat

Data on harvoin työryhmän koon monikerta. Ryhmien määrä pyöristetään
ylöspäin, ja varjostin tarkistaa indeksinsä:

```{.cpp tiedosto="esimerkit/yhteinen/laskenta.hpp" osa="ryhmia"}
```

Jos tarkistus puuttuu, viimeisen ryhmän ylimääräiset säikeet lukevat ja
kirjoittavat puskurin ohi. Vulkan ei tarkista rajoja oletuksena. Tulos
on määrittelemätöntä käytöstä: virheellistä dataa, toisen puskurin
korruptoituminen tai laitteen menetys (`VK_ERROR_DEVICE_LOST`).
Laitteen piirre `robustBufferAccess` tekee rajojen yli menevästä
luvusta nollan ja kirjoituksesta tyhjän, mutta se maksaa ja on
virheiden etsintään, ei korjaukseksi.

Pyöristys alaspäin on toinen yleinen virhe. Se ei kaadu eikä näy
validoinnissa, koska kaikki käsitellyt indeksit ovat kelvollisia. Osa
datasta vain jää käsittelemättä:

```{.cpp tiedosto="esimerkit/01-saxpy.cpp" osa="vaarin"}
```

Tällainen virhe löytyy vain vertailemalla tulosta referenssiin
*kokoilla, jotka eivät ole ryhmän monikertoja*. Esimerkin miljoona ja
kolme alkiota on valittu siksi.

Ryhmien määrällä on myös yläraja: `maxComputeWorkGroupCount` on
vähintään 65 535 kuhunkin suuntaan, ja monella laitteella se on juuri
tämä. 256 säikeen ryhmillä yksiulotteinen ajo kattaa siis noin 16,7
miljoonaa alkiota. Luvun 10 esimerkki ylitti rajan ensimmäisessä
versiossaan, ja validointikerros ilmoitti siitä
(`VUID-vkCmdDispatch-groupCountX-00386`). Suuremmalle datalle on kaksi
tapaa: kaksiulotteinen ajo tai silmukka, jossa jokainen säie käsittelee
useita alkioita ajon koko säiemäärän harppauksin (*grid-stride loop*).

## Push-vakiot

Push-vakiot ovat pieni muistialue, joka tallennetaan suoraan
komentopuskuriin. Niihin sopii vähintään 128 tavua. Ne ovat oikea
paikka koolle, kertoimille ja silmukan kierroksen numerolle, kuten
bitonisen lajittelun askeleelle (luku 7). C++-rakenteen on vastattava
varjostimen lohkoa tavulleen:

```{.cpp tiedosto="esimerkit/01-saxpy.cpp" osa="vakiot"}
```

`static_assert` havaitsee käännöksessä, jos kenttiä lisätään vain
toiselle puolelle. `Putki::aja` tarkistaa lisäksi, että rakenteen koko
on sama kuin putkea luotaessa annettu koko.

## Erikoistusvakiot

Työryhmän koko on usein viritettävä parametri. Paras arvo riippuu
laitteesta, eikä sitä tiedetä varjostinta kirjoitettaessa.
**Erikoistusvakio** (specialization constant) on varjostimen vakio,
jonka arvon isäntä antaa putkea luotaessa. Kääntäjä näkee sen
vakiona, joten silmukat voi avata ja jaetun muistin taulukon koon
voi määrätä sillä. Esimerkin laatikkosumennus ottaa erikoistusvakioina
työryhmän koon molempiin suuntiin ja sumennuksen säteen:

```{.glsl tiedosto="esimerkit/varjostimet/sumennus.comp" osa="erikoistus"}
```

```{.glsl tiedosto="esimerkit/varjostimet/sumennus.comp" osa="main"}
```

Isäntä luo putken jokaiselle kokoonpanolle ja ajaa sen
kaksiulotteisena. Ryhmien määrä lasketaan erikseen kumpaankin
suuntaan:

```{.cpp tiedosto="esimerkit/02-erikoistus.cpp" osa="kokoonpanot"}
```

```{.tuloste tiedosto="esimerkit/02-erikoistus.odotettu"}
```

Tulos on kokonaislukuja, joten vertailu on tarkka, ja tiiviste on sama
kaikille ryhmäkoille. Työryhmän muoto vaikuttaa vain nopeuteen.
Laatikkosumennuksessa naapurit ovat kahdessa suunnassa, joten neliön
muotoinen ryhmä (16 × 16) lukee vähemmän eri rivejä kuin pitkä
(256 × 1). Lavapipe kertoo rajaksi 1 024 säiettä ryhmässä. Määrittely
lupaa vain 128, joten siirrettävä koodi käyttää enintään 128:aa tai
kysyy rajan (`maxComputeWorkGroupInvocations`).

Erikoistusvakioilla on yksi Vulkanin piirre: työryhmän koon antaminen
niillä (`local_size_x_id`) tuottaa SPIR-V:hen suoritustilan
`LocalSizeId`, joka vaatii Vulkan 1.3:n piirteen `maintenance4`.
Esimerkin ensimmäinen versio toimi lavapipellä ilman piirrettä, mutta
validointikerros ilmoitti virheestä
(`VUID-RuntimeSpirv-LocalSizeId-06434`). Laite luodaan siksi näin:

```{.cpp tiedosto="esimerkit/yhteinen/vk.hpp" osa="piirteet"}
```

## Varjostimien kääntäminen

Varjostimet käännetään SPIR-V:ksi rakennuksessa kuten
GPU-ohjelmoinnin tutoriaalissa. Laskentavarjostimen pääte on `.comp`:

```{.makefile tiedosto="esimerkit/Makefile" osa="spirv"}
```

`--target-env=vulkan1.3` sallii SPIR-V 1.6:n ominaisuudet ja
aliryhmäoperaatiot. `-O` optimoi SPIR-V:n, vaikka ajuri optimoi sen
uudelleen omalle laitteelleen. Käännetty moduuli toimii sellaisenaan
kaikilla valmistajilla.

## Käytännössä

- **Tarkista reunat ja testaa epätasaisilla koilla.** Jokainen
  varjostin, joka saa koon push-vakiona, tarkistaa indeksinsä. Testit
  käyttävät kokoja, jotka eivät ole ryhmän, laatan tai lohkon
  monikertoja, koska ne paljastavat sekä reunavirheet että alaspäin
  pyöristetyt ryhmämäärät.
- **Työryhmän koko on 64:n monikerta.** NVIDIA ajaa 32 säikeen ja AMD
  32 tai 64 säikeen ryhmissä (luku 3). 64, 128 ja 256 ovat
  turvallisia lähtöarvoja. Erikoistusvakio tekee koon virittämisestä
  halpaa ilman varjostimen muutoksia.
- **Rajat kysytään, ei oleteta.** `maxComputeWorkGroupInvocations`,
  `maxComputeWorkGroupCount`, `maxComputeSharedMemorySize` ja
  `maxPushConstantsSize` vaihtelevat laitteittain. Määrittelyn
  vähimmäisarvot ovat turvallisia kaikkialla.
- **Validointi kertoo, mitä ajuri ei kerro.** Kaksi tämän luvun
  virhettä (puuttuva `maintenance4` ja liian suuri ryhmämäärä)
  toimivat lavapipellä, mutta voisivat kaatua toisella ajurilla.
- **Tyypitä isännän rajapinta.** Vulkanin kutsuissa on paljon
  samantyyppisiä kokonaislukuja. Omat pienet rakenteet (ryhmät,
  push-vakiot) siirtävät virheet ajosta käännökseen.

## Itsearviointi

- Osaat kirjoittaa laskentavarjostimen, joka lukee ja kirjoittaa
  varastopuskureita, ja käyttää säikeen tunnisteita oikein yksi- ja
  kaksiulotteisessa ajossa.
- Osaat laskea työryhmien määrän ja selittää, miksi varjostimen on
  tarkistettava indeksinsä ja miksi ryhmien määrällä on yläraja.
- Osaat välittää parametreja push-vakioina ja erikoistusvakioina ja
  perustella, kumpaa käytät mihinkin.
- Osaat luoda laskentaputken ja kuvaajajoukon isännällä ja kertoa,
  miksi työryhmät eivät voi odottaa toisiaan saman ajon aikana.
