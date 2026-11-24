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

Suhde edellisiin lukuihin: suunnattu graafi on relaatio, ja
suuntaamaton graafi symmetrinen relaatio. Transitiivinen sulkeuma
kertoo, mistä solmusta pääsee mihin.

## Esitystavat

Ohjelmassa graafi esitetään kahdella tavalla:

| Esitys | Tila | Kaari $u$–$v$? | Naapurit | Sopii |
|--------|------|----------------|----------|-------|
| vierekkäisyyslistat | $O(V + E)$ | $O(\deg u)$ | $O(\deg u)$ | harvat graafit (useimmat) |
| vierekkäisyysmatriisi | $O(V^2)$ | $O(1)$ | $O(V)$ | tiheät graafit, matriisilaskenta |

```{.python tiedosto="esimerkit/10-graafit.py" osa="esitys"}
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

## Yhtenäisyys ja komponentit

Komponentit löytyvät **leveyshaulla** (*breadth-first search*, BFS):
aloitetaan solmusta, käydään läpi sen naapurit, sitten naapurien
naapurit, ja merkitään käydyt solmut. Kun haku päättyy, löydetyt
solmut ovat yksi komponentti, ja haku aloitetaan seuraavasta
käymättömästä solmusta.

```{.python tiedosto="esimerkit/10-graafit.py" osa="komponentit"}
```

```{.tuloste tiedosto="esimerkit/10-graafit.odotettu"}
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

**Hamiltonin kehä** käy jokaisessa *solmussa* täsmälleen kerran.
Kysymys näyttää yhtä viattomalta, mutta se on NP-täydellinen: tehokasta
algoritmia ei tunneta, ja yleinen ratkaisu kokeilee pahimmillaan
kaikki järjestykset. Kauppamatkustajan ongelma (lyhin Hamiltonin
kehä) on sen painotettu versio.

```{.python tiedosto="esimerkit/10-euler.py" osa="hamilton"}
```

```{.tuloste tiedosto="esimerkit/10-euler.odotettu"}
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

Kromaattisen luvun laskeminen on NP-vaikea, ja pienillä graafeilla sen
voi ratkaista kokeilemalla. Suuremmilla käytetään SAT-ratkaisijaa
(luku *Predikaatit ja SAT*) tai heuristiikkoja.

```{.python tiedosto="esimerkit/10-varitys.py" osa="tarkka"}
```

Kaksi väriä riittää täsmälleen, kun graafissa ei ole paritonta kehää.
Tällainen **kaksijakoinen** graafi tunnistetaan leveyshaulla, joka
värittää tasot vuorotellen:

```{.python tiedosto="esimerkit/10-varitys.py" osa="kaksijakoinen"}
```

```{.tuloste tiedosto="esimerkit/10-varitys.odotettu"}
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
