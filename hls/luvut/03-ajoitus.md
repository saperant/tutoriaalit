# Ajoitus

*Ajoitus* (*scheduling*) päättää, millä kellojaksolla kukin
tietovuograafin operaatio suoritetaan. Se on HLS:n tärkein vaihe, koska
se määrää samalla latenssin, tarvittavien laitteistoyksiköiden määrän ja
sen, montako rekisteriä välituloksille tarvitaan. Ajoituksen on
noudatettava kolmea ehtoa:

1. **Riippuvuudet**: operaatio voi alkaa vasta, kun sen operandit ovat
   valmiita.
2. **Kellojakso**: samalla jaksolla peräkkäin laskettavien operaatioiden
   viiveiden summa ei saa ylittää jakson pituutta.
3. **Resurssit**: samalla jaksolla ei saa käyttää enempää yksiköitä
   kuin on varattu, eikä muistista voi lukea enempää kuin sen portit
   sallivat.

## Esimerkki: differentiaaliyhtälö

HLS-kirjallisuuden klassinen ajoitusesimerkki on differentiaaliyhtälön
y'' + 3xy' + 3y = 0 numeerinen ratkaisu Eulerin menetelmällä. Paulin ja
Knight käyttivät sitä vuonna 1989 HAL-järjestelmän esittelyssä, ja
sitä on käytetty vertailukohtana siitä lähtien. Silmukan rungossa on
kuusi kertolaskua ja neljä yhteen- tai vähennyslaskua:

```{.cpp tiedosto="esimerkit/03-ajoitus/diffeq.cpp" osa="ydin"}
```

## ASAP ja ALAP

Yksinkertaisin ajoitus on *ASAP* (*as soon as possible*): jokainen
operaatio sijoitetaan heti, kun sen operandit ovat valmiita. Sen
peilikuva *ALAP* (*as late as possible*) sijoittaa operaation niin
myöhään kuin mahdollista ilman, että koko ajoitus pitenee. Molemmat
lasketaan yhdellä läpikäynnillä graafin topologisessa järjestyksessä,
ALAP lopusta alkuun. Oppikirjoissa ne esitetään *yksikköviivemallilla*,
jossa jokainen operaatio vie yhden jakson:

```{.python tiedosto="esimerkit/minihls/raportti.py" osa="asap"}
```

```{.tuloste tiedosto="esimerkit/03-ajoitus/odotettu" osa="ajo1"}
```

ALAP- ja ASAP-jakson erotus on operaation *liikkuvuus* (*mobility*).
Liikkuvuus 0 tarkoittaa, että operaatio on *kriittisellä polulla*:
jos se viivästyy, koko ajoitus pitenee. Kertolaskuketju
`3 * x * u * dx` ja sitä seuraavat vähennyslaskut ovat kriittisellä
polulla, kun taas `x + dx` voi tapahtua millä tahansa jaksolla 0–4.
Liikkuvuus on listaajoituksen tärkein apuväline: kun resursseja on liian
vähän, ensin sijoitetaan operaatio, jolla on vähiten liikkumavaraa.

## Listaajoitus

*Listaajoitus* (*list scheduling*) etenee jakso kerrallaan. Jokaisella
jaksolla se kokoaa listan operaatioista, joiden operandit ovat valmiita,
ja sijoittaa niistä niin monta kuin resurssit sallivat, kiireellisimmät
ensin. Kiireellisyys on ALAP-jakso: mitä pienempi, sitä kiireellisempi.
Algoritmi on ahne eikä löydä aina lyhintä ajoitusta, mutta se on nopea ja
käytännössä hyvä, ja lähes kaikki HLS-työkalut käyttävät sitä tai sen
muunnelmaa.

```{.python tiedosto="esimerkit/minihls/ajoitus.py" osa="ajoitus"}
```

Jaksoa ei suljeta heti ensimmäisen sijoituksen jälkeen: kun operaatio
sijoitetaan, sen käyttäjät voivat tulla valmiiksi samalle jaksolle.
Tämä on *ketjutus* (*chaining*): peräkkäiset operaatiot lasketaan
samalla jaksolla kombinaatiologiikkana, kunhan viiveet mahtuvat
kellojaksoon. minihls käyttää seuraavia viiveitä:

```{.python tiedosto="esimerkit/minihls/ajoitus.py" osa="viiveet"}
```

Luvut ovat FPGA:n suuruusluokkaa mutta eivät minkään piirin mittauksia.
Oikea työkalu lukee viiveet kohdepiirin ja bittileveyden mukaan
karakterisoidusta kirjastosta, ja sama 32-bittinen kertolasku voi viedä
DSP-lohkossa 3 ns ja LUT-logiikassa 10 ns.

## Ajoitus kellojaksolle

Valitsin `--ajoitus` näyttää jokaisen operaation jakson ja ajan, jolloin
sen tulos on valmis jakson alusta laskien:

```{.tuloste tiedosto="esimerkit/03-ajoitus/odotettu" osa="ajo2"}
```

10 ns:n jaksoon mahtuu yksi kertolasku ja kaksi yhteenlaskua
(6 + 2 + 2 ns), joten kolmen kertolaskun ketju `3 * x`, `* u`, `* dx`
vie kolme jaksoa. Jaksolla 2 kertolaskun perään ketjutetaan kaksi
vähennyslaskua, ja viimeinen valmistuu täsmälleen jakson lopussa
(10,0 ns). Muuttujien lukeminen (`t3 = x`) ei vie aikaa: arvo tulee
rekisteristä jakson alussa.

Alla oleva kuva on sama ajoitus tietovuograafina. minihls tuottaa sen
valitsimella `--dot askel`, ja testi tarkistaa, että kuva vastaa
ajoitusta. Jokainen sarake on yksi kellojakso, nuolet ovat
datariippuvuuksia, ja katkoviivat ovat silmukan kantamia riippuvuuksia
(etäisyys `d` kierrosta): seuraava kierros lukee `x`:n, `y`:n ja
`u`:n uudet arvot.

```{.dot tiedosto="esimerkit/kaaviot/diffeq-askel.dot" otsikko="Differentiaaliyhtälön silmukan ajoitettu tietovuograafi"}
```

Samalla jaksolla on kolme kertolaskua, joten tarvitaan kolme kertojaa
(`mul0`–`mul2`). Kertojat ovat kalliita: 32-bittinen kertoja vie
FPGA:lla kolme–neljä DSP-lohkoa tai yli tuhat LUTia. Seuraava luku
näyttää, miten niiden määrää rajoitetaan.

## Kellojakso ja latenssi

Kellojakson pituus on suunnittelijan tärkein valinta. Kun jaksoa
pidennetään 20 nanosekuntiin, kolme kertolaskua mahtuu samaan jaksoon:

```{.tuloste tiedosto="esimerkit/03-ajoitus/odotettu" osa="ajo3"}
```

Kierros vie nyt kaksi jaksoa kolmen sijaan, ja latenssi lyheni 15
jaksosta 11 jaksoon. Ajassa mitattuna tulos on kuitenkin huonompi:
11 · 20 ns = 220 ns, kun 10 ns:n kellolla 15 · 10 ns = 150 ns. Lisäksi
kaikki kuusi kertolaskua tarvitsevat oman kertojansa, koska ne
ketjutetaan samaan jaksoon. Lyhyt kellojakso taas lisää rekistereitä ja
latenssia jaksoina. Oikea vastaus riippuu siitä, mikä muu piirissä
määrää kellotaajuuden: yleensä HLS-lohko saa saman kellon kuin
ympäröivä järjestelmä, ja työkalu ajoittaa sen mukaan.

Vitis HLS:ssä kellojakso annetaan projektin asetuksena
(`create_clock -period 10`) ja *epävarmuus* (*clock uncertainty*,
oletuksena 27 % jaksosta), jonka verran jaksosta jätetään käyttämättä
sijoittelun ja reitityksen varaksi. Jos ajoitus ei myöhemmin toteudu,
ensimmäinen korjaus on kasvattaa epävarmuutta, jolloin työkalu ketjuttaa
vähemmän.

## Muita ajoitusmenetelmiä

| Menetelmä | Periaate | Käyttö |
|------------------------------|------------------------------|------------------------------|
| ASAP, ALAP | ilman resurssirajoja | alarajat, liikkuvuus |
| listaajoitus | ahne, jakso kerrallaan | useimmat työkalut |
| voimiin perustuva (*force-directed*) | tasoittaa resurssien käyttöä jaksojen välillä | aikarajoitettu ajoitus, HAL |
| SDC (*system of difference constraints*) | ehdot lineaarisena ohjelmana | Vivado ja Vitis HLS, LegUp |
| kokonaislukuoptimointi (ILP) | optimaalinen ratkaisu | pienet graafit, tutkimus |
| dynaaminen ajoitus | kättelyt, ajoitus ajon aikana | Dynamatic |

SDC-ajoituksessa jokainen riippuvuus ja ajoitusehto kirjoitetaan
muotoon $t_b - t_a \geq d$, ja koko joukko ratkaistaan lineaarisella
ohjelmoinnilla. Menetelmä käsittelee ketjutuksen, monijaksoiset
operaatiot ja silmukoiden ehdot samassa kehyksessä.

## Käytännössä

- **Kriittinen polku ratkaisee.** Latenssia lyhennetään lyhentämällä
  kriittistä polkua: puurakenne ketjun sijaan (`(a + b) + (c + d)`
  eikä `((a + b) + c) + d`), vakiokertolaskut siirroiksi tai
  laskennan siirtäminen pois riippuvuusketjusta.
- **Kellojakso on rajoite, ei tavoite.** Ajoita sille kellolle, jolla
  lohko toimii järjestelmässä, ja jätä marginaalia sijoittelulle.
- **Raportin arvio ei ole lopullinen.** HLS:n viiveet ovat arvioita
  ennen sijoittelua. Lopullinen ajoitus selviää vasta toteutuksen
  ajoitusanalyysistä.
- **Ketjutus maksaa logiikkaa.** Pitkä ketju yhdessä jaksossa estää
  yksiköiden jakamisen ja kasvattaa reitityksen viivettä.

## Itsearviointi

- Osaat laskea pienelle tietovuograafille ASAP- ja ALAP-ajoituksen ja
  liikkuvuuden yksikköviivemallilla.
- Osaat selittää, miten listaajoitus valitsee sijoitettavat operaatiot
  ja miksi kiireellisyys perustuu ALAP-jaksoon.
- Osaat selittää ketjutuksen ja laskea, montako operaatiota mahtuu
  annettuun kellojaksoon.
- Osaat arvioida, miten kellojakson pidentäminen vaikuttaa latenssiin
  jaksoina, latenssiin ajassa ja yksiköiden määrään.
