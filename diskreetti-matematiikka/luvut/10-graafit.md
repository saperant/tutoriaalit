# Graafit

Graafi on solmujen ja niitä yhdistävien kaarten joukko. Sillä
mallinnetaan kaikkea, missä asiat ovat yhteydessä toisiinsa:
tieverkot, tietoverkot, riippuvuudet, sosiaaliset verkostot, tilakoneet
ja aikataulujen ristiriidat. Tämä luku esittelee käsitteet ja
klassiset kysymykset; algoritmit, kuten lyhimmät polut, käsitellään
taidossa *Algoritmit*.

## Käsitteet

**Graafi** $G = (V, E)$ koostuu solmujoukosta $V$ ja kaarijoukosta $E$.
**Suuntaamattomassa** graafissa kaari $\{u, v\}$ yhdistää kaksi solmua
symmetrisesti, **suunnatussa** kaari $(u, v)$ kulkee yhteen suuntaan.
Muita käsitteitä:

- **Aste** $\deg(v)$: solmuun liittyvien kaarten määrä. Suunnatussa
  graafissa erotetaan lähtö- ja tuloaste.
- **Polku**: solmujono, jonka peräkkäisten solmujen välillä on kaari.
  **Kehä** on polku, joka palaa alkuun.
- **Yhtenäinen**: jokaisesta solmusta on polku jokaiseen. Muuten graafi
  jakautuu **komponentteihin**.
- **Painotettu** graafi liittää kaariin luvun, kuten etäisyyden tai
  kapasiteetin.

```{.dot otsikko="Luvun esimerkkigraafi: ratayhteyksiä. Solmun alla on sen aste. Graafissa on kaksi komponenttia ja yksi kehä (Helsinki–Tampere–Turku)."}
graph {
  layout=neato; overlap=false;
  node [shape=box];
  Oulu [label="Oulu\n1", pos="2.2,3.2!"];
  Pori [label="Pori\n1", pos="0,1.9!"];
  Tampere [label="Tampere\n4", pos="2.2,1.9!"];
  Turku [label="Turku\n2", pos="0.6,0.4!"];
  Helsinki [label="Helsinki\n2", pos="2.9,0.4!"];
  Nurmes [label="Nurmes\n1", pos="5.0,2.6!"];
  Joensuu [label="Joensuu\n1", pos="5.0,1.2!"];
  Helsinki -- Tampere; Tampere -- Oulu; Helsinki -- Turku;
  Turku -- Tampere; Tampere -- Pori; Joensuu -- Nurmes;
}
```

Suhde edellisiin lukuihin: suunnattu graafi on relaatio, ja
suuntaamaton graafi symmetrinen relaatio. Transitiivinen sulkeuma
kertoo, mistä solmusta pääsee mihin. Luvun *Relaatiot* nuolikaaviot
olivat suunnattuja graafeja.

## Esitystavat

Ohjelmassa graafi esitetään kahdella tavalla:

| Esitys | Tila | Kaari $u$–$v$? | Naapurit | Sopii |
|--------|------|----------------|----------|-------|
| vierekkäisyyslistat | $O(V + E)$ | $O(\deg u)$ | $O(\deg u)$ | harvat graafit (useimmat) |
| vierekkäisyysmatriisi | $O(V^2)$ | $O(1)$ | $O(V)$ | tiheät graafit, matriisilaskenta |

```{.python tiedosto="esimerkit/10-graafit.py" osa="esitys"}
```

```{.tuloste tiedosto="esimerkit/10-graafit.odotettu" rivit="1-7"}
```

Tieverkossa, jossa on miljoona risteystä ja kustakin muutama tie,
matriisissa olisi biljoona alkiota, joista lähes kaikki nollia.
Vierekkäisyyslista on siksi oletus. Tietokannoissa graafi on usein
kaaritaulu `(lahto, kohde)`, ja suuret graafit käsitellään
grafitietokannoilla tai -kirjastoilla (esim. NetworkX).

## Asteet ja kättelylemma

Jokainen kaari lisää kahden solmun astetta, joten
$\sum_v \deg(v) = 2 \lvert E \rvert$. Tästä **kättelylemmasta**
seuraa, että paritonasteisia solmuja on aina parillinen määrä: juhlissa
pariton määrä kättelyjä tehneitä on parillinen määrä.

```{.python tiedosto="esimerkit/10-graafit.py" osa="asteet"}
```

```{.tuloste tiedosto="esimerkit/10-graafit.odotettu" rivit="8-9"}
```

## Yhtenäisyys ja komponentit

Komponentit löytyvät **leveyshaulla** (*breadth-first search*, BFS):
aloitetaan solmusta, käydään läpi sen naapurit, sitten naapurien
naapurit, ja merkitään käydyt solmut. Kun haku päättyy, löydetyt
solmut ovat yksi komponentti, ja haku aloitetaan seuraavasta
käymättömästä solmusta.

```{.python tiedosto="esimerkit/10-graafit.py" osa="komponentit"}
```

```{.tuloste tiedosto="esimerkit/10-graafit.odotettu" rivit="10-"}
```

Haku käy jokaisen solmun ja kaaren läpi kerran, joten se on
$O(V + E)$. Leveyshaku löytää myös lyhimmät polut painottamattomassa
graafissa, koska se etenee kerros kerrokselta.

## Eulerin ja Hamiltonin polut

Kaksi samannäköistä kysymystä havainnollistaa laskennan vaikeutta.
**Eulerin polku** kulkee jokaisen kaaren läpi täsmälleen kerran. Euler
osoitti 1736 Königsbergin siltojen ongelmalla, että yhtenäisessä
graafissa sellainen on olemassa täsmälleen silloin, kun
paritonasteisia solmuja on nolla (kehä) tai kaksi (polku niiden
välillä). Ehto on helppo tarkistaa, ja Hierholzerin algoritmi
rakentaa polun lineaarisessa ajassa:

```{.python tiedosto="esimerkit/10-euler.py" osa="euler"}
```

```{.python tiedosto="esimerkit/10-euler.py" osa="konigsberg"}
```

```{.dot otsikko="Königsbergin sillat (vasemmalla) ja kirjekuori (oikealla). Solmun aste on merkitty; tummennetut solmut ovat paritonasteisia."}
graph {
  layout=neato; overlap=false;
  node [shape=circle, width=0.42, fixedsize=true, fontsize=9];
  A [label="A 5", pos="0,1!", fillcolor="#C9D3D6"];
  B [label="B 3", pos="0,2.2!", fillcolor="#C9D3D6"];
  C [label="C 3", pos="0,-0.2!", fillcolor="#C9D3D6"];
  D [label="D 3", pos="1.6,1!", fillcolor="#C9D3D6"];
  A:nw -- B:sw; A:ne -- B:se; A:sw -- C:nw; A:se -- C:ne;
  A -- D; B -- D; C -- D;
  k1 [label="1 3", pos="3.6,-0.2!", fillcolor="#C9D3D6"];
  k2 [label="2 3", pos="5.2,-0.2!", fillcolor="#C9D3D6"];
  k3 [label="3 4", pos="5.2,1.3!", fillcolor="#FFFFFF"];
  k4 [label="4 4", pos="3.6,1.3!", fillcolor="#FFFFFF"];
  k5 [label="5 2", pos="4.4,2.4!", fillcolor="#FFFFFF"];
  k1 -- k2; k2 -- k3; k3 -- k4; k4 -- k1; k1 -- k3; k2 -- k4;
  k3 -- k5; k4 -- k5;
}
```

Königsbergissä kaikki neljä solmua ovat paritonasteisia, joten polkua
ei ole. Kirjekuoressa paritonasteisia on kaksi, ja löydetty polku
alkaa toisesta (1) ja päättyy toiseen (2).

```{.tuloste tiedosto="esimerkit/10-euler.odotettu" rivit="1-2"}
```

**Hamiltonin kehä** käy jokaisessa *solmussa* täsmälleen kerran.
Kysymys näyttää yhtä viattomalta, mutta se on NP-täydellinen (luku
*Predikaatit ja SAT*): tehokasta
algoritmia ei tunneta, ja yleinen ratkaisu kokeilee pahimmillaan
kaikki järjestykset. Kauppamatkustajan ongelma (lyhin Hamiltonin
kehä) on sen painotettu versio.

```{.python tiedosto="esimerkit/10-euler.py" osa="hamilton"}
```

```{.tuloste tiedosto="esimerkit/10-euler.odotettu" rivit="3-"}
```

Opetus ohjelmoijalle: kahden ongelman kuvaukset voivat erota yhden
sanan verran ja vaikeudet eksponentiaalisesti. Kannattaa tunnistaa,
kumpaan luokkaan oma ongelma kuuluu, ennen kuin yrittää tarkkaa
ratkaisua.

## Väritys

Graafin **väritys** antaa jokaiselle solmulle värin niin, ettei
naapureilla ole samaa väriä. Pienin riittävä värimäärä on graafin
**kromaattinen luku** $\chi(G)$. Värityksellä mallinnetaan resurssien
jakoa ristiriitojen kanssa: tentit aikaväleihin, rekisterit muuttujiin
kääntäjässä, taajuudet tukiasemille.

**Ahne väritys** antaa jokaiselle solmulle pienimmän värin, jota
naapureilla ei vielä ole. Se on nopea mutta herkkä järjestykselle:
**kruunugraafi** on kaksijakoinen, joten kaksi väriä riittää, mutta
huono järjestys vaatii yhtä monta väriä kuin graafissa on solmupareja.

```{.python tiedosto="esimerkit/10-varitys.py" osa="ahne"}
```

```{.tuloste tiedosto="esimerkit/10-varitys.odotettu" rivit="1-3"}
```

```{.dot otsikko="Ahne väritys: tenttien ristiriitagraafi kolmella värillä (vasemmalla) ja kruunugraafi huonossa järjestyksessä neljällä (oikealla). Numero on väri."}
graph {
  layout=neato; overlap=false;
  node [shape=box, style="rounded,filled", fontsize=9];
  matikka [label="matikka\n1", pos="1.2,2.4!", fillcolor="#DDE4E6"];
  fysiikka [label="fysiikka\n0", pos="0,1.2!", fillcolor="#FFFFFF"];
  ohjelmointi [label="ohjelmointi\n0", pos="2.4,1.2!", fillcolor="#FFFFFF"];
  tilastot [label="tilastot\n2", pos="3.2,2.4!", fillcolor="#9FB0B5"];
  kemia [label="kemia\n1", pos="1.2,0!", fillcolor="#DDE4E6"];
  matikka -- fysiikka; matikka -- ohjelmointi; matikka -- tilastot;
  fysiikka -- kemia; ohjelmointi -- tilastot; ohjelmointi -- kemia;
  node [shape=circle, style=filled, width=0.42, fixedsize=true];
  a1 [label="a1 0", pos="5.0,2.4!", fillcolor="#FFFFFF"];
  a2 [label="a2 1", pos="6.0,2.4!", fillcolor="#DDE4E6"];
  a3 [label="a3 2", pos="7.0,2.4!", fillcolor="#9FB0B5"];
  a4 [label="a4 3", pos="8.0,2.4!", fillcolor="#5B6B70", fontcolor="#FFFFFF"];
  b1 [label="b1 0", pos="5.0,0.2!", fillcolor="#FFFFFF"];
  b2 [label="b2 1", pos="6.0,0.2!", fillcolor="#DDE4E6"];
  b3 [label="b3 2", pos="7.0,0.2!", fillcolor="#9FB0B5"];
  b4 [label="b4 3", pos="8.0,0.2!", fillcolor="#5B6B70", fontcolor="#FFFFFF"];
  a1 -- b2; a1 -- b3; a1 -- b4; a2 -- b1; a2 -- b3; a2 -- b4;
  a3 -- b1; a3 -- b2; a3 -- b4; a4 -- b1; a4 -- b2; a4 -- b3;
}
```

Kruunugraafissa järjestys $a_1, b_1, a_2, b_2, \ldots$ antaa parille
$a_i, b_i$ aina saman värin, koska ne eivät ole naapureita, ja uuden
värin jokaiselle parille. Järjestys ”ensin kaikki $a$:t” värittää
ylärivin värillä 0 ja alarivin värillä 1.

Kromaattisen luvun laskeminen on NP-vaikea, ja pienillä graafeilla sen
voi ratkaista kokeilemalla. Suuremmilla käytetään SAT-ratkaisijaa
(luku *Predikaatit ja SAT*) tai heuristiikkoja.

```{.python tiedosto="esimerkit/10-varitys.py" osa="tarkka"}
```

```{.tuloste tiedosto="esimerkit/10-varitys.odotettu" rivit="4-4"}
```

Kaksi väriä riittää täsmälleen, kun graafissa ei ole paritonta kehää.
Tällainen **kaksijakoinen** graafi tunnistetaan leveyshaulla, joka
värittää tasot vuorotellen:

```{.python tiedosto="esimerkit/10-varitys.py" osa="kaksijakoinen"}
```

```{.tuloste tiedosto="esimerkit/10-varitys.odotettu" rivit="5-"}
```

## Käytännössä

- **Tunnista graafiongelma.** Kun tehtävässä on ”yhteydessä”,
  ”riippuu”, ”naapuri” tai ”ristiriita”, se on usein graafiongelma,
  jolle on valmis algoritmi.
- **Käytä vierekkäisyyslistaa oletuksena.** Matriisi vain tiheille tai
  pienille graafeille. Sanakirja `solmu → lista naapureista` riittää
  pitkälle.
- **Merkitse käydyt solmut.** Unohtunut `nahty`-joukko johtaa
  ikuiseen silmukkaan heti, kun graafissa on kehä.
- **Erota helpot ja vaikeat ongelmat.** Euler, yhtenäisyys ja
  kaksijakoisuus ovat lineaarisia; Hamilton ja väritys yleisesti
  NP-vaikeita. Vaikeissa tyydy heuristiikkaan tai käytä ratkaisijaa.
- **Käytä kirjastoa suurille graafeille.** NetworkX (Python), Boost
  Graph Library (C++) ja tietokantojen graafilaajennukset ovat
  testattuja ja dokumentoituja.

## Itsearviointi

- Osaat määritellä graafin perustermit ja valita esitystavan
  (vierekkäisyyslista tai -matriisi) tilanteen mukaan.
- Osaat käyttää kättelylemmaa ja etsiä graafin komponentit
  leveyshaulla.
- Osaat ratkaista, onko graafissa Eulerin polku, ja selittää, miksi
  Hamiltonin kehän etsiminen on vaikeaa.
- Osaat mallintaa resurssien jaon väritysongelmana ja tunnistaa
  kaksijakoisen graafin.
