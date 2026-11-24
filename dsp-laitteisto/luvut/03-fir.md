# FIR-rakenteet laitteistossa

FIR-suodin on summa $y[n] = \sum_{k=0}^{N-1} h_k\, x[n-k]$. C:ssä se
on silmukka, jonka järjestys ei kiinnosta ketään. Laitteistossa sama
summa voidaan järjestää monella tavalla, ja jokainen järjestys on eri
piiri: kertojien määrä, rekisterien määrä, latenssi ja suurin
kellotaajuus vaihtelevat. Tässä luvussa toteutetaan kolme rakennetta,
joilla kaikilla on uusi näyte joka kellojaksolla. Neljäs rakenne, joka
jakaa yhden kertojan, on luvussa 8.

Kaikki rakenteet laskevat tarkan kokonaislukusumman ja kaventavat sen
samalla `kavenna`-moduulilla. Siksi ne antavat bitilleen saman
tuloksen, ja yksi malli `malli.suotimet.fir` on niiden kaikkien
referenssi:

```{.python tiedosto="esimerkit/malli/suotimet.py" osa="fir"}
```

## Liitäntä

Suotimilla on virtaliitäntä molemmin puolin. Näyte siirtyy, kun
`s_valid` ja `s_ready` ovat ykkösiä samalla nousevalla reunalla;
ulostulossa samoin `m_valid` ja `m_ready`. Parametrit kertovat
kertoimien määrän, sanaleveydet ja pudotettavien bittien määrän:

```{.systemverilog tiedosto="esimerkit/rtl/fir_suora.sv" osa="liitanta"}
```

Kertoimet ovat parametri, joka saa oletusarvonsa generoidusta
vakiosta. Vakiokertoimet ovat laitteistolle edullisia: synteesi voi
korvata kertojan siirroilla ja yhteenlaskuilla, jos kerroin on
yksinkertainen, ja yhdistää samat tulot. Ajon aikana vaihdettavat
kertoimet vaatisivat rekisterit ja yleiset kertojat.

Pysähtyminen on toteutettu yhdellä signaalilla. Kun ulostulossa on
näyte, jota vastaanottaja ei ota, mikään vaihe ei etene:

```{.systemverilog tiedosto="esimerkit/rtl/fir_suora.sv" osa="pysaytys"}
```

Tämä on yksinkertaisin oikea tapa käsitellä vastapainetta
liukuhihnassa. Sen hinta ja vaihtoehdot käsitellään luvussa 8.

## Suora muoto

Suorassa muodossa näytteet kulkevat viivelinjassa, jokaisella
viivelinjan paikalla on oma kertoja, ja tulot lasketaan yhteen.
Datapolku on kolmivaiheinen liukuhihna:

```{.systemverilog tiedosto="esimerkit/rtl/fir_suora.sv" osa="datapolku"}
```

1. Uusi näyte siirtyy viivelinjaan.
2. Kertojat laskevat kaikki tulot rinnakkain ja rekisteröivät ne.
3. Summainpuu laskee tulot yhteen, `kavenna` pyöristää ja saturoi,
   ja tulos rekisteröidään ulostuloon.

Valid-bitit `v1` ja `v2` kulkevat datan rinnalla. Ne kertovat, onko
vaiheessa oikea näyte vai tyhjä paikka. Kun sisääntulossa on tauko,
viivelinja ei siirry, mutta tulot lasketaan silti uudelleen samoista
näytteistä. Tulos hylätään, koska valid-bitti on nolla. Turha laskenta
on halvempaa kuin ohjaus, joka estäisi sen.

`always_comb`-silmukka kuvaa summan ketjuna, ja synteesityökalut
toteuttavat sen usein juuri niin: $N - 1$ summainta peräkkäin. Puun,
jossa on vain $\lceil \log_2 N \rceil$ summainta peräkkäin, saa
varmasti vain kirjoittamalla sen itse. Kumpikin on pitkässä
suotimessa kriittinen polku. Ratkaisu on rekisteröidä puu
tasoittain (luku 8) tai valita transponoitu muoto.

## Transponoitu muoto

Transponoidussa muodossa uusi näyte kerrotaan kaikilla kertoimilla
samassa jaksossa, ja osasummat kulkevat rekisteriketjussa:

$$z_{N-1}[n] = h_{N-1} x[n], \qquad
z_i[n] = h_i x[n] + z_{i+1}[n-1], \qquad
y[n] = h_0 x[n] + z_1[n-1].$$

```{.systemverilog tiedosto="esimerkit/rtl/fir_transponoitu.sv" osa="datapolku"}
```

Rekisterien välissä on yksi kertoja ja yksi summain, suotimen
pituudesta riippumatta. Kriittinen polku ei siis pitene, kun
kertoimia lisätään, ja latenssi on yksi jakso. Hintana on, että
sisääntulo menee kaikille kertojille yhtä aikaa. Pitkässä suotimessa
tämä suuri haarautuminen (*fan-out*) hidastaa signaalia ja on usein
transponoidun muodon todellinen raja. Toinen hinta: osasummarekisterit
ovat summan levyisiä (31 bittiä), kun suoran muodon viivelinja on
näytteen levyinen (12 bittiä).

Molemmat muodot ovat samaa matematiikkaa. Transponointi kääntää
signaalivuograafin nuolet ja vaihtaa haarautumiset summaimiksi, joten
siirtofunktio säilyy. Bittitarkkaan tulokseen tämä ei vaikuta, koska
summat ovat tarkkoja.

## Symmetrinen rakenne

Lineaarivaiheisen suotimen kertoimet ovat symmetriset:
$h_k = h_{N-1-k}$. Silloin näytteet $x[n-k]$ ja $x[n-N+1+k]$ voidaan
laskea ensin yhteen ja kertoa kerran:

$$y[n] = \sum_{k=0}^{N/2-1} h_k \bigl(x[n-k] + x[n-N+1+k]\bigr).$$

```{.systemverilog tiedosto="esimerkit/rtl/fir_symmetrinen.sv" osa="datapolku"}
```

Kertojia on puolet vähemmän. Esisumma on bitin leveämpi kuin näyte,
joten kertojan sisääntulo kasvaa 12:sta 13 bittiin. Tämä on syy siihen,
että FPGA:iden DSP-lohkoissa on usein oma esisummain: esimerkiksi
Xilinxin DSP48E2-lohkossa on 27-bittinen esisummain ennen 27 × 18
-kertojaa juuri symmetrisiä suotimia varten.

## Systolinen rakenne

FPGA-valmistajien DSP-lohkot ketjutetaan omilla nopeilla
johdotuksillaan, ja niiden suositeltu FIR-rakenne on *systolinen*:
suora muoto, jossa viivelinjassa on kaksi rekisteriä kertojaa kohden
ja summaketju on rekisteröity jokaisen kertojan jälkeen. Jokainen
DSP-lohko laskee $h_k x + z$ omista rekistereistään, joten kriittinen
polku on yksi lohko, eikä sisääntulolla ole suurta haarautumista.
Hintana on latenssi, joka kasvaa suotimen pituuden mukana. iCE40:n
SB_MAC16-lohkojen välillä kulkee vain kertymän kantoketju, ei dataa
eikä osasummia, joten tämän tutoriaalin esimerkeissä rakennetta ei
toteuteta.

## Rakenteiden vertailu

| Rakenne | Kertojia | Rekisterit | Latenssi | Kriittinen polku |
|---------------|----------|-------------------------------|----------|---------------------------------|
| suora | $N$ | viivelinja, tulot | 3 | summainpuu |
| transponoitu | $N$ | osasummat (summan levyisiä) | 1 | kertoja + summain, haarautuminen |
| symmetrinen | $N/2$ | viivelinja, tulot | 3 | esisummain + kertoja |
| systolinen | $N$ | $2N$ näytettä, $N$ osasummaa | $N + 2$ | kertoja + summain |
| jaettu (luku 8) | 1 | viivelinja, kertymä | $N + 1$ | kertoja + summain |

Kaikki kolme toteutettua rakennetta läpäisevät saman testisarjan
saman mallin kanssa. Transponoidun muodon ajo:

```{.tuloste tiedosto="esimerkit/odotetut/cocotb-fir-transponoitu.odotettu"}
```

Tulos on sama kuin luvun 1 suoralla muodolla, rivi riviltä. Testi
ei tiedä rakenteesta mitään: se vertaa ulostulojonoa malliin, eikä
latenssi tai tauot vaikuta vertailuun. Luvussa 10 nähdään, mitä
rakenteet maksavat FPGA:lla.

## Käytännössä

- Valitse rakenne kellotaajuuden ja resurssien mukaan, ei tottumuksesta.
  Lyhyessä suotimessa kaikki kelpaavat; pitkässä suora muoto
  rekisteröidään puuksi tai korvataan transponoidulla tai
  systolisella muodolla.
- Hyödynnä symmetria aina, kun kertoimet ovat symmetriset.
  Lineaarivaiheisessa suotimessa se puolittaa kertojat.
- Kirjoita kaikille rakenteille sama liitäntä ja sama malli.
  Silloin rakenteen voi vaihtaa ilman, että testipenkkiin koskee.
- Valid-bitit kulkevat datan rinnalla jokaisessa liukuhihnan
  vaiheessa. Turhaa laskentaa ei kannata estää, kunhan tulos
  hylätään.
- Lue DSP-lohkon dokumentaatio ennen rakenteen valintaa: esisummain,
  kaskadit ja sisäiset rekisterit ratkaisevat, mikä rakenne sopii
  piirille. Kirjoita RTL niin, että synteesi tunnistaa ne.

## Itsearviointi

- Osaat piirtää suoran, transponoidun ja symmetrisen FIR-rakenteen ja
  kertoa niiden kertojien ja rekisterien määrän sekä latenssin.
- Osaat selittää, miksi eri rakenteet antavat bitilleen saman
  tuloksen ja miksi yksi malli riittää niiden kaikkien testaamiseen.
- Osaat nimetä kunkin rakenteen kriittisen polun ja keinon
  lyhentää sitä.
- Osaat kuljettaa valid-bitit liukuhihnan läpi ja selittää, miksi
  tyhjän paikan laskentaa ei tarvitse estää.
