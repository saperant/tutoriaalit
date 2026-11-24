# Reaaliaikainen lohkokäsittely C++:lla

Edellisten lukujen vastaanottimet käsittelevät koko tallenteen
kerralla NumPyllä. Se sopii kehitykseen ja analyysiin, mutta oikea
radio tuottaa jatkuvaa virtaa: RTL-SDR 2,4 MS/s:lla tuottaa 4,8 MB
sekunnissa loputtomiin. Vastaanottimen on käsiteltävä virta paloina
(*lohkoina*) vähintään yhtä nopeasti kuin näytteitä tulee, eikä se saa
pitää koko historiaa muistissa. Tässä luvussa luvun 6 ketjun raskain
osa, kanavan valinta ja FM-ilmaisu, toteutetaan C++:lla lohkoittain,
ja tulosta verrataan Python-viitteeseen.

## Lohkorajapinta ja tila

Lohkokäsittelyn tärkein sääntö on, että **tuloksen on oltava sama
lohkon koosta riippumatta**. Suotimet, oskillaattorit ja ilmaisimet
muistavat edellisen lohkon lopun:

- NCO:n vaiheakkumulaattori jatkaa siitä, mihin se jäi.
- FIR-suotimella on historia, jossa on edellisen lohkon $N - 1$
  viimeistä näytettä. Desimoivan suotimen on lisäksi muistettava,
  monennenko näytteen kohdalla seuraava lähtö lasketaan.
- FM-ilmaisin muistaa edellisen näytteen.

Jos tila unohtuu, lohkojen saumoihin syntyy virheitä, jotka kuuluvat
äänessä napsahduksina noin lohkon taajuudella. Virheet ovat
vaikeita löytää kuuntelemalla mutta helppoja testillä.

```{.cpp tiedosto="esimerkit/08-reaaliaika/lohkot.hpp" osa="nco"}
```

```{.cpp tiedosto="esimerkit/08-reaaliaika/lohkot.cpp" osa="nco_toteutus"}
```

NCO on luvun 4 vaiheakkumulaattori. Etumerkitön ylivuoto on C++:ssa
määriteltyä, joten `vaihe_ += askel_` kiertää täsmälleen kuten
laitteistossa. Etumerkillisillä kokonaisluvuilla sama olisi
määrittelemätöntä toimintaa, ja UBSan pysäyttäisi testin.

```{.cpp tiedosto="esimerkit/08-reaaliaika/lohkot.hpp" osa="fir"}
```

```{.cpp tiedosto="esimerkit/08-reaaliaika/lohkot.cpp" osa="fir_toteutus"}
```

Desimoija laskee vain joka $D$:nnen lähdön. Muuttuja `vaihe_` kertoo,
monesko seuraavan lohkon näyte on seuraavan lähdön kohdalla. Kun
lohkon koko ei ole $D$:n monikerta, lähtöjen paikat siirtyvät lohkosta
toiseen. Ilmaisin tuottaa ensimmäisestä näytteestä lähtiessä yhden
lähdön vähemmän kuin tuloja, koska vaihe-eroon tarvitaan kaksi
näytettä:

```{.cpp tiedosto="esimerkit/08-reaaliaika/lohkot.hpp" osa="ilmaisin"}
```

```{.cpp tiedosto="esimerkit/08-reaaliaika/lohkot.cpp" osa="ilmaisin_toteutus"}
```

## Ketju ja itsetesti

Ketju kokoaa osat yhteen ja varaa välipuskurin kerran. Muistin
varaaminen jokaiselle lohkolle on reaaliaikaisessa käsittelyssä
vältettävä, koska varauksen kesto ei ole ennustettava.

```{.cpp tiedosto="esimerkit/08-reaaliaika/main.cpp" osa="ketju"}
```

Itsetesti käsittelee FM-moduloidun äänen kerran kokonaisena ja kerran
vaihtelevan kokoisina lohkoina (1–5000 näytettä, toistettava
näennäissatunnainen jono). Tulosten on oltava **bitilleen samat**,
ei vain lähellä toisiaan. Samat laskutoimitukset samassa järjestyksessä
antavat liukuluvuillakin saman tuloksen, ja pieninkin ero kertoo
tilan käsittelyn virheestä.

```{.cpp tiedosto="esimerkit/08-reaaliaika/main.cpp" osa="itsetesti"}
```

```{.tuloste tiedosto="esimerkit/08-reaaliaika.odotettu"}
```

## Putki: tallenteesta tai laitteesta

Tila `--suodin` lukee `cu8`-näytteitä vakiosyötteestä 64 kt:n
lohkoina ja kirjoittaa 32-bittiset liukuluvut vakiotulosteeseen.
Unix-putkessa ohjelman voi yhdistää suoraan laitteeseen. Esimerkiksi
`rtl_sdr` kirjoittaa näytteet vakiotulosteeseen, kun tiedostonimeksi
annetaan `-`.

```{.cpp tiedosto="esimerkit/08-reaaliaika/main.cpp" osa="suodin"}
```

```text
rtl_sdr -f 98000000 -s 912000 -g 20 - | ./ketju --suodin 200000 > mpx.f32
```

Komentoriviesimerkki on testaamaton, koska testiympäristössä ei ole
radiota. Putken etuna on, että laitteen luku, käsittely ja
tallennus ovat eri prosesseissa ja käyttöjärjestelmän putkipuskuri
tasaa hetkelliset viiveet. Jos käsittely on keskimäärin liian hidas,
puskuri täyttyy, `rtl_sdr` ei ehdi lukea USB-väylää ja laite hukkaa
näytteitä (*overrun*). Saman ohjelman sisällä sama rakenne tehdään
kahdella säikeellä ja niiden välisellä rengaspuskurilla.

## Vertailu Python-viitteeseen

C++-toteutus tarkistetaan Python-viitteellä, joka tekee saman
laskennan NumPyllä koko tallenteelle kerralla. Viitteessä on sama NCO-
taulukko, sama suodin (`scipy.signal.firwin` ja C++:n `alipaasto`
tuottavat saman Hamming-ikkunoidun sincin) ja sama ilmaisin:

```{.python tiedosto="esimerkit/vertailu/viite.py" osa="viite"}
```

Vertailuohjelma kääntää C++-ketjun, tekee testisignaalin ja syöttää
sen ohjelmalle putkella:

```{.python tiedosto="esimerkit/vertailu/main.py" osa="kaanna"}
```

```{.python tiedosto="esimerkit/vertailu/main.py" osa="syote"}
```

```{.python tiedosto="esimerkit/vertailu/main.py" osa="vertaa"}
```

```{.tuloste tiedosto="esimerkit/vertailu.odotettu"}
```

Tässä vertailu tehdään toleranssilla eikä bitilleen. NumPyn ja C++:n
summausjärjestys eroaa, ja C++ kirjoittaa 32-bittisiä liukulukuja.
Toleranssi $10^{-5}$ on kymmenkertainen 32-bittisen liukuluvun
tarkkuuteen nähden. Esimerkkien Makefile ajaa saman vertailun myös
Clangilla käännettynä:

```{.make tiedosto="esimerkit/Makefile" osa="clang"}
```

## Nopeus

Mittaustila käsittelee 2,3 sekunnin synteettisen signaalin
16 384 näytteen lohkoina ja raportoi läpäisyn:

```{.cpp tiedosto="esimerkit/08-reaaliaika/main.cpp" osa="mittaa"}
```

Kirjoittajan koneella `-O2`-käännös käsitteli noin 29 MS/s eli noin
30 kertaa reaaliaikaa nopeammin (`make mittaa`). Mittaus tehtiin
kuormitetulla virtuaalikoneella, ja tulos on suuntaa-antava.
Toteutus on tarkoituksella suoraviivainen. Nopeuttamiseen on useita
tunnettuja keinoja:

- **`float`-tyyppi.** 8-bittiselle datalle `double` on tarpeettoman
  tarkka. `float` puolittaa muistiliikenteen ja kaksinkertaistaa
  SIMD-leveyden.
- **Symmetria.** Lineaarivaiheisen suotimen kertoimet ovat
  symmetriset, ja $h[j]x[n-j] + h[N-1-j]x[n-N+1+j]$ laskee kaksi
  termiä yhdellä kertolaskulla.
- **Kaksivaiheinen desimointi** (luku 4) ja kevyt ensimmäinen vaihe.
- **SIMD ja kirjastot.** Kääntäjän automaattinen vektorointi
  (`-O3 -march=native`) tai valmiit kirjastot, kuten VOLK
  (GNU Radion vektorikirjasto) ja liquid-dsp.
- **Säikeet.** Kanavan valinta ja ilmaisu voivat olla eri säikeissä,
  ja polyfaasipankin kanavat voidaan jakaa ytimille.

Ennen optimointia kannattaa kuitenkin mitata. Jo suoraviivainen versio
on kertaluokkaa reaaliaikaa nopeampi.

## Käytännössä

- **Testaa lohkoinvarianssi bitilleen.** Käsittele sama data
  kokonaisena ja satunnaisina lohkoina ja vertaa tuloksia
  operaattorilla `==`. Tämä löytää tilan käsittelyn virheet, jotka
  muuten kuuluisivat vain satunnaisina napsahduksina.
- **Pidä Python-viite.** NumPy-versio on lyhyt ja helppo tarkistaa
  teoriaa vastaan. Nopea toteutus verrataan siihen toleranssilla.
- **Ei muistinvarauksia lohkosilmukassa.** Varaa puskurit kerran ja
  käytä `clear()`-kutsua, joka säilyttää kapasiteetin.
- **Käytä etumerkittömiä akkumulaattoreita.** Etumerkittömän luvun
  ylivuoto on määriteltyä. Sanitoija paljastaa etumerkillisen
  ylivuodon.
- **Mittaa läpäisy reaaliaikakertoimena.** "30 kertaa reaaliaika"
  kertoo suoraan, mahtuuko ketju laitteeseen, ja jättääkö se tilaa
  muulle käsittelylle.

## Itsearviointi

- Osaat toteuttaa tilallisen NCO:n, desimoivan FIR-suotimen ja
  FM-ilmaisimen, jotka toimivat mielivaltaisen kokoisilla lohkoilla.
- Osaat testata, että lohkokäsittely antaa bitilleen saman tuloksen
  kuin kertakäsittely, ja selittää, miksi se on mahdollista
  liukuluvuilla.
- Osaat verrata nopeaa toteutusta Python-viitteeseen perustellulla
  toleranssilla.
- Osaat yhdistää ohjelman laitteeseen putkella ja selittää
  ylivuodon (*overrun*) syyn ja estämisen.
- Osaat mitata läpäisyn ja luetella tavallisimmat
  optimointikeinot.
