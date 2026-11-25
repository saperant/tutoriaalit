# Kellotusalueiden ylitys

Kellotusalue (clock domain) on joukko kiikkuja, joita ajaa sama kello.
Kun signaali siirtyy alueelta toiselle, vastaanottavan kiikun
asetus- ja pitoaikoja ei voi taata: lähettäjän reunat osuvat
vastaanottajan jakson mihin kohtaan tahansa. Kellotusalueen ylitys
(clock domain crossing, CDC) on digitaalisuunnittelun salakavalin
virhelähde, koska virhe ei näy simuloinnissa ja ilmenee piirissä
harvoin ja satunnaisesti.

## Metastabiilius

Kun kiikun syöte muuttuu asetusaikaikkunan sisällä, kiikku voi jäädä
hetkeksi välitilaan nollan ja ykkösen väliin: se on *metastabiili*.
Lopulta se asettuu jompaankumpaan arvoon, mutta asettumisaika on
satunnainen ja voi olla pidempi kuin kellojakso. Jos metastabiili arvo
leviää logiikkaan, eri kiikut voivat tulkita sen eri tavoin.

```{.ajoituskaavio otsikko="Periaatekuva: asetusikkunassa muuttuva syöte jättää kiikun hetkeksi välitilaan"}
{"signal": [
  {"name": "clk", "wave": "0...1.......0..."},
  {"name": "d (toinen alue)", "wave": "0...1..........."},
  {"name": "q", "wave": "0...x....=......", "data": ["0 tai 1"]}
], "config": {"hscale": 0.7}}
```

Metastabiiliutta ei voi estää, mutta sen todennäköisyyttä voi
pienentää. Keskimääräinen aika virheiden välillä (MTBF) kasvaa
eksponentiaalisesti sen ajan mukana, jonka kiikku saa asettua. Siksi
asynkroninen signaali viedään kahden peräkkäisen kiikun läpi ennen
käyttöä.

Simulaattori ei mallinna metastabiiliutta. Verilatorissa ja muissakin
RTL-simulaattoreissa kiikku näytteistää aina joko vanhan tai uuden
arvon. CDC-virheet löydetään siksi rakenteellisesti: oikeilla
malleilla, koodikatselmoinnilla ja CDC-analyysityökaluilla.

## Kahden kiikun tahdistin

Yksibittinen, hitaasti muuttuva tasosignaali (asetus, tilabitti, painonappi)
ylittää rajan kahden kiikun tahdistimella:

```{.systemverilog tiedosto="esimerkit/10-tahdistimet.sv" osa="taso"}
```

```{.dot otsikko="Kahden kiikun tahdistin: vain toisen kiikun lähtöä käytetään"}
digraph {
  rankdir=LR; nodesep=0.4; ranksep=0.7;
  d [shape=plaintext, label="d\n(toinen alue)"];
  f1 [shape=box, label="kiikku\nD   Q"];
  f2 [shape=box, label="kiikku\nD   Q"];
  q [shape=plaintext, label="q\n(oma alue)"];
  d -> f1; f1 -> f2 [label="meta: saa asettua\nyhden jakson"]; f2 -> q;
}
```

Tahdistimen ulostulo on vastaanottavan alueen signaali, joka voi
myöhästyä yhden jakson. Tahdistin toimii vain yksittäiselle bitille.
Jos kaksi bittiä tahdistetaan erikseen, toinen voi ehtiä perille
jaksoa aiemmin, ja vastaanottaja näkee hetken yhdistelmän, jota
lähettäjä ei koskaan lähettänyt.

## Pulssin siirto

Lyhyt pulssi nopealta alueelta voi kadota kokonaan hitaan kellon
reunojen väliin. Pulssi muutetaan siksi tasonvaihdoksi, taso
tahdistetaan, ja vastaanottaja tunnistaa vaihdoksen reunantunnistimella
(luku 5):

```{.systemverilog tiedosto="esimerkit/10-tahdistimet.sv" osa="pulssi"}
```

Pulssien välin on oltava riittävän pitkä, jotta edellinen tasonvaihdos
ehtii tahdistimen läpi ennen seuraavaa.

Alla olevassa simulaatiossa lähettävä kello on 2,5 kertaa
vastaanottavaa nopeampi. Yhden jakson `pulssi_a` kääntää tason
`taso_a`, taso kulkee vastaanottajan kahden kiikun läpi (`meta`,
`taso_b`), ja muutoksesta syntyy vastaanottajan kellon mittainen
`pulssi_b`. Pelkkä `pulssi_a` olisi mahtunut `clk_b`:n kahden reunan
väliin ja kadonnut.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/10-pulssi.json" otsikko="Pulssin siirto nopealta kellolta hitaalle tasonvaihdoksena"}
```

## Kättely monibittiselle arvolle

Monibittinen arvo siirretään niin, että data on vakaa koko siirron ajan
ja vain yksibittinen ohjaussignaali ylittää rajan. Nelivaiheinen
kättely: lähettäjä asettaa datan ja nostaa pyynnön, vastaanottaja
näkee tahdistetun pyynnön, lukee datan ja nostaa kuittauksen. Sen
jälkeen lähettäjä laskee pyynnön ja vastaanottaja kuittauksen.

```{.systemverilog tiedosto="esimerkit/10-tahdistimet.sv" osa="kattely"}
```

`pito` ylittää rajan ilman tahdistinta, mutta se on vakaa aina, kun
vastaanottaja lukee sitä: tahdistettu pyyntö saapuu vasta, kun data on
ollut paikallaan vähintään kaksi vastaanottajan jaksoa. Kättely on
hidas, sillä yksi siirto vie useita jaksoja molemmilla kelloilla, mutta
se toimii mille tahansa kellosuhteelle.

Alla oleva kaavio näyttää yhden siirron vaiheet periaatteena. Kaavio
ei ole tietyn kellon tahdissa: kukin `_t`-signaali on toisen alueen
kellolla tahdistettu kopio, joka seuraa alkuperäistä parin jakson
viiveellä.

```{.ajoituskaavio otsikko="Nelivaiheinen kättely kellotusalueiden välillä"}
{"signal": [
  ["Lähettäjä",
    {"name": "pito", "wave": "x=..........x", "data": ["arvo"]},
    {"name": "pyynto", "wave": "01.....0....."},
    {"name": "kuittaus_t", "wave": "0....1.....0."}
  ],
  {},
  ["Vastaanottaja",
    {"name": "pyynto_t", "wave": "0..1.....0..."},
    {"name": "kuittaus", "wave": "0...1.....0.."}
  ]
], "config": {"hscale": 0.8}}
```

Testipenkissä kellot ovat 100 MHz ja noin 27 MHz, eikä niillä ole
yhteistä jaksoa:

```{.tuloste tiedosto="esimerkit/10-tahdistimet.odotettu"}
```

## Asynkroninen FIFO

Jatkuva datavirta alueelta toiselle kulkee asynkronisen FIFOn kautta.
Muisti on kaksiporttinen: kirjoitus käyttää kirjoituskelloa ja luku
lukukelloa. Ongelma on osoittimissa. Kirjoittaja tarvitsee
lukuosoitteen täyden ehdon laskemiseen, ja lukija tarvitsee
kirjoitusosoitteen tyhjän ehdon laskemiseen.

Binäärinen osoitin ei voi ylittää rajaa: siirtymässä 0111 → 1000
kaikki bitit vaihtuvat, ja tahdistin voi napata minkä tahansa
välimuodon. Osoittimet muunnetaan siksi *Gray-koodiksi*, jossa
peräkkäiset arvot eroavat vain yhdellä bitillä. Tahdistettu Gray-
osoitin on aina joko vanha tai uusi arvo:

```{.dot otsikko="Asynkronisen FIFOn rakenne: vain Gray-osoittimet ylittävät rajan"}
digraph {
  rankdir=LR; nodesep=0.35; ranksep=0.7; newrank=true;
  subgraph cluster_k { label="kirjoituskello"; style=dashed;
    kos [label="kirjoitusosoitin\n(binääri + Gray)"];
    taynna [label="täynnä?", shape=diamond];
  }
  subgraph cluster_l { label="lukukello"; style=dashed;
    los [label="lukuosoitin\n(binääri + Gray)"];
    tyhja [label="tyhjä?", shape=diamond];
  }
  muisti [label="kaksiporttinen\nmuisti", penwidth=2];
  t1 [label="2 kiikkua"];
  t2 [label="2 kiikkua"];
  { rank=same; kos; taynna; }
  { rank=same; muisti; t1; t2; }
  { rank=same; los; tyhja; }
  kos -> muisti [label="data"];
  muisti -> los [label="data"];
  kos -> t1 [label="Gray"];
  t1 -> tyhja;
  taynna -> t2 [dir=back];
  t2 -> los [dir=back, label="Gray"];
  kos -> taynna [constraint=false];
  los -> tyhja [constraint=false];
}
```

```{.systemverilog tiedosto="esimerkit/10-asynk-fifo/asynk_fifo.sv" osa="gray"}
```

Kirjoituspuoli laskee täyden ehdon omasta osoittimestaan ja
tahdistetusta lukuosoittimesta. Gray-koodissa kierroksen ero näkyy
kahden ylimmän bitin kääntymisenä:

```{.systemverilog tiedosto="esimerkit/10-asynk-fifo/asynk_fifo.sv" osa="kirjoitus"}
```

```{.systemverilog tiedosto="esimerkit/10-asynk-fifo/asynk_fifo.sv" osa="luku"}
```

Osoittimet tahdistetaan kahden kiikun ketjuilla. Rajan ylittävät
Gray-osoittimet tulevat suoraan rekistereistä, eivät kombinaatiologiikasta,
koska logiikan piikit voisivat näkyä vastaanottajalle:

```{.systemverilog tiedosto="esimerkit/10-asynk-fifo/asynk_fifo.sv" osa="tahdistus"}
```

Tahdistus viivästää osoittimia, joten liput ovat *pessimistisiä*:
kirjoittaja voi nähdä jonon täytenä, vaikka lukija on jo vapauttanut
paikan. Tämä on turvallista, koska tieto ei katoa eikä jonosta lueta
olematonta dataa.

Testipenkki kirjoittaa 300 tavua nopealla kellolla ja lukee ne
hitaammalla:

```{.systemverilog tiedosto="esimerkit/10-asynk-fifo/testipenkki.sv"}
```

```{.tuloste tiedosto="esimerkit/10-asynk-fifo.odotettu"}
```

Rakenne on Clifford Cummingsin artikkelista *Simulation and Synthesis
Techniques for Asynchronous FIFO Design*, joka on aiheen
perusteos.

## Käytännössä

- **Valitse menetelmä datan mukaan.** Hitaasti muuttuva bitti: kahden
  kiikun tahdistin. Yksittäinen tapahtuma: pulssin siirto. Satunnainen
  monibittinen arvo: kättely. Jatkuva virta: asynkroninen FIFO.
  Laskurin arvo: Gray-koodi ja tahdistin.
- **Ei logiikkaa ennen tahdistinta.** Rajan ylittävän signaalin on
  lähdettävä suoraan kiikusta. Kombinaatiologiikan piikit voivat osua
  vastaanottajan reunaan, vaikka logiikan lopputulos olisi oikea.
- **Merkitse tahdistimet.** Tahdistinkiikut merkitään attribuutilla
  (Xilinxillä `ASYNC_REG`), jotta synteesi sijoittaa ne vierekkäin eikä
  monista niitä. Ajoitusanalyysille kerrotaan, että rajan ylittävät
  polut ovat asynkronisia (`set_max_delay -datapath_only` tai
  `set_clock_groups -asynchronous`).
- **Yksi tahdistin signaalia kohden.** Jos samaa signaalia tahdistetaan
  kahdessa paikassa, kaksi kopiota voivat olla eri mieltä yhden jakson
  ajan.
- **Keskitä ylitykset.** Kellotusalueiden ylitykset kootaan muutamaan
  tunnettuun moduuliin (tahdistin, pulssi, kättely, FIFO), jotka on
  tarkistettu kerran. CDC-työkalut (esim. Questa CDC, Spyglass CDC)
  tunnistavat nämä rakenteet ja varoittavat muista.
- **Testaa ilman yhteistä jaksoa.** Testipenkin kellot valitaan niin,
  että niiden suhde ei ole kokonaisluku. Silloin reunat osuvat
  jakson eri kohtiin, ja ainakin protokollan virheet löytyvät.

## Itsearviointi

- Osaat selittää metastabiiliuden ja sen, miksi kaksi kiikkua riittää
  käytännössä.
- Osaat valita oikean ylitysmenetelmän tasolle, pulssille,
  monibittiselle arvolle ja datavirralle.
- Osaat toteuttaa pulssin siirron ja nelivaiheisen kättelyn.
- Osaat selittää, miksi asynkronisen FIFOn osoittimet Gray-koodataan
  ja miksi liput ovat pessimistisiä.
- Osaat kertoa, mitkä CDC-virheet simulointi löytää ja mitkä eivät.
