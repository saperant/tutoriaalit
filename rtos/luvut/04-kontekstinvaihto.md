# Kontekstinvaihto

Tehtävän *konteksti* on kaikki, mitä sen jatkaminen vaatii:
rekisterit r0–r12, ohjelmalaskuri, paluuosoite, tilarekisteri xPSR ja
pino. Kontekstinvaihto tallentaa nykyisen tehtävän kontekstin ja
palauttaa toisen. Koska jokaisella tehtävällä on oma pinonsa, riittää
tallentaa rekisterit pinoon ja muistaa pino-osoitin TCB:ssä. Tämä luku
käy läpi Kiden Cortex-M3-portin, joka on noin 170 riviä ja sisältää
ytimen ainoat assemblyrivit.

## Kaksi pinoa

Cortex-M:ssä on kaksi pino-osoitinta (taito *Mikrokontrollerit*,
luku 2): pääpino MSP, jota käytetään resetin jälkeen ja aina
keskeytyksissä, sekä prosessipino PSP, jota Thread-tila käyttää, kun
CONTROL-rekisterin SPSEL-bitti on 1. RTOS antaa jokaiselle tehtävälle
oman PSP-pinon. Kun keskeytys tulee tehtävän aikana, laitteisto
tallentaa kehyksen tehtävän pinoon, mutta käsittelijä itse ja
sisäkkäiset keskeytykset käyttävät yhteistä MSP-pinoa. Tehtävän pinoon
on siis varattava tilaa yhdelle kehykselle, ei keskeytysten
sisäkkäisyydelle.

Esimerkki `05-konteksti` lukee rekisterit `CONTROL`, `IPSR`, MSP ja PSP
ja näyttää tilan kolmessa paikassa (tuloste on seuraavassa
osiossa): `main` ajaa ennen
vuorontajan käynnistystä MSP:llä, tehtävä PSP:llä (CONTROL = 2), ja
keskeytys taas MSP:llä. Keskeytyksen paluuosoite LR on EXC_RETURN-arvo
`0xFFFFFFFD`, joka käskee prosessoria palaamaan Thread-tilaan ja
lukemaan kehyksen PSP-pinosta.

## Kehys

Kun keskeytys tulee, prosessori tallentaa itse kahdeksan sanaa
keskeytetyn koodin pinoon: r0–r3, r12, lr, pc ja xPSR. Nämä ovat
AAPCS-kutsukäytännön mukaan kutsujan tallennettavat rekisterit, joten
käsittelijä voi olla tavallinen C-funktio. Rekisterit r4–r11 ovat
kutsutun tallennettavia: C-funktio palauttaa ne ennalleen, joten
keskeytyksestä palatessa niiden arvot ovat ennallaan. Kontekstinvaihto
kuitenkin vaihtaa tehtävää kesken kaiken, joten sen on tallennettava
myös r4–r11. PendSV-käsittelijä tekee sen ohjelmallisesti samaan
pinoon. Tehtävän pinoon jää siis 16 sanan kehys, ja TCB:n pino-osoitin
osoittaa sen alkuun.

Uudelle tehtävälle kehys rakennetaan valmiiksi, aivan kuin tehtävä
olisi keskeytetty juuri ennen ensimmäistä käskyään. PC osoittaa
tehtäväfunktioon, r0 on sen parametri, ja LR on funktio, johon
tehtävä päätyisi, jos funktio palaisi. xPSR:n bitti 24 on Thumb-bitti,
jonka on oltava 1, tai ensimmäinen käsky aiheuttaa UsageFaultin. Muut
rekisterit täytetään tunnistettavilla arvoilla, jotta ne erottuvat
muistivedoksessa.

```{.c tiedosto="esimerkit/kide/portti_cm3.c" osa="kehys"}
```

```{.tuloste tiedosto="esimerkit/testit/05-konteksti.odotettu"}
```

## PendSV

Kontekstinvaihto tehdään PendSV-poikkeuksessa. Ohjelma laukaisee sen
kirjoittamalla ICSR-rekisterin bitin PENDSVSET, ja sen prioriteetti on
heikoin mahdollinen. Valinnalla on kaksi seurausta. Ensinnäkin vaihto
ei koskaan keskeytä keskeytyskäsittelijää: jos SysTick tai UART-
käsittelijä pyytää vaihtoa, PendSV ajetaan vasta, kun kaikki
käsittelijät ovat valmiita, ja prosessori ketjuttaa sen suoraan
viimeisen perään (*tail-chaining*). Toiseksi useampi pyyntö samassa
keskeytysketjussa yhdistyy yhdeksi vaihdoksi.

```{.c tiedosto="esimerkit/kide/portti_cm3.c" osa="pendsv"}
```

Käsittelijä on `naked`: kääntäjä ei lisää siihen omaa alku- tai
loppukoodia, joka koskisi pinoon. Vaiheet ovat:

1. Lue keskeytetyn tehtävän PSP. Laitteisto on jo tallentanut sinne
   kahdeksan rekisteriä.
2. Tallenna r4–r11 samaan pinoon ja pino-osoitin TCB:hen
   (`kide_nykyinen->pino_osoitin`, TCB:n ensimmäinen kenttä).
3. Nosta BASEPRI ja kutsu C-funktiota `kide_valitse_seuraava`, joka
   tarkistaa pinon ja vaihtaa muuttujan `kide_nykyinen`.
4. Lue uuden tehtävän pino-osoitin, palauta sen r4–r11 ja aseta PSP.
5. Palaa poikkeuksesta. Laitteisto purkaa loput kahdeksan sanaa uuden
   tehtävän pinosta, ja suoritus jatkuu siitä, mihin se jäi, tai
   ensimmäisestä käskystä.

LR tallennetaan MSP-pinoon C-kutsun ajaksi, koska `bl` ylikirjoittaa
sen ja vaihdon lopussa tarvitaan EXC_RETURN-arvo. Vaihto vie
Cortex-M3:lla noin 12 jaksoa sisäänmenoon, 30–40 käskyä
käsittelijässä ja 12 jaksoa paluuseen: 25 MHz:n kellolla muutaman
mikrosekunnin. Liukulukuyksiköllä varustetussa Cortex-M4F:ssä tai
M7:ssä on tallennettava myös s16–s31, ja laitteisto käyttää laiskaa
tallennusta (*lazy stacking*): liukulukurekisterit tallennetaan vain,
jos tehtävä on käyttänyt niitä. EXC_RETURN-arvon bitti 4 kertoo sen,
ja FreeRTOSin M4F-portti tarkistaa bitin.

## Ensimmäinen tehtävä ja tikki

Ensimmäinen tehtävä käynnistetään samalla tavalla kuin mikä tahansa
muu: palaamalla poikkeuksesta sen pinoon rakennetun kehyksen kautta.
`portti_kaynnista` asettaa PendSV:n ja SysTickin prioriteetit,
käynnistää tikin ja suorittaa SVC-käskyn. SVC-käsittelijä palauttaa
r4–r11, asettaa PSP:n ja muuttaa EXC_RETURN-arvon Thread-tilaan ja
PSP:hen (`orr lr, lr, #0xd`, `0xFFFFFFF9` → `0xFFFFFFFD`).

```{.c tiedosto="esimerkit/kide/portti_cm3.c" osa="kaynnistys"}
```

```{.c tiedosto="esimerkit/kide/portti_cm3.c" osa="svc"}
```

SysTick-käsittelijä peittää ytimen keskeytykset BASEPRI:llä, käsittelee
tikin ja pyytää tarvittaessa vaihtoa. Vaihto tapahtuu, kun käsittelijä
päättyy.

```{.c tiedosto="esimerkit/kide/portti_cm3.c" osa="systick"}
```

## Vuoron luovutus

`taskYIELD` antaa vuoron saman prioriteetin seuraavalle tehtävälle:
nykyinen siirtyy valmislistansa perälle, ja PendSV laukaistaan.
Esimerkin `ping` ja `pong` vuorottelevat näin. Kumpikin tulee valituksi
neljästi: kerran alussa ja kolmesti luovutuksen jälkeen.

```{.c tiedosto="esimerkit/05-konteksti/main.c" osa="vuorottelu"}
```

Jos tehtävä luovuttaa vuoron kriittisessä osiossa, BASEPRI peittää
PendSV:n, ja vaihto tapahtuu vasta, kun osio päättyy. Ydin käyttää tätä
hyväkseen. Kun tehtävä jää odottamaan, ydin siirtää sen odotuslistaan
ja pyytää vaihtoa kriittisen osion sisällä, ja vaihto tapahtuu
osion lopussa ilman erillistä tarkistusta.

## Portin rajapinta

Kaikki prosessorista riippuva on porttikerroksen takana. Kun ydin
siirretään toiselle prosessorille, kirjoitetaan uusi portti, ja muu
ydin pysyy ennallaan. Luvun 11 isäntäportti toteuttaa saman rajapinnan
Linuxilla.

```{.c tiedosto="esimerkit/kide/portti.h" osa="rajapinta"}
```

## Käytännössä

- **Anna PendSV:lle ja SysTickille heikoin prioriteetti.** Jos PendSV
  olisi kiireellisempi kuin jokin keskeytys, se voisi vaihtaa tehtävää
  kesken keskeytyskäsittelijän. FreeRTOS-portit tarkistavat tämän.
- **Älä käytä MSP-pinoa tehtävissä.** Tehtävät ajavat PSP:llä, ja MSP:n
  koko mitoitetaan keskeytysten sisäkkäisyyden mukaan
  (linkkeriskriptin `PINON_KOKO`).
- **Ota liukulukujen laiska tallennus huomioon.** M4F:ssä kehys kasvaa
  34 sanalla (laitteiston 18 ja PendSV:n 16), kun tehtävä käyttää
  liukulukuja, ja keskeytyksen viive kasvaa, jos rekisterit pitää
  tallentaa.
- **Lue portti, kun vaihdat piiriä.** Valmistajan SDK:n FreeRTOS-
  portti voi olla eri versio kuin virallinen, ja sen asetukset
  (BASEPRI, prioriteettibittien määrä) on tarkistettava.

## Itsearviointi

- Osaat piirtää tehtävän pinon 16 sanan kehyksen ja kertoa, kumpi osa
  tallennetaan laitteistolla ja kumpi ohjelmallisesti.
- Osaat selittää PendSV:n vaiheet ja sen, miksi sen prioriteetti on
  heikoin.
- Osaat rakentaa uudelle tehtävälle alkukehyksen ja kertoa, miksi
  xPSR:n Thumb-bitti on asetettava.
- Osaat kertoa, mitä EXC_RETURN-arvot `0xFFFFFFF9` ja `0xFFFFFFFD`
  tarkoittavat.
- Osaat selittää, miksi tehtävänvaihto kriittisessä osiossa siirtyy
  osion loppuun.
