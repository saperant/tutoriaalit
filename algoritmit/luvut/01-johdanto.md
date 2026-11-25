# Johdanto {.runko-johdanto}

Algoritmi on täsmällinen menetelmä, joka ratkaisee tehtävän äärellisellä
määrällä askelia. Samaan tehtävään on yleensä monta algoritmia, ja ne
eroavat siinä, miten niiden työmäärä kasvaa syötteen mukana. Pienellä
syötteellä ero ei näy, mutta suurella se ratkaisee: neliöllinen
algoritmi, joka käsittelee tuhat alkiota sekunnissa, tarvitsee
miljoonaan alkioon yksitoista päivää. Yhtä nopea lineaarinen algoritmi
tarvitsee siihen vajaat 17 minuuttia.

Tämä tutoriaali käy läpi algoritmien suunnittelun perusmenetelmät ja
niiden analyysin C:llä:

- **Vaativuus:** O-, Θ- ja Ω-merkinnät, pahin, keskimääräinen ja
  tasoitettu tapaus sekä kasvun mittaaminen operaatiolaskureilla.
- **Lajittelu:** lisäys-, lomitus-, pika- ja kekolajittelu, vakaus,
  laskemis- ja kantalukulajittelu sekä vertailulajittelun alaraja.
- **Haku:** binäärihaku, sen ala- ja yläraja sekä haku vastauksen
  arvoalueelta.
- **Hajota ja hallitse:** rekursio, inversioiden laskeminen ja
  Karatsuban kertolasku.
- **Ahneet algoritmit:** aikataulutus, vaihtoargumentti ja
  Huffmanin koodaus.
- **Dynaaminen ohjelmointi:** muistiinpano ja taulukointi,
  reppuongelma, pisin yhteinen osajono, editointietäisyys ja
  ratkaisun rekonstruointi.
- **Graafialgoritmit:** leveys- ja syvyyshaku, topologinen järjestys,
  syklien etsintä, Dijkstra, Bellman–Ford sekä Kruskalin ja Primin
  virittävät puut.

Menetelmiä sovelletaan oikeisiin tehtäviin: reitinhakuun kartalla,
käännösriippuvuuksien järjestämiseen, diff-työkalun ytimeen ja
tiedoston pakkaamiseen Huffmanin koodilla.

## Esitiedot ja rajaus

Tutoriaali rakentuu taidon *Tietorakenteet* ja sen esitietojen
*C-kieli* ja *Diskreetti matematiikka* päälle. Dynaaminen taulukko,
hajautustaulu, binäärikeko ja graafien esitystavat ovat tuttuja
tietorakenteista, eikä niitä toisteta. O-merkintä, rekursioyhtälöt,
master-lause, induktio ja silmukkainvariantit ovat tuttuja
diskreetistä matematiikasta; luku 2 kertaa merkinnät ja käyttää
niitä mittauksiin.

Rajauksen ulkopuolelle jäävät:

- tasapainotetut puut, merkkijonohaku, virtausalgoritmit,
  NP-täydellisyys ja approksimointi (jatkotaito *Edistyneet algoritmit
  ja tietorakenteet*); peruuttavasta hausta ja karsinnasta on tässä
  vain perusmuoto (luku 9),
- yhtälönratkaisu, interpolointi ja muut liukulukualgoritmit
  (*Numeeriset menetelmät*) ja
- algoritmin sovittaminen välimuistiin ja prosessoriin
  (*Suorituskyvyn analyysi ja optimointi*).

## Kolme tapaa samaan vastaukseen

Mittarin lukemat ovat muuttuneet 400 päivän aikana. Millä yhtenäisellä
jaksolla lukema kasvoi eniten? Tehtävä on *suurimman osasumman*
ongelma: etsitään peräkkäisten lukujen jakso, jonka summa on suurin.
Suorin ratkaisu käy läpi kaikki jaksot ja laskee jokaisen summan
alusta:

```{.c tiedosto="esimerkit/01-osajono.c" osa="kuutio"}
```

Jaksoja on noin $n^2/2$, ja kunkin summa vie keskimäärin $n/3$
yhteenlaskua, joten työtä on noin $n^3/6$. Turhaa työtä on helppo
huomata: jakson $[i, j]$ summa on jakson $[i, j-1]$ summa plus $x_j$.
Kun sisin silmukka poistetaan, työ putoaa noin $n^2/2$:een:

```{.c tiedosto="esimerkit/01-osajono.c" osa="nelio"}
```

Kolmas ratkaisu vaatii oivalluksen. Paras kohtaan $j$ päättyvä jakso on
joko pelkkä $x_j$ tai paras kohtaan $j - 1$ päättyvä jakso jatkettuna
$x_j$:llä. Jos edellinen summa on negatiivinen, sen jatkaminen vain
huonontaa tulosta, joten aloitetaan alusta. Tämä on *Kadanen
algoritmi*, ja se käy luvut läpi kerran:

```{.c tiedosto="esimerkit/01-osajono.c" osa="lineaarinen"}
```

```{.tuloste tiedosto="esimerkit/01-osajono.odotettu"}
```

Kaikki kolme löytävät saman jakson, mutta työmäärät eroavat
kertaluokilla. Kymmenen miljoonaa yhteenlaskua on nykykoneelle
muutama millisekunti, mutta jo 40 000 päivän sarjalla kuutiollinen
versio tekisi yli $10^{13}$ yhteenlaskua. Kadanen algoritmi on myös
esimerkki dynaamisesta ohjelmoinnista (luku 9): ratkaisu rakennetaan
pienempien osatehtävien ratkaisuista.

## Oikeellisuus ennen nopeutta

Nopea algoritmi on hyödytön, jos se antaa väärän vastauksen. Siksi
jokaisen tämän tutoriaalin algoritmin oikeellisuus perustellaan, yleensä
*invariantilla*: ehdolla, joka pätee silmukan jokaisen kierroksen
alussa ja josta oikea tulos seuraa silmukan päättyessä. Kadanen
algoritmin invariantti on, että `nykyinen` on suurin kohtaan $j - 1$
päättyvän jakson summa ja `paras` suurin koko alkuosassa
$x_0 \ldots x_{j-1}$ esiintyvä summa.

Perustelu ei korvaa testausta. Kirjoittaja voi perustella väärin, ja
toteutus voi poiketa perustelusta. Tutoriaalin esimerkit testataan
kahdella tavalla:

1. **Tunnetut tulokset:** pieni syöte, jonka oikean vastauksen voi
   laskea käsin tai tarkistaa kirjallisuudesta. Esimerkiksi Fibonaccin
   luku $F(93)$ tai tunnettu tieverkon lyhin reitti.
2. **Raaka vertailu:** nopean algoritmin tulosta verrataan
   satunnaisilla syötteillä yksinkertaiseen, hitaaseen mutta ilmeisesti
   oikeaan ratkaisuun. Reppuongelmalle se on kaikkien osajoukkojen
   läpikäynti, lajittelulle kirjaston `qsort`. Pienet syötteet ja pieni
   arvoalue tuottavat paljon rajatapauksia: tyhjiä taulukoita, toistoja
   ja tasapelejä.

Kolmen algoritmin esimerkki on jo tällainen vertailu: kolme toisistaan
riippumatonta toteutusta antavat saman vastauksen.

## Esimerkit ja testaus

Kaikki esimerkit ovat C23:a hakemistossa `esimerkit/`, ja `make testaa`
kääntää ja ajaa ne. Valmis ympäristö on kehityskontissa (ks.
*Kehitysympäristöt ja Dev Containers*). Esimerkit käännetään GCC 14:llä
ja Clang 20:llä varoitukset virheinä, AddressSanitizerin ja
UndefinedBehaviorSanitizerin kanssa. Sanitoijat pysäyttävät ohjelman,
jos indeksi menee taulukon ohi tai etumerkillinen kokonaisluku
ylivuotaa. Algoritmeissa ne ovat yleisimmät virheet: väärä silmukan raja
ja keskikohdan laskeminen kahden suuren luvun summasta.

Satunnaistetut testit käyttävät samaa pientä generaattoria kuin
tietorakenteet, jotta sama siemen antaa saman sarjan joka koneella ja
jokaisella kääntäjällä:

```{.c tiedosto="esimerkit/satunnainen.h"}
```

Työmäärää ei mitata kellolla vaan laskureilla: vertailuja,
yhteenlaskuja tai funktiokutsuja. Laskuri on toistettava, se ei riipu
koneesta, ja se mittaa juuri sitä, mitä analyysi ennustaa. Kirjaston
`qsort`-funktion vertailuja ei lasketa, koska niiden määrä riippuu
C-kirjaston toteutuksesta. Esimerkit käyttävät omia lajittelujaan,
kun vertailuja lasketaan. Ajoitus on mukana vain yhdessä erillisessä
mittauksessa (luku 5), joka käännetään optimoinneilla ja tulostaa vain
väljän vertailun tuloksen.

Esimerkkien koodi on kirjoitettu luettavaksi. Esimerkiksi pienten
graafien solmut ja kaaret ovat kiinteän kokoisissa taulukoissa, jotta
algoritmi näkyy selvästi. Kun jotain on yksinkertaistettu, se kerrotaan.
