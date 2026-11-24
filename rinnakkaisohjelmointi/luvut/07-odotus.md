# Ehtomuuttujat ja muut odotusvälineet

Lukko suojaa dataa, mutta säikeet tarvitsevat myös tavan odottaa: jonoon
tulevaa työtä, vapautuvaa tilaa, muiden säikeiden valmistumista tai
rajallista resurssia. Tämä luku käy läpi ehtomuuttujan tarkasti sekä
C++20:n uudet odotusvälineet `std::latch`, `std::barrier` ja
`std::counting_semaphore` ja kertaalustuksen.

## Ehtomuuttuja

Ehtomuuttuja yhdistää lukon ja odotuksen. `wait(lukko, ehto)` tekee
seuraavan atomisesti:

1. Jos ehto on tosi, palaa heti lukko otettuna.
2. Muuten vapauttaa lukon ja nukahtaa *samalla* operaatiolla, joten
   herätys ei voi mennä ohi lukon vapautuksen ja nukahtamisen välissä.
3. Herättyään ottaa lukon ja tarkistaa ehdon uudelleen.

Ehdon tarkistus silmukassa on välttämätön kahdesta syystä. Odotus voi
palata ilman herätystä (*spurious wakeup*), ja herätyksen ja lukon oton
välissä toinen säie on voinut jo kuluttaa sen, minkä vuoksi herätettiin.
Predikaatin ottava `wait` tekee silmukan valmiiksi. Ilman predikaattia
syntyy myös **kadonnut herätys** (*lost wakeup*): jos ilmoitus tulee
ennen kuin odottaja ehtii odottamaan, se nukkuu ikuisesti. Predikaatti
tarkistetaan lukon alla ennen nukahtamista, joten ilmoitettu tila ei
katoa.

## Rajattu jono ja vastapaine

*Moderni C++* toteutti rajoittamattoman suljettavan työjonon. Jos tuottaja
on kuluttajaa nopeampi, rajoittamaton jono kasvaa, kunnes muisti loppuu.
**Rajattu jono** pysäyttää tuottajan, kun jono on täynnä. Tämä on
**vastapaine** (*backpressure*): hidas kuluttaja hidastaa tuottajaa eikä
ohjelmaa kaada. Kaksi ehtomuuttujaa erottaa odotukset toisistaan:

```{.cpp tiedosto="esimerkit/07-rajattu-jono.cpp" osa="jono"}
```

```{.cpp tiedosto="esimerkit/07-rajattu-jono.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-rajattu-jono.odotettu"}
```

- `notify_one` riittää, kun mikä tahansa yksi odottaja kelpaa ja jokainen
  herätys vastaa yhtä muutosta. `notify_all` tarvitaan sulkemisessa,
  koska kaikkien odottajien on huomattava se.
- Ilmoitus annetaan lukon vapauttamisen jälkeen. Lukon alla annettu
  ilmoitus on yhtä oikea mutta herättää säikeen odottamaan lukkoa.
- Sulkeminen on osa jonon rajapintaa. Ilman sitä kuluttaja ei tiedä,
  tuleeko töitä vielä, ja lopetus vaatisi erillisen lipun tai
  "myrkkypillerin" jokaiselle kuluttajalle.

## Este: vaiheittainen laskenta

`std::barrier` pysäyttää säikeet, kunnes kaikki ovat saapuneet, ja
päästää ne sitten seuraavaan vaiheeseen. Este on uudelleenkäytettävä, ja
sille voi antaa **valmistumisfunktion**, jonka yksi säie ajaa vaiheen
lopussa ennen kuin kukaan jatkaa. Lämmön tasoittuminen sauvassa on
tyypillinen vaiheittainen laskenta: jokainen askel lukee edellisen askeleen
taulukkoa ja kirjoittaa uuteen.

```{.cpp tiedosto="esimerkit/07-vaiheet.cpp" osa="rinnakkainen"}
```

```{.cpp tiedosto="esimerkit/07-vaiheet.cpp" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/07-vaiheet.odotettu"}
```

Rinnakkainen tulos on bitilleen sama kuin sarjallinen, koska jokainen
piste lasketaan samoista luvuista samassa järjestyksessä; rinnakkaisuus
vain jakaa pisteet säikeille. Valmistumisfunktio vaihtaa puskurit
turvallisesti, sillä sen aikana kukaan ei lue niitä. Este synkronoi:
vaiheen kirjoitukset tapahtuvat ennen seuraavan vaiheen lukuja.

`std::latch` on kertakäyttöinen laskuri: `count_down` vähentää, ja
`wait` odottaa nollaa. Se sopii lähtöporttiin ("kaikki aloittavat yhtä
aikaa") ja valmistumisen odottamiseen ("odota, että N alustusta on
valmiina").

## Semafori: rajallinen resurssi

`std::counting_semaphore<N>` pitää kirjaa vapaista paikoista: `acquire`
odottaa, kunnes paikka vapautuu, ja `release` palauttaa sen. Toisin kuin
lukko, semaforia ei omista mikään säie, joten toinen säie saa vapauttaa
sen. Tyypillinen käyttö on samanaikaisten yhteyksien tai muistia
vievien tehtävien rajoittaminen:

```{.cpp tiedosto="esimerkit/07-semafori.cpp" osa="yhteydet"}
```

```{.cpp tiedosto="esimerkit/07-semafori.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-semafori.odotettu"}
```

Paikka on RAII-olio, joten poikkeus ei jätä paikkaa varatuksi.
Tilastoinnin `suurin` päivitetään CAS-silmukalla (luku *Atomiset
operaatiot*). `std::binary_semaphore` on semafori, jossa on yksi paikka.
Se sopii säikeiden väliseen signaaliin ("data on valmis"), kun
ehtomuuttuja ja lippu olisivat raskaampia.

## Kertaalustus

Laiska alustus ("alusta, kun ensimmäinen tarvitsee") on rinnakkain
hankala: kaksi säiettä voi huomata alustamattoman tilan yhtä aikaa.
Kaksoistarkistettu lukitus (*double-checked locking*) tehdään helposti
väärin, ja C++ tarjoaa kaksi valmista ratkaisua:

```{.cpp tiedosto="esimerkit/07-kerran.cpp" osa="kerran"}
```

```{.cpp tiedosto="esimerkit/07-kerran.cpp" osa="static"}
```

```{.tuloste tiedosto="esimerkit/07-kerran.odotettu"}
```

`std::call_once` takaa, että funktio ajetaan kerran ja että kaikki
kutsujat näkevät alustuksen tuloksen. Jos alustus heittää poikkeuksen,
seuraava kutsuja yrittää uudelleen. Funktion paikallisen staticin
alustus on C++11:stä alkaen samalla tavalla säieturvallinen (*magic
statics*), ja se on yksinkertaisin tapa tehdä laiska yksittäisolio.

## Valinta

| Tarve | Väline |
|------------------------------|--------------------|
| Odota, että ehto lukon suojaamassa tilassa toteutuu | `std::condition_variable` |
| Sama ja pysäytyspyyntö | `std::condition_variable_any` ja `stop_token` |
| Odota yhden atomisen arvon muutosta | `std::atomic::wait` ja `notify_*` |
| Kaikki lähtevät yhtä aikaa, tai odota N tapahtumaa kerran | `std::latch` |
| Toistuvat vaiheet, joiden välissä kaikki tahdistuvat | `std::barrier` |
| Enintään N samanaikaista käyttäjää | `std::counting_semaphore` |
| Yksi tulos toisesta säikeestä | `std::promise` ja `std::future` |
| Alusta kerran | Paikallinen `static` tai `std::call_once` |

## Käytännössä

- **Aina predikaatti.** `wait` ilman predikaattia on virhe lähes
  jokaisessa koodissa. Predikaatti lukee vain lukon suojaamaa tilaa.
- **Tila muuttuu lukon alla, ilmoitus sen jälkeen.** Jos tila muutetaan
  ilman lukkoa ja ilmoitetaan, odottaja voi tarkistaa ehdon juuri ennen
  muutosta ja nukahtaa sen jälkeen: herätys katoaa.
- **Rajaa jonot.** Rajoittamaton jono siirtää ylikuorman muistiin.
  Rajattu jono tekee ylikuormasta näkyvää ja hallittua.
- **Sulkeminen on osa rajapintaa.** Jonot, poolit ja tuottajat tarjoavat
  operaation, joka herättää kaikki odottajat ja kertoo, ettei töitä enää
  tule.
- **Valmis väline ennen omaa.** Este, salpa ja semafori ovat standardissa
  oikein toteutettuina; ehtomuuttujasta ja laskurista koottu oma este on
  tavallinen virhelähde.

## Itsearviointi

- Osaat selittää, miksi ehtomuuttujan odotus tarvitsee predikaatin ja
  mitä kadonnut herätys tarkoittaa.
- Osaat toteuttaa rajatun estävän jonon, jossa on vastapaine ja
  sulkeminen.
- Osaat rakentaa vaiheittaisen laskennan `std::barrier`illa ja
  käyttää valmistumisfunktiota vaiheiden välisiin töihin.
- Osaat valita tilanteeseen sopivan odotusvälineen ja tehdä
  kertaalustuksen säieturvallisesti.
