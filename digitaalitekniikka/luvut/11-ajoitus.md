# Ajoitus ja kellotus

Synkroninen piiri toimii oikein, jos jokainen rekisterien välinen
logiikkapolku ehtii asettua kellojakson aikana. Tämä luku laskee,
kuinka nopea kello voi olla, ja näyttää, miten suunnittelija nopeuttaa
piiriä.

## Ajoitusyhtälöt

Tarkastellaan polkua kiikusta A logiikan läpi kiikkuun B. Reunalla A
päivittyy viiveellä $t_{cq}$, logiikka laskee ajan $t_{logiikka}$, ja
tuloksen on oltava B:n tulossa asetusajan $t_{su}$ ennen seuraavaa
reunaa:

$$T \geq t_{cq} + t_{logiikka,max} + t_{su}$$

```{.ajoituskaavio otsikko="Asetusehto: lähettävältä reunalta vastaanottavalle. Jakson on katettava kiikun viive, logiikan viive ja asetusaika; loppu on marginaalia."}
{"signal": [
  {"name": "clk", "wave": "lh......l......h."},
  {"name": "A:n lähtö", "wave": "=..=.............", "data": ["vanha", "uusi"]},
  {"name": "B:n tulo", "wave": "=.........=......", "data": ["vanha", "uusi"]},
  {"name": "jakso T", "wave": "z2.3......4..5.z.", "data": ["t_cq", "t_logiikka", "vara", "t_su"]}
], "config": {"hscale": 0.75}}
```

Pisin tällainen polku on *kriittinen polku*, ja se määrää suurimman
kellotaajuuden $f_{max} = 1/T_{min}$. Aika, joka jaksosta jää yli, on
*marginaali* (*slack*); negatiivinen marginaali on asetusrike.

Toinen ehto koskee lyhintä polkua. B näytteistää vanhan arvon samalla
reunalla, jolla A muuttuu. Uusi arvo ei saa ehtiä B:hen ennen kuin
pitoaika $t_h$ on kulunut:

$$t_{cq} + t_{logiikka,min} \geq t_h$$

```{.ajoituskaavio otsikko="Pitoehto: sama reuna molemmissa kiikuissa. Uusi arvo saa tulla B:n tuloon vasta pitoajan jälkeen."}
{"signal": [
  {"name": "clk", "wave": "l..h........"},
  {"name": "A:n lähtö", "wave": "=....=......", "data": ["vanha", "uusi"]},
  {"name": "B:n tulo", "wave": "=......=....", "data": ["vanha", "uusi"]},
  {"name": "polku", "wave": "z..2.3.z....", "data": ["t_cq", "t_min"]},
  {"name": "B:n ikkuna", "wave": "z..4.5.z....", "data": ["t_h", "vara"]}
], "config": {"hscale": 0.75}}
```

Asetusehto riippuu kellojaksosta, pitoehto ei. Asetusrikkeen voi
korjata hidastamalla kelloa; pitorikettä ei voi, vaan piiriin on
lisättävä viivettä. Siksi pitorike on vakavampi: se rikkoo piirin
kaikilla taajuuksilla.

## Staattinen ajoitusanalyysi

Staattinen ajoitusanalyysi (static timing analysis, STA) laskee
jokaisen signaalin myöhäisimmän ja aikaisimman saapumisajan käymällä
piirin läpi kerran. Simulointia ei tarvita, joten analyysi kattaa
kaikki syötteet. Saapumisaika on suurin (tai pienin) tulojen
saapumisaika lisättynä portin viiveellä:

```{.python tiedosto="esimerkit/11-ajoitus.py" osa="parametrit"}
```

```{.python tiedosto="esimerkit/11-ajoitus.py" osa="sta"}
```

Analysoitava piiri on 16-bittinen ripple-carry-summain kahden rekisterin
välissä:

```{.python tiedosto="esimerkit/11-ajoitus.py" osa="summain"}
```

```{.python tiedosto="esimerkit/11-ajoitus.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/11-ajoitus.odotettu" rivit="1-8"}
```

Kriittinen polku alkaa bitistä 0, kulkee muistibittien ketjun läpi ja
päättyy muistibittiin 16, kuten luvussa 6 nähtiin. Lyhin polku on
yhden XOR-portin mittainen, ja pitomarginaali on positiivinen.

STA olettaa pahimman tapauksen, myös polkuja, joita mikään syöte ei
koskaan herätä (*false path*). Suunnittelija kertoo tällaiset polut
työkalulle rajoitteina, samoin polut, joilla on tarkoituksella useampi
jakso aikaa (*multicycle path*).

## Liukuhihnoitus

Kun kriittinen polku on liian pitkä, sen voi katkaista rekisterillä.
Esimerkissä summain jaetaan kahteen kahdeksan bitin vaiheeseen, joiden
välissä on rekisteri: alaosa lasketaan ensimmäisessä jaksossa, yläosa
ja sen muistibitti toisessa. Polku puolittuu ja kellotaajuus lähes
kaksinkertaistuu (704 → 1282 MHz).

```{.dot otsikko="Summain yhdessä jaksossa ja kahtena liukuhihnavaiheena. Välirekisteri kuljettaa alaosan summan, muistibitin ja yläosan syötteet seuraavaan jaksoon."}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.4;
  node [shape=box, style="rounded,filled"];
  subgraph cluster_jalkeen {
    label="jälkeen: 700 ps kummassakin vaiheessa"; color="#B8C4C8";
    p1 [label="rekisteri\na, b", style="filled"];
    ala [label="summain\nbitit 0–7"];
    p2 [label="välirekisteri\ns[7:0], c8,\na[15:8], b[15:8]", style="filled"];
    yla [label="summain\nbitit 8–15"];
    p3 [label="rekisteri\nsumma", style="filled"];
    p1 -> ala -> p2 -> yla -> p3;
  }
  subgraph cluster_ennen {
    label="ennen: 1340 ps logiikkaa rekisterien välissä"; color="#B8C4C8";
    r1 [label="rekisteri\na, b", style="filled"];
    s16 [label="summain\nbitit 0–15"];
    r2 [label="rekisteri\nsumma", style="filled"];
    r1 -> s16 -> r2;
  }
}
```

Hinta on *latenssi*: yksittäinen summa valmistuu kahdessa jaksossa
yhden sijaan. *Läpäisy* sen sijaan kasvaa: uusi summa voi alkaa joka
jakso. Liukuhihnoitus kannattaa, kun laskentaa on paljon peräkkäin
(suoritin, signaalinkäsittely), ja vaihe-erojen lisärekisterit (yläosan
syötteet ja alaosan tulos viivästettyinä) kuuluvat toteutukseen.

| Toimenpide | Kriittinen polku | Latenssi | Pinta-ala |
|------------|------------------|----------|-----------|
| Nopeampi rakenne (lookahead) | lyhenee | ennallaan | kasvaa |
| Liukuhihnoitus | lyhenee | kasvaa | rekistereitä lisää |
| Rinnakkaistus | ennallaan | ennallaan | kasvaa paljon |
| Hitaampi kello | ennallaan | kasvaa ajassa | ennallaan |

## Kellon vino ja värinä

Todellisuudessa kello ei saavu kaikkiin kiikkuihin samaan aikaan. Ero
on *kellon vino* (clock skew), ja jakso jaksolta vaihteleva epätarkkuus
on *värinä* (jitter). Jos kello saapuu B:hen myöhemmin kuin A:han,
asetusehtoon jää enemmän aikaa mutta pitoehto tiukkenee; jos se saapuu
aikaisemmin, käy päinvastoin. Kun suuntaa ei tunneta, vino
$t_{vino}$ kiristää molempia ehtoja:

$$T \geq t_{cq} + t_{logiikka,max} + t_{su} + t_{vino}
\qquad
t_{cq} + t_{logiikka,min} \geq t_h + t_{vino}$$

Esimerkin liukuhihnoitettu summain kestää 50 pikosekunnin vinon, mutta
sadalla pitomarginaali on jo negatiivinen:

```{.python tiedosto="esimerkit/11-ajoitus.py" osa="vino"}
```

```{.tuloste tiedosto="esimerkit/11-ajoitus.odotettu" alkaen="sama, kellon vino 50 ps"}
```

Asetusehdossa vino maksaa vain taajuutta (1282 → 1136 MHz).
Pitoehdossa se rikkoo piirin, koska lyhin polku on yhden XOR-portin
mittainen. Siksi kellopuu suunnitellaan erikseen niin, että vino on
pieni, ja ajoitusanalyysi ottaa sen huomioon molemmissa ehdoissa.

## Käytännössä

- **Ajoitusraportti on piirin totuus.** Synteesin ja sijoittelun
  jälkeen STA-raportti kertoo, saavuttiko piiri tavoitetaajuuden.
  Simulaatio ei kerro sitä koskaan.
- **Pitorikkeet korjataan aina.** Asetusrikkeen voi joskus hyväksyä
  laskemalla taajuutta; pitorikettä ei. Työkalut lisäävät
  viivepuskureita automaattisesti, mutta suuri vino voi tehdä
  korjauksesta mahdotonta.
- **Rekisteröi lohkojen rajat.** Kun jokaisen lohkon lähdöt ja tulot
  ovat rekistereitä, kriittinen polku pysyy lohkon sisällä ja lohkot
  voi analysoida erikseen.
- **Liukuhihna vasta tarpeeseen.** Jokainen vaihe lisää latenssia ja
  ohjauslogiikkaa. Ensin katsotaan, löytyykö polulta turhaa
  logiikkaa, sitten nopeampi rakenne, vasta sitten uusi vaihe.

## Itsearviointi

- Osaat kirjoittaa asetus- ja pitoehdon ja laskea suurimman
  kellotaajuuden ja marginaalin.
- Osaat kertoa, miten kellon vino vaikuttaa kumpaankin ehtoon.
- Osaat selittää, miksi pitorike on vakavampi kuin asetusrike.
- Osaat kuvata staattisen ajoitusanalyysin periaatteen ja käsitteet
  false path ja multicycle path.
- Osaat arvioida, mitä liukuhihnoitus tekee kellotaajuudelle,
  latenssille ja läpäisylle.
