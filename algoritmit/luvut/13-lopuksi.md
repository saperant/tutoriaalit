# Lopuksi {.runko-lahteet}

## Menetelmän valinta

Uuden tehtävän edessä kannattaa kysyä ensin, mikä on syötteen
enimmäiskoko ja mikä kasvuluokka siihen riittää (luku 2). Sen jälkeen
taulukko auttaa valitsemaan menetelmän:

| Tehtävän piirre | Menetelmä | Luku |
|-----------------|-----------|------|
| järjestys auttaa (duplikaatit, haku, mediaani) | lajittelu | 3–5 |
| pienet kokonaislukuavaimet | laskemis- tai kantalukulajittelu | 5 |
| järjestetty data, kohta tai lukumäärä | binäärihaku | 6 |
| ehdokkaan tarkistus helppo, monotoninen ehto | haku arvoalueelta | 6 |
| riippumattomat osat, halpa yhdistäminen | hajota ja hallitse | 7 |
| turvallinen paikallinen valinta | ahne algoritmi | 8 |
| päällekkäiset osatehtävät, optimi tai lukumäärä | dynaaminen ohjelmointi | 9–10 |
| yhteydet, painottomat reitit, riippuvuudet | leveys- ja syvyyshaku | 11 |
| painotetut reitit, yhdistäminen | Dijkstra, Bellman–Ford, MST | 12 |

Jos mikään ei sovi ja syöte on pieni, raaka haku on hyvä aloitus. Se
on myös aina hyödyllinen testireferenssi nopeammalle algoritmille.

## Nyrkkisäännöt

1. Laske kasvuluokka ennen koodaamista ja vertaa sitä syötteen
   kokoon.
2. Kirjoita silmukan tai taulukon invariantti kommenttiin. Se on
   todistuksen ja koodin välinen sopimus.
3. Testaa jokainen nopea algoritmi raakaa referenssiä vastaan pienillä
   satunnaisilla syötteillä kiinteällä siemenellä.
4. Testaa ominaisuudet, kun oikeita vastauksia on monta: ratkaisun on
   oltava sallittu ja yhtä hyvä kuin referenssin.
5. Mittaa työtä laskureilla. Kello kuuluu erilliseen, optimoituun
   mittaukseen, jonka tulos tarkistetaan väljällä rajalla.
6. Kirjoita binäärihaku aina alarajan muodossa ja keskikohta
   muodossa `lo + (hi - lo) / 2`.
7. Kirjoita vertailija muodossa `(a > b) - (a < b)` ja pidä se
   johdonmukaisena.
8. Älä ota pikalajittelun jakoalkioksi ensimmäistä tai viimeistä
   alkiota, ja varaudu yhtä suuriin avaimiin.
9. Todista ahne algoritmi vaihtoargumentilla tai etsi sille
   vastaesimerkki raa'alla haulla.
10. Määrittele dynaamisen ohjelmoinnin osatehtävä sanoin ennen
    rekursiota ja tarkista rekonstruoitu ratkaisu.
11. Käytä Dijkstraa vain ei-negatiivisille painoille.
12. Rajoita rekursion syvyys: syötteen kokoinen syvyys kaataa ohjelman.

## Testaaminen

Tutoriaalin algoritmit testattiin kolmella kerroksella:

- **Tunnetut tulokset:** käsin tarkistettavat pienet syötteet ja
  kirjallisuuden arvot, kuten $F(93)$, lajittelualgoritmien tarkat
  vertailumäärät järjestetyillä syötteillä ja alaraja $\log_2 n!$.
- **Raaka vertailu:** satunnaiset syötteet, joiden koko ja arvoalue on
  pidetty pieninä, jotta reunatapaukset (tyhjät taulukot, toistot,
  tasapelit, epäyhtenäiset graafit) tulevat vastaan. Referenssinä
  kaikkien osajoukkojen tai kaikkien parien läpikäynti, kirjaston
  `qsort` tai toinen algoritmi samalle tehtävälle.
- **Sanitoijat:** UndefinedBehaviorSanitizer löytää etumerkillisen
  ylivuodon vertailijassa ja keskikohdassa, AddressSanitizer
  taulukon ohi menevät indeksit.

Ominaisuuspohjaiset testikirjastot ja sumeat testaajat (libFuzzer,
AFL++) automatisoivat saman idean: ne tuottavat syötteet itse ja
pienentävät virheen aiheuttavan syötteen lyhimmäksi mahdolliseksi.

## Jatkotaidot

- **Edistyneet algoritmit ja tietorakenteet** jatkaa tästä:
  tasapainotetut puut ja B-puut, union-find tarkemmin, segmenttipuu,
  merkkijonohaku, virtausalgoritmit ja laskennallinen vaativuus
  (P, NP ja NP-täydellisyys).
- **Kääntäjätekniikka** käyttää graafialgoritmeja ja dynaamista
  ohjelmointia: riippuvuusjärjestys, kontrollivuograafi, rekisterien
  varaus graafin värityksenä ja käskyjen valinta.
- **Hajautetut järjestelmät** soveltaa graafeja ja ahneita valintoja
  verkossa: reititys, kuormantasaus ja hajautettu konsensus.
- **Säteenseuranta ja fysikaalinen valaistus** rakentaa avaruuden
  jakavia puita hajota ja hallitse -menetelmällä.
- **Suorituskyvyn analyysi ja optimointi** jatkaa siitä, mihin
  asymptoottinen analyysi loppuu: välimuisti, haarautumisen ennustus ja
  vektorointi.

## Lähteet

- Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest ja Clifford
  Stein: *Introduction to Algorithms*, 4. painos, MIT Press 2022.
  Kaikkien tämän tutoriaalin algoritmien analyysi ja todistukset.
- Jon Kleinberg ja Éva Tardos: *Algorithm Design*, Pearson 2005.
  Ahneiden algoritmien vaihtoargumentit ja dynaamisen ohjelmoinnin
  suunnittelu erinomaisin esimerkein.
- Robert Sedgewick ja Kevin Wayne: *Algorithms*, 4. painos,
  Addison-Wesley 2011, <https://algs4.cs.princeton.edu>. Kolmijako,
  lajittelujen mittaukset ja graafialgoritmit käytännönläheisesti.
- Donald E. Knuth: *The Art of Computer Programming*, osa 2
  (*Seminumerical Algorithms*: Karatsuba ja nopea kertolasku) ja osa 3
  (*Sorting and Searching*: lajittelun alaraja, kantalukulajittelu).
  Addison-Wesley.
- Antti Laaksonen: *Kisakoodarin käsikirja*, 2018,
  <https://www.cs.helsinki.fi/u/ahslaaks/kkkk.pdf>. Suomenkielinen
  algoritmiikan kirja, jossa paljon dynaamista ohjelmointia ja
  graafialgoritmeja.
- Jon Bentley: *Programming Pearls*, 2. painos, Addison-Wesley 1999.
  Suurimman osasumman neljä ratkaisua ja binäärihaun oikeellisuus.
- Joshua Bloch: *Extra, Extra – Read All About It: Nearly All Binary
  Searches and Mergesorts are Broken*, Google Research Blog 2006.
  Keskikohdan ylivuoto.
- David A. Huffman: *A Method for the Construction of
  Minimum-Redundancy Codes*, Proceedings of the IRE 40(9), 1952.
- Eugene W. Myers: *An O(ND) Difference Algorithm and Its Variations*,
  Algorithmica 1, 1986. Gitin ja GNU diffin perusalgoritmi.
- Edsger W. Dijkstra: *A Note on Two Problems in Connexion with Graphs*,
  Numerische Mathematik 1, 1959. Lyhimmät polut ja pienin virittävä
  puu.
- David R. Musser: *Introspective Sorting and Selection Algorithms*,
  Software: Practice and Experience 27(8), 1997. Introsort.

## Lisenssi

Tämä tutoriaali ja sen esimerkkikoodit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0,
<https://creativecommons.org/licenses/by-sa/4.0/deed.fi>). Teosta saa
kopioida, levittää ja muokata, kunhan alkuperäinen lähde mainitaan ja
muokatut versiot jaetaan samalla lisenssillä.
