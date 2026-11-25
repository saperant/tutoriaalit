# Kombinaatiologiikka

Kombinaatiologiikan ulostulo riippuu vain sen nykyisistä syötteistä:
siinä ei ole muistia eikä kelloa. Se kuvataan joko jatkuvilla
sijoituksilla (`assign`) tai `always_comb`-lohkolla. Tämän luvun
tärkein sääntö on lyhyt: *jokaisen `always_comb`-lohkossa sijoitetun
signaalin on saatava arvo jokaisella suorituspolulla.* Muuten syntyy
salpa.

## assign ja always_comb

Yksinkertainen lauseke kirjoitetaan `assign`-lauseena. Kun logiikassa on
ehtoja, välimuuttujia tai useita ulostuloja, `always_comb` on
luettavampi. Lohko näyttää peräkkäiseltä ohjelmalta, mutta kuvaa
rinnakkaista logiikkaa. Simulaattori suorittaa sen aina, kun jokin sen
lukemista signaaleista muuttuu, ja synteesi muuttaa sen
porttiverkoksi, jolla on sama käyttäytyminen.

`always_comb` korvaa Verilogin `always @*`-lohkon ja tekee kolme asiaa
paremmin:

- herkkyyslista muodostuu automaattisesti, myös kutsuttujen funktioiden
  lukemista signaaleista
- lohko suoritetaan kerran simuloinnin alussa, joten ulostulot saavat
  arvon heti
- työkalu tarkistaa, ettei samaa signaalia sijoiteta muualla ja että
  lohkosta ei synny salpaa.

Lohkossa käytetään *estävää* sijoitusta `=`: arvo päivittyy heti, ja
seuraava rivi näkee uuden arvon. Se vastaa signaalin kulkua portista
toiseen.

## Ehdot ja case

`if`–`else` tuottaa prioriteettiketjun: ensimmäinen tosi ehto voittaa.
`case` valitsee yhden haaran lausekkeen arvon perusteella, ja kun haarat
sulkevat toisensa pois, synteesi tekee siitä rinnakkaisen
multiplekserin. SystemVerilogissa on kaksi määrettä, jotka kertovat
suunnittelijan aikeen:

| Määre | Lupaus | Simulaattori tarkistaa |
|-------|--------|------------------------|
| `unique case` | täsmälleen yksi haara osuu | ei osumaa tai useita osumia |
| `priority case` | ainakin yksi haara osuu, järjestys ratkaisee | ei osumaa |
| (ei määrettä) | – | – |

`unique` sallii synteesin olettaa, että haarat ovat toisensa
poissulkevia, ja jättää prioriteettilogiikan pois. Lupaus on
tarkistettava simuloinnissa. Jos lupaus ei pidä, simuloinnin ja
synteesin tulokset eroavat. Verilator tarkistaa lisäksi jo käännöksessä,
että `case`-lause kattaa kaikki arvot.

Ero näkyy syntyvässä rakenteessa. Kolmen ehdon `if`–`else if` -ketjusta
tulee kolme peräkkäistä multiplekseriä: viimeisenä kirjoitettu haara on
syvimmällä, ja sen data kulkee kaikkien läpi. `unique case` tuottaa
yhden leveän multiplekserin, jossa kaikki haarat ovat yhtä kaukana
ulostulosta.

```{.dot otsikko="Periaatekuva: if–else-ketjusta syntyy prioriteettiketju"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.5;
  node [shape=plaintext];
  d [label="d (else)"]; c [label="c"]; b [label="b"]; a [label="a"];
  y [label="y"];
  node [shape=trapezium, orientation=270, fixedsize=true,
        width=0.9, height=0.5];
  m3 [label="ehto3"]; m2 [label="ehto2"]; m1 [label="ehto1"];
  d -> m3; c -> m3; m3 -> m2; b -> m2; m2 -> m1; a -> m1; m1 -> y;
}
```

```{.dot otsikko="Periaatekuva: unique case tuottaa yhden rinnakkaisen multiplekserin"}
digraph {
  rankdir=LR; nodesep=0.15; ranksep=0.6;
  node [shape=plaintext];
  a [label="a"]; b [label="b"]; c [label="c"]; d [label="d"];
  s [label="valinta"]; y [label="y"];
  m [shape=trapezium, orientation=270, fixedsize=true,
     width=1.6, height=0.6, label="4:1"];
  a -> m; b -> m; c -> m; d -> m; m -> y;
  s -> m [style=dashed];
}
```

Seuraava ALU käyttää luettelotyyppiä operaatiokoodina. Koska
`unique case` kattaa kaikki kahdeksan arvoa, `default`-haaraa ei tarvita.

```{.systemverilog tiedosto="esimerkit/04-alu.sv" osa="alu"}
```

Etumerkillinen ylivuoto tunnistetaan etumerkkibiteistä: kahden
samanmerkkisen luvun summa ei saa vaihtaa merkkiä. Sama yhteenlaskin
toimii sekä etumerkillisille että etumerkittömille luvuille, ja vain
liput tulkitaan eri tavalla. Muuttuva siirto `a << b[SW-1:0]` tuottaa
siirtoverkon, jossa on `log2(W)` multiplekseritasoa.

Testipenkki käyttää tehtävää (`task`) toistuvaan koerakenteeseen:

```{.systemverilog tiedosto="esimerkit/04-alu.sv" osa="testipenkki"}
```

```{.tuloste tiedosto="esimerkit/04-alu.odotettu"}
```

## Jokerit: case inside ja casez

Dekooderissa vain osa biteistä ratkaisee: käskyn laji luetaan
ylimmistä biteistä, ja loput ovat operandeja. `case (…) inside`
vertaa lauseketta malleihin, joissa `?` tarkoittaa "ei väliä". Yhdessä
`unique`-määreen kanssa simulaattori tarkistaa, etteivät mallit mene
päällekkäin:

```{.systemverilog tiedosto="esimerkit/04-dekooderi.sv" osa="dekooderi"}
```

Vanhempi muoto on `casez`, jossa `?` (tai `z`) on jokeri. Sillä
kirjoitetaan usein prioriteettivalinta: mallit saavat mennä
päällekkäin, ja ensimmäinen osuva haara voittaa.

```{.systemverilog tiedosto="esimerkit/04-dekooderi.sv" osa="keskeytys"}
```

Testipenkki käy läpi kaikki 256 käskyä ja kaikki 16 pyyntöyhdistelmää:

```{.tuloste tiedosto="esimerkit/04-dekooderi.odotettu"}
```

Kolmas muoto `casex` pitää jokerina myös arvoa `X`. Silloin
alustamaton valintasignaali osuu ensimmäiseen haaraan ja virhe jää
simuloinnissa piiloon, joten `casex`:ää ei käytetä.

## Silmukat purkautuvat

`for`-silmukka `always_comb`-lohkossa ei ole aikaa kuluttava silmukka,
vaan käännösaikainen toisto. Synteesi purkaa sen, ja jokainen kierros
tuottaa oman logiikkansa. Rajojen on oltava vakioita. Silmukka sopii
esimerkiksi prioriteettienkooderiin, jossa korkein aktiivinen pyyntö
voittaa:

```{.systemverilog tiedosto="esimerkit/04-prioriteetti.sv" osa="enkooderi"}
```

Myöhemmät kierrokset ohittavat aiemmat sijoitukset, joten korkein
indeksi voittaa. Tuloksena on N-tasoinen prioriteettiketju.
Testipenkki vertaa kaikkia 256 syötettä eri tavalla kirjoitettuun
viitemalliin:

```{.tuloste tiedosto="esimerkit/04-prioriteetti.odotettu"}
```

## Salpa: puuttuva sijoitus

Jos `always_comb`-lohkon jollakin polulla signaali jää sijoittamatta,
sen on säilytettävä edellinen arvonsa. Muistava kombinaatiologiikka on
*salpa* (latch). Se on lähes aina virhe: salpa on herkkä
ajoitusongelmille, ajoitusanalyysi ei käsittele sitä hyvin, eikä
FPGA:ssa ole sille luontevaa rakennetta. Verilator tunnistaa salvan
`LATCH`-varoituksella:

```{.systemverilog tiedosto="esimerkit/04-salpa.ei-kaanny.sv"}
```

```{.tuloste tiedosto="esimerkit/04-salpa.odotettu"}
```

Alla vasemmalla on rakenne, jota virheellinen moduuli pyytää: salpa
päästää datan läpi, kun `valinta` on ykkönen, ja pitää arvonsa
muulloin. Oikealla on oletussijoituksella korjattu versio, joka on
pelkkä multiplekseri.

```{.dot otsikko="Periaatekuva: puuttuva haara tuottaa salvan, oletussijoitus multiplekserin"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.5;
  subgraph cluster_s { label="if (valinta) y = a;"; style=dashed;
    d1 [shape=plaintext, label="a"]; s1 [shape=plaintext, label="valinta"];
    y1 [shape=plaintext, label="y"];
    l [shape=box, label="salpa\nD   Q\nEN"];
    d1 -> l; s1 -> l [style=dashed]; l -> y1;
  }
  subgraph cluster_m { label="y = '0; if (valinta) y = a;"; style=dashed;
    d2 [shape=plaintext, label="a"]; z2 [shape=plaintext, label="'0"];
    s2 [shape=plaintext, label="valinta"]; y2 [shape=plaintext, label="y"];
    m [shape=trapezium, orientation=270, fixedsize=true, width=0.9,
       height=0.5, label="2:1"];
    d2 -> m; z2 -> m; s2 -> m [style=dashed]; m -> y2;
  }
}
```

Korjauksia on kaksi: jokaiseen `if`-lauseeseen `else`-haara ja jokaiseen
`case`-lauseeseen `default`, tai oletussijoitukset lohkon alkuun.
Jälkimmäinen on luotettavampi, koska se toimii myös, kun lohkoon
lisätään myöhemmin uusia haaroja.

## Käytännössä

- **Oletussijoitukset ensin.** Jokainen `always_comb`-lohko alkaa
  sijoittamalla kaikille ulostuloilleen oletusarvon. Sen jälkeen haarat
  muuttavat vain poikkeavat arvot. Malli estää salvat rakenteellisesti
  ja lyhentää koodia, kun useimmat ulostulot ovat useimmiten nollia.
- **`unique case` luettelotyypille.** Kun haarat ovat toisensa
  poissulkevia, `unique` kertoo sen lukijalle, simulaattorille ja
  synteesille. `priority` on harvinainen; tavallisesti prioriteetti
  kirjoitetaan `if`–`else if` -ketjuna.
- **Jokerit `inside`-muodolla, ei `casex`.** Uudessa koodissa
  jokerivertailu kirjoitetaan `case (…) inside` -lauseena ja `unique`-
  määreellä, kun mallit sulkevat toisensa pois. `casez` on tavallinen
  vanhassa koodissa; `casex` on virhe odottamassa.
- **`default` ei korvaa ajattelua.** `default`-haara, joka asettaa
  ulostulot nolliksi, poistaa salvan mutta voi peittää puuttuvan
  haaran. Luettelotyypin kanssa kaikkien arvojen luetteleminen ilman
  `default`-haaraa antaa lint-työkalun huomata, kun tyyppiin lisätään
  arvo.
- **Ei estäviä sijoituksia `always_ff`-lohkoon eikä ei-estäviä
  `always_comb`-lohkoon.** Sääntö on mekaaninen, ja sen rikkominen
  tuottaa eroja simuloinnin ja synteesin välille (luku 5).
- **Logiikan syvyys on ajoitusta.** Jokainen porttitaso lisää viivettä.
  Pitkä `if`-ketju, muuttuva siirto ja leveä vertailu pidentävät
  kriittistä polkua. Kombinaatiologiikan määrä kahden rekisterin välillä
  rajoittaa kellotaajuutta.
- **Viitemalli eri tavalla.** Testipenkin malli kirjoitetaan
  suoraviivaisesti ja eri rakenteella kuin suunnitelma. Saman koodin
  kopio mallina löytää vain kirjoitusvirheet.

## Itsearviointi

- Osaat kirjoittaa kombinaatiologiikan `assign`-lauseilla ja
  `always_comb`-lohkolla ja valita niiden välillä.
- Osaat selittää, milloin `always_comb` tuottaa salvan, ja estää sen
  oletussijoituksilla.
- Osaat käyttää `unique case` -lausetta ja selittää, mitä se lupaa
  synteesille.
- Osaat kirjoittaa dekooderin jokerimalleilla (`case inside`) ja
  selittää, miksi `casex`:ää ei käytetä.
- Osaat kirjoittaa `for`-silmukan, joka purkautuu rinnakkaiseksi
  logiikaksi, ja ennustaa sen tuottaman rakenteen.
- Osaat tunnistaa etumerkillisen ylivuodon summaimen etumerkkibiteistä.
