# Lopuksi {.runko-lahteet}

## Rakenteen valinta

Ensin kannattaa kysyä, mitä datalle tehdään useimmin, ja vasta sitten
valita rakenne. Taulukko kokoaa tutoriaalin rakenteet:

| Tarve | Rakenne | Hinta | Luku |
|-------|---------|-------|------|
| Lisäys loppuun, indeksointi | vektori | tasoitettu $O(1)$, $O(1)$ | 3 |
| Pysyvät osoittimet, irrotus keskeltä | kaksoislinkitetty lista | $O(1)$ | 4 |
| LIFO | pino taulukossa | $O(1)$ | 5 |
| FIFO, kiinteä koko | rengaspuskuri | $O(1)$ | 5 |
| FIFO tai molemmat päät, kasvava | pakka (kasvava rengaspuskuri) | tasoitettu $O(1)$ | 5 |
| Onko avain mukana? | hajautustaulu | odotusarvo $O(1)$ | 6–7 |
| Järjestys, välit, lähin arvo | tasapainotettu hakupuu | $O(\log n)$ (väli: lisäksi tulosten määrä) | 8 |
| Harvoin muuttuva järjestetty joukko | lajiteltu taulukko | haku $O(\log n)$ | 2 |
| Pienin ensin | binäärikeko | $O(\log n)$, kekoutus $O(n)$ | 9 |
| Harva graafi | vierekkäisyyslistat, CSR | $O(n + m)$ muistia | 10 |
| Pieni $n$ (kymmeniä) | taulukko ja lineaarihaku | $O(n)$, mutta nopea | 11 |

## Nyrkkisäännöt

1. Aloita taulukosta. Vaihda rakennetta vasta, kun mittaus tai
   operaatioiden hinta osoittaa, että taulukko ei riitä.
2. Piilota toteutus rajapinnan taakse, jotta rakenteen voi vaihtaa
   koskematta käyttäjän koodiin.
3. Kasvata dynaamisia rakenteita kertomalla, älä lisäämällä.
4. Viittaa kasvavaan taulukkoon indeksillä, ei osoittimella.
5. Varaa muisti ennen kuin muutat rakennetta, jotta muistin loppuminen
   jättää sen ennalleen.
6. Käytä valmista hajautusfunktiota, ja avaimellista, jos avaimet
   tulevat ulkoa.
7. Pidä hajautustaulun kuormituskerroin kurissa ja laske hautakivet
   kuormaan.
8. Älä käytä tasapainottamatonta hakupuuta datalle, joka voi tulla
   järjestyksessä.
9. Kirjoita jokaiselle rakenteelle invariantin tarkistusfunktio ja
   satunnaistettu vertailutesti kiinteällä siemenellä.
10. Mittaa välimuistin vaikutus laskureilla tai väljillä rajoilla, älä
    tarkoilla ajoilla.

## Testaaminen

Tutoriaalin rakenteet testattiin samalla kolmen kerroksen mallilla,
joka sopii mihin tahansa omaan rakenteeseen:

- **Vertailutesti:** satunnainen operaatiosarja kiinteällä siemenellä,
  vertailu yksinkertaiseen referenssiin (totuusarvotaulukko, lajiteltu
  taulukko). Pieni avainalue tuottaa toistoja ja rajatapauksia.
- **Invariantti:** tarkistusfunktio, jota kutsutaan jokaisen
  operaation jälkeen testissä ja `assert`-makrolla kehitysversiossa.
- **Sanitoijat:** AddressSanitizer ja UndefinedBehaviorSanitizer
  havaitsevat roikkuvat osoittimet, taulukon ylitykset ja
  ylivuodot heti.

Ominaisuuspohjaiset testikirjastot (C:ssä esimerkiksi *theft*) ja
sumeat testaajat (libFuzzer, AFL++) vievät saman idean pidemmälle:
ne generoivat syötteet ja pienentävät löytämänsä virheelliset
operaatiosarjat lyhimmiksi mahdollisiksi.

## Jatkotaidot

- **Algoritmit** käyttää tämän tutoriaalin rakenteita ja määrittelee
  aika- ja tilavaativuuden täsmällisesti: lajittelu ja haku, ahneet
  algoritmit ja dynaaminen ohjelmointi sekä graafialgoritmit (leveys-
  ja syvyyshaku, Dijkstra keolla, virittävät puut).
- **Edistyneet algoritmit ja tietorakenteet** jatkaa siitä:
  tasapainotetut puut ja B-puut, trie, segmenttipuu, union–find ja
  satunnaistetut rakenteet.
- **Suorituskyvyn analyysi ja optimointi** syventää luvun 11 aiheita:
  suorituskykylaskurit, profilointi ja välimuistitietoinen
  ohjelmointi.

## Lähteet

- Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest ja Clifford
  Stein: *Introduction to Algorithms*, 4. painos, MIT Press 2022. Kaikkien
  tämän tutoriaalin rakenteiden analyysi: tasoitettu aika, hajautus,
  hakupuut, keot.
- Robert Sedgewick ja Kevin Wayne: *Algorithms*, 4. painos,
  Addison-Wesley 2011. Käytännönläheinen esitys, jossa paljon
  mittauksia; aineisto osoitteessa <https://algs4.cs.princeton.edu>.
- Donald E. Knuth: *The Art of Computer Programming*, osa 1
  (*Fundamental Algorithms*: listat, pinot, puut) ja osa 3 (*Sorting
  and Searching*: hajautus, hakupuut, lineaarisen kokeilun analyysi).
  Addison-Wesley.
- Ulrich Drepper: *What Every Programmer Should Know About Memory*,
  2007, <https://people.freebsd.org/~lstewart/articles/cpumemory.pdf>.
  Välimuistit, muistihierarkia ja niiden vaikutus ohjelmiin.
- Glenn Fowler, Landon Curt Noll, Kiem-Phong Vo ja Donald Eastlake:
  *The FNV Non-Cryptographic Hash Algorithm*, IETF-luonnos,
  <https://datatracker.ietf.org/doc/draft-eastlake-fnv/>.
- Jean-Philippe Aumasson ja Daniel J. Bernstein: *SipHash: a fast
  short-input PRF*, INDOCRYPT 2012. Avaimellinen hajautus
  vihamielisiä avaimia vastaan.
- Linuxin ytimen tunkeileva lista: `include/linux/list.h` ja makro
  `container_of`, <https://www.kernel.org/doc/html/latest/core-api/kernel-api.html>.
- Malte Skarupke: *I Wrote The Fastest Hashtable*, 2017, ja Abseilin
  Swiss Tables -dokumentaatio <https://abseil.io/about/design/swisstables>.
  Avoimen osoitteistuksen nykyaikaiset toteutukset.

## Lisenssi

Tämä tutoriaali ja sen esimerkkikoodit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0,
<https://creativecommons.org/licenses/by-sa/4.0/deed.fi>). Teosta saa
kopioida, levittää ja muokata, kunhan alkuperäinen lähde mainitaan ja
muokatut versiot jaetaan samalla lisenssillä.
