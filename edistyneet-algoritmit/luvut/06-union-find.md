# Union-find

*Union-find* eli erillisten joukkojen rakenne (engl. *disjoint-set
union*) pitää kirjaa alkioiden jaosta erillisiin joukkoihin. Se tukee
kahta operaatiota: `yhdista(a, b)` yhdistää a:n ja b:n joukot, ja
`etsi(a)` palauttaa a:n joukon edustajan. Kaksi alkiota ovat samassa
joukossa, jos niiden edustajat ovat samat. Rakenne on Kruskalin
algoritmin ydin (taito *Algoritmit*), ja sitä käytetään myös
yhtenäisten alueiden etsintään kuvista ja verkoista, tyyppien
yhdistämiseen tyyppipäättelyssä ja yhtäsuuruusrajoitteiden
ratkaisemiseen.

## Metsä ja kaksi parannusta

Jokainen joukko on puu, jonka juuri on edustaja, ja jokainen alkio
osoittaa vanhempaansa. Etsintä kulkee vanhempilinkkejä juureen, ja
yhdistäminen liittää toisen juuren toisen alle. Ilman parannuksia
puusta voi tulla lista, ja etsintä vie ajan $O(n)$. Kaksi parannusta
korjaavat tämän:

- **Polun tiivistys** (engl. *path compression*): etsinnän jälkeen
  jokainen polun solmu liitetään suoraan juuren alle. Seuraava
  etsintä samalta polulta on silloin yhden askeleen mittainen.
- **Yhdistäminen tason mukaan** (engl. *union by rank*): matalampi
  puu liitetään korkeamman alle. Taso on korkeuden yläraja, ja se
  kasvaa vain, kun yhdistettävien puiden tasot ovat yhtä suuret.
  Tason $k$ puussa on vähintään $2^k$ solmua, joten korkeus on
  enintään $\log_2 n$, vaikka polun tiivistystä ei käytettäisi.

```{.dot otsikko="Polun tiivistys: find(e) liittää polun solmut suoraan juureen"}
digraph {
  nodesep=0.25; ranksep=0.35;
  node [shape=circle, width=0.38, fixedsize=true, fontsize=10];
  edge [dir=back];
  subgraph cluster_ennen { label="ennen find(e)"; color="#D9E0E3";
    a -> b; b -> c; c -> d; d -> e; a -> f; }
  subgraph cluster_jalkeen { label="jälkeen"; color="#D9E0E3";
    a2 [label="a"]; b2 [label="b"]; c2 [label="c"]; d2 [label="d"];
    e2 [label="e"]; f2 [label="f"];
    a2 -> b2; a2 -> c2; a2 -> d2; a2 -> e2; a2 -> f2; }
}
```

Malliparametrit valitsevat parannukset erikseen, jotta niiden
vaikutus voidaan mitata:

```{.cpp tiedosto="esimerkit/unionfind.hpp" osa="rakenne"}
```

Polun tiivistys tehdään kahdella kierroksella: ensin etsitään juuri,
sitten polku kuljetaan uudelleen ja jokainen solmu liitetään juureen.
*Polun puolitus* tekee saman yhdellä kierroksella liittämällä joka
toisen solmun isovanhempaansa. Taidon *Algoritmit* Kruskalin
esimerkki käytti sitä. Tasoitettu raja on molemmilla sama.

## Vertailutesti

Malli antaa jokaiselle alkiolle joukon nimiön, ja yhdistäminen
nimeää toisen joukon kaikki alkiot uudelleen. Operaatio on hidas,
mutta oikeellisuus on ilmeinen. Kaikki neljä muunnelmaa testataan
saman mallin avulla, ja tulosteen ensimmäinen rivi kertoo testin
laajuuden.

## Parannusten vaikutus

Kolme kuormaa rakentaa kukin yhden 8192 alkion joukon eri
järjestyksessä. Sen jälkeen mitataan, kuinka monta vanhempilinkkiä
satunnainen etsintä kulkee keskimäärin:

```{.cpp tiedosto="esimerkit/06-unionfind.cpp" osa="kuormat"}
```

```{.tuloste tiedosto="esimerkit/06-unionfind.odotettu"}
```

Ilman parannuksia ketju on lista, ja etsintä kulkee keskimäärin
puolet siitä. Tasot estävät ketjun syntymisen. Pelkkä polun tiivistys
antaa ketjulle arvon 2,00: ensimmäinen etsintä kulkee koko listan ja
tiivistää sen, ja sen jälkeen jokainen etsintä on yhden askeleen
mittainen. Tämä on tasoitetun analyysin ydin. Kallis operaatio
maksaa itsensä takaisin, koska se tekee tulevista halvoja.

Kuorma "parit" yhdistää aina kaksi yhtä suurta joukkoa. Se on tasojen
pahin tapaus: syntyy *binomipuu*, jonka korkeus on $\log_2 n = 13$.
Etsintä kulkee keskimäärin puolet siitä. Polun tiivistys puolittaa
matkan, koska yhdistämisten etsinnät ovat jo tiivistäneet polkuja.

## Käänteinen Ackermannin funktio

Molemmilla parannuksilla $m$ operaatiota $n$ alkiolla vievät ajan
$O(m\,\alpha(n))$ (Tarjan 1975). Tässä $\alpha$ on Ackermannin
funktion käänteisfunktio. Se kasvaa niin hitaasti, että
$\alpha(n) \le 4$ kaikilla $n$, jotka mahtuvat havaittavaan
maailmankaikkeuteen. Raja on lisäksi tiukka: Fredmanin ja Saksin
(1989) mukaan mikään osoitinrakenne ei pääse siihen tasoitetusti
vakioaikaan. Käytännössä operaatiot ovat siis vakioaikaisia.
Pelkällä polun tiivistyksellä raja on $O(m \log_{1+m/n} n)$ ja
pelkillä tasoilla $O(m \log n)$. Mittauksen satunnaisessa kuormassa
kumpikin pitää polut yksinäänkin lyhyinä, mutta vain yhdessä ne ovat
hyviä kaikissa kuormissa.

## Sovellus: perkolaatio

Ruudukon ruutuja avataan yksi kerrallaan satunnaisessa
järjestyksessä. Missä vaiheessa avoimia ruutuja pitkin pääsee
yläreunasta alareunaan? Tehtävä on fysiikan *perkolaatio*. Sillä
mallinnetaan veden kulkua huokoisessa aineessa ja sähkön kulkua
seoksessa. Union-find yhdistää jokaisen avatun ruudun sen avoimiin
naapureihin. Kaksi *virtuaalisolmua* edustavat reunoja, joten
"onko reitti?" on yksi `samassa()`-kysely:

```{.cpp tiedosto="esimerkit/06-perkolaatio.cpp" osa="perkolaatio"}
```

Kustakin ruudukon koosta tehdään 40 koetta:

```{.tuloste tiedosto="esimerkit/06-perkolaatio.odotettu"}
```

Suurilla ruudukoilla kynnys lähestyy arvoa $0{,}5927$. Sitä ei tunneta
suljetussa muodossa, ja se on määritetty juuri tällaisilla
simulaatioilla. Jokainen koe on $O(n^2 \alpha(n^2))$. Leveyshaku
jokaisen avauksen jälkeen veisi ajan $O(n^4)$.

## Rajoitukset

Union-find osaa vain yhdistää, ei erottaa. Kun verkosta poistetaan
kaaria, yhtenäisyyden ylläpitoon tarvitaan raskaampia rakenteita
(dynaaminen yhtenäisyys, *link-cut*-puut). Usein tehtävän voi kuitenkin
kääntää. Jos kaikki poistot tiedetään etukäteen, ne käsitellään
käänteisessä järjestyksessä lisäyksinä (engl. *offline*). Rakenteeseen
voi myös lisätä tietoa joukon juureen, kuten koon, summan tai
pienimmän alkion, ja yhdistää sen yhdistämisen yhteydessä.

## Käytännössä

- Käytä aina molempia parannuksia. Koodia on muutama rivi lisää, ja
  rajoista tulee riippumattomia kuormasta.
- Iteratiivinen etsintä on parempi kuin rekursiivinen. Ensimmäinen
  etsintä pitkältä polulta voi ylittää pinon koon, jos rakenne on
  vielä tiivistämättä.
- Koon mukaan yhdistäminen toimii yhtä hyvin kuin tason mukaan, ja
  koko on usein hyödyllinen tieto muutenkin.
- Kokonaislukutaulukko on nopeampi kuin solmut ja osoittimet. Jos
  alkiot ovat merkkijonoja tai olioita, ne numeroidaan ensin
  hajautustaululla.
- Virtuaalisolmut, kuten reunat, "kaikki maadoitetut" tai "tunnettu
  arvo", muuttavat usein moniehtoisen kyselyn yhdeksi
  `samassa()`-kutsuksi.

## Itsearviointi

- Osaat toteuttaa union-findin polun tiivistyksellä ja tason mukaan
  yhdistämällä ja testata sen nimiömallia vastaan.
- Osaat selittää, miksi tasojen kanssa korkeus on enintään $\log_2 n$
  ja miksi polun tiivistys tekee toistuvista etsinnöistä halpoja.
- Osaat kertoa, mitä raja $O(m\,\alpha(n))$ tarkoittaa käytännössä ja
  mitä kumpikin parannus yksinään takaa.
- Osaat mallintaa yhtenäisyystehtävän, kuten perkolaation,
  union-findilla virtuaalisolmujen avulla.
- Osaat tunnistaa, milloin union-find ei riitä (poistot), ja kääntää
  tehtävän tarvittaessa offline-muotoon.
