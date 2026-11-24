# Testaus isäntäkoneella

Kohdelaitteessa testaaminen on hidasta: käännös, ohjelmointi,
käynnistys ja tulosteen lukeminen sarjaportista vievät kymmeniä
sekunteja, eikä sanitoijia tai Valgrindia ole. Siksi RTOS-ohjelman
logiikka kannattaa testata myös isäntäkoneella. FreeRTOSissa tähän on
POSIX-portti (aiemmin Linux-simulaattori) ja Windows-portti: ydin
kääntyy tavalliseksi ohjelmaksi, ja tehtävät ovat käyttöjärjestelmän
säikeitä. Sama sovelluskoodi ajetaan näin sekä isännällä että
laitteessa.

## Kiden isäntäportti

Kiden isäntäportti toteuttaa luvun 4 porttirajapinnan Linuxilla. Siinä
on kaksi ratkaisua, jotka erottavat sen FreeRTOSin POSIX-portista.

**Tehtävät ovat ucontext-konteksteja, eivät säikeitä.** Jokaisella
tehtävällä on oma pinonsa, ja tehtävänvaihto on yksi `swapcontext`-
kutsu. Ohjelmassa on vain yksi käyttöjärjestelmän säie, joten
kilpailutilanteita isäntäkoneen tasolla ei ole. FreeRTOSin POSIX-portti
käyttää säikeitä ja signaaleja, ja sen ajo riippuu isäntäkoneen
vuorontajasta.

**Tikki on simuloitu.** Ajastinta ei ole. Aika etenee vain, kun tehtävä
kuluttaa laskenta-aikaa (`kide_kuormita`) tai kun idle-tehtävä odottaa,
jolloin aika hyppää suoraan seuraavaan tikkiin. Ajo on täysin
deterministinen ja niin nopea kuin kone sallii. Sama ajatus on QEMU:n
`-icount`-tilassa: aika on ohjelman funktio, ei seinäkellon.

```{.c tiedosto="esimerkit/isanta/portti_isanta.c" osa="tila"}
```

```{.c tiedosto="esimerkit/isanta/portti_isanta.c" osa="vaihto"}
```

```{.c tiedosto="esimerkit/isanta/portti_isanta.c" osa="kuormita"}
```

Muuttuja `vaihto_odottaa` vastaa PendSV:n odotustilaa. Jos vaihtoa
pyydetään kriittisessä osiossa tai simuloidussa tikkikeskeytyksessä,
se tehdään vasta, kun osio tai tikki päättyy, aivan kuten
Cortex-M3:lla. Ytimen loppuosa ei tiedä, kumpi portti on käytössä.

Isäntäportin rajat ovat yhtä tärkeitä kuin sen hyödyt:

- **Laitteistoa ei ole.** Esimerkit, jotka käyttävät NVIC:tä, UART:ia
  tai pinon rekistereitä (luvut 4–6 ja 10), ajetaan vain QEMU:ssa.
- **Keskeytykset tulevat vain tikkeinä.** Tehtävä voi vaihtua vain
  ytimen kutsussa tai `kide_kuormita`n sisällä. Laitteessa
  keskeytys voi tulla minkä tahansa kahden käskyn välissä. Isäntäportti
  ei siksi löydä kilpailutilanteita, jotka syntyvät puuttuvasta
  kriittisestä osiosta.
- **Ajoitus on mallin aikaa.** Tulos kertoo, toimiiko logiikka
  oletetuilla laskenta-ajoilla, ei sitä, ovatko oletukset oikeat.
- **Pinot ovat isäntäkoneen pinoja.** Portti varaa jokaiselle
  tehtävälle 256 KiB:n pinon, koska isäntäkoneen kirjastot tarvitsevat
  enemmän kuin Cortex-M:n tehtävän pino. Pinon mittaukset ja
  ylivuototarkistukset eivät kerro isännällä mitään.

## Sama ohjelma kahdessa paikassa

Esimerkkien Makefile kääntää laitteistoa käyttämättömät esimerkit
myös isäntäkoneelle AddressSanitizerin ja UBSanin kanssa ja vertaa
tulosteen *samaan* odotettuun tiedostoon kuin QEMU-ajon. Jos ne
eroavat, joko ytimen porttiriippumaton osa käyttäytyy eri tavalla
kahdella prosessorilla (esimerkiksi tyyppien koko tai etumerkki) tai
toinen porteista on väärin.

```{.make tiedosto="esimerkit/Makefile" osa="isanta"}
```

```{.make tiedosto="esimerkit/Makefile" osa="rakennus"}
```

Muunnelmat, kuten `13-inversio-mutex`, käännetään samoista lähteistä
eri valitsimilla. AddressSanitizer varoittaa ucontext-pinonvaihdoista,
koska se ei tunne niitä täysin. Varoitukset ohjataan omaan
tiedostoonsa, ja ne näytetään vain, jos vertailu epäonnistuu.
Sanitoija löytää isännällä virheet, jotka laitteessa näkyisivät vasta
satunnaisena kaatumisena: ylivuodot jonon kopioinnissa, kohdistamaton
osoitin poolissa ja etumerkillisen kokonaisluvun ylivuodon
tikkilaskennassa.

## Mitä testataan missä

| Taso | Mitä testataan | Väline |
|----------|------------------------|--------------|
| yksikkötesti isännällä | tilakoneet, jäsentimet, algoritmit ilman RTOSia | tavallinen testikehys, sanitoijat |
| isäntäportti | tehtävien yhteistyö, jonot, aikarajat, virhepolut | POSIX- tai Kiden isäntäportti |
| emulaattori | portti, keskeytykset, käynnistys, ajurit emuloituja laitteita vasten | QEMU, Renode |
| kohdelaite | todelliset ajoitukset, laitteet, virrankulutus | kehityskortti, logiikka-analysaattori |
| HIL | koko järjestelmä simuloitua ympäristöä vasten | *hardware-in-the-loop* -testipenkki |

Jokainen taso löytää virheitä, joita edellinen ei löydä, mutta on
hitaampi ja kalliimpi. Siksi mahdollisimman suuri osa testeistä
kirjoitetaan alimmille tasoille, ja ylemmät tasot keskittyvät siihen,
mitä vain ne voivat testata.

## Käytännössä

- **Erota laitteisto ohuen rajapinnan taakse.** Kun ajuri ja logiikka
  ovat eri tiedostoissa, logiikan voi kääntää isännälle ja ajurin tilalle
  voi kirjoittaa testiversion.
- **Tee aika testattavaksi.** Lue aika ytimestä (`xTaskGetTickCount`),
  älä laitteistoajastimesta, niin testi voi ajaa sitä eteenpäin.
- **Aja samat testit isännällä ja emulaattorissa.** Sama odotettu
  tuloste kahdella portilla on vahva todiste siitä, että porttiriippumaton
  koodi on oikein.
- **Älä luota isäntäporttiin kilpailutilanteissa.** Puuttuvat kriittiset
  osiot löytyvät katselmoinnilla, staattisella analyysillä ja
  kuormitustesteillä kohdelaitteessa.
- **Tee emulaattoriajosta deterministinen**, jos testi vertaa
  ajoitusta: QEMU:n `-icount` tai Renoden virtuaaliaika.

## Itsearviointi

- Osaat kertoa, miten Kiden isäntäportti toteuttaa tehtävänvaihdon ja
  ajan, ja miten se eroaa FreeRTOSin POSIX-portista.
- Osaat luetella, mitä isäntäportti ei voi testata.
- Osaat jakaa RTOS-ohjelman testit isäntäkoneen, emulaattorin,
  kohdelaitteen ja HIL-tason kesken.
- Osaat rakentaa saman ohjelman kahdelle portille ja vertailla
  tulosteita.
