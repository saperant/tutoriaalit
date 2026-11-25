# Arvot, esitykset ja muisti {.runko-muisti}

Tcl-ohjelmoija ei varaa eikä vapauta muistia. Silti arvojen
muistimallin tunteminen ratkaisee, onko skripti nopea vai neliöllisen
hidas. Tämä luku selittää, miten tulkki säilyttää arvot ja milloin se
kopioi niitä.

## Kaksi esitystä ja viitelaskenta

Jokainen arvo on C-tason olio (`Tcl_Obj`), jolla on

- **merkkijonoesitys**, joka luodaan vain tarvittaessa,
- **sisäinen esitys** viimeisimmän käytön mukaan: kokonaisluku,
  liukuluku, lista, sanakirja, tavukoodi tai komentoviite,
- ja **viitemäärä**: montako muuttujaa, listan alkiota tai
  argumenttia viittaa olioon.

Sijoitus `set b $a` ei kopioi arvoa, vaan kasvattaa viitemäärää. Arvo
vapautuu, kun viitemäärä laskee nollaan, esimerkiksi `unset`-komennolla
tai kun proseduuri palaa. Viitesyklejä ei synny, koska arvot ovat
muuttumattomia: arvo ei voi sisältää viitettä itseensä.

## Esitysten muunnos

Kun arvoa käytetään eri tyyppinä kuin edellisellä kerralla, tulkki
muuntaa sisäisen esityksen. Tätä kutsutaan nimellä *shimmering*.
`tcl::unsupported::representation` näyttää esityksen, ja sitä voi
käyttää vianetsintään:

```{.tcl tiedosto="esimerkit/05-esitykset.tcl" osa="muunnos"}
```

`string length` tarvitsi merkkijonon, joten listaesitys korvautui
merkkijonoesityksellä. Seuraava `llength` jäsensi merkkijonon takaisin
listaksi. Yksittäin tämä on halpaa, mutta silmukassa jokainen
kierros jäsentää koko listan uudelleen.

## Kopiointi kirjoitettaessa

Arvot ovat muuttumattomia, joten muokkaus tuottaa uuden arvon. Tulkki
muokkaa kuitenkin paikallaan, jos arvoon on vain yksi viite (arvo on
*jakamaton*). Jaettu arvo kopioidaan ensin (*copy-on-write*).

```{.tcl tiedosto="esimerkit/05-esitykset.tcl" osa="osoite"}
```

```{.tuloste tiedosto="esimerkit/05-esitykset.odotettu"}
```

```{.dot otsikko="Kopiointi kirjoitettaessa. Jaettu arvo (kaksi viitettä) kopioidaan ennen muokkausta; K-yhdistelmän jälkeen viitteitä on yksi, ja listaa muokataan paikallaan."}
digraph {
  rankdir=LR; ranksep=0.4; node [shape=box];
  subgraph cluster_a {
    label="lreplace $data 0 0 1"; labeljust=l; style=dashed;
    m1 [label="muuttuja data", shape=plaintext];
    g1 [label="argumentti", shape=plaintext];
    o1 [label="lista\nviitteitä 2"];
    k1 [label="kopio\nmuokattu"];
    m1 -> o1; g1 -> o1; o1 -> k1 [label="kopioi 100 000\nalkiota"];
  }
  subgraph cluster_b {
    label="lreplace $data[set data {}] 0 0 2"; labeljust=l; style=dashed;
    m2 [label="muuttuja data\n(tyhjennetty)", shape=plaintext];
    g2 [label="argumentti", shape=plaintext];
    o2 [label="lista\nviitteitä 1\nmuokataan paikallaan"];
    g2 -> o2; m2 -> o2 [style=invis];
  }
}
```

Lausekkeessa `set data [lreplace $data 0 0 1]` arvoon viittaavat sekä
muuttuja että `lreplace`-komennon argumentti, joten koko 100 000 alkion
lista kopioidaan yhden alkion vaihtamiseksi. *K-yhdistelmä*
`$data[set data {}]` tyhjentää muuttujan argumentin laskemisen
aikana. Silloin arvoon jää vain argumentin viite, ja `lreplace` muokkaa
sitä paikallaan. Komennot `lappend`, `lset`, `dict set`, `dict lappend`
ja `append` muokkaavat muuttujaa suoraan, joten niissä ongelmaa ei ole.

## Hinnat mitattuna

Esimerkki mittaa kolme tyypillistä hintaa. Ajat vaihtelevat koneittain,
joten tulostetaan vain suuruusluokka.

```{.tcl tiedosto="esimerkit/05-hinnat.tcl" osa="kasvatus"}
```

```{.tcl tiedosto="esimerkit/05-hinnat.tcl" osa="muunnos"}
```

```{.tcl tiedosto="esimerkit/05-hinnat.tcl" osa="expr"}
```

```{.tuloste tiedosto="esimerkit/05-hinnat.odotettu"}
```

Mittauksessa merkkijonona kasvatettu lista oli noin 25 kertaa ja
aaltosulkeeton `expr` noin 24 kertaa hitaampi. Esitysten muunnos
silmukassa oli 2 000 alkion listalla tuhansia kertoja hitaampi, koska
työ muuttui neliölliseksi.

## Muistin vapauttaminen

- Suuret väliaikaiset arvot vapautuvat, kun proseduuri palaa. Päätason
  ja nimiavaruuksien muuttujat elävät tulkin loppuun asti: vapauta
  ne `unset`-komennolla.
- EDA-työkalujen oliokahvat (solut, netit, pinnit) ovat merkkijonoja,
  jotka viittaavat työkalun sisäisiin olioihin. Työkalu vapauttaa
  ne omien sääntöjensä mukaan; suuret kokoelmat kannattaa käsitellä
  työkalun omilla iteraattoreilla eikä muuntaa Tcl-listoiksi.
- TclOO-oliot ja korutiinit ovat komentoja, jotka on tuhottava
  (`$olio destroy`, `rename korutiini {}`), jos ne eivät pääty itse.

## Käytännössä

- **Älä sekoita lista- ja merkkijono-operaatioita samaan arvoon**
  silmukassa. Lista käsitellään listakomennoilla (`llength`, `lindex`,
  `foreach`), merkkijono merkkijonokomennoilla.
- **Kasvata listaa `lappend`-komennolla** ja merkkijonoa
  `append`-komennolla. `set s "$s …"` kopioi koko merkkijonon joka
  kerta.
- **Muokkaa suuria listoja paikallaan:** `lset` tai K-yhdistelmä
  `[lreplace $l[set l {}] …]`.
- **`foreach` on nopein tapa käydä lista läpi.** Indeksisilmukka
  `lindex`-komennolla on hitaampi ja altis muunnoksille.
- **Mittaa ennen optimointia:** `time {…} n` kertoo keskimääräisen ajan
  mikrosekunteina (luku 12).

## Itsearviointi

- Osaat selittää, mitä *shimmering* tarkoittaa ja miksi se voi tehdä
  silmukasta neliöllisen.
- Osaat kertoa, milloin Tcl kopioi arvon ja milloin muokkaa sitä
  paikallaan, ja käyttää K-yhdistelmää.
- Osaat tarkistaa arvon esityksen `tcl::unsupported::representation`
  -komennolla.
- Osaat vapauttaa suuret globaalit arvot, oliot ja korutiinit.
