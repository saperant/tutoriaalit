# Binäärihakupuut

Hajautustaulu löytää avaimen nopeasti mutta ei tiedä mitään avainten
järjestyksestä. *Binäärihakupuu* (engl. binary search tree) säilyttää
järjestyksen: jokaisen solmun vasemmassa alipuussa ovat sitä pienemmät
avaimet ja oikeassa suuremmat. Haku, lisäys ja poisto kulkevat yhden
polun juuresta alaspäin, joten niiden hinta on puun *korkeus*. Puun
peruskäsitteet ja rekursio ovat tuttuja diskreetistä matematiikasta;
tässä luvussa puu rakennetaan muistiin ja mitataan, mitä korkeudelle
tapahtuu.

## Solmu, haku ja lisäys

Solmussa on avain ja kaksi lapsiosoitinta:

```{.dot otsikko="Binäärihakupuu: vasemmassa alipuussa pienemmät, oikeassa suuremmat avaimet" leveys="50%"}
digraph {
  nodesep=0.3; ranksep=0.35;
  node [shape=circle, width=0.4, fixedsize=true, fontsize=10];
  8 -> 3; 8 -> 10; 3 -> 1; 3 -> 6; 6 -> 4; 6 -> 7; 10 -> 14; 14 -> 13;
  n1 [shape=point, style=invis]; 10 -> n1 [style=invis];
}
```

```{.c tiedosto="esimerkit/08-hakupuu.c" osa="solmu"}
```

Haku vertaa avainta solmun avaimeen ja jatkaa vasemmalle tai oikealle.
Lisäys tekee saman ja kiinnittää uuden solmun siihen tyhjään linkkiin,
johon haku päättyi. Osoitin osoittimeen (luku 4) tekee juuresta
tavallisen linkin, joten tyhjä puu ei ole erikoistapaus:

```{.c tiedosto="esimerkit/08-hakupuu.c" osa="lisaa"}
```

Kummassakin silmukka korvaa rekursion. Rekursiivinen versio olisi yhtä
lyhyt, mutta epätasapainoisessa puussa (alla) rekursion syvyys voisi
olla tuhansia kutsuja.

## Läpikäynnit

Puun solmut voi käydä läpi kolmessa syvyyshakujärjestyksessä sen
mukaan, milloin solmu käsitellään suhteessa lapsiinsa:

| Järjestys | Solmu käsitellään | Tyypillinen käyttö |
|-----------|-------------------|--------------------|
| esijärjestys (preorder) | ennen lapsia | puun kopiointi, sarjallistaminen |
| sisäjärjestys (inorder) | lasten välissä | avaimet kasvavassa järjestyksessä |
| jälkijärjestys (postorder) | lasten jälkeen | vapautus, alipuiden koot |

Hakupuun sisäjärjestys tuottaa avaimet lajiteltuina – se on suora
seuraus järjestysehdosta:

```{.c tiedosto="esimerkit/08-hakupuu.c" osa="sisajarjestys"}
```

Puun vapautus on jälkijärjestys: lapset vapautetaan ennen solmua,
jonka kentistä niiden osoitteet luetaan. Leveyshaku (taso kerrallaan)
tehdään jonolla, kuten graafeissa (luku 10).

## Poisto

Poistossa on kolme tapausta. Lehti poistetaan suoraan. Solmu, jolla
on yksi lapsi, korvataan lapsellaan. Solmulla, jolla on kaksi lasta,
ei ole yhtä paikkaa, johon molemmat alipuut voisi kiinnittää. Siksi
sen avain korvataan *seuraajalla* – oikean alipuun pienimmällä
avaimella – ja seuraajan solmu poistetaan. Seuraajalla ei voi olla
vasenta lasta, joten sen poisto on yksi kahdesta helposta tapauksesta.

```{.c tiedosto="esimerkit/08-hakupuu.c" osa="poista"}
```

Avaimet 50, 30, 70, 20, 40, 60, 80 ja 35 tuottavat puun, jossa
solmulla 30 on kaksi lasta. Sen seuraaja on 35:

```{.tuloste tiedosto="esimerkit/08-hakupuu.odotettu"}
```

Tulosteen kaksi ensimmäistä riviä näyttävät, että sisäjärjestys
säilyy poistossa, ja kolmas, että 35 nousi poistetun solmun paikalle.
Seuraavat rivit käsitellään alla.

## Epätasapaino

Puun korkeus riippuu lisäysjärjestyksestä. Satunnaisessa järjestyksessä
lisätyn puun odotettu korkeus on $O(\log n)$, noin $3 \log_2 n$
suurilla $n$. Mutta jos avaimet tulevat järjestyksessä, jokainen uusi
avain on edellistä suurempi ja menee oikealle, ja puusta tulee
linkitetty lista:

```{.c tiedosto="esimerkit/08-hakupuu.c" osa="korkeus"}
```

Tuhannen avaimen puun korkeus on järjestyksessä lisättynä 1000 ja
satunnaisesti lisättynä 21 (vertailun vuoksi $\log_2 1000 \approx 10$).
Järjestyksessä tulevat avaimet eivät ole harvinainen erikoistapaus:
aikaleimat, juoksevat tunnisteet ja valmiiksi lajiteltu syöte tuottavat
niitä jatkuvasti. Tavallinen hakupuu on siksi käyttökelpoinen vain,
kun syötteen järjestys on satunnainen tai sen voi sekoittaa.

*Tasapainotetut* hakupuut korjaavat ongelman: punamusta puu, AVL-puu
ja treap säilyttävät korkeuden $O(\log n)$ kääntämällä solmuja
(engl. rotation) lisäyksen ja poiston jälkeen. Ne ovat tavallisen
hakupuun laajennuksia: haku ja läpikäynnit ovat samat, vain lisäys ja
poisto tekevät lisätyötä. Tasapainotusalgoritmit kuuluvat taitoon
*Edistyneet algoritmit ja tietorakenteet*. Levylle ja muistille, jossa lukeminen tapahtuu lohkoina,
käytetään B-puuta, jonka solmussa on kymmeniä tai satoja avaimia.

## Invariantti ja vertailutesti

Hakupuun invariantti on helppo muotoilla väärin. Ei riitä, että
jokainen lapsi on oikealla puolella vanhempaansa: puussa, jonka juuri
on 50, vasen lapsi 30 ja sen oikea lapsi 60, jokainen vanhempi–lapsi-pari
on kunnossa, mutta 60 on väärässä alipuussa. Oikea ehto on, että
jokainen avain on niiden rajojen sisällä, jotka sen kaikki esivanhemmat
määräävät:

```{.c tiedosto="esimerkit/08-hakupuu.c" osa="invariantti"}
```

Testi ajaa satunnaisen operaatiosarjan sekä puulle että
totuusarvotaulukolle ja tarkistaa invariantin jokaisen operaation
jälkeen. Pieni avainalue saa poistot osumaan usein kahden lapsen
solmuihin, joissa virheet tavallisesti ovat:

```{.c tiedosto="esimerkit/08-hakupuu.c" osa="vertailu"}
```

Invariantin tarkistus jokaisen operaation jälkeen on $O(n)$, joten
testi on hidas suurilla puilla. Se ei haittaa: tarkoitus on löytää
virhe pienestä puusta heti sen synnyttyä, ei mitata nopeutta.

## Käytännössä

- **Älä käytä tasapainottamatonta puuta järjestyksessä tulevalle
  datalle.** Korkeus on silloin $n$, ja jokainen operaatio $O(n)$.
- **Valmis tasapainotettu puu** (esimerkiksi BSD:n `<sys/tree.h>`
  -makrot tai kirjaston punamusta puu) on parempi kuin oma.
- **Lajiteltu taulukko** on usein parempi kuin puu, jos data
  muuttuu harvoin: sama $O(\log n)$-haku, ei osoittimia, ja välikyselyt
  ovat peräkkäisiä lukuja.
- **Iteratiivinen haku ja lisäys.** Rekursio on selkeä
  läpikäynneissä, mutta syvässä puussa se voi ylittää kutsupinon.
- **Invariantti rajoilla, ei vanhempi–lapsi-pareilla.**

## Itsearviointi

- Osaat toteuttaa hakupuun haun, lisäyksen ja poiston, myös kahden
  lapsen solmun poiston seuraajalla.
- Osaat kertoa, mitä esi-, sisä- ja jälkijärjestys tuottavat ja mihin
  kutakin käytetään.
- Osaat selittää, miksi järjestyksessä lisätty puu rappeutuu listaksi,
  ja näyttää sen korkeutta mittaamalla.
- Osaat kirjoittaa hakupuun invariantin, joka tarkistaa avainten rajat
  esivanhempien perusteella.
