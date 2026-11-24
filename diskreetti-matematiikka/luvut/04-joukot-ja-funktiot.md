# Joukot ja funktiot

Joukko on matematiikan perusrakenne: kokoelma erillisiä alkioita
ilman järjestystä ja toistoja. Funktio liittää jokaiseen alkioon
täsmälleen yhden kuvan. Ohjelmoijalle molemmat ovat tuttuja
tietotyyppeinä (`set`, `dict`), mutta matemaattiset käsitteet,
kuten injektio, potenssijoukko ja kardinaliteetti, kertovat, mitä
rakenteella voi tehdä ja mitä ei: miksi hajautustaulussa on aina
törmäyksiä ja miksi salaus on purettavissa.

## Joukko-operaatiot

Joukko määritellään luettelemalla, $A = \{1, 2, 3\}$, tai ehdolla,
$B = \{x \in \mathbb{Z} \mid x^2 < 10\}$. Jälkimmäinen merkintä on
Pythonin joukkokoosteen esikuva: `{x for x in range(-3, 4) if x*x < 10}`.
Perusoperaatiot ovat **yhdiste** $A \cup B$, **leikkaus** $A \cap B$,
**erotus** $A \setminus B$, **symmetrinen erotus** $A \triangle B$ ja
**komplementti** $A'$ suhteessa perusjoukkoon $U$.

```{.python tiedosto="esimerkit/04-joukot.py" osa="operaatiot"}
```

Joukko-opin lait ovat propositiologiikan lakeja: $x \in A \cup B$
tarkoittaa $x \in A \lor x \in B$, joten esimerkiksi De Morganin laki
$(A \cup B)' = A' \cap B'$ seuraa suoraan logiikan vastaavasta.
Pythonin `set` toteuttaa operaatiot hajautuksella: jäsenyystesti ja
lisäys ovat keskimäärin vakioaikaisia, toisin kuin listassa, jossa
`in` käy läpi kaikki alkiot.

## Potenssijoukko ja karteesinen tulo

Joukon $A$ **potenssijoukko** $\mathcal{P}(A)$ on sen kaikkien
osajoukkojen joukko. Jokaisesta alkiosta päätetään erikseen, kuuluuko
se osajoukkoon, joten $\lvert \mathcal{P}(A) \rvert = 2^{\lvert A
\rvert}$. Tiedoston oikeuksien yhdistelmät ovat potenssijoukko:

```{.python tiedosto="esimerkit/04-joukot.py" osa="potenssijoukko"}
```

Tämä on myös bittivektorin idea: $n$-bittinen luku valitsee
osajoukon $n$ alkion joukosta, ja Unixin oikeusbitit `rwx` koodaavat
juuri yllä olevat kahdeksan yhdistelmää luvuiksi 0–7.

**Karteesinen tulo** $A \times B = \{(a, b) \mid a \in A, b \in B\}$
on kaikkien järjestettyjen parien joukko, ja
$\lvert A \times B \rvert = \lvert A \rvert \cdot \lvert B \rvert$.
Tuotevariantit, testimatriisit ja tietokannan liitos ilman ehtoa
(`CROSS JOIN`) ovat karteesisia tuloja.

```{.python tiedosto="esimerkit/04-joukot.py" osa="tulo"}
```

```{.tuloste tiedosto="esimerkit/04-joukot.odotettu"}
```

## Funktiot

**Funktio** $f: A \to B$ liittää jokaiseen **määrittelyjoukon** $A$
alkioon täsmälleen yhden **maalijoukon** $B$ alkion. Ohjelmointikielen
funktio on matemaattinen funktio vain, jos sillä ei ole
sivuvaikutuksia ja sama syöte antaa aina saman tuloksen (*puhdas
funktio*). Äärellisen funktion voi esittää sanakirjana.

Funktion keskeiset ominaisuudet:

- **Injektio** (yksi yhteen): eri alkiot kuvautuvat eri alkioiksi,
  $f(x) = f(y) \Rightarrow x = y$. Tieto ei häviä.
- **Surjektio** (päälle): jokaiseen maalijoukon alkioon kuvautuu
  jokin alkio. Kaikki arvot ovat saavutettavissa.
- **Bijektio**: sekä injektio että surjektio. Vain bijektiolla on
  **käänteisfunktio** $f^{-1}$, jolle $f^{-1}(f(x)) = x$.

```{.python tiedosto="esimerkit/04-funktiot.py" osa="ominaisuudet"}
```

Funktio $x \mapsto 3x \bmod 8$ sekoittaa luvut 0–7 mutta säilyttää
ne kaikki, kun taas $x \mapsto 2x \bmod 8$ menettää tietoa: parittomat
luvut eivät ole saavutettavissa, ja kaksi syötettä kuvautuu aina
samaan. Ero johtuu siitä, onko kertoimella yhteisiä tekijöitä
modulin kanssa (luku *Modulaariaritmetiikka*).

## Kardinaliteetti ja hajautus

Äärellisille joukoille pätee: jos on olemassa injektio $A \to B$,
niin $\lvert A \rvert \le \lvert B \rvert$. Kääntäen: jos
$\lvert A \rvert > \lvert B \rvert$, mikään funktio $A \to B$ ei ole
injektio. Hajautusfunktio kuvaa valtavan avainjoukon pieneen
lokerojoukkoon, joten **törmäykset ovat väistämättömiä**, ja
hajautustaulun on varauduttava niihin:

```{.python tiedosto="esimerkit/04-funktiot.py" osa="hajautus"}
```

Sama periaate pätee kryptografisiin tiivisteisiin: SHA-256 kuvaa
mielivaltaisen pitkät syötteet 256 bittiin, joten törmäyksiä on
olemassa äärettömästi. Tiivisteen turvallisuus perustuu siihen, ettei
niitä osata löytää (taito *Kryptografia*).

Bijektion käänteisfunktio on purku. Funktio $x \mapsto 3x \bmod 8$
kumoutuu kertomalla kolmella, koska $3 \cdot 3 = 9 \equiv 1$:

```{.python tiedosto="esimerkit/04-funktiot.py" osa="kaanteis"}
```

```{.tuloste tiedosto="esimerkit/04-funktiot.odotettu"}
```

Äärettömillä joukoilla kardinaliteetti mitataan bijektioilla:
luonnolliset luvut ja kokonaisluvut ovat ”yhtä suuria”, koska niiden
välillä on bijektio ($0, -1, 1, -2, 2, \ldots$). Reaalilukuja on
Cantorin diagonaaliargumentin mukaan aidosti enemmän. Tietojenkäsittelyn
kannalta tärkeä seuraus: ohjelmia on numeroituvasti ääretön määrä
(ne ovat äärellisiä merkkijonoja), mutta funktioita
$\mathbb{N} \to \{0, 1\}$ ylinumeroituvasti, joten useimpia
funktioita ei voi laskea millään ohjelmalla.

## Käytännössä

- **Valitse `set`, kun järjestys ja toistot ovat merkityksettömiä.**
  Jäsenyystesti on keskimäärin vakioaikainen ja joukko-operaatiot
  ilmaisevat tarkoituksen suoraan (`vanhat - uudet` = poistetut).
- **Muista, että `set` ja `dict` vaativat hajautettavat alkiot.**
  Muuttumaton `frozenset` kelpaa joukon alkioksi ja sanakirjan
  avaimeksi, `set` ei.
- **Tarkista, tarvitsetko bijektion.** Koodaus, joka pitää purkaa
  (sarjallistus, salaus, tunnisteiden muunnos), on oltava injektio.
  Pelkkä surjektio tai tiiviste hukkaa tietoa.
- **Varaudu törmäyksiin.** Kun kuvaat suuren joukon pieneen
  (hajautus, lyhyet tunnisteet, tarkistussummat), törmäykset ovat
  varmoja; kysymys on vain niiden todennäköisyydestä.
- **Pidä funktiot puhtaina.** Puhdas funktio on matemaattinen funktio:
  sen voi testata, välimuistittaa ja ajaa rinnakkain ilman yllätyksiä.

## Itsearviointi

- Osaat käyttää joukko-operaatioita ja selittää niiden yhteyden
  propositiologiikkaan.
- Osaat laskea potenssijoukon ja karteesisen tulon koon ja tunnistaa
  ne ohjelmointitehtävissä.
- Osaat tunnistaa, onko äärellinen funktio injektio, surjektio vai
  bijektio, ja muodostaa bijektion käänteisfunktion.
- Osaat perustella kardinaliteetilla, miksi hajautusfunktiolla on
  väistämättä törmäyksiä.
