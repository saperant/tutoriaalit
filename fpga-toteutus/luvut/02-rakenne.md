# FPGA:n rakenne

FPGA ei koostu porteista vaan muutamasta toistuvasta rakennuspalikasta.
Synteesi kuvaa RTL:n niihin, ja suunnittelijan on hyvä tuntea ne,
koska palikoiden ominaisuudet määräävät, mikä on halpaa ja mikä
kallista.

## Logiikkasolu

Perusyksikkö on **logiikkasolu** (logic cell, iCE40:ssä `ICESTORM_LC`).
Siinä on

- **hakutaulu** (look-up table, LUT): neljän tulon LUT on 16 bitin
  muisti, jonka osoitteena ovat tulot. Sillä voi toteuttaa minkä tahansa
  neljän muuttujan Boolen funktion samalla viiveellä.
- **kiikku**, jonka tulona on LUT:n lähtö tai solun tulo. Kiikussa on
  valinnaiset sallinta-, asetus- ja nollaustulot.
- **kantologiikka** (carry, `SB_CARRY`): nopea, erillinen reitti
  summaimen muistibitille viereiseen soluun.

Kuvassa on solun rakenne. Kiikun ohi kulkeva reitti tekee solusta
kombinatorisen, ja kantoketju jatkuu suoraan viereiseen soluun
reititysverkon ohi.

```{.dot otsikko="iCE40:n logiikkasolu (ICESTORM_LC): LUT4, kantologiikka ja kiikku"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.4;
  tulot [label="I0 I1 I2 I3", shape=plaintext, style=""];
  lut [label="LUT4\n16 bitin muisti"];
  carry [label="SB_CARRY"];
  ff [label="kiikku\n(sallinta, nollaus)"];
  mux [label="valitsin", shape=trapezium, orientation=270];
  ulos [label="O", shape=plaintext, style=""];
  cin [label="kanto sisään\n(edellinen solu)", shape=plaintext, style=""];
  cout [label="kanto ulos\n(seuraava solu)", shape=plaintext, style=""];
  ohjaus [label="kello, sallinta,\nnollaus (yhteiset\nkoko lohkolle)", shape=plaintext, style=""];
  tulot -> lut; tulot -> carry [label="I1, I2"];
  cin -> carry; carry -> cout;
  cin -> lut [label="I3:n tilalle", style=dashed];
  lut -> ff; lut -> mux [label="ohitus"]; ff -> mux; mux -> ulos;
  ohjaus -> ff [style=dashed];
}
```

Kahdeksan solua muodostaa logiikkalohkon (PLB), jonka solut jakavat
kellon, sallinnan ja nollauksen. Siksi samassa lohkossa voivat olla
vain kiikut, joilla on samat ohjaussignaalit. Suunnittelu, jossa
jokaisella rekisterillä on oma sallintansa, kuluttaa lohkoja
tehottomasti.

Suuremmissa piireissä LUT on yleensä 6-tuloinen (AMD, Intel), ja
lohkoissa on enemmän soluja. Periaate on sama.

## Kantoketju

Summain on yleisin aritmeettinen rakenne, ja yleiskäyttöinen reititys
olisi sille hidas. Siksi solut on ketjutettu omalla kantolinjallaan:
jokainen bitti käyttää yhden LUT:n ja kantologiikan, ja muistibitti
etenee viereiseen soluun ilman reititysverkkoa.

```{.systemverilog tiedosto="esimerkit/02-kertyma/kertyma.sv" osa="kertyma"}
```

```{.tuloste tiedosto="esimerkit/raportit/kertyma.odotettu"}
```

16-bittinen summain tarvitsee 15 kantosolua: alimman bitin muistitulo
on vakio. Koko kertymä vie 18 logiikkasolua ja toimii noin 100 MHz:llä.
Kantoketju rajoittaa sijoittelua: ketjun solut ovat peräkkäin samassa
sarakkeessa, ja hyvin pitkä ketju voi ylittää lohkon rajan.

Testipenkki laskee odotetun summan rinnalla ja tarkistaa sen joka
jaksolla:

```{.systemverilog tiedosto="esimerkit/02-kertyma/testipenkki.sv" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/02-kertyma.odotettu"}
```

## Lohko-RAM

Muistia ei kannata rakentaa kiikuista. iCE40UP5K:ssa on 30
**lohko-RAMia** (embedded block RAM, `SB_RAM40_4K`), kukin 4 kilobittiä.
Lohkon leveys ja syvyys valitaan: 256 × 16, 512 × 8, 1024 × 4 tai
2048 × 2 bittiä. Lohkossa on erillinen luku- ja kirjoitusportti, ja
molemmat ovat **synkronisia**: luettu tieto tulee ulos vasta kellon
reunan jälkeen. Tämä on tärkein yksittäinen asia, joka koodaustavan on
huomioitava (luku 4).

Lisäksi UltraPlus-piireissä on neljä 256 kilobitin yksiporttista RAMia
(`SB_SPRAM256KA`) suurta puskurimuistia varten. Ne on instansioitava
suoraan; synteesi ei päättele niitä.

Suuremmissa piireissä on myös **hajautettua RAMia** (distributed RAM):
LUT toimii pienenä muistina, jota voi lukea kombinatorisesti. iCE40:ssä
sitä ei ole.

## DSP-lohko

Kertolasku logiikkasoluilla on kallis: 8 × 8 bitin kertoja vie yli 150
solua. Siksi FPGA:issa on **DSP-lohkoja** (iCE40UP5K:ssa kahdeksan
`SB_MAC16`-lohkoa). Lohkossa on 16 × 16 bitin kertoja, 32 bitin
summain–kertymä ja valinnaiset rekisterit tuloissa ja lähdössä. Yksi
lohko korvaa satoja logiikkasoluja ja on myös nopeampi. Luku 4 näyttää,
miten kertoja päätyy DSP-lohkoon.

## Kellot

Kellon on saavuttava kaikkiin kiikkuihin yhtä aikaa. Tavallinen
reititys ei siihen pysty, joten piirissä on kahdeksan **globaalia
verkkoa** (`SB_GB`), joilla on pieni ja tasainen viive koko piirin yli.
nextpnr sijoittaa kellot niihin automaattisesti. Globaaleja verkkoja
käytetään myös suuren tuulettuvuuden signaaleille, kuten nollaukselle.

Kellotaajuuden muuttamiseen on **PLL** (phase-locked loop, `SB_PLL40`):
se tuottaa tulokellosta toisen taajuuden kertomalla ja jakamalla (luku
7). UltraPlus-piirissä on myös sisäiset oskillaattorit (48 MHz ja
10 kHz), joten piiri toimii ilman ulkoista kidettä, joskin
epätarkemmin.

## IO-lohkot

Jokaisella nastalla on IO-lohko (`SB_IO`). Siinä ovat puskuri,
valinnaiset rekisterit tuloon ja lähtöön sekä asetukset, kuten
jännitestandardi, ylösvetovastus ja DDR-tila. IO-rekisterit ovat
hyödyllisiä: kun rekisteri on nastan vieressä, signaalin ajoitus
nastalla ei riipu sisäisestä reitityksestä.

Nastojen määrä on todellinen rajoite. iCE40UP5K:n SG48-kotelossa on
39 käyttäjän IO-nastaa. Siksi tämän tutoriaalin esimerkit on
suunniteltu kapeilla liitännöillä: 16 + 16 bitin kertoja 32 bitin
tuloksineen ei mahtuisi koteloon.

## Konfigurointi

Bittivirta luetaan käynnistyksessä ulkoisesta SPI-flashista tai
syötetään piirille suoraan. iCE40:ssä konfiguraatiomuisti on SRAMia,
joten piiri unohtaa sen virran katketessa. Konfigurointi kestää
kymmeniä millisekunteja, minkä jälkeen kaikki kiikut ovat alkuarvoissaan
ja logiikka käynnistyy.

## Käytännössä

- **Ajattele palikoina.** Ennen kuin kirjoitat RTL:ää, mieti, mihin
  palikoihin se päätyy: LUT:t ja kiikut, kantoketju, lohko-RAM tai DSP.
  Kertolasku ilman vapaata DSP-lohkoa ja muisti ilman lohko-RAMia ovat
  kalliita.
- **Lue piirin tiedot.** Resurssit (LUT, RAM, DSP, PLL, IO) ja niiden
  ominaisuudet ovat valmistajan datalehdessä. Resurssit loppuvat
  yleensä tässä järjestyksessä: IO-nastat, DSP-lohkot, lohko-RAM,
  logiikkasolut.
- **Jätä tilaa.** Yli 80 %:n käyttöaste vaikeuttaa reititystä ja
  heikentää ajoitusta. Valitse piiri, johon suunnitelma mahtuu
  väljästi, tai varaa tila tuleville muutoksille.
- **Ohjaussignaalit yhteisiksi.** Kiikut, joilla on sama kello,
  sallinta ja nollaus, pakkautuvat samoihin lohkoihin.

## Itsearviointi

- Osaat kertoa, mitä logiikkasolussa on ja miksi neljän tulon LUT
  toteuttaa minkä tahansa neljän muuttujan funktion.
- Osaat selittää, miksi summain käyttää kantoketjua ja kertolasku
  DSP-lohkoa.
- Osaat kertoa lohko-RAMin koot ja sen, että luku on synkroninen.
- Osaat kertoa, mihin globaaleja verkkoja, PLL:ää ja IO-lohkojen
  rekistereitä käytetään.
