# Rajapintaprotokollat

C++-funktion parametrit ja paluuarvo muuttuvat laitteistossa porteiksi,
ja jokaisella porttiryhmällä on *protokolla*, joka kertoo, milloin data
on voimassa. Protokollia on kahdella tasolla: *lohkotason* protokolla
käynnistää ytimen ja kertoo, milloin se on valmis, ja *porttitason*
protokollat siirtävät parametrien datan. HLS-työkalu valitsee
oletusprotokollan parametrin tyypin mukaan, ja pragma `interface`
vaihtaa sen.

| C++-parametri | Oletus (Vitis HLS) | minihls | Portit |
|------------------------------|--------------------|--------------------|----------------------------------------|
| skalaari `int k` | `ap_none` | `ap_none` | `k` |
| taulukko `int a[N]` | `ap_memory` | `ap_memory` (luku- ja kirjoitusportti) | `a_address0`, `a_ce0`, `a_q0`, `a_we1`, `a_d1` |
| virta `hls::stream<int>&` | `axis` | `axis` (`virta<int>&`) | `x_TDATA`, `x_TVALID`, `x_TREADY` |
| paluuarvo | `ap_return` | `ap_return` | `ap_return` |
| funktio | `ap_ctrl_hs` | `ap_ctrl_hs` | `ap_start`, `ap_done`, `ap_idle`, `ap_ready` |

minihls:n `virta<int>` vastaa Vitis HLS:n luokkaa `hls::stream<int>`.
Se on määritelty tiedostossa `esimerkit/yhteinen/virta.hpp`, jotta
C-simulaatio toimii ilman HLS-työkalun otsakkeita.

## Lohkotason protokolla: ap_ctrl_hs

Ydin odottaa lepotilassa (`ap_idle` = 1), kunnes `ap_start` nousee.
Kun laskenta on valmis, `ap_done` on yhden jakson ajan 1, ja silloin
`ap_return` ja kirjoitetut muistit ovat voimassa. `ap_ready` kertoo,
että ydin voi ottaa vastaan uudet syötteet; minihls:ssä se on sama
kuin `ap_done`, mutta tietovuo-ytimissä se voi nousta aiemmin, jolloin
seuraava kutsu alkaa ennen kuin edellinen on valmis.

| Jakso | 0 | 1 | 2 | ... | L | L + 1 |
|------------------|-----|-----|-----|-----|-----|-------|
| `ap_start` | 1 | 0 | 0 | ... | 0 | 0 |
| `ap_idle` | 1 | 0 | 0 | ... | 0 | 1 |
| `ap_done` | 0 | 0 | 0 | ... | 1 | 0 |

Alla oleva kuva näyttää saman kättelyn johdannon pistetulon simuloidusta
RTL:stä. Kutsuja antaa yhden jakson `ap_start`-pulssin, ydin lukee
muistia `ap_memory`-liitännän kautta (osoite ja `a_ce0`, data
seuraavalla jaksolla), ja `ap_done` on ylhäällä yhden jakson, jolloin
`ap_return` on voimassa.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/mac-ap-ctrl.json" otsikko="ap_ctrl_hs ja ap_memory pistetulon RTL:ssä"}
```

Vitis HLS:n mukaan `ap_start` pidetään ylhäällä, kunnes `ap_ready`
nousee; minihls lukee sen vain lepotilassa, joten yhden jakson pulssi
riittää. Skalaarin protokolla `ap_none` ei sisällä kättelyä: kutsujan on
pidettävä arvo vakaana koko ajon ajan. Protokollat `ap_vld` ja `ap_ack`
lisäävät voimassaolo- ja kuittaussignaalin. `ap_ctrl_none` poistaa
lohkotason protokollan kokonaan: ydin laskee jatkuvasti, mikä sopii
virtoja käsittelevälle ytimelle.

## Muistirajapinta: ap_memory

`ap_memory` olettaa, että ytimen ulkopuolella on synkroninen RAM:
osoite ja `ce0` annetaan jaksolla *t*, ja data tulee porttiin `q0`
jaksolla *t + 1*. Luvun 4 pistetulon kytkennät näyttivät tämän:
osoite tulee suoraan silmukkalaskurista. Jaetusta taulukosta tulee
yksi porttiryhmä pankkia kohti (`a_0_address0`, `a_1_address0` jne.),
joten kutsujan on myös jaettava data pankkeihin samalla tavalla.

Prosessorijärjestelmässä ydin liitetään väylään. Vitis HLS tuottaa
siihen kaksi muuta rajapintaa:

- **`s_axilite`**: AXI4-Lite-orjarajapinta, jonka kautta prosessori
  kirjoittaa skalaariparametrit ja ohjausrekisterin. Työkalu tuottaa
  rekisterikartan ja C-ajurin: osoitteessa 0 on ohjausrekisteri, jonka
  bitit ovat `ap_start` (0), `ap_done` (1), `ap_idle` (2) ja
  `ap_ready` (3), ja parametrit ovat keskeytysrekisterien jälkeen
  osoitteesta 0x10 alkaen.
- **`m_axi`**: AXI4-isäntärajapinta, jolla ydin lukee ja kirjoittaa
  järjestelmän muistia purskeina itse (luku 7).

## Virrat: AXI-Stream

Virta siirtää dataa kättelyllä. Lähettäjä asettaa `TDATA`:n ja
`TVALID`:n, vastaanottaja `TREADY`:n, ja siirto tapahtuu jaksolla,
jolla molemmat ovat 1. AXI-Streamin kaksi sääntöä tekevät kättelystä
luotettavan:

1. Lähettäjä ei saa odottaa `TREADY`:tä ennen kuin asettaa `TVALID`:n,
   eli `TVALID` ei saa riippua samasta rajapinnasta tulevasta
   `TREADY`:stä. Muuten kaksi toisiaan odottavaa lohkoa lukkiutuisi.
2. Kun `TVALID` on asetettu, sitä ja dataa on pidettävä, kunnes siirto
   tapahtuu.

Lisäksi rajapinnassa voi olla `TLAST` paketin viimeiselle sanalle sekä
`TKEEP` ja `TUSER`; minihls tukee vain kolmea perussignaalia.

## FIR-suodin virroilla

Kahdeksan kertoimen FIR-suodin lukee näytteen ja kirjoittaa tuloksen
joka jaksolla. Viivelinja `z` on jaettu kokonaan rekistereiksi, ja
kertoimet ovat vakiotaulukossa, joten kertolaskut ovat vakiolla
kertomisia:

```{.cpp tiedosto="esimerkit/09-fir/fir.cpp" osa="ydin"}
```

Liukuhihnoitetun silmukan sisäsilmukat avataan: siirto
`z[k] = z[k - 1]` muuttuu rekisterien väliseksi siirroksi ja summa
kahdeksaksi kertolaskuksi ja seitsemäksi yhteenlaskuksi. Tuotetun
ytimen portit ovat pelkät virrat ja lohkotason ohjaus:

```{.verilog tiedosto="esimerkit/09-fir/fir.v" osa="portit"}
```

## Pysäytys

Liukuhihnan on pysähdyttävä, jos syötettä ei ole saatavilla tai
vastaanottaja ei ole valmis. minihls laskee jokaiselle virralle
*tarpeen*, joka on tosi niinä jaksoina, joilla virtaa käytetään, ja
sallintasignaalin `en`, joka on tosi, kun kaikki tarvitut virrat ovat
valmiita:

```{.verilog tiedosto="esimerkit/09-fir/fir.v" osa="virrat"}
```

```{.verilog tiedosto="esimerkit/09-fir/fir.v" osa="kytkennat"}
```

Kun `en` on 0, tilakone, kaikki rekisterit ja muistien
kirjoitusportit pysähtyvät. `x_TREADY` kertoo lähettäjälle, että
näyte otetaan vastaan, vain jos koko piiri etenee. `y_TVALID` riippuu
tulevan virran valmiudesta `x_ok` mutta ei omasta `y_TREADY`:stään,
kuten AXI-Stream vaatii.

Testipenkki ajaa ytimen kahdesti: ensin virrat ovat aina valmiita, ja
sitten valitsin `--paine` lisää satunnaisen vastapaineen. Silloin
testipenkin lähettäjä pitää `TVALID`:n alhaalla ja vastaanottaja
`TREADY`:n alhaalla näennäissatunnaisesti:

```{.tuloste tiedosto="esimerkit/09-fir/odotettu"}
```

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/fir-virta.json" otsikko="Suotimen virrat vastapaineella RTL-simulaatiosta. Lähettäjä pitää taukoja (x_TVALID) ja vastaanottaja ei aina ole valmis (y_TREADY). Kun jompikumpi puuttuu, koko piiri pysähtyy: x_TREADY laskee, x_TDATA ei vaihdu eikä y_nro kasva. Yhtään näytettä ei katoa eikä toistu."}
```

Kaavion syöte on juokseva numero ja `y_nro` testipenkin laskuri
siirtyneistä tuloksista; kumpikin etenee vain jaksoilla, joilla oman
virran `TVALID` ja `TREADY` ovat molemmat ykkösiä.

Ilman vastapainetta 32 näytettä vievät 34 jaksoa, kun mukaan lasketaan
kolmivaiheisen liukuhihnan täyttyminen; viivelinjan nollaus ja
käynnistys tuovat kokonaislatenssiksi 36 jaksoa. Vastapaineen kanssa latenssi vaihtelee
tapauksittain 108:sta 144 jaksoon, mutta tulokset ovat samat. Tämä on
rajapinnan tärkein testi: oikea protokolla ei saa riippua siitä, kuinka
nopeasti ympäristö toimii.

Koko piirin pysäyttäminen on yksinkertaista mutta kallista: `en` on
yhteydessä jokaiseen rekisteriin, ja sen viive kasvaa piirin mukana.
Suurissa liukuhihnoissa käytetään vaiheiden välisiä puskureita (*skid
buffer*) tai vapaasti kulkevaa liukuhihnaa, jossa voimassaolo kulkee
datan mukana, kuten luvussa 6 mainittiin.

## Käytännössä

- **Valitse rajapinta järjestelmän mukaan.** Virta (`axis`) sopii
  ketjutettuihin suodatinlohkoihin, `ap_memory` paikalliseen muistiin
  ja `m_axi` järjestelmän DRAM:iin; ohjaus ja parametrit
  prosessorilta kulkevat `s_axilite`-rajapinnan kautta.
- **Virran järjestys on osa rajapintaa.** Ydin lukee ja kirjoittaa
  virtaa ohjelman järjestyksessä. C-testipenkin on tuotettava ja
  luettava sama määrä arvoja, ja `virta`-luokka keskeyttää, jos
  tyhjästä virrasta luetaan.
- **Testaa vastapaineella.** Protokollavirheet näkyvät vain, jos
  ympäristö ei aina ole valmis.
- **Lue rajapintaraportti.** Oikea työkalu listaa jokaisen portin
  protokollan ja leveyden; sen on vastattava ympäröivää RTL:ää tai
  järjestelmää.

## Itsearviointi

- Osaat selittää `ap_ctrl_hs`-protokollan signaalit ja ajoituksen.
- Osaat kertoa, mitkä portit `ap_memory`-rajapinta tuottaa ja millä
  jaksolla luettu data on voimassa.
- Osaat selittää AXI-Streamin kättelyn säännöt ja sen, miksi
  `TVALID` ei saa riippua `TREADY`:stä.
- Osaat kuvata, miten liukuhihnoitettu ydin pysähtyy, kun virta ei ole
  valmis, ja miksi rajapintaa testataan satunnaisella vastapaineella.
