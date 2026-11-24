# Lopuksi {.runko-lahteet}

## Rakenteen valinta

| Tarve | Rakenne | Luku |
|-------|---------|------|
| järjestetty joukko, pahimman tapauksen takuu | punamusta puu (`std::map`) | 3 |
| järjestystilastot, jako ja yhdistäminen | treap | 3 |
| levy tai välimuisti, välikyselyt | B-puu, B+-puu | 4 |
| yhtenäisyys, ekvivalenssiluokat | union-find | 6 |
| etuliitesummat ja pistepäivitykset | Fenwick-puu | 7 |
| välikyselyt ja välipäivitykset | (laiska) segmenttipuu | 7 |
| hahmon haku tekstistä | KMP, Z, Rabin–Karp | 8 |
| etuliitekyselyt sanastosta | trie | 9 |
| toistuvat haut samasta tekstistä | suffiksi- ja LCP-taulukko | 9 |
| kapasiteetit, paritus, leikkaukset | Dinic, Kuhn | 10 |
| rinnakkainen järjestetty joukko | skip-lista | 11 |
| jäsenyys pienellä muistilla | Bloom-suodatin | 12 |
| esiintymät ja suosituimmat virrasta | Count-Min | 12 |
| NP-vaikea optimointi | approksimaatio, heuristiikka, karsinta | 14 |

## Nyrkkisäännöt

1. Käytä kirjaston rakennetta, kun se riittää. Oma rakenne on
   perusteltu, kun tarvitset jotain, mitä kirjasto ei anna.
2. Kirjoita malli ja vertailutesti ennen toteutusta. Malli on usein
   kirjaston säiliö tai raaka haku.
3. Kirjoita invarianttien tarkistus jäsenfunktioksi ja kutsu sitä
   testissä jokaisen operaation jälkeen.
4. Testaa pienillä avainavaruuksilla ja pienillä rakenteilla.
   Rajatapaukset toistuvat silloin usein.
5. Pienennä epäonnistunut operaatiosarja ja tallenna se
   regressiotestiksi.
6. Tarkista, mitä operaatioita tasoitettu raja koskee. Uusi
   operaatio voi kumota sen.
7. Käytä hystereesiä kaikissa kasvatus- ja kutistuskynnyksissä.
8. Satunnaista jakoalkiot ja prioriteetit, ja pidä siemen
   arvaamattomana, kun syöte tulee ulkoa.
9. Älä luota hajautusarvoon ilman vertailua. Käytä
   alkulukumodulia ja satunnaista kantaa.
10. Mallinna ongelma virtauksena tai parituksena ennen oman
    algoritmin keksimistä, ja tulosta leikkaus tai peite todistukseksi.
11. Tunnista NP-vaikea ongelma reduktiolla, ja valitse sitten
    approksimaatio, heuristiikka tai karsinta tietoisesti.
12. Laske ala- tai yläraja jokaiselle heuristiikalle, niin tiedät
    tuloksen laadun ilman optimia.

## Testaaminen

Jokaisen tämän tutoriaalin rakenteen ja algoritmin testaus nojaa
kolmeen kerrokseen:

- **Vertailu malliin:** satunnaiset operaatiosarjat kiinteällä
  siemenellä. Mallina toimii kirjaston säiliö, raaka haku, toinen
  algoritmi samalle tehtävälle tai matemaattinen lause, kuten
  max-flow min-cut ja Königin lause.
- **Invariantit:** punamustan puun värisäännöt, B-puun avainmäärät ja
  lehtisyvyydet, tasoitetun hinnan raja ja Count-Minin "ei koskaan liian
  pieni".
- **Mittaus laskureilla:** korkeus, luetut solmut, kuljetut linkit,
  vertailut ja hakupuun solmut. Ne todentavat analyysin ennusteet
  toistettavasti.

Lisäksi kaikki esimerkit ajetaan AddressSanitizerin ja
UndefinedBehaviorSanitizerin kanssa, jotka löytävät muistivirheet ennen
kuin ne näkyvät tuloksissa.

## Jatkotaidot

- **Kääntäjätekniikka** käyttää trietä ja automaatteja
  sanastoanalyysissä, verkon väritystä rekisterien varauksessa
  (NP-täydellinen, ratkaistaan heuristiikoilla) ja union-findia
  tyyppipäättelyssä.
- **Suorituskyvyn analyysi ja optimointi** jatkaa siitä, mihin
  laskurit loppuvat: B-puun solmun koko välimuistirivien mukaan,
  haun vektorointi ja muistin asettelu mitataan oikealla kellolla.
- **Hajautetut järjestelmät** käyttää Bloom-suodattimia, tiivistelmiä,
  johdonmukaista hajautusta ja Merkle-puita datan synkronointiin.
- **Säteenseuranta ja fysikaalinen valaistus** rakentaa avaruutta
  jakavia puita (BVH, kd-puu), joiden rakentaminen on
  optimointitehtävä samaan tapaan kuin tämän tutoriaalin luvuissa.

## Lähteet

- Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest ja Clifford
  Stein: *Introduction to Algorithms*, 4. painos, MIT Press 2022.
  B-puut (luku 18), tasoitettu analyysi, union-find, virtaukset,
  merkkijonohaku, NP-täydellisyys ja approksimointi.
- Robert Sedgewick ja Kevin Wayne: *Algorithms*, 4. painos,
  Addison-Wesley 2011, <https://algs4.cs.princeton.edu>. Vasemmalle
  kallistuva punamusta puu, union-find ja perkolaatio, trie ja
  suffiksitaulukot.
- Robert Sedgewick: *Left-leaning Red-Black Trees*, Dagstuhl Workshop
  on Data Structures 2008. Lisäys ja poisto, joita luku 3 seuraa.
- Jon Kleinberg ja Éva Tardos: *Algorithm Design*, Pearson 2005.
  Virtausten sovellukset, reduktiot ja approksimointi.
- Michael Mitzenmacher ja Eli Upfal: *Probability and Computing*,
  2. painos, Cambridge University Press 2017. Satunnaistetut
  algoritmit, Bloom-suodattimet ja tiivistelmät.
- Rajeev Motwani ja Prabhakar Raghavan: *Randomized Algorithms*,
  Cambridge University Press 1995. Treap, skip-lista ja Freivaldsin
  menetelmä.
- David P. Williamson ja David B. Shmoys: *The Design of
  Approximation Algorithms*, Cambridge University Press 2011,
  <https://www.designofapproxalgs.com>. Vapaasti luettavissa.
- Dan Gusfield: *Algorithms on Strings, Trees, and Sequences*,
  Cambridge University Press 1997. Z-algoritmi, suffiksipuut ja
  -taulukot.
- Antti Laaksonen: *Kisakoodarin käsikirja*, 2018,
  <https://www.cs.helsinki.fi/u/ahslaaks/kkkk.pdf>. Suomeksi:
  segmenttipuu, Fenwick-puu, union-find, merkkijonohajautus ja
  virtaukset kilpaohjelmoinnin näkökulmasta.
- Michael R. Garey ja David S. Johnson: *Computers and
  Intractability: A Guide to the Theory of NP-Completeness*,
  W. H. Freeman 1979. NP-täydellisten ongelmien luettelo.
- Burton H. Bloom: *Space/Time Trade-offs in Hash Coding with
  Allowable Errors*, Communications of the ACM 13(7), 1970.
- Graham Cormode ja S. Muthukrishnan: *An Improved Data Stream
  Summary: The Count-Min Sketch and its Applications*, Journal of
  Algorithms 55(1), 2005.
- William Pugh: *Skip Lists: A Probabilistic Alternative to Balanced
  Trees*, Communications of the ACM 33(6), 1990.
- Toru Kasai ym.: *Linear-Time Longest-Common-Prefix Computation in
  Suffix Arrays and Its Applications*, CPM 2001.
- Robert E. Tarjan: *Efficiency of a Good But Not Linear Set Union
  Algorithm*, Journal of the ACM 22(2), 1975.

## Lisenssi

Tämä tutoriaali ja sen esimerkkikoodit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0,
<https://creativecommons.org/licenses/by-sa/4.0/deed.fi>). Teosta saa
kopioida, levittää ja muokata, kunhan alkuperäinen lähde mainitaan ja
muokatut versiot jaetaan samalla lisenssillä.
