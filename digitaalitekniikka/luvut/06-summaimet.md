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

```{.dot otsikko="Neljän bitin ripple-carry-summain: muistibitti kulkee ketjuna bitistä 0 bittiin 3"}
digraph {
  rankdir=RL; nodesep=0.3; ranksep=0.45;
  node [shape=plaintext, style=""];
  fa0 [label=<<table border="0" cellborder="0" cellspacing="2">
    <tr><td>a0 b0</td></tr>
    <tr><td border="1" bgcolor="#E4DCF0" cellpadding="6">täyssummain</td></tr>
    <tr><td>s0</td></tr></table>>];
  fa1 [label=<<table border="0" cellborder="0" cellspacing="2">
    <tr><td>a1 b1</td></tr>
    <tr><td border="1" bgcolor="#E4DCF0" cellpadding="6">täyssummain</td></tr>
    <tr><td>s1</td></tr></table>>];
  fa2 [label=<<table border="0" cellborder="0" cellspacing="2">
    <tr><td>a2 b2</td></tr>
    <tr><td border="1" bgcolor="#E4DCF0" cellpadding="6">täyssummain</td></tr>
    <tr><td>s2</td></tr></table>>];
  fa3 [label=<<table border="0" cellborder="0" cellspacing="2">
    <tr><td>a3 b3</td></tr>
    <tr><td border="1" bgcolor="#E4DCF0" cellpadding="6">täyssummain</td></tr>
    <tr><td>s3</td></tr></table>>];
  c0 [label="c0"]; c4 [label="c4"];
  c0 -> fa0; fa0 -> fa1 [label="c1"]; fa1 -> fa2 [label="c2"];
  fa2 -> fa3 [label="c3"]; fa3 -> c4;
}
```

Ketju on pieni, mutta muistibitti kulkee pahimmillaan kaikkien bittien
läpi. Jokainen täyssummain lisää muistipolulle kaksi porttiviivettä
(AND ja OR), joten viive kasvaa lineaarisesti: $n$-bittisen summaimen
muistipolku on noin $2n$ porttiviivettä, ja 64-bittinen summain on
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

## Viive laskettuna

Kumpi on nopeampi ja paljonko? Karkean arvion saa laskemalla portit
pisimmällä polulla. Ripple-carry-summaimessa muistibitti kulkee
kahden portin läpi bittiä kohden, eli $2n$ porttiviivettä.
Lohkoittaisessa lookaheadissa muistibitti ylittää neljän bitin lohkon
kahdessa porttiviiveessä, joten viive on noin $n/2$ ja muutama
porttiviive lohkon sisällä. Luvussa 7 sama mitataan
porttisimulaattorilla, ja tulos vastaa arviota.

Nopeammat rakenteet (Kogge–Stone, Brent–Kung) järjestävät generoi- ja
välitä-termit puuksi, jolloin viive kasvaa logaritmisesti.
Synteesityökalu valitsee rakenteen ajoitusvaatimuksen mukaan: kun
kello on hidas, se tekee pienen ripple-carry-summaimen.

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

## Siirrin ja kertoja

Kaksi muuta aritmetiikan lohkoa rakentuu suoraan luvun 5
multipleksereistä ja tämän luvun summaimista.

*Siirrin* (*barrel shifter*) siirtää sanaa valitun määrän bittejä
yhdessä jaksossa. Siirtomäärän jokainen bitti ohjaa yhtä
multiplekserikerrosta: ensimmäinen kerros siirtää yhden bitin tai ei
mitään, toinen kaksi, kolmas neljä. $n$-bittinen siirrin tarvitsee
$\log_2 n$ kerrosta, ja viive on sama kaikilla siirtomäärillä:

```{.systemverilog tiedosto="esimerkit/06-siirrin.sv" osa="siirrin"}
```

*Kertoja* tekee saman kuin kertolasku kynällä ja paperilla. Kertojan
jokainen bitti valitsee AND-porteilla, otetaanko siirretty kerrottava
mukaan (*osatulo*), ja osatulot lasketaan yhteen. $n$-bittisessä
taulukkokertojassa on $n^2$ AND-porttia ja $n - 1$ summainriviä, joten
se on sekä suuri että hidas: 32-bittinen kertoja on suorittimen
suurimpia kombinaatiolohkoja.

```{.systemverilog tiedosto="esimerkit/06-siirrin.sv" osa="kertoja"}
```

```{.systemverilog tiedosto="esimerkit/06-siirrin.sv" osa="testipenkki"}
```

```{.tuloste tiedosto="esimerkit/06-siirrin.odotettu"}
```

Oikeat kertojat laskevat osatulot yhteen puuna (Wallace, Dadda) ja
puolittavat osatulojen määrän Boothin koodauksella. Jakolasku on
iteratiivinen eikä mahdu yhteen kombinaatiolohkoon samalla tavalla;
algoritmit käsitellään taidossa *Miten tietokone laskee*.

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
- **Siirto vakiolla on ilmaista, kertolasku ei.** Siirto vakiomäärällä
  on pelkkää johdotusta. Kertoja sen sijaan on suuri: FPGA:ssa käytetään
  valmiita kertojalohkoja, ja leveä kertolasku liukuhihnoitetaan
  (luku 11).
- **Liput ovat sopimus.** Lipun merkitys (erityisesti C vähennyksessä)
  vaihtelee arkkitehtuureittain. Tarkista dokumentaatio ennen kuin
  kirjoitat vertailuja assemblyllä.

## Itsearviointi

- Osaat rakentaa täyssummaimen porteista ja selittää generoi- ja
  välitä-termit.
- Osaat selittää, miksi ripple-carry-summaimen viive kasvaa lineaarisesti
  ja miten carry-lookahead lyhentää sitä ja millä hinnalla.
- Osaat toteuttaa vähennyksen summaimella.
- Osaat selittää siirtimen multiplekserikerroksina ja kertojan
  osatuloina ja summainriveinä.
- Osaat laskea ALUn liput N, Z, C ja V ja tulkita ne etumerkittömälle
  ja etumerkilliselle laskulle.
