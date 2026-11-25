# Johdanto {.runko-johdanto}

Tietorakenne on tapa järjestää data muistiin niin, että ohjelman
tarvitsemat operaatiot ovat halpoja. Sama data – esimerkiksi joukko
käyttäjätunnuksia – voidaan tallentaa taulukkoon, linkitettyyn listaan,
hajautustauluun tai puuhun. Jokainen rakenne tekee jostain operaatiosta
halvan ja jostain kalliin. Rakenteen valinta on siksi kysymys siitä,
mitä datalle tehdään useimmin.

Tämä tutoriaali käy läpi ohjelmoinnin perusrakenteet C:llä:

- **Abstraktit tietotyypit:** rajapinta erillään toteutuksesta,
  virhekoodit ja omistajuus.
- **Taulukot ja listat:** dynaaminen taulukko ja sen kasvatus,
  yksöis- ja kaksoislinkitetyt listat, tunnussolmu ja tunkeileva lista.
- **Pinot, jonot ja rengaspuskurit:** LIFO ja FIFO taulukolla,
  rengaspuskurin indeksit.
- **Hajautustaulut:** hajautusfunktiot, ketjutus ja avoin
  osoitteistus, kuormituskerroin ja hautakivet.
- **Puut ja keot:** binäärihakupuu, sen epätasapaino ja binäärikeko
  prioriteettijonona.
- **Graafit:** vierekkäisyysmatriisi, -listat ja CSR.
- **Välimuisti ja datan asettelu:** miksi taulukko voittaa listan
  käytännössä useammin kuin teoria antaa ymmärtää.

## Esitiedot ja rajaus

Tutoriaali rakentuu taitojen *C-kieli* ja *Diskreetti matematiikka*
päälle. Osoittimet, `malloc` ja `free` sekä rakenteet oletetaan
tutuiksi C-kielestä; graafit, puut, rekursio ja O-merkintä
($O(1)$, $O(\log n)$, $O(n)$) diskreetistä matematiikasta.

Rajauksen ulkopuolelle jäävät:

- lajittelu- ja graafialgoritmit sekä algoritmien analyysi
  (jatkotaito *Algoritmit*),
- tasapainotetut hakupuut, B-puut, trie ja union-find (*Edistyneet
  algoritmit ja tietorakenteet*),
- lukottomat ja usean säikeen rakenteet (*Rinnakkaisohjelmointi*) ja
- välimuistin mittaaminen suorituskykylaskureilla (*Suorituskyvyn
  analyysi ja optimointi*); luku 11 näyttää ilmiön, ei mittaustekniikkaa.

## Miksi rakenteella on väliä

Kirjautumislokissa on 5000 käyttäjätunnusta väliltä 0–19 999. Kuinka
moni tunnus esiintyy useammin kuin kerran? Kysymykseen voi vastata
vertaamalla jokaista tunnusta kaikkiin aiempiin:

```{.c tiedosto="esimerkit/01-duplikaatit.c" osa="naiivi"}
```

Lajittelu tuo samat tunnukset vierekkäin, jolloin yksi läpikäynti
riittää. Esimerkki käyttää omaa lomituslajittelua, joka laskee
vertailut; standardin `qsort` tekisi saman, mutta sen vertailujen määrä
riippuu C-kirjaston toteutuksesta:

```{.c tiedosto="esimerkit/01-duplikaatit.c" osa="lajittelu"}
```

Koska tunnukset ovat pieniä kokonaislukuja, ne käyvät suoraan
taulukon indekseiksi. Taulukko kertoo, montako kertaa tunnus on nähty:

```{.c tiedosto="esimerkit/01-duplikaatit.c" osa="taulukko"}
```

```{.tuloste tiedosto="esimerkit/01-duplikaatit.odotettu"}
```

Vastaus on sama, mutta työn määrä vaihtelee 12,5 miljoonasta
vertailusta 5000 taulukon lukuun. Ero kasvaa datan mukana: kun lokissa
on miljoona tunnusta, naiivi tapa vaatii noin $5 \cdot 10^{11}$
vertailua, lajittelu noin $2 \cdot 10^7$ ja laskuritaulukko miljoona
lukua. Laskuritaulukko maksaa kuitenkin muistia koko *arvoalueen*
verran. Jos tunnukset olisivat 64-bittisiä, taulukko olisi mahdoton, ja
tarvittaisiin hajautustaulu (luvut 6 ja 7), joka tekee saman
odotusarvoisesti vakioajassa ja vie muistia vain tallennettujen
avainten verran.

## Abstrakti tietotyyppi ja toteutus

Tietorakenteista puhuttaessa kannattaa erottaa kaksi tasoa:

| Taso | Mitä se kertoo | Esimerkki |
|------|----------------|-----------|
| Abstrakti tietotyyppi | Operaatiot ja niiden merkitys | joukko: lisää, poista, sisältää |
| Tietorakenne | Miten data on muistissa | lajiteltu taulukko, hajautustaulu, puu |

Joukko voidaan toteuttaa monella rakenteella, ja jokainen antaa eri
hinnat samoille operaatioille. Hyvin suunniteltu rajapinta piilottaa
toteutuksen, jolloin rakenteen voi vaihtaa mittausten perusteella
muuttamatta käyttäjän koodia. Luku 2 näyttää, miten tämä tehdään C:ssä.

## Esimerkit ja testaus

Kaikki esimerkit ovat C23:a hakemistossa `esimerkit/`, ja `make testaa`
kääntää ja ajaa ne. Valmis ympäristö on kehityskontissa (ks.
*Kehitysympäristöt ja Dev Containers*). Esimerkit käännetään GCC 14:llä
ja Clang 20:llä varoitukset virheinä, AddressSanitizerin ja
UndefinedBehaviorSanitizerin kanssa. Sanitoijat pysäyttävät ohjelman,
jos se lukee vapautettua muistia tai taulukon ohi – tietorakenteiden
yleisimmät virheet.

Satunnaistetut testit käyttävät omaa pientä satunnaislukugeneraattoria,
jotta sama siemen antaa saman sarjan joka koneella:

```{.c tiedosto="esimerkit/satunnainen.h"}
```

Rakenteet testataan kolmella tavalla, jotka toistuvat koko
tutoriaalissa:

1. **Vertailutesti:** satunnainen operaatiosarja ajetaan sekä
   testattavalle rakenteelle että yksinkertaiselle referenssille, jonka
   oikeellisuus on ilmeinen (esimerkiksi totuusarvotaulukko). Tulosten on
   oltava samat.
2. **Invariantin tarkistus:** rakenteelle kirjoitetaan funktio, joka
   tarkistaa sen sisäiset ehdot (esimerkiksi hakupuun järjestyksen), ja
   sitä kutsutaan testeissä jokaisen operaation jälkeen.
3. **Sanitoijat:** muistivirheet ja määrittelemätön käyttäytyminen
   havaitaan heti eikä vasta, kun data on jo turmeltunut.

Vertailutestin menetelmä – malli, invariantit ja löydetyn virheen
pienentäminen – käsitellään perusteellisesti taidossa *Edistyneet
algoritmit ja tietorakenteet*. Tässä tutoriaalissa sitä käytetään
työkaluna.

Rakenteita kuvaavat kaaviot piirretään esimerkkien tulosteista
(`kaaviot/tee.py`), ja `make testaa` tarkistaa, että ne vastaavat
tulosteita. Kuva näyttää siis sen taulukon tai puun, jonka ohjelma
oikeasti rakensi.
