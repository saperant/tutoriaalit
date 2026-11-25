# Yksikkötestaus C:lle

Yksikkötesti kutsuu yhtä funktiota tai pientä funktiojoukkoa tunnetulla
syötteellä ja tarkistaa tuloksen. Hyvä yksikkötesti on nopea (koko
joukko ajetaan sekunneissa), eristetty (ei verkkoa, levyä, kelloa eikä
satunnaisuutta) ja yksiselitteinen (epäonnistuessaan se kertoo, mikä
meni pieleen). C:ssä ei ole sisäänrakennettua testikehystä, joten
valinta on tehtävä itse: pieni oma kehys, valmis kehys (Unity, cmocka,
Check, CTestin pelkät testiohjelmat) tai C++-kehys (GoogleTest,
Catch2) C-koodin testaamiseen.

Kaikki kehykset tekevät samat kolme asiaa: ne tarjoavat
tarkistusmakrot, ajavat testit ja raportoivat tuloksen. Kun ymmärtää,
miten tämä toteutetaan muutamalla kymmenellä rivillä, ymmärtää myös
valmiit kehykset.

## Pieni testikehys

Edellisen luvun testi käytti `assert`-makroa. Se pysähtyy ensimmäiseen
virheeseen eikä kerro, mitä arvoja verrattiin. Oma kehys korjaa
molemmat: tarkistus kirjaa virheen ja jatkaa, ja liukulukuvertailu
tulostaa saadun ja odotetun arvon.

```{.c tiedosto="esimerkit/08-testit/testi.h"}
```

Tarkistukset ovat makroja eivätkä funktioita, koska `__FILE__`,
`__LINE__` ja lausekkeen merkkijonoksi muuttava `#ehto` toimivat vain
tarkistuksen kohdalla laajenevassa makrossa: näin virheilmoitus kertoo
testin rivin ja tarkistetun lausekkeen. `TARKISTA_LAHELLA` laskee
argumenttinsa kerran väliaikaisiin muuttujiin, jotta sivuvaikutteinen
lauseke ei suoritu kahdesti. Makrojen tekniikat, kuten
`do { ... } while (0)`, selittää taito *C-kieli* (esikääntäjä).
Ajaja on lyhyt:

```{.c tiedosto="esimerkit/08-testit/testi.c"}
```

Testit ovat tavallisia funktioita, ja ne rekisteröidään taulukkoon
`main`-funktiossa. Testin nimi kertoo, mitä se varmistaa, joten
epäonnistunut testi on ymmärrettävä pelkästä nimestä:

```{.c tiedosto="esimerkit/08-testit/testit.c" osa="tilasto"}
```

Odotetut arvot on laskettu käsin, ei testattavalla koodilla. Sarjan
`2, 4, 4, 4, 5, 5, 7, 9` keskiarvo on 5 ja otoskeskihajonta
$\sqrt{32/7}$. Jos odotettu arvo laskettaisiin samalla kaavalla kuin
toteutus, testi toistaisi toteutuksen virheet. Mediaanin testit
kattavat parittoman ja parillisen pituuden, koska ne ovat eri
koodipolkuja.

## Testikaksoset linkkerillä

Raportti sisältää kellonajan:

```{.c tiedosto="esimerkit/08-testit/raportti.c"}
```

Kelloa ei voi testata: tulos muuttuu joka sekunti. Ratkaisu on
*testikaksonen* (*test double*): testissä oikea riippuvuus korvataan
versiolla, jonka käytös on ennalta tiedossa. Oliokielissä korvaaminen
tehdään rajapinnalla ja riippuvuuden injektoinnilla. C:ssä on
yksinkertaisempi keino: linkkeri. Kellonaika on eristetty omaan
rajapintaansa ja tiedostoonsa:

```{.c tiedosto="esimerkit/08-testit/kello.h"}
```

Tuotanto-ohjelma linkitetään tiedoston `kello.c` kanssa, joka kutsuu
`time`-funktiota. Testit linkitetään valekellon kanssa, joka palauttaa
aina saman hetken:

```{.c tiedosto="esimerkit/08-testit/kello_vale.c"}
```

```{.dot otsikko="Linkityssauma. Molemmat ohjelmat sisältävät saman `raportti.c`:n; vain se, mikä tiedosto toteuttaa `kello.h`:n rajapinnan, vaihtuu."}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.7;
  subgraph cluster_t {
    label="tuotanto: raportti"; style="rounded,dashed";
    tm [label="raportti_main.c"]; tr [label="raportti.c\ntilasto.c"];
    tk [label="kello.c\n(kutsuu time())", penwidth=1.6];
    tm -> tr; tr -> tk [label="kello.h"];
  }
  subgraph cluster_e {
    label="testi: testit"; style="rounded,dashed";
    em [label="testit.c\ntesti.c"]; er [label="raportti.c\ntilasto.c"];
    ek [label="kello_vale.c\n(kiinteä hetki)", penwidth=1.6];
    em -> er; er -> ek [label="kello.h"];
  }
}
```

Koodia ei muuteta testejä varten, eikä siinä ole ehtolauseita tai
funktio-osoittimia. Ero on vain siinä, mitkä tiedostot linkitetään.
Makefile kuvaa molemmat:

```{.makefile tiedosto="esimerkit/08-testit/Makefile" osa="testit"}
```

Testi kirjoittaa raportin muistipuskuriin `fmemopen`-funktiolla ja
vertaa sitä tarkkaan odotettuun merkkijonoon. Samalla se varmistaa,
ettei raportti muuttanut syötettä, vaikka mediaani lajittelee:

```{.c tiedosto="esimerkit/08-testit/testit.c" osa="valekello"}
```

## Kääreet: --wrap

Linkkerin valitsin `--wrap=malloc` ohjaa jokaisen `malloc`-kutsun
funktioon `__wrap_malloc` ja antaa alkuperäisen funktion nimellä
`__real_malloc`. Näin testi voi tehdä muistinvarauksesta epäonnistuvan
ja tarkistaa, että virhepolku toimii:

```{.c tiedosto="esimerkit/08-testit/testit.c" osa="wrap"}
```

Virhepolut ovat koodin vähiten testattu osa, koska niitä on vaikea
saada aikaan. Kääreellä niistä tulee tavallisia testitapauksia.
Valitsin koskee vain symboleita, jotka viittaavat toisiin
objektitiedostoihin: saman tiedoston sisäiset kutsut eivät ohjaudu
kääreeseen. Mekanismi on GNU ld:n ja LLD:n ominaisuus. Muilla alustoilla
sama tehdään esimerkiksi linkittämällä testiin oma `malloc`-toteutus
tai, viimeisenä keinona, esikäsittelijällä.

## Ajo ja virheiden lukeminen

Esimerkki ajaa testit, rakentaa tuotanto-ohjelman ja lopuksi rikkoo
keskiarvon tarkoituksella:

```{.bash tiedosto="esimerkit/08-testit/aja.sh"}
```

```{.tuloste tiedosto="esimerkit/08-testit.odotettu"}
```

Epäonnistunut ajo näyttää, miltä hyvän testin pitää epäonnistua. Rivit
kertovat tiedoston ja rivin, lausekkeen sekä saadun ja odotetun arvon.
Yksi virhe toteutuksessa rikkoi kaksi testiä, koska hajonta ja
raportti käyttävät keskiarvoa. Mediaanin testit menivät läpi, mikä
rajaa vian keskiarvoon. Ohjelman paluuarvo on 1, joten rakennusjärjestelmä
ja CI tunnistavat epäonnistumisen.

## CTest

CTest ei ole testikehys vaan testien ajaja: se ajaa rekisteröidyt
ohjelmat ja tulkitsee niiden paluuarvon. Siksi sen kanssa voi käyttää
mitä tahansa kehystä. Muutama sen ominaisuus on CI:ssä tärkeä:

```text
ctest --preset kehitys -j 8               rinnakkain
ctest -R mediaani                         vain nimeen osuvat
ctest --output-on-failure                 epäonnistuneiden tuloste
ctest --repeat until-fail:50 -R raportti  epävakaan testin metsästys
ctest --output-junit tulokset.xml         CI:n raportointiin
```

Testeille voi asettaa ominaisuuksia: `TIMEOUT` pysäyttää jumiutuneen
testin, `LABELS` ryhmittelee testit (esimerkiksi `nopea` ja `hidas`),
ja `ENVIRONMENT` asettaa ympäristömuuttujat. Kun testikehys osaa ajaa
yksittäisen testin nimellä, kukin testi kannattaa rekisteröidä
erikseen (`add_test(NAME mediaani COMMAND testit mediaani)`), jolloin
CTest rinnakkaistaa ja raportoi ne yksitellen.

## Käytännössä

- **Testaa rajapintaa, ei toteutusta.** Testi, joka kutsuu
  julkista funktiota ja tarkistaa tuloksen, kestää toteutuksen
  muutokset. Sisäisten funktioiden testit on kirjoitettava uudelleen
  jokaisessa refaktoroinnissa.
- **Eristä ulkoiset riippuvuudet saumoiksi.** Kello, satunnaisuus,
  tiedostot ja verkko omiin rajapintoihinsa, jotka testi korvaa
  linkittämällä. Näin testit ovat deterministisiä, eikä tuotantokoodissa
  ole testiä varten lisättyjä ehtoja.
- **Testaa virhepolut.** `--wrap` ja testikaksoset tekevät muistin
  loppumisesta, levyvirheistä ja aikakatkaisuista tavallisia
  testitapauksia.
- **Hyvä epäonnistuminen kertoo kaiken.** Tiedosto, rivi, lauseke,
  saatu ja odotettu arvo. Jos testin epäonnistuminen vaatii
  debuggeria, tarkistusmakroissa on parannettavaa.
- **Odotetut arvot käsin.** Testi, joka laskee odotetun arvon samalla
  kaavalla kuin toteutus, ei löydä kaavan virhettä.

## Itsearviointi

- Osaat kirjoittaa tarkistusmakron, joka raportoi tiedoston, rivin ja
  lausekkeen ja jatkaa seuraavaan tarkistukseen.
- Osaat korvata riippuvuuden testikaksosella linkitysvaiheessa ja
  kertoa, miksi se ei vaadi muutoksia testattavaan koodiin.
- Osaat käyttää linkkerin `--wrap`-valitsinta virhepolun testaamiseen.
- Osaat ajaa testit CTestillä rinnakkain, suodattaen ja toistaen.
