# Lohkopohjainen reaaliaikakäsittely C:llä

Reaaliaikainen signaalinkäsittely on palvelu, jolla on takaraja.
Äänikortti pyytää 32 näytettä 0,67 millisekunnin välein, ja jos
käsittely ei ehdi, kuuluu napsahdus. Keskimääräinen nopeus ei riitä:
jokaisen lohkon on valmistuttava ajallaan. Tämä luku kokoaa aiempien
lukujen tekniikat reaaliaikasilmukaksi, jossa on kiinteän pilkun
käsittely, jonot keskeytysten ja käsittelyn välillä sekä laskettu
latenssi ja laskentabudjetti.

## Silmukan rakenne

Tyypillisessä sulautetussa järjestelmässä on kolme toimijaa:

1. **ADC-keskeytys** tai DMA kirjoittaa näytteitä sisääntulojonoon
   laitteen tahdissa.
2. **Käsittely** ottaa jonosta kiinteän kokoisen lohkon, käsittelee
   sen ja kirjoittaa tuloksen ulostulojonoon.
3. **DAC-keskeytys** lukee ulostulojonoa samassa tahdissa.

Jonojen ansiosta käsittelyn lohkokoon ei tarvitse olla sama kuin
laitteen lohkokoon. Ulostulojono esitäytetään ennen kuin DAC
käynnistetään, jotta ensimmäinen hidas lohko ei aiheuta alivuotoa.
Esitäyttö on suoraan latenssia.

Käsittelyfunktiolle on reaaliaikasääntöjä, joita tavallinen koodi ei
noudata:

| Sääntö | Syy |
|------------------------------|---------------------------------------------|
| ei muistinvarausta | `malloc` voi kestää arvaamattoman kauan tai epäonnistua |
| ei lukkoja | lukon haltija voi olla matalamman prioriteetin säie |
| ei I/O:ta eikä lokitusta | tiedostojärjestelmä ja konsoli estävät |
| rajattu silmukoiden pituus | pahin tapaus ratkaisee, ei keskiarvo |
| ei poikkeuksia eikä hidasta virhepolkua | virhetilanteenkin on oltava nopea |
| denormaalit pois päältä | lähes nollaan vaimenevat IIR-tilat voivat hidastaa satakertaisesti |

Viimeinen kohta koskee liukulukuja: kun IIR-suotimen tila vaimenee
hiljaisuudessa kohti nollaa, se päätyy denormaaleihin lukuihin, joita
monet prosessorit laskevat mikrokoodilla. Korjaus on asettaa
prosessorin *flush-to-zero*-tila tai lisätä tilaan hyvin pieni
vakio.

## Jono keskeytyksen ja käsittelyn välillä

Yhden tuottajan ja yhden kuluttajan rengasjono toimii ilman lukkoja.
Tuottaja kirjoittaa vain kirjoitusindeksiä ja kuluttaja vain
lukuindeksiä. Indeksit kasvavat vapaasti, ja täyttöaste on niiden
erotus, joten täysi ja tyhjä jono erotetaan ilman ylimääräistä paikkaa.

```{.c tiedosto="esimerkit/11-reaaliaika/jono.h" osa="jono"}
```

```{.c tiedosto="esimerkit/11-reaaliaika/jono.c" osa="kirjoita"}
```

Atomiset operaatiot muistijärjestyksineen takaavat, että kuluttaja ei
näe uutta indeksiä ennen kuin data on kirjoitettu. Yksiytimisessä
mikrokontrollerissa kääntäjä saisi muuten järjestää kirjoitukset
uudelleen. Moniytimisessä järjestelmässä myös prosessori tekee niin.
Muistijärjestykset käsitellään tarkemmin taidossa
*Rinnakkaisohjelmointi*.

## Kiinteän pilkun käsittelijä

Käsittelijä on Q1.15-muotoinen FIR-suodin, jonka perässä on vahvistus.
Kertoimet ja näytteet ovat 16-bittisiä. Tulot kerätään 64-bittiseen
kertymään, joten välisumma ei voi ylivuotaa. Lopuksi tulos
pyöristetään ja saturoidaan 16 bittiin. Q-formaatit, pyöristys ja
saturaatio esitellään taidossa *Lukujen esitys ja kiinteän pilkun
aritmetiikka*. Suodin on sama 15 kertoimen alipäästö kuin siellä.

```{.c tiedosto="esimerkit/11-reaaliaika/q15.h" osa="q15"}
```

```{.c tiedosto="esimerkit/11-reaaliaika/prosessori.h" osa="tyyppi"}
```

```{.c tiedosto="esimerkit/11-reaaliaika/prosessori.c" osa="lohko"}
```

Saturaatiot lasketaan. Saturaatio on parempi kuin kiertävä ylivuoto,
koska se tuottaa särön eikä täyden asteikon hyppyä. Silti se on
virhetilanne, josta järjestelmän on kerrottava, eikä sitä saa piilottaa.
Laskuria voi lukea valvontasäikeestä ja näyttää käyttäjälle
leikkautumisen ilmaisimena.

## Simulointi ja testaus

Reaaliaikasilmukka testataan simuloimalla keskeytykset tavallisessa
ohjelmassa. ADC tuottaa 48 näytettä millisekunnissa, käsittely toimii
32 näytteen lohkoissa, ja DAC käynnistyy, kun ulostulojonossa on
64 näytettä.

```{.c tiedosto="esimerkit/11-reaaliaika/main.c" osa="silmukka"}
```

Tärkein testi on sama kuin luvussa 5: lohkoittain käsitelty ulostulo on
bitilleen sama kuin koko signaali yhdellä kutsulla, kun latenssi
otetaan huomioon. Kiinteässä pilkussa vertailu on täsmällinen.

```{.c tiedosto="esimerkit/11-reaaliaika/main.c" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/11-reaaliaika.odotettu"}
```

Vertailuohjelma ajaa saman käsittelijän ctypesilla ja vertaa sitä
bitilleen kokonaislukumalliin, joka on kirjoitettu NumPylla.
Testiin kuuluvat myös saturaatioiden määrät:

```{.python tiedosto="esimerkit/vertailu/mallit.py" osa="q15"}
```

```{.python tiedosto="esimerkit/vertailu/test_vertailu.py" osa="q15"}
```

## Latenssi ja budjetti

Järjestelmän kokonaislatenssi on summa:

| Osa | Tässä | Huomio |
|-------------------------|--------------------|----------------------------------------|
| ADC:n ja DAC:n omat suotimet | (laite) | sigma–delta-muuntimissa usein 0,5–1 ms |
| esitäyttö ja lohkot | 48 näytettä | käsittelyn lohko ja jonojen marginaali |
| suotimen ryhmäviive | 7 näytettä | lineaarivaiheinen FIR: $(N-1)/2$ |
| yhteensä | 55 näytettä = 1,15 ms | 48 kHz:llä |

Pienempi lohko pienentää latenssia mutta kasvattaa lohkokohtaista
kuormaa (funktiokutsut, välimuistin lämpeneminen, keskeytykset).
Musiikkisovelluksissa yli 10 ms:n latenssi tuntuu soittajasta
viiveeltä, puheessa yli 150 ms häiritsee keskustelua, ja
aktiivisessa melunvaimennuksessa jo 100 µs voi olla liikaa.

**Laskentabudjetti** lasketaan kertolasku–yhteenlaskuina (MAC):
15 kertoimen suodin 48 kHz:llä on 0,72 miljoonaa MAC:ia sekunnissa.
Prosessori, joka tekee 100 miljoonaa MAC:ia sekunnissa, käyttää siihen
0,7 % ajastaan. Budjetti tarkistetaan pahimman tapauksen mukaan, ja
siihen lisätään marginaali keskeytyksille ja muille tehtäville.
Todellinen aika mitataan laitteessa syklilaskurilla, ja tulosta
verrataan aikarajaan, tässä 0,667 ms lohkoa kohti.

## Käytännössä

- **Erota laite ja käsittely jonoilla.** Silloin lohkokoot voivat erota,
  ja hetkellinen viive ei kaada järjestelmää.
- **Älä varaa muistia, lukitse tai tulosta käsittelyfunktiossa.** Kaikki
  muisti alustetaan ennen käynnistystä.
- **Laske ja raportoi saturaatiot, alivuodot ja ylivuodot.** Hiljainen
  virhe reaaliaikajärjestelmässä löytyy vasta kentältä.
- **Testaa lohkoittain ja kerralla bitilleen** ja vertaa kiinteän pilkun
  toteutusta bittitarkkaan malliin.
- **Laske latenssi ja budjetti** ennen toteutusta ja mittaa ne
  laitteessa pahimman tapauksen mukaan.

## Itsearviointi

- Osaat suunnitella reaaliaikasilmukan, jossa ADC, käsittely ja DAC
  kommunikoivat jonoilla, ja laskea sen latenssin.
- Osaat toteuttaa lukottoman yhden tuottajan ja kuluttajan rengasjonon
  ja perustella muistijärjestykset.
- Osaat toteuttaa Q1.15-käsittelijän, jossa on leveä kertymä,
  pyöristys, saturaatio ja saturaatioiden laskenta.
- Osaat testata lohkokäsittelyn bitilleen ja laskea laskentabudjetin
  MAC-operaatioina.
