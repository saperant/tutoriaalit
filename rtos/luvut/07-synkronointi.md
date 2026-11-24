# Semaforit, tapahtumaryhmät ja ilmoitukset

Jono välittää dataa. Usein välitettävää on kuitenkin vain tieto siitä,
että jotain on tapahtunut: näyte on valmis, resurssi vapautui tai
alustus on tehty. Siihen RTOSissa on kolme kevyempää välinettä:
semafori laskee tapahtumia tai resursseja, tapahtumaryhmä yhdistää
useita ehtoja, ja tehtäväilmoitus on kevyin herätys yhdelle tehtävälle.
Taidossa *Käyttöjärjestelmät* semafori ja ehtomuuttuja käsiteltiin
säikeiden välineinä. Tässä painopiste on siinä, mitä kukin maksaa ja
mihin se sopii keskeytyksen ja tehtävän välissä.

## Semaforit

Kide toteuttaa semaforit kuten FreeRTOS: semafori on jono, jonka
alkion koko on 0. Jäljelle jää laskuri (`maara`) ja kaksi
odotuslistaa. `xSemaphoreTake` on vastaanotto ilman dataa ja
`xSemaphoreGive` lähetys.

```{.c tiedosto="esimerkit/kide/jono.c" osa="luonti"}
```

**Binäärisemafori** on jono, johon mahtuu yksi alkio. Se alkaa
tyhjänä, ja sen tavallisin käyttö on luvun 5 merkinanto: keskeytys
antaa, tehtävä ottaa. Jos keskeytys antaa kahdesti ennen kuin tehtävä
ehtii ottaa, toinen anto katoaa, koska semafori on jo täynnä. Silloin
tehtävän on käsiteltävä kaikki valmiina oleva data kerralla, esimerkiksi
lukemalla laitteen FIFO tyhjäksi.

**Laskeva semafori** laskee joko tapahtumia (keskeytys antaa
jokaisesta, tehtävä ottaa yhden kerrallaan, eikä yksikään katoa) tai
resursseja (laskuri alkaa resurssien määrästä, ja jokainen käyttäjä
ottaa yhden ja palauttaa sen). Esimerkissä on kaksi tulostinta ja neljä
tehtävää, jotka pyytävät niitä eri aikoina:

```{.c tiedosto="esimerkit/10-semafori/main.c" osa="tulostus"}
```

```{.tuloste tiedosto="esimerkit/testit/10-semafori.odotettu"}
```

T1 ja T2 saavat tulostimet hetkellä 1. T3 alkaa odottaa hetkellä 2 ja
T4 hetkellä 3. Kun T1 vapauttaa tulostimen hetkellä 5, sen saa T4,
vaikka T3 on odottanut kauemmin, koska odotuslista on järjestetty
prioriteetin mukaan. T4 on T1:tä tärkeämpi ja ajaa heti, joten sen
"tulostaa" näkyy ennen T1:n "vapautti"-riviä. Laskeva semafori kertoo
vain, *montako* resurssia on vapaana, ei *mikä*. Siksi sen kanssa
tarvitaan usein vapaalista tai muu kirjanpito, kuten luvun 10
muistipoolissa.

## Tapahtumaryhmät

Tapahtumaryhmä on bittikenttä, jonka bittejä tehtävät ja keskeytykset
asettavat. Tehtävä voi odottaa, että *kaikki* annetut bitit ovat
asetettuina (alustuksen synkronointi) tai että *mikä tahansa* niistä
on (useasta lähteestä tuleva hälytys). Halutessaan se nollaa
odottamansa bitit herätessään.

```{.c tiedosto="esimerkit/11-tapahtumat/main.c" osa="bitit"}
```

```{.c tiedosto="esimerkit/11-tapahtumat/main.c" osa="alijarjestelma"}
```

```{.c tiedosto="esimerkit/11-tapahtumat/main.c" osa="sovellus"}
```

```{.c tiedosto="esimerkit/11-tapahtumat/main.c" osa="halytys"}
```

```{.tuloste tiedosto="esimerkit/testit/11-tapahtumat.odotettu"}
```

Sovellus käynnistyy vasta, kun viimeinen alijärjestelmä on valmis.
Hälytystehtävä aikakatkaistaan ensin, koska hälytyksiä ei tule
kymmeneen tikkiin. Toisella kierroksella se saa painikkeen ja
kolmannella molemmat bitit kerralla. Lopuksi hälytysbitit ovat
nollautuneet, mutta alustusbitit ovat yhä asetettuina, koska sovellus
ei pyytänyt niiden nollausta.

Bittien asettaminen herättää kaikki tehtävät, joiden ehto täyttyy, ei
vain tärkeintä. Siksi asetus käy odottajat läpi, ja sen kesto riippuu
odottajien määrästä. FreeRTOS ei tästä syystä aseta bittejä
keskeytyksessä vaan välittää pyynnön `xEventGroupSetBitsFromISR`illä
ajastinpalvelun tehtävälle, joka asettaa ne.

```{.c tiedosto="esimerkit/kide/tapahtumat.c" osa="aseta"}
```


## Tehtäväilmoitukset

Jokaisessa TCB:ssä on 32-bittinen ilmoitusarvo. `xTaskNotifyGive`
kasvattaa sitä ja herättää tehtävän, jos se odottaa ilmoitusta.
`ulTaskNotifyTake` odottaa, kunnes arvo on nollaa suurempi, ja
palauttaa sen. Parametri `tyhjenna` valitsee, nollataanko arvo
(binäärisemaforin tapaan) vai vähennetäänkö sitä yhdellä (laskevan
semaforin tapaan).

```{.c tiedosto="esimerkit/kide/tehtava.c" osa="ilmoitus"}
```

```{.c tiedosto="esimerkit/12-ilmoitus/main.c" osa="vastaanottaja"}
```

```{.c tiedosto="esimerkit/12-ilmoitus/main.c" osa="lahettaja"}
```

```{.tuloste tiedosto="esimerkit/testit/12-ilmoitus.odotettu"}
```

Ilmoitus ei tarvitse omaa oliota eikä odotuslistaa, koska odottajia on
aina yksi: ilmoitusarvon omistava tehtävä. Siksi se on nopein ja
pienin tapa herättää tehtävä. FreeRTOSin mukaan ilmoitus on jopa 45 %
nopeampi kuin binäärisemafori ja vie vähemmän RAMia. Rajoitukset
seuraavat samasta: vain yksi tehtävä voi odottaa, lähettäjän on
tiedettävä vastaanottajan kahva, eikä arvoa voi lähettää jonon tapaan
puskuroituna. FreeRTOSissa ilmoitusarvoa voi myös käyttää
bittikenttänä (`xTaskNotify` ja `eSetBits`) tai 32-bittisenä viestinä.

## Valinta

| Tarve | Väline | Huomio |
|--------------------|------------------|--------------|
| data tehtävältä toiselle | jono | kopioi, puskuroi |
| keskeytys herättää yhden tehtävän | tehtäväilmoitus | kevyin |
| tapahtumia laskettava | laskeva semafori tai ilmoitus (`pdFALSE`) | ei katoa |
| resurssien määrä | laskeva semafori | ei kerro, mikä resurssi |
| useita ehtoja tai useita odottajia | tapahtumaryhmä | herättää kaikki |
| yhteinen resurssi | mutex | luku 8 |

## Käytännössä

- **Aloita ilmoituksesta**, kun yksi keskeytys tai tehtävä herättää
  yhden tehtävän. Käytä semaforia, kun odottajia voi olla useita tai
  kahvaa ei tunneta.
- **Älä suojaa yhteistä dataa binäärisemaforilla.** Se toimii, mutta
  siltä puuttuu omistaja ja prioriteetin periytys (luku 8).
- **Muista, että binäärisemafori hukkaa kertoja.** Jos tapahtumia voi
  tulla useampi kuin tehtävä ehtii käsitellä, käytä laskevaa
  semaforia tai lue kaikki data kerralla.
- **Käytä tapahtumaryhmää käynnistyksen synkronointiin.** Se tekee
  riippuvuuksista näkyviä, ja aikaraja kertoo, mikä alijärjestelmä ei
  käynnistynyt.
- **Varo tapahtumaryhmää keskeytyksessä.** Sen asetus voi herättää
  monta tehtävää, joten keskeytyksestä se kannattaa tehdä
  viivästettynä.

## Itsearviointi

- Osaat kertoa, miksi semafori voidaan toteuttaa jonona ja mitä
  binääri- ja laskevan semaforin ero merkitsee keskeytyksen kanssa.
- Osaat suojata joukon samanlaisia resursseja laskevalla semaforilla
  ja selittää palvelujärjestyksen.
- Osaat odottaa useaa ehtoa tapahtumaryhmällä joko kaikki- tai mikä
  tahansa -ehdolla.
- Osaat käyttää tehtäväilmoitusta binääri- tai laskevan semaforin
  korvikkeena ja tunnet sen rajoitukset.
