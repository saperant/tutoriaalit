# Summaimet ja ALU

Summain on suorittimen tärkein lohko: sillä lasketaan yhteen- ja
vähennyslaskut, osoitteet, vertailut ja laskurit. Sen rakenne näyttää
myös digitaalisuunnittelun keskeisen vaihtokaupan: pieni ja hidas vai
suuri ja nopea.

## Puoli- ja täyssummain

Kahden bitin summa on XOR ja muistibitti AND: tämä on *puolisummain*.
Monibittisessä summassa jokainen bitti lisää myös edellisen bitin
muistibitin, joten tarvitaan kolmen tulon *täyssummain*:

```{.systemverilog tiedosto="esimerkit/06-summain/taysisummain.sv" osa="taysisummain"}
```

Muistibitti $c_{out} = ab + (a \oplus b)c_{in}$ on luvun 4
enemmistöfunktio: muistia syntyy, kun vähintään kaksi tuloa on 1.
Lauseke on kirjoitettu *generoi*- ja *välitä*-termeiksi: $g = ab$
synnyttää muistibitin aina, ja $p = a \oplus b$ välittää tulevan
muistibitin eteenpäin. Sama jako on carry-lookahead-summaimen pohja.

## Ripple-carry

Yksinkertaisin $n$-bittinen summain on $n$ täyssummainta ketjussa:

```{.systemverilog tiedosto="esimerkit/06-summain/rca.sv" osa="rca"}
```

Ketju on pieni, mutta muistibitti kulkee pahimmillaan kaikkien bittien
läpi. Jokainen täyssummain lisää muistipolulle kaksi porttiviivettä
(AND ja OR), joten viive kasvaa lineaarisesti: 64-bittinen summain on
16 kertaa hitaampi kuin 4-bittinen.

## Carry-lookahead

Carry-lookahead-summain laskee muistibitit suoraan tulomuistista
avaamalla rekursion $c_{i+1} = g_i + p_i c_i$:

$$c_2 = g_1 + p_1 g_0 + p_1 p_0 c_0$$

Jokainen muistibitti on nyt kaksitasoinen AND–OR-lauseke, joten
neljän bitin lohkon kaikki muistibitit valmistuvat yhtä aikaa:

```{.systemverilog tiedosto="esimerkit/06-summain/cla4.sv" osa="cla4"}
```

Hinta näkyy lausekkeista: termien ja tulojen määrä kasvaa bittien
mukana neliöllisesti. Siksi täyttä lookaheadia ei tehdä 64 bitin yli,
vaan lohkoja yhdistetään. Esimerkin testipenkki ketjuttaa kaksi
neljän bitin lohkoa ja tarkistaa molemmat summaimet kaikilla
syötteillä:

```{.systemverilog tiedosto="esimerkit/06-summain/testipenkki.sv" osa="testipenkki"}
```

```{.tuloste tiedosto="esimerkit/06-summain.odotettu"}
```

## Viiveet simuloituina

Kumpi on nopeampi ja paljonko? Luvun 7 porttisimulaattori rakentaa
molemmat porttitasolla ja mittaa pahimman tapauksen asettumisajan,
kun jokaisen portin viive on yksi aikayksikkö:

```{.python tiedosto="esimerkit/06-summaimet.py" osa="cla"}
```

```{.python tiedosto="esimerkit/06-summaimet.py" osa="mittaus"}
```

```{.tuloste tiedosto="esimerkit/06-summaimet.odotettu"}
```

Ripple-carry kasvaa $2n$:nä, lohkoittainen lookahead noin $n/2$:na:
lohkon läpi muistibitti kulkee kahdessa porttiviiveessä neljän bitin
sijaan. Nopeammat rakenteet (Kogge–Stone, Brent–Kung) järjestävät
generoi- ja välitä-termit puuksi, jolloin viive kasvaa
logaritmisesti. Synteesityökalu valitsee rakenteen ajoitusvaatimuksen
mukaan: kun kello on hidas, se tekee pienen ripple-carry-summaimen.

## ALU ja tilaliput

Aritmeettis-looginen yksikkö (ALU) laskee yhden monesta operaatiosta
valintasignaalin mukaan. Vähennys tehdään samalla summaimella:
$a - b = a + \bar{b} + 1$, joten b käännetään ja tulomuistiksi annetaan
1.

```{.systemverilog tiedosto="esimerkit/06-alu.sv" osa="alu"}
```

ALU tuottaa *tilaliput*, joista suorittimen ehdolliset hypyt
päättelevät tuloksen:

| Lippu | Merkitys | Laskenta |
|-------|----------|----------|
| N | tulos on negatiivinen | tuloksen MSB |
| Z | tulos on nolla | kaikkien bittien NOR |
| C | etumerkitön ylivuoto (tai lainaamattomuus vähennyksessä) | muistibitti ulos |
| V | etumerkillinen ylivuoto | muistibitti MSB:hen XOR muistibitti MSB:stä |

V-lipun laskentatapa on lyhyin tapa ilmaista sääntö "kahden
samanmerkkisen luvun summa vaihtoi merkkiä": jos muistibitti MSB:hen ja
siitä ulos eroavat, tulos ei mahdu. C-lippu on vähennyksessä 1, kun
*lainaa ei tarvittu* ($a \geq b$ etumerkittöminä). Arm käyttää tätä
käytäntöä, x86:ssa lippu päinvastoin kertoo lainan, ja RISC-V:ssä
lippuja ei ole lainkaan: vertailu tehdään omilla käskyillään.

```{.systemverilog tiedosto="esimerkit/06-alu.sv" osa="testipenkki"}
```

```{.tuloste tiedosto="esimerkit/06-alu.odotettu"}
```

Esimerkit näyttävät, että sama bittitulos tulkitaan lipuilla eri
tavoin: 7 + 1 = 1000 on etumerkittömänä 8 (C = 0, oikein) mutta
etumerkillisenä −8 (V = 1, ylivuoto). Laitteisto laskee kummankin
lipun aina; ohjelma valitsee, kumpaa se katsoo.

## Käytännössä

- **Kirjoita `a + b`, älä summainta.** RTL-kuvauksessa summa kirjoitetaan
  operaattorilla, ja synteesityökalu valitsee rakenteen ajoituksen
  mukaan. Käsin kirjoitettu porttitason summain estää työkalua
  optimoimasta.
- **Jaa summaimet, kun voit.** Summain on suuri lohko. Jos kaksi
  laskua ei tapahdu samassa jaksossa, yksi summain multiplekserin
  kanssa riittää (*resurssien jakaminen*).
- **Leveys kasvaa yhdellä bitillä.** Kahden $n$-bittisen luvun summa
  tarvitsee $n+1$ bittiä. Jos ylimääräistä bittiä ei säilytetä,
  ylivuoto on hiljainen.
- **Liput ovat sopimus.** Lipun merkitys (erityisesti C vähennyksessä)
  vaihtelee arkkitehtuureittain. Tarkista dokumentaatio ennen kuin
  kirjoitat vertailuja assemblyllä.

## Itsearviointi

- Osaat rakentaa täyssummaimen porteista ja selittää generoi- ja
  välitä-termit.
- Osaat selittää, miksi ripple-carry-summaimen viive kasvaa lineaarisesti
  ja miten carry-lookahead lyhentää sitä ja millä hinnalla.
- Osaat toteuttaa vähennyksen summaimella.
- Osaat laskea ALUn liput N, Z, C ja V ja tulkita ne etumerkittömälle
  ja etumerkilliselle laskulle.
