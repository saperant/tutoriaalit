# Puut

Puu on yhtenäinen graafi, jossa ei ole kehiä. Se on graafien
yksinkertaisin ja ohjelmoinnissa yleisin muoto: hakemistorakenne,
HTML-dokumentti, jäsennyspuu, organisaatiokaavio, päätöspuu ja
hakupuut ovat kaikki puita. Puiden ominaisuudet takaavat, että
jokaiseen solmuun on yksikäsitteinen reitti, ja niistä seuraa, miksi
puurakenteita käsitellään luontevasti rekursiolla.

## Puun ominaisuudet

Seuraavat ehdot ovat $n$ solmun graafille yhtäpitäviä; mikä tahansa
niistä määrittelee puun:

1. Graafi on yhtenäinen ja kehätön.
2. Graafi on yhtenäinen, ja siinä on $n - 1$ kaarta.
3. Graafi on kehätön, ja siinä on $n - 1$ kaarta.
4. Minkä tahansa kahden solmun välillä on täsmälleen yksi polku.
5. Graafi on yhtenäinen, mutta minkä tahansa kaaren poisto rikkoo
   yhtenäisyyden.
6. Graafi on kehätön, mutta minkä tahansa kaaren lisäys synnyttää
   kehän.

Ominaisuus 2 todistetaan induktiolla: puussa on aina **lehti** (aste
1), ja sen poisto jättää $n - 1$ solmun puun. Ominaisuudet antavat
käytännön testin: kaarijoukko on puu, jos kaaria on $n - 1$ eikä
yksikään sulje kehää. Kehän havaitsee **union–find**-rakenne, joka
pitää kirjaa siitä, mihin komponenttiin kukin solmu kuuluu:

```{.python tiedosto="esimerkit/11-puut.py" osa="puu"}
```

```{.python tiedosto="esimerkit/11-puut.py" osa="ominaisuudet"}
```

```{.tuloste tiedosto="esimerkit/11-puut.odotettu" rivit="6-"}
```

```{.dot otsikko="Esimerkin kolme kaarijoukkoa: puu, kaaren (2, 4) lisäys sulkee kehän 1–2–4–3 ja kaaren (1, 3) poisto katkaisee yhtenäisyyden"}
graph {
  nodesep=0.3; ranksep=0.3;
  node [shape=circle, width=0.3, fixedsize=true, fontsize=9];
  subgraph cluster_a { label="puu"; color="#B8C4C8";
    a0 [label="0"]; a1 [label="1"]; a2 [label="2"]; a3 [label="3"];
    a4 [label="4"];
    a0 -- a1; a1 -- a2; a1 -- a3; a3 -- a4; }
  subgraph cluster_b { label="kehä"; color="#B8C4C8";
    b0 [label="0"]; b1 [label="1"]; b2 [label="2"]; b3 [label="3"];
    b4 [label="4"];
    b0 -- b1; b1 -- b2; b1 -- b3; b3 -- b4;
    b2 -- b4 [style=dashed, penwidth=1.6, color="#9A6524"]; }
  subgraph cluster_c { label="epäyhtenäinen"; color="#B8C4C8";
    c0 [label="0"]; c1 [label="1"]; c2 [label="2"]; c3 [label="3"];
    c4 [label="4"];
    c0 -- c1; c1 -- c2; c3 -- c4; c1 -- c3 [style=invis]; }
}
```

## Puiden lukumäärä

Montako erilaista puuta on $n$ numeroidulla solmulla? **Cayleyn
kaava** antaa yllättävän siistin vastauksen: $n^{n-2}$. Kaavan voi
todistaa Prüferin koodilla, joka on bijektio puiden ja
$(n-2)$-pituisten jonojen välillä. Tarkistus kokeilee kaikki
$(n-1)$-kaariset osajoukot ja laskee, moniko on puu:

```{.python tiedosto="esimerkit/11-puut.py" osa="cayley"}
```

```{.tuloste tiedosto="esimerkit/11-puut.odotettu" rivit="1-5"}
```

Luku selittää, miksi **virittävien puiden** (*spanning tree*)
luettelointi on toivotonta: täydellisessä 20 solmun graafissa niitä on
$20^{18} \approx 2{,}6 \cdot 10^{23}$. Pienimmän painon virittävä puu
löytyy silti tehokkaasti ahneilla algoritmeilla (Kruskal käyttää juuri
yllä olevaa union–findia) taidossa *Algoritmit*.

## Juurelliset puut

**Juurellisessa puussa** yksi solmu on **juuri**, ja kaaret
suuntautuvat siitä poispäin. Jokaisella solmulla paitsi juurella on
yksi **vanhempi** ja mahdollisesti **lapsia**; lapsettomat solmut ovat
**lehtiä**. Solmun **syvyys** on sen etäisyys juuresta ja puun
**korkeus** suurin syvyys. Hakemistorakenne on juurellinen puu:

```{.python tiedosto="esimerkit/11-hakemistopuu.py" osa="solmu"}
```

```{.python tiedosto="esimerkit/11-hakemistopuu.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/11-hakemistopuu.odotettu"}
```

```{.dot otsikko="Esimerkin hakemistopuu. Juuri on ylimpänä, syvyys kasvaa alaspäin ja lehdet (tiedostot) on tummennettu. Puun korkeus on 3."}
digraph {
  nodesep=0.25; ranksep=0.35;
  node [shape=box, fontname="DejaVu Sans Mono", fontsize=9];
  edge [arrowsize=0.6];
  projekti -> src; projekti -> tests; projekti -> readme;
  src -> main; src -> apu; apu -> io; apu -> laskenta; tests -> test;
  readme [label="README.md", fillcolor="#C9D3D6"];
  main [label="main.py", fillcolor="#C9D3D6"];
  io [label="io.py", fillcolor="#C9D3D6"];
  laskenta [label="laskenta.py", fillcolor="#C9D3D6"];
  test [label="test_main.py", fillcolor="#C9D3D6"];
  node [shape=plaintext, style="", fontname="Inter"];
  s0 [label="syvyys 0"]; s1 [label="syvyys 1"]; s2 [label="syvyys 2"];
  s3 [label="syvyys 3"];
  edge [style=invis];
  s0 -> s1 -> s2 -> s3;
  { rank=same; s0; projekti; } { rank=same; s1; src; }
  { rank=same; s2; main; } { rank=same; s3; io; }
}
```

Jokainen metodi on rakenteellista rekursiota: tulos lasketaan lasten
tuloksista. Oikeellisuus seuraa induktiosta puun korkeuden suhteen
(luku *Todistaminen ja invariantit*), ja rekursio päättyy, koska
puussa ei ole kehiä. Rekursion syvyys on puun korkeus, joten
tasapainoisissa puissa se on logaritminen ja turvallinen, mutta
listaksi rappeutuneessa puussa lineaarinen (luku *Rekursio ja
rekursioyhtälöt*).

## Binääripuut

**Binääripuussa** jokaisella solmulla on enintään kaksi lasta. Täydessä
binääripuussa, jonka korkeus on $h$, on $2^{h+1} - 1$ solmua ja
$2^h$ lehteä; kääntäen $n$ solmun tasapainoisen puun korkeus on noin
$\log_2 n$. Tämä logaritmi on hakupuiden, kekojen ja lajittelun
alarajan taustalla: miljoona alkiota mahtuu 20 tason puuhun.
Binäärihakupuut ja keot käsitellään taidossa *Tietorakenteet*.

## Käytännössä

- **Tarkista, että rakenne todella on puu.** Viitteet, jotka voivat
  muodostaa kehän (esim. vanhempiviitteet käyttäjän syötteestä), on
  validoitava; muuten rekursio jää silmukkaan.
- **Käsittele puu rakenteellisella rekursiolla.** Koko, korkeus,
  summa ja haku ovat ”tulos lapsista ja solmusta”. Kirjoita perustapaus
  lehdelle ja yhdistä lasten tulokset.
- **Varo syviä puita.** Käyttäjän syötteestä rakennettu puu (sisäkkäinen
  JSON, hakemistorakenne) voi olla syvä. Kriittisessä koodissa käytä
  eksplisiittistä pinoa ja rajoita syvyyttä.
- **Käytä union–findia yhtenäisyyskysymyksiin.** ”Ovatko nämä samassa
  ryhmässä?” ja ”sulkeeko tämä kaari kehän?” ratkeavat lähes
  vakioajassa.
- **Pidä puu tasapainossa.** Hakupuun hyöty on logaritminen korkeus.
  Ilman tasapainotusta järjestyksessä lisätyt avaimet tekevät siitä
  listan.

## Itsearviointi

- Osaat luetella puun yhtäpitävät määritelmät ja tunnistaa
  ohjelmallisesti, onko kaarijoukko puu.
- Osaat soveltaa Cayleyn kaavaa ja selittää, miksi virittävien puiden
  luettelointi on mahdotonta suurille graafeille.
- Osaat määritellä juurellisen puun käsitteet (juuri, lapsi, lehti,
  syvyys, korkeus) ja käsitellä puuta rakenteellisella rekursiolla.
- Osaat selittää binääripuun korkeuden ja solmumäärän yhteyden ja sen
  merkityksen tehokkaille tietorakenteille.
