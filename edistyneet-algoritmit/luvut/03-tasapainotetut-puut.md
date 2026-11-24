# Tasapainotetut hakupuut

Tavallinen binäärihakupuu (taito *Tietorakenteet*) toimii ajassa
$O(h)$, missä $h$ on puun korkeus. Satunnaisessa järjestyksessä
lisätyn puun korkeus on odotusarvoisesti $O(\log n)$. Järjestyksessä
tulevat avaimet, kuten aikaleimat ja juoksevat numerot, tekevät
puusta kuitenkin listan, jonka korkeus on $n$. Tasapainotettu puu
korjaa rakennetta jokaisen muutoksen jälkeen niin, että korkeus pysyy
logaritmisena syötteestä riippumatta. Korjausten perusoperaatio on
*kierto* (engl. *rotation*), joka muuttaa puun muotoa mutta säilyttää
sisäjärjestyksen.

Tämä luku käy läpi kaksi lähestymistapaa. *Punamusta puu* takaa
korkeuden deterministisesti värisäännöillä. *Treap* nojaa
satunnaisuuteen: se on hakupuu, jonka muoto on sama kuin
satunnaisessa järjestyksessä rakennetun puun, olipa syöte mikä tahansa.

## 2-3-puut ja punamustat puut

*2-3-puussa* solmussa on yksi tai kaksi avainta ja kaksi tai kolme
lasta, ja kaikki lehdet ovat samalla syvyydellä. Lisäys menee aina
lehteen. Jos lehteen tulee kolmas avain, keskimmäinen nousee
vanhempaan, ja halkaisu voi jatkua juureen asti. Puu kasvaa vain
juuresta, joten se pysyy täydellisesti tasapainossa: korkeus on
$\log_3 n \ldots \log_2 n$.

Kahden avaimen solmut tekevät toteutuksesta hankalan. Punamusta puu
esittää saman rakenteen binääripuuna. 3-solmu on kaksi tavallista
solmua, joita yhdistää *punainen* linkki. Muut linkit ovat *mustia*.
Robert Sedgewickin *vasemmalle kallistuvassa* punamustassa puussa
(engl. *left-leaning red-black tree*, LLRB) punaiset linkit
osoittavat aina vasemmalle. Silloin jokaista 2-3-puuta vastaa
täsmälleen yksi punamusta puu. Väri tallennetaan linkin alapään
solmuun:

Sama kolmen avaimen joukko 2-3-puuna ja vasemmalle kallistuvana
punamustana puuna; punainen linkki yhdistää 3-solmun kaksi avainta:

```{.dot otsikko="2-3-puu ja sitä vastaava LLRB-puu"}
digraph {
  nodesep=0.3; ranksep=0.35;
  node [fontsize=10];
  subgraph cluster_23 { label="2-3-puu"; color="#D9E0E3";
    r [shape=record, label="E|J"];
    l1 [shape=record, label="A|C"]; l2 [label="H", shape=box];
    l3 [label="L", shape=box];
    r -> l1; r -> l2; r -> l3; }
  subgraph cluster_rb { label="LLRB-puu"; color="#D9E0E3";
    node [shape=circle, width=0.4, fixedsize=true];
    J -> E [color="#B04848", penwidth=2, label=" punainen", fontcolor="#B04848",
            fontsize=8];
    J -> Lb [arrowhead=normal]; Lb [label="L"];
    E -> C; E -> Hb; Hb [label="H"];
    C -> A [color="#B04848", penwidth=2]; }
}
```

```{.cpp tiedosto="esimerkit/punamusta.hpp" osa="kierrot"}
```

Punamustan puun invariantit seuraavat suoraan 2-3-puusta:

1. Hakupuun järjestys: vasemman alipuun avaimet ovat pienempiä ja
   oikean suurempia.
2. Punainen linkki osoittaa vasemmalle.
3. Kahta punaista linkkiä ei ole peräkkäin, koska 2-3-puussa ei ole
   neljän avaimen solmuja.
4. Jokaisella polulla juuresta tyhjään linkkiin on yhtä monta mustaa
   linkkiä, koska 2-3-puun lehdet ovat samalla syvyydellä.

Ehdoista 3 ja 4 seuraa korkeuden raja. Mustia linkkejä on polulla
enintään $\log_2 n$, ja punaisia on enintään yhtä monta, joten korkeus
on enintään $2 \log_2 n$. Invariantit kannattaa kirjoittaa
tarkistusfunktioksi heti, ennen lisäystä:

```{.cpp tiedosto="esimerkit/punamusta.hpp" osa="invariantit"}
```

## Lisäys

Uusi avain liitetään lehteen punaisella linkillä, kuten 2-3-puussa
avain lisätään lehtisolmuun. Paluumatkalla kolme paikallista korjausta
palauttavat invariantit:

- Oikealle osoittava punainen linkki käännetään vasemmalle.
- Kaksi peräkkäistä punaista linkkiä kierretään oikealle, jolloin
  syntyy solmu, jolla on kaksi punaista lasta (2-3-4-puun 4-solmu).
- Kahden punaisen lapsen solmu halkaistaan värinvaihdolla: lapset
  muuttuvat mustiksi ja solmu punaiseksi. Keskimmäinen avain nousee
  siis ylöspäin kuten 2-3-puun halkaisussa.

```{.cpp tiedosto="esimerkit/punamusta.hpp" osa="lisays"}
```

Juuri väritetään lopuksi mustaksi. Jos juuren värinvaihto teki siitä
punaisen, puu kasvoi juuresta yhdellä mustalla tasolla.

## Poisto

Poisto on lisäystä vaikeampi. Lehdestä poistetaan helposti avain, joka
on 3-solmussa, mutta 2-solmun poistaminen jättäisi aukon ja rikkoisi
mustan korkeuden. Sedgewickin ratkaisu varmistaa matkalla alas, että
nykyinen solmu ei ole 2-solmu. Tarvittaessa se lainaa avaimen
sisarukselta (kierrolla) tai yhdistää solmun sisaruksen kanssa
(värinvaihdolla). Kun poistettava avain on sisäsolmussa, se korvataan
seuraajallaan, ja seuraaja poistetaan oikean alipuun pienimpänä
avaimena. Paluumatkalla sama `tasapainota()` siivoaa jäljet.
Toteutus on esimerkkitiedostossa `punamusta.hpp` (funktiot `poista`,
`poista_pienin` ja `siirra_punainen_vasemmalle`/`_oikealle`). Se on
noin 70 riviä, ja se seuraa Sedgewickin artikkelia.

Tällainen koodi on liian monimutkainen todennettavaksi lukemalla.
Siksi vertailutesti tarkistaa invariantit jokaisen operaation jälkeen
ja vertaa sisältöä `std::set`-malliin:

```{.cpp tiedosto="esimerkit/03-punamusta.cpp" osa="testi"}
```

Lopuksi ohjelma lisää tuhat ja satatuhatta avainta järjestyksessä ja
mittaa puun korkeuden:

```{.tuloste tiedosto="esimerkit/03-punamusta.odotettu"}
```

Järjestyksessä lisätyt avaimet ovat tavallisen hakupuun pahin
tapaus. Punamustalle puulle ne eivät ole ongelma: korkeus on lähes
optimaalinen $\lceil \log_2(n+1) \rceil$.

## Kun invariantti rikkoutuu

Seuraava ohjelma kääntää saman puun makrolla `KIERTOVIRHE`, jolloin
`kierra_vasen()` jättää nousevan solmun punaiseksi eikä anna sille
vanhan juuren väriä. Rivi puuttuu vain yhdestä paikasta, ja hakupuun
järjestys säilyy, joten haut toimivat edelleen:

```{.cpp tiedosto="esimerkit/03-kierto.kaatuu.cpp"}
```

```{.tuloste tiedosto="esimerkit/03-kierto.virhe"}
```

Pelkkä vertailu malliin ei olisi huomannut virhettä. Sisältö täsmää,
ja virhe näkyisi vasta hitautena tai myöhemmin poistossa, joka
olettaa invarianttien pätevän. Tarkistus löytää sen heti.

## Treap

*Treap* (engl. *tree* + *heap*) antaa jokaiselle avaimelle
satunnaisen *prioriteetin*. Puu on hakupuu avainten suhteen ja keko
prioriteettien suhteen: vanhemman prioriteetti on suurempi kuin
lasten. Annetuilla avaimilla ja prioriteeteilla tällainen puu on
yksikäsitteinen. Se on sama puu, joka syntyisi, jos avaimet
lisättäisiin tavalliseen hakupuuhun prioriteettien mukaan laskevassa
järjestyksessä. Koska prioriteetit ovat satunnaisia, puu on
satunnaisesti rakennettu hakupuu riippumatta siitä, missä järjestyksessä
avaimet todellisuudessa tulivat. Solmun odotettu syvyys on noin
$2 \ln n$ ja korkeus noin $4{,}3 \ln n$.

Treapin operaatiot rakentuvat kahdesta perusoperaatiosta. *Jako*
erottaa avaimet kahteen puuhun annetun rajan mukaan. *Yhdistäminen*
liittää kaksi puuta, kun toisen kaikki avaimet ovat pienempiä:

```{.cpp tiedosto="esimerkit/03-treap.cpp" osa="jako"}
```

Lisäys jakaa puun avaimen kohdalta ja yhdistää osat uuden solmun
kanssa. Poisto erottaa avaimen kahdella jaolla:

```{.cpp tiedosto="esimerkit/03-treap.cpp" osa="lisays"}
```

Kun jokainen solmu tietää alipuunsa koon, saadaan myös
*järjestystilastot*. $k$:nneksi pienin avain löytyy laskeutumalla:
jos vasemmassa alipuussa on alle $k$ solmua, mennään oikealle ja
vähennetään $k$:sta vasemman alipuun koko ja yksi. Avaimen
järjestysluku kertyy samalla tavalla. Molemmat vievät ajan
$O(\log n)$, eikä `std::set` tarjoa kumpaakaan logaritmisessa
ajassa.

Vertailutesti on sama kuin punamustalle puulle. Lisäksi se vertaa
järjestyslukua ja $k$:nnetta alkiota `std::set`-mallin arvoihin, jotka
lasketaan `std::distance`- ja `std::next`-funktioilla lineaarisessa ajassa.

Korkeus mitataan samoin järjestyksessä lisätyillä avaimilla:

```{.tuloste tiedosto="esimerkit/03-treap.odotettu"}
```

Treapin puu on korkeampi kuin punamustan puun, mutta koodi on paljon
lyhyempi ja helpommin oikein kirjoitettavissa. Jako ja yhdistäminen
sopivat myös koko puiden käsittelyyn: kahden joukon yhdisteen tai
välin poiston voi tehdä muutamalla jaolla.

## AVL-puu ja muut

*AVL-puu* (Adelson-Velski ja Landis 1962) on vanhin tasapainotettu
hakupuu. Se vaatii, että jokaisen solmun alipuiden korkeudet eroavat
enintään yhdellä. Korkeus on enintään $1{,}44 \log_2 n$, siis
pienempi kuin punamustassa puussa. Sen vuoksi haut ovat nopeampia,
mutta lisäys ja poisto tekevät enemmän kiertoja. *Splay-puu* nostaa
jokaisen haetun solmun juureksi. Se ei takaa yksittäisen operaation
aikaa, mutta $m$ operaatiota vievät tasoitetusti $O(m \log n)$ (luku
5), ja usein haetut avaimet pysyvät juuren lähellä.

| Rakenne | Korkeus | Takuu | Tyypillinen käyttö |
|---------|---------|-------|--------------------|
| punamusta puu | $\le 2 \log_2 n$ | pahin tapaus | `std::map`, Javan `TreeMap`, Linuxin ajastimet |
| AVL-puu | $\le 1{,}44 \log_2 n$ | pahin tapaus | hakuvoittoiset joukot, tietokantojen muistirakenteet |
| treap | $\approx 4{,}3 \ln n$ | odotusarvo | jako ja yhdistäminen, järjestystilastot |
| splay-puu | ei rajaa | tasoitettu | välimuistit, paikallisuutta sisältävät haut |
| skip-lista | $O(\log n)$ | odotusarvo | rinnakkaiset joukot (luku 11) |

## Käytännössä

- Käytä kirjaston järjestettyä säiliötä (`std::map`, `std::set`),
  ellei tarvitse jotain, mitä se ei anna: järjestystilastoja, jakoa ja
  yhdistämistä tai omaa muistinhallintaa. libstdc++:n `std::map` on
  punamusta puu.
- Jos kirjoitat oman puun, kirjoita ensin invarianttien tarkistus ja
  vertailutesti. Tasapainotuskoodi on helppo kirjoittaa väärin niin,
  että vain tehokkuus kärsii.
- Treap on hyvä valinta, kun tarvitaan omaa rakennetta nopeasti.
  Lisätiedon (alipuun koko, summa, maksimi) ylläpito on helppoa, koska
  sen tarvitsee päivittää vain jaossa ja yhdistämisessä.
- Satunnaistetun rakenteen siemen on osa sen tilaa. Jos hyökkääjä
  tuntee siemenen ja voi valita avaimet, hän voi pakottaa pahimman
  tapauksen. Verkosta tulevalle syötteelle käytä arvaamatonta siementä.
- `std::unique_ptr`-lapset tekevät omistuksen selväksi. Syvän puun
  rekursiivinen purku voi kuitenkin kuluttaa pinoa: tasapainotetussa
  puussa syvyys on pieni, mutta tasapainottamattomassa ei.

## Itsearviointi

- Osaat selittää punamustan puun 2-3-puun binääriesityksenä ja johtaa
  korkeuden rajan $2 \log_2 n$ invarianteista.
- Osaat toteuttaa kierrot ja värinvaihdon ja perustella, miksi kierto
  säilyttää sisäjärjestyksen.
- Osaat kirjoittaa punamustan puun invariantit tarkistusfunktioksi ja
  käyttää sitä vertailutestissä.
- Osaat toteuttaa treapin jaolla ja yhdistämisellä sekä laajentaa sen
  järjestystilastoihin alipuun koon avulla.
- Osaat valita punamustan puun, AVL-puun, treapin ja splay-puun
  välillä takuun ja käyttötavan perusteella.
