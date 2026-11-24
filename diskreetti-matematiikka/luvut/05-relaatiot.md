# Relaatiot

Relaatio kertoo, mitkä alkiot liittyvät toisiinsa: ”moduuli $a$
riippuu moduulista $b$”, ”sanat ovat toistensa anagrammeja”,
”asemalta pääsee asemalle”. Funktio on relaation erikoistapaus, jossa
jokaisella alkiolla on täsmälleen yksi pari. Relaatioiden
ominaisuuksista seuraa, mitä niillä voi tehdä: ekvivalenssirelaatio
jakaa aineiston ryhmiin, järjestysrelaatio antaa käsittelyjärjestyksen.

## Relaatiot ja niiden ominaisuudet

Joukon $A$ **relaatio** $R$ on karteesisen tulon osajoukko,
$R \subseteq A \times A$. Merkitään $a\, R\, b$, kun $(a, b) \in R$.
Ohjelmassa relaation voi esittää parien joukkona, totuusarvomatriisina
tai funktiona, joka palauttaa totuusarvon. Tärkeimmät ominaisuudet:

| Ominaisuus | Määritelmä | Esimerkki |
|------------|------------|-----------|
| refleksiivinen | $a\, R\, a$ kaikilla $a$ | $\le$, ”sama pituus” |
| symmetrinen | $a\, R\, b \Rightarrow b\, R\, a$ | ”on naapuri” |
| antisymmetrinen | $a\, R\, b \land b\, R\, a \Rightarrow a = b$ | $\le$, ”on alkuosa” |
| transitiivinen | $a\, R\, b \land b\, R\, c \Rightarrow a\, R\, c$ | $<$, ”riippuu” |

Määritelmät ovat kvanttorilausekkeita, joten äärellisellä joukolla ne
tarkistetaan suoraan:

```{.python tiedosto="esimerkit/05-relaatiot.py" osa="ominaisuudet"}
```

”Eri sana” on symmetrinen mutta ei transitiivinen: kissa ≠ sakki ja
sakki ≠ kissa, mutta kissa = kissa. Tällainen relaatio ei kelpaa
ryhmittelyyn.

## Ekvivalenssirelaatiot

Refleksiivinen, symmetrinen ja transitiivinen relaatio on
**ekvivalenssirelaatio**. Se jakaa joukon erillisiin
**ekvivalenssiluokkiin**: jokainen alkio kuuluu täsmälleen yhteen
luokkaan, ja saman luokan alkiot ovat keskenään ekvivalentteja.
Ekvivalenssi on yleistetty ”yhtäsuuruus”: sama sisältö, sama
jakojäännös, sama kirjaimisto.

Ohjelmassa luokat muodostetaan **kanonisella avaimella**: funktiolla,
joka antaa saman arvon täsmälleen ekvivalenteille alkioille.
Anagrammien avain on kirjainten järjestetty jono, samojen tiedostojen
avain sisällön tiiviste ja saman päivän tapahtumien avain päivämäärä.

```{.python tiedosto="esimerkit/05-relaatiot.py" osa="luokat"}
```

Kanoninen avain tekee ryhmittelystä lineaarisen: jokainen alkio
käsitellään kerran, kun taas parivertailu vaatisi $\binom{n}{2}$
vertailua. Sama ajatus on tietokannan `GROUP BY` -lauseessa ja
sanakirjan hajautuksessa. Pythonin `__eq__` ja `__hash__` on
toteutettava yhdenmukaisesti juuri siksi: ekvivalenttien olioiden
hajautusarvon on oltava sama.

## Transitiivinen sulkeuma

Relaation **transitiivinen sulkeuma** $R^+$ on pienin transitiivinen
relaatio, joka sisältää $R$:n. Suorista junayhteyksistä se antaa
kaikki reitit vaihtoineen, suorista riippuvuuksista kaikki epäsuorat.
Warshallin algoritmi laskee sen matriisista: $a$ tavoittaa $c$:n, jos
se tavoittaa sen suoraan tai jonkin välisolmun $k$ kautta.

```{.python tiedosto="esimerkit/05-relaatiot.py" osa="sulkeuma"}
```

```{.tuloste tiedosto="esimerkit/05-relaatiot.odotettu"}
```

Algoritmi on $O(n^3)$, mikä riittää sadoille solmuille. Harvoille
graafeille on nopeampaa tehdä haku jokaisesta solmusta (luku
*Graafit*). Esimerkin relaatio ei ole symmetrinen (yhteydet ovat
yksisuuntaisia), joten Oulusta ei pääse minnekään.

## Järjestysrelaatiot ja topologinen järjestys

Refleksiivinen, antisymmetrinen ja transitiivinen relaatio on
**osittainen järjestys**. ”Osittainen”, koska kaikkia pareja ei
tarvitse voida verrata: tiedostojärjestelmässä hakemisto on toisen
alkuosa tai ei ole, ja kaksi rinnakkaista hakemistoa ovat
vertailukelvottomia. **Täydellisessä järjestyksessä** kaikki parit
ovat vertailukelpoisia, kuten luvuilla ja aakkosjärjestyksessä.

Riippuvuudet muodostavat osittaisen järjestyksen, jos niissä ei ole
kehää. **Topologinen järjestys** asettaa alkiot jonoon, joka on
sopusoinnussa osittaisen järjestyksen kanssa: jokainen moduuli tulee
riippuvuuksiensa jälkeen. Kahnin algoritmi käsittelee ensin alkiot,
joilla ei ole käsittelemättömiä riippuvuuksia:

```{.python tiedosto="esimerkit/05-topologinen.py" osa="kahn"}
```

```{.python tiedosto="esimerkit/05-topologinen.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/05-topologinen.odotettu"}
```

Topologinen järjestys ratkaisee käännösjärjestyksen (Make, Bazel),
pakettien asennusjärjestyksen, tietokantamigraatioiden järjestyksen ja
taulukkolaskentaohjelman solujen päivitysjärjestyksen. Järjestys ei
ole yksikäsitteinen, ja algoritmi tuottaa yhden niistä; lajittelu
jonossa tekee tuloksesta toistettavan. Kehä tarkoittaa, ettei
järjestystä ole, ja hyvä työkalu kertoo, mitkä alkiot kehään
osallistuvat.

## Käytännössä

- **Ryhmittele kanonisella avaimella.** `defaultdict(list)` ja avain,
  joka on sama ekvivalenteille alkioille, on lineaarinen ja selkeä.
  Parivertailu on neliöllinen ja helppo tehdä väärin.
- **Tarkista transitiivisuus ennen ryhmittelyä.** ”Riittävän lähellä”
  (esim. etäisyys alle 1 km) ei ole transitiivinen, joten se ei jaa
  aineistoa yksikäsitteisiin ryhmiin. Tarvitset klusterointia, et
  ekvivalenssiluokkia.
- **Pidä `__eq__` ja `__hash__` yhdenmukaisina.** Jos kaksi oliota
  ovat yhtä suuret, niiden hajautusarvon on oltava sama, muuten
  joukot ja sanakirjat toimivat väärin.
- **Tee topologisesta järjestyksestä toistettava.** Kun valinnanvaraa
  on, valitse aina samalla säännöllä (esim. aakkosjärjestys), jotta
  käännökset ja ajot ovat toistettavia.
- **Raportoi kehä osallisineen.** ”Riippuvuuskehä” ilman tietoa
  osallisista moduuleista on käyttäjälle hyödytön virheilmoitus.

## Itsearviointi

- Osaat tunnistaa, onko relaatio refleksiivinen, symmetrinen,
  antisymmetrinen ja transitiivinen, ja tarkistaa sen ohjelmallisesti.
- Osaat muodostaa ekvivalenssiluokat kanonisella avaimella ja
  selittää, miksi `__hash__` on yhdenmukaistettava `__eq__`:n kanssa.
- Osaat laskea transitiivisen sulkeuman Warshallin algoritmilla.
- Osaat muodostaa topologisen järjestyksen Kahnin algoritmilla ja
  tunnistaa riippuvuuskehän.
