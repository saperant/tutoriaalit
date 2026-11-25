# Törmäysvaste

Kosketuspiste ja normaali kertovat, missä kappaleet koskettavat.
Tässä luvussa lasketaan, mitä kosketuksessa tapahtuu: kuinka suuri
impulssi kappaleiden välillä vaihtuu, kun kumpikin saa myös pyöriä.
Kaava on sama kuin taidon *Peliohjelmointi* impulssivasteessa, mutta
nimittäjään tulee kaksi uutta termiä. Luku käsittelee yhden
kosketuspisteen; monta yhtäaikaista kosketusta on luvun 7 aihe.

## Impulssi, kun kappaleet pyörivät

Kosketuspisteessä $\mathbf p$ kappaleiden pinnoilla on nopeudet
$\mathbf v_a + \boldsymbol\omega_a \times \mathbf r_a$ ja
$\mathbf v_b + \boldsymbol\omega_b \times \mathbf r_b$. Niiden erotuksen
komponentti normaalin suunnassa, $v_n$, on negatiivinen, kun pinnat
lähestyvät toisiaan. Törmäys antaa kappaleelle $b$ impulssin
$j\mathbf n$ ja kappaleelle $a$ vastakkaisen. Suuruus $j$ valitaan
niin, että törmäyksen jälkeen normaalinopeus on $-e\,v_n$, missä $e$ on
kimmokerroin:

$$j = \frac{-(1 + e)\,v_n}
  {\dfrac1{m_a} + \dfrac1{m_b}
   + \mathbf n \cdot \bigl[(I_a^{-1}(\mathbf r_a \times \mathbf n))
     \times \mathbf r_a\bigr]
   + \mathbf n \cdot \bigl[(I_b^{-1}(\mathbf r_b \times \mathbf n))
     \times \mathbf r_b\bigr]}.$$

Nimittäjä kertoo, kuinka paljon yksikköimpulssi muuttaa pisteiden
nopeuseroa. Kaksi ensimmäistä termiä ovat tutut käänteismassat. Kaksi
jälkimmäistä tulevat pyörimisestä: impulssi panee kappaleen
kääntymään, ja kääntyminen liikuttaa kosketuspistettä. Mitä kauempana
massakeskipisteestä osuma on ja mitä pienempi hitausmomentti, sitä
suurempi termi ja sitä pienempi impulssi tarvitaan. Edellisen luvun
havainto pätee: osumakohdasta katsoen pyörimään pääsevä kappale on
kevyempi kuin sen massa.

```{.cpp tiedosto="esimerkit/05-tormays.cpp" osa="impulssi"}
```

## Säilymislait testinä

Esimerkissä pallo osuu avaruudessa leijuvan lankun päähän. Ulkoisia
voimia ei ole, joten kokonaisliikemäärän ja
kokonaisliikemäärämomentin on säilyttävä jokaisella kimmokertoimella.

```{.cpp tiedosto="esimerkit/05-tormays.cpp" osa="tilanne"}
```

```{.cpp tiedosto="esimerkit/05-tormays.cpp" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/05-tormays.odotettu" rivit="1-18"}
```

![Pallo osuu lankun päähän ylhäältä katsottuna, kimmokerroin 0,5,
puolen sekunnin välein. Lankku lähtee sekä etenemään että
pyörimään.](kuvat/tormays.png){width=100%}

Liikemäärä ja liikemäärämomentti ovat samat ennen ja jälkeen kaikissa
kolmessa tapauksessa. Liike-energia säilyy vain, kun $e = 1$.
Kimmottomassa törmäyksessä ($e = 0$) pallon nopeus on sama kuin lankun
osumakohdan nopeus, eli kappaleet liikkuvat kosketuskohdassa yhdessä,
vaikka lankun massakeskipiste liikkuu hitaammin.

Tällainen testi on fysiikkakoodin tärkein: se ei vertaa lukuja
aiempaan ajoon vaan lakiin, jonka täytyy päteä. Merkkivirhe ristitulossa
tai väärä varsi näkyy heti liikemäärämomentin muutoksena.

## Osuma, joka panee pyörimään

Toinen tarkistus käyttää liikemäärämomenttia toisin. Kun lankku putoaa
niin, että vain sen toinen pää osuu esteeseen, impulssin varsi
osumakohdan suhteen on nolla. Lankun liikemäärämomentti *osumakohdan
suhteen* ei siis muutu, vaikka sen liike muuttuu täysin.

```{.cpp tiedosto="esimerkit/05-tormays.cpp" osa="pudotus"}
```

```{.tuloste tiedosto="esimerkit/05-tormays.odotettu" alkaen="lankun pää osuu"}
```

Osunut pää pysähtyy pystysuunnassa, massakeskipiste jatkaa alas
hitaammin ja vapaa pää kiihtyy: se liikkuu osuman jälkeen nopeammin
kuin ennen sitä. Lautapelin nappula tai pudonnut kirja käyttäytyy
juuri näin, ja ilmiö syntyy kaavasta ilman erillistä koodia.

Osuneen pään vaakanopeus ei ole nolla, koska tässä luvussa ei ole
kitkaa: impulssi vaikuttaa vain normaalin suunnassa.

## Kimmokerroin

Kimmokerroin on kahden materiaalin yhteinen ominaisuus, mutta
moottorissa se tallennetaan kappaleeseen. Parin arvo yhdistetään
säännöllä; tämän tutoriaalin moottori käyttää suurempaa arvoista,
jolloin superpallo pomppaa myös betonilattialta.

Todellinen kimmokerroin riippuu törmäysnopeudesta, ja hitaissa
osumissa se on käytännössä nolla. Moottorissa on siksi nopeusraja
(`kimmoraja`), jota hitaampi osuma käsitellään kimmottomana. Ilman
rajaa lattialla lepäävä kappale pomppisi loputtomasti painovoiman
joka askeleella antamasta nopeudesta, kuten taidon *Peliohjelmointi*
lepäävien kosketusten esimerkissä.

## Käytännössä

- **Nopeus muuttuu, sijainti ei.** Impulssi korjaa nopeudet. Jo
  syntynyt limitys on eri ongelma, ja se ratkaistaan luvussa 7.
- **Erkanevaa kosketusta ei kosketa.** Jos pinnat jo loittonevat,
  impulssia ei anneta; muuten kappaleet liimautuisivat toisiinsa.
- **Säilymislait yksikkötesteiksi.** Liikemäärä ja liikemäärämomentti
  ennen ja jälkeen ovat halpoja laskea, ja ne paljastavat useimmat
  virheet. Energia ei saa kasvaa.
- **Kimmokerroin alle yhden.** Arvolla 1 pyöristysvirheet voivat
  lisätä energiaa, ja kappale pomppii yhä korkeammalle. Peleissä
  suurin käytetty arvo on tavallisesti 0,8–0,9.
- **Yksi piste kerrallaan ei riitä.** Kun kappaleella on monta
  kosketusta, jokaisen impulssi muuttaa muiden tilannetta. Pisteet
  on ratkaistava yhdessä, mihin seuraavat kaksi lukua tähtäävät.

## Itsearviointi

- Osaat kirjoittaa törmäysimpulssin kaavan ja selittää nimittäjän
  jokaisen termin.
- Osaat perustella, miksi päähän osuva impulssi on pienempi kuin
  keskelle osuva.
- Osaat käyttää liikemäärän ja liikemäärämomentin säilymistä
  törmäyskoodin testinä.
- Osaat selittää, miksi hitaat osumat käsitellään kimmottomina.
