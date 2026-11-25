# Aika ja järjestys

Yhdellä koneella tapahtumilla on luonnollinen järjestys: prosessori
tekee ne yksi kerrallaan, ja kello kertoo, mikä tapahtui ensin.
Hajautetussa järjestelmässä kummallakaan solmulla ei ole koko kuvaa.
Kellot käyvät eri tahtiin, eikä toisen solmun kellosta saa tietoa
muuten kuin viestillä, joka on jo matkalla vanhentunut. Tämä luku
näyttää, miksi fyysiseen aikaan nojaava järjestys pettää, ja esittelee
kolme loogista kelloa, jotka säilyttävät sen järjestyksen, jolla on
merkitystä: syy-seuraussuhteen.

## Fyysiset kellot

Tietokoneen kello on kvartsikide, jonka taajuus poikkeaa nimellisestä
tyypillisesti kymmeniä miljoonasosia (ppm) lämpötilan ja yksilön
mukaan. 50 ppm on neljä sekuntia vuorokaudessa. Kelloja synkronoidaan
NTP:llä (*Network Time Protocol*), joka arvioi verkon viiveen
kiertoajasta ja korjaa kelloa vähitellen. Lähiverkossa NTP pääsee
yleensä millisekunnin tarkkuuteen, internetin yli kymmeniin
millisekunteihin, ja virhetilanteessa kello voi hypätä sekunteja kerralla
eteen- tai taaksepäin. PTP (IEEE 1588) ja laitteistotuki pääsevät
mikrosekunteihin, ja Googlen Spanner käyttää atomikelloja ja
GPS-vastaanottimia sekä kertoo kellon epävarmuuden välinä.

Seinäkello (`CLOCK_REALTIME`) voi siis siirtyä taaksepäin, eikä sitä
pidä käyttää kestojen mittaamiseen; siihen käytetään monotonista kelloa
(`CLOCK_MONOTONIC`, ks. *Verkko-ohjelmointi*). Monotoninenkaan kello ei
kuitenkaan auta vertaamaan kahden koneen tapahtumia, koska sen
nollakohta on koneen oma.

Simulaattorissa jokaisella solmulla on alkupoikkeama ja ajautuma,
jotka arvotaan siemenestä asetusten `poikkeama_max` ja `ajautuma_max`
rajoissa. `Yhteys::kello()` palauttaa solmun oman näkemyksen ajasta.

## Viimeinen kirjoitus voittaa

Yleinen tapa ratkaista samanaikaiset kirjoitukset on *viimeinen
kirjoitus voittaa* (*last writer wins*, LWW): jokainen kirjoitus saa
aikaleiman, ja suurin leima voittaa. Sääntö on yksinkertainen ja
vaihdannainen, joten replikat päätyvät samaan arvoon riippumatta
viestien järjestyksestä. Ongelma on aikaleima.

Kokeessa varasto säilyttää arvon, jolla on suurin leima:

```{.cpp tiedosto="esimerkit/03-kellot.cpp" osa="varasto"}
```

Kirjoittaja A kirjoittaa hetkellä 100. Kirjoittaja B lukee hetkellä
130, näkee A:n arvon ja kirjoittaa vasta sitten. B:n kirjoitus on
syy-seuraussuhteessa A:n jälkeen: B on nähnyt A:n arvon ja korvaa sen
tietoisesti. Leima on joko fyysinen kello, Lamportin kello tai
hybridikello:

```{.cpp tiedosto="esimerkit/03-kellot.cpp" osa="kirjoittaja"}
```

```{.tuloste tiedosto="esimerkit/03-kellot.odotettu"}
```

Kun kellot ovat samassa ajassa, fyysinen leima toimii. Kun poikkeama
on 50 ms, neljäsosa B:n kirjoituksista häviää, koska B:n kello on
jäljessä A:n kelloa enemmän kuin kirjoitusten väli. Häviö on
hiljainen: kumpikin kirjoitus kuitattiin, mutta myöhempi katosi. Tämä
on Cassandran ja monien muiden LWW-järjestelmien tunnettu
ominaisuus, ja syy siihen, miksi niissä vaaditaan tarkasti
synkronoidut kellot.

## Lamportin kello

Lamport (1978) määritteli *tapahtui ennen* -relaation (→):

1. Jos a ja b ovat saman prosessin tapahtumia ja a on ensin, a → b.
2. Jos a on viestin lähetys ja b saman viestin vastaanotto, a → b.
3. Relaatio on transitiivinen: jos a → b ja b → c, niin a → c.

Jos kumpikaan ei tapahtunut ennen toista, tapahtumat ovat
*samanaikaisia* ($a \parallel b$). Samanaikaisuus ei tarkoita samaa
kellonaikaa, vaan sitä, ettei kumpikaan voinut vaikuttaa toiseen.

Lamportin kello on laskuri, joka kasvaa jokaisessa tapahtumassa ja
hyppää vastaanotossa viestin leiman yli:

```{.cpp tiedosto="esimerkit/yhteinen/kellot.hpp" osa="lamport"}
```

Kello takaa, että jos a → b, niin L(a) < L(b). Kääntäen ei päde:
pienempi leima ei kerro, että tapahtuma vaikutti toiseen. Kun leimaan
liitetään solmun tunniste tasapelin ratkaisijaksi, saadaan
kokonaisjärjestys, joka on yhteensopiva syy-seuraussuhteen kanssa.
Edellisessä kokeessa B:n kirjoitus voitti aina Lamportin leimalla, koska
B oli lukenut A:n leiman ennen kirjoitusta.

Kolme prosessia ja kolme viestiä; luvut ovat Lamportin kellon arvoja
tapahtumissa. Lähetys kasvattaa kelloa ja kantaa leiman viestissä,
vastaanotto hyppää leiman yli. Kun vastaanotto ja seuraava lähetys
osuvat samaan kohtaan, arvot on erotettu pilkulla: P2 saa m1:n
arvolla 2 ja lähettää m2:n arvolla 3.

```{.dot otsikko="Lamportin kellot kolmella prosessilla"}
digraph {
  nodesep=1.0; ranksep=0.32;
  node [shape=point, width=0.04, color="#5B6B70"];
  edge [arrowhead=none, style=dashed, color="#B8C4C8"];
  t0 [shape=box, width=1, label="P1"];
  t0 -> t0_0 -> t0_1 -> t0_2 -> t0_3;
  t1 [shape=box, width=1, label="P2"];
  t1 -> t1_0 -> t1_1 -> t1_2 -> t1_3;
  t2 [shape=box, width=1, label="P3"];
  t2 -> t2_0 -> t2_1 -> t2_2 -> t2_3;
  {rank=same; t0_0; t1_0; t2_0;}
  {rank=same; t0_1; t1_1; t2_1;}
  {rank=same; t0_2; t1_2; t2_2;}
  {rank=same; t0_3; t1_3; t2_3;}
  {rank=same; t0; t1; t2;}
  t0 -> t1 -> t2 [style=invis];
  t0_0 -> t1_1 [style=solid, arrowhead=normal, color="#1F2A2E", constraint=false, label="m1, leima 1"];
  t1_1 -> t2_2 [style=solid, arrowhead=normal, color="#1F2A2E", constraint=false, label="m2, leima 3"];
  t2_2 -> t0_3 [style=solid, arrowhead=normal, color="#1F2A2E", constraint=false, label="m3, leima 5"];
  t0_0 [xlabel="1"]; t1_1 [xlabel="2, 3"];
  t2_2 [xlabel="4, 5"]; t0_3 [xlabel="6"];
}
```

## Vektorikello

Vektorikello pitää laskurin jokaiselle solmulle. Solmu kasvattaa omaa
laskuriaan, ja vastaanotossa vektorit yhdistetään alkioittain
maksimilla. Kahta vektoria verrataan alkioittain: V(a) < V(b), jos
jokainen alkio on pienempi tai yhtä suuri ja ainakin yksi pienempi.
Jos kumpikaan ei ole pienempi, tapahtumat ovat samanaikaisia:

```{.cpp tiedosto="esimerkit/yhteinen/kellot.hpp" osa="vektori"}
```

Vektorikello tunnistaa relaation tarkasti: a → b, jos ja vain jos
V(a) < V(b). Hinta on koko: vektorissa on yksi alkio jokaista solmua
kohden, ja dynaamisessa järjestelmässä solmujen joukko muuttuu.

Esimerkki ajaa samat tapahtumat kolmessa prosessissa kummallakin
kellolla. Apufunktiot `paikallinen`, `laheta` ja `vastaanota`
päivittävät molemmat kellot edellä kuvatulla tavalla:

```{.cpp tiedosto="esimerkit/03-vektorikellot.cpp" osa="tapahtumat"}
```

```{.tuloste tiedosto="esimerkit/03-vektorikellot.odotettu" asti="g P2"}
```

Samat tapahtumat aikajanoilla vektoreineen:

```{.dot otsikko="Tulosteen tapahtumat a–g ja niiden vektorikellot"}
digraph {
  nodesep=1.2; ranksep=0.3;
  node [shape=point, width=0.04, color="#5B6B70"];
  edge [arrowhead=none, style=dashed, color="#B8C4C8"];
  t0 [shape=box, width=1, label="P0"];
  t0 -> t0_0 -> t0_1 -> t0_2 -> t0_3 -> t0_4;
  t1 [shape=box, width=1, label="P1"];
  t1 -> t1_0 -> t1_1 -> t1_2 -> t1_3 -> t1_4;
  t2 [shape=box, width=1, label="P2"];
  t2 -> t2_0 -> t2_1 -> t2_2 -> t2_3 -> t2_4;
  {rank=same; t0_0; t1_0; t2_0;}
  {rank=same; t0_1; t1_1; t2_1;}
  {rank=same; t0_2; t1_2; t2_2;}
  {rank=same; t0_3; t1_3; t2_3;}
  {rank=same; t0_4; t1_4; t2_4;}
  {rank=same; t0; t1; t2;}
  t0 -> t1 -> t2 [style=invis];
  t0_1 -> t1_2 [style=solid, arrowhead=normal, color="#1F2A2E", constraint=false, label="m1"];
  t1_3 -> t2_4 [style=solid, arrowhead=normal, color="#1F2A2E", constraint=false, label="m2"];
  t0_0 [xlabel="a [1,0,0]"]; t0_1 [xlabel="b [2,0,0]"];
  t1_0 [xlabel="c [0,1,0]"]; t1_2 [xlabel="d [2,2,0]"];
  t1_3 [xlabel="e [2,3,0]"];
  t2_0 [xlabel="f [0,0,1]"]; t2_4 [xlabel="g [2,3,2]"];
}
```

Kuvassa tapahtumasta toiseen on syy-seurausketju täsmälleen silloin,
kun toiseen pääsee seuraamalla aikajanoja alaspäin ja viestejä nuolen
suuntaan. Pisteestä f ei pääse pisteeseen d eikä päinvastoin.

```{.tuloste tiedosto="esimerkit/03-vektorikellot.odotettu" alkaen="pari" asti="c-d"}
```

Parit näyttävät kellojen eron. Tapahtumat a ja g ovat ketjussa
viestien m1 ja m2 kautta, ja kumpikin kello järjestää ne oikein.
Tapahtumat f ja d ovat samanaikaisia, mutta Lamportin leimoista
1 < 3 voisi päätellä, että f oli ensin. Vain vektorikello kertoo, ettei
kumpikaan voinut vaikuttaa toiseen.

## Samanaikaiset versiot

Samanaikaisuuden tunnistaminen on hyödyllistä, kun replikat ottavat
kirjoituksia vastaan toisistaan tietämättä. Amazonin Dynamo (2007)
versioi jokaisen arvon vektorikellolla. Uusi versio korvaa vanhat,
jotka se kattaa, ja samanaikaiset versiot säilyvät *sisaruksina*
(*siblings*), kunnes asiakas yhdistää ne:

```{.cpp tiedosto="esimerkit/03-vektorikellot.cpp" osa="sisarukset"}
```

```{.cpp tiedosto="esimerkit/03-vektorikellot.cpp" osa="kori"}
```

```{.tuloste tiedosto="esimerkit/03-vektorikellot.odotettu" alkaen="r0 kirjoittaa"}
```

Replika 1 lisäsi leivän nähtyään
maidon, joten sen versio korvasi alkuperäisen. Replika 2 lisäsi kahvin
näkemättä leipää, joten versiot jäivät rinnakkain. Asiakas yhdisti
sisarukset, ja yhdistetyn version kello kattaa molemmat. LWW olisi
valinnut toisen ja hukannut leivän tai kahvin. Seuraava luku esittelee
tietorakenteet, joissa yhdistäminen tapahtuu automaattisesti.

## Hybridikello

Loogiset kellot eivät kerro mitään seinäkellosta, mutta ihmiset ja
monet sovellukset haluavat aikaleiman, joka on lähellä oikeaa aikaa.
Hybridikello (*hybrid logical clock*, HLC; Kulkarni ym. 2014) yhdistää
molemmat. Leima on pari (l, c): l seuraa suurinta nähtyä fyysistä
aikaa ja c on laskuri, joka erottaa tapahtumat, joilla on sama l:

```{.cpp tiedosto="esimerkit/yhteinen/kellot.hpp" osa="hlc"}
```

HLC:llä on Lamportin kellon takuu (a → b ⇒ H(a) < H(b)), ja l poikkeaa
solmun fyysisestä kellosta enintään kellojen suurimman eron verran.
Kellokokeessa hybridileima ei hävinnyt kertaakaan. CockroachDB ja
YugabyteDB käyttävät HLC:tä transaktioiden aikaleimoina, ja MongoDB
käyttää samaa ajatusta istuntojensa syy-seuraustakuuseen.

## Käytännössä

- **Älä järjestä tapahtumia eri koneiden seinäkelloilla.** Jos
  järjestyksellä on merkitystä, käytä loogista kelloa, hybridikelloa
  tai yhtä solmua, joka antaa järjestysnumerot (johtaja, ks. *Raft*).
- **LWW hukkaa kirjoituksia.** Se sopii arvoille, joiden menetys on
  hyväksyttävää (välimuisti, viimeisin sijainti), mutta ei laskureille
  eikä joukoille. Jos LWW:tä käytetään, kellot pitää valvoa ja
  poikkeama rajata.
- **Vektorikellot kasvavat.** Dynamon tapaiset järjestelmät käyttävät
  pisteversioituja vektoreita (*dotted version vectors*) ja karsivat
  vanhoja alkioita. Pienessä kiinteässä joukossa tavallinen vektori
  riittää.
- **Kerro epävarmuus.** Spannerin TrueTime palauttaa välin [aikaisin,
  myöhäisin], ja transaktio odottaa välin yli ennen sitoutumista. Ilman
  epävarmuuden rajaa fyysisen ajan järjestykselle ei ole takuuta.
- **Mittaa kestot monotonisella kellolla.** Aikakatkaisut ja viiveet
  lasketaan aina monotonisesta kellosta.

## Itsearviointi

- Osaat selittää, miksi fyysiset kellot poikkeavat toisistaan ja mitä
  NTP voi ja ei voi taata.
- Osaat määritellä tapahtui ennen -relaation ja samanaikaisuuden ja
  toteuttaa Lamportin kellon.
- Osaat toteuttaa vektorikellon, vertailla kahta vektoria ja käyttää
  sitä samanaikaisten versioiden tunnistamiseen.
- Osaat näyttää, miten LWW fyysisillä aikaleimoilla hukkaa
  kirjoituksen, ja korjata sen loogisella tai hybridikellolla.
- Osaat kertoa, mitä hybridikello takaa ja missä sitä käytetään.
