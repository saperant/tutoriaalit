# Trie ja suffiksitaulukko

Edellisen luvun algoritmit esikäsittelevät hahmon ja lukevat tekstin.
Kun samasta tekstistä tai sanastosta haetaan toistuvasti, kannattaa
esikäsitellä teksti. *Trie* järjestää sanaston etuliitteiden mukaan,
ja *suffiksitaulukko* järjestää tekstin kaikki loppuosat. Molemmat
vastaavat etuliitekyselyihin ajassa, joka riippuu hahmon pituudesta
eikä tekstin pituudesta.

## Trie

Trien (Fredkin 1960, engl. *retrieval*) jokainen solmu vastaa
etuliitettä. Juuri vastaa tyhjää merkkijonoa, ja solmun lapset
jatkavat etuliitettä yhdellä merkillä. Sana lisätään kulkemalla sen
merkkejä pitkin ja luomalla puuttuvat solmut. Haku, lisäys ja
etuliitekysely vievät ajan $O(m)$ riippumatta sanaston koosta.
Hajautustaulu vastaa kysymykseen "onko sana sanastossa" yhtä nopeasti,
mutta trie vastaa myös kysymyksiin "monta sanaa alkaa näin" ja "mitkä
sanat alkavat näin aakkosjärjestyksessä".

```{.cpp tiedosto="esimerkit/09-trie.cpp" osa="lisays"}
```

Jokainen solmu laskee, monenko sanan polku kulkee sen kautta (`ohi`)
ja monta sanaa päättyy siihen (`paattyy`). Etuliitekysely kulkee
etuliitteen solmuun ja palauttaa sen `ohi`-laskurin. Ehdotukset kerää
syvyyshaku etuliitteen solmusta:

```{.cpp tiedosto="esimerkit/09-trie.cpp" osa="keraa"}
```

Solmut ovat yhdessä `std::vector`-taulukossa ja viittaavat toisiinsa
indekseillä. Rakenne ei tarvitse erillistä varausta solmua kohden, se
vapautuu kerralla, ja sen voi tallentaa levylle sellaisenaan.
Lapsitaulukko `std::array<int, 26>` on nopea mutta vie paljon tilaa:
104 tavua solmua kohden, vaikka useimmilla solmuilla on yksi lapsi.
Suurille aakkostoille, kuten Unicodelle, lapset tallennetaan
järjestettyyn listaan tai hajautustauluun, tai merkkijono käsitellään
tavuina. *Pakattu trie* (radix-puu, Patricia) yhdistää yksilapsiset
ketjut yhdeksi kaareksi, jossa on merkkijono. IP-reitityksen pisimmän
etuliitteen haku ja Linuxin sivuvälimuisti käyttävät tällaisia puita.

Malliksi käy järjestetty sanalista. Etuliitteellä alkavat sanat ovat
siinä peräkkäin, ja niiden alku löytyy binäärihaulla. Lukumäärä on
välin pituus ja ehdotukset sen ensimmäiset eri sanat:

```{.cpp tiedosto="esimerkit/09-trie.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/09-trie.odotettu"}
```

Etuliitteellä "kal" alkaa kuusi lisättyä sanaa, joista "kala" kahdesti.
Ehdotukset tulevat aakkosjärjestyksessä, koska syvyyshaku käy lapset
läpi merkkijärjestyksessä. Suosituimpien sanojen ehdottaminen vaatii
lisäksi, että solmuun tallennetaan alipuun parhaat sanat.

## Suffiksitaulukko

Tekstin $T$ *suffiksit* eli loppuosat ovat $T[i..]$, $i = 0 \ldots
n-1$. *Suffiksitaulukko* $SA$ (Manber ja Myers 1990) on niiden
alkukohdat aakkosjärjestyksessä. Jokainen tekstin osajono on jonkin
suffiksin etuliite, ja samalla etuliitteellä alkavat suffiksit ovat
taulukossa peräkkäin. Siksi hahmon kaikki esiintymät ovat
taulukossa yksi väli, ja sen löytää kahdella binäärihaulla ajassa
$O(m \log n)$.

Suora lajittelu vertaa suffikseja merkki kerrallaan, ja
pahimmillaan se vie ajan $O(n^2 \log n)$. *Etuliitteiden tuplaus*
järjestää suffiksit ensin yhden, sitten kahden, neljän ja niin
edelleen ensimmäisen merkin mukaan. Kierroksen $k$ järjestys saadaan
edellisen kierroksen luokista pareina
$(\text{luokka}[i], \text{luokka}[i + 2^k])$, koska $2^{k+1}$ merkin
etuliite on kaksi $2^k$ merkin etuliitettä peräkkäin:

```{.cpp tiedosto="esimerkit/09-suffiksit.cpp" osa="taulukko"}
```

Kierroksia on enintään $\lceil \log_2 n \rceil$, ja `std::sort` tekee
kustakin $O(n \log n)$. Kantalukulajittelulla kierros on $O(n)$, ja
SA-IS-algoritmi (Nong, Zhang ja Chan 2009) rakentaa koko taulukon
lineaarisessa ajassa. Kirjastot, kuten libdivsufsort, käyttävät
tällaisia algoritmeja.

## LCP-taulukko

*LCP-taulukko* tallentaa vierekkäisten suffiksien yhteisen etuliitteen
pituuden. Kasain algoritmi (Kasai ym. 2001) laskee sen ajassa
$O(n)$. Kun siirrytään suffiksista $i$ suffiksiin $i+1$, eli
poistetaan ensimmäinen merkki, yhteinen pituus järjestyksessä
edeltävän suffiksin kanssa pienenee enintään yhdellä. Laskuria ei siis
tarvitse aloittaa joka kerta nollasta:

```{.cpp tiedosto="esimerkit/09-suffiksit.cpp" osa="lcp"}
```

Esimerkkiohjelma tulostaa ensin sanan "banaani" suffiksitaulukon,
LCP-arvot ja suffiksit (tuloste on alempana).

Taulukoista saa vastauksia, joita on vaikea laskea muuten:

- **Esiintymät:** hahmon väli suffiksitaulukossa.
- **Pisin toistuva osajono:** suurin LCP-arvo, koska kaksi saman
  osajonon esiintymää ovat vierekkäisiä suffikseja tai niiden välissä
  olevat suffiksit jakavat saman etuliitteen.
- **Eri osajonojen määrä:** $n(n+1)/2 - \sum \text{LCP}$. Jokainen
  suffiksi tuo pituutensa verran etuliitteitä, ja LCP:n verran niistä
  on jo nähty edellisessä suffiksissa.

```{.cpp tiedosto="esimerkit/09-suffiksit.cpp" osa="kaytto"}
```

Vertailutesti lajittelee suffiksit suoraan
`std::string_view`-vertailulla, kerää kaikki osajonot `std::set`-joukkoon ja laskee
esiintymät `find`-funktiolla.

Lopuksi ohjelma laskee samat suureet lauseelle "kalastaja kalasti
kalaa kalasaaresta ja kalasatamasta":

```{.tuloste tiedosto="esimerkit/09-suffiksit.odotettu"}
```

Sanan "banaani" rivit näyttävät rakenteen: suffiksit "anaani" ja
"ani" jakavat etuliitteen "an", joten jälkimmäisen LCP on 2.
Tekstiesimerkin pisin toistuva osajono on "a kalasa" (kohdista
"kalaa kalasaaresta" ja "ja kalasatamasta").

## Suffiksipuu ja muut

*Suffiksipuu* on kaikkien suffiksien pakattu trie. Se vastaa samoihin
kysymyksiin ajassa $O(m)$ ja voidaan rakentaa lineaarisessa ajassa
(Ukkonen 1995), mutta se vie 10–20 kertaa tekstin verran muistia.
Suffiksitaulukko ja LCP-taulukko yhdessä vastaavat suffiksipuuta
(Abouelhoda ym. 2004) ja vievät murto-osan tilasta. *Burrowsin–
Wheelerin muunnos* ja siihen perustuva FM-indeksi pakkaavat tekstin ja
indeksin yhteen. Ne ovat bzip2:n ja DNA-lukujen kohdistustyökalujen
(BWA, Bowtie) perusta.

## Käytännössä

- Täsmähakuun riittää hajautustaulu. Valitse trie, kun tarvitset
  etuliitekyselyjä, aakkosjärjestystä tai pisimmän etuliitteen hakua.
- Trien muisti kasvaa nopeasti. Mittaa solmujen määrä, ja pakkaa
  yksilapsiset ketjut tai käytä järjestettyä lapsilistaa, jos aakkosto
  on suuri.
- Suffiksitaulukko on staattinen. Tekstin muuttuessa se rakennetaan
  uudelleen, joten se sopii indekseihin, jotka luodaan kerran ja
  joista haetaan usein.
- Käytä merkkijonojen vertailussa `std::string_view`-tyyppiä, jotta
  suffikseista ei tehdä kopioita. Suora lajittelu kopioilla vie
  neliöllisen määrän muistia.
- Rakenna nopea algoritmi vasta, kun suora versio toimii. Suora
  suffiksilajittelu on täydellinen malli lyhyille merkkijonoille.

## Itsearviointi

- Osaat toteuttaa trien taulukkoon tallennetuilla solmuilla ja
  vastata etuliitekyselyihin ja täydennysehdotuksiin.
- Osaat arvioida trien muistinkulutuksen ja kertoa, miten pakattu
  trie ja lapsilistat pienentävät sitä.
- Osaat rakentaa suffiksitaulukon etuliitteiden tuplauksella ja
  selittää, miksi kierroksia on $\lceil \log_2 n \rceil$.
- Osaat laskea LCP-taulukon Kasain algoritmilla ja perustella sen
  lineaarisen ajan.
- Osaat käyttää suffiksi- ja LCP-taulukkoa esiintymien,
  pisimmän toistuvan osajonon ja eri osajonojen määrän laskemiseen.
