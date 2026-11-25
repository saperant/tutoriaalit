# Joukot ja funktiot

Joukko on matematiikan perusrakenne: kokoelma erillisiä alkioita
ilman järjestystä ja toistoja. Funktio liittää jokaiseen alkioon
täsmälleen yhden kuvan. Ohjelmoijalle molemmat ovat tuttuja
tietotyyppeinä (`set`, `dict`), mutta matemaattiset käsitteet,
kuten injektio, potenssijoukko ja kardinaliteetti, kertovat, mitä
rakenteella voi tehdä ja mitä ei: miksi hajautustaulussa on aina
törmäyksiä ja miksi salaus on purettavissa. Luvun lopussa funktioita
verrataan niiden kasvunopeuden mukaan: O-merkintä on kieli, jolla
loppuosa tutoriaalista puhuu algoritmien työmäärästä.

## Joukko-operaatiot

Joukko määritellään luettelemalla, $A = \{1, 2, 3\}$, tai ehdolla,
$B = \{x \in \mathbb{Z} \mid x^2 < 10\}$. Jälkimmäinen merkintä on
Pythonin joukkokoosteen esikuva: `{x for x in range(-3, 4) if x*x < 10}`.
Perusoperaatiot ovat **yhdiste** $A \cup B$, **leikkaus** $A \cap B$,
**erotus** $A \setminus B$, **symmetrinen erotus** $A \triangle B$ ja
**komplementti** $A'$ suhteessa perusjoukkoon $U$.

```{.python tiedosto="esimerkit/04-joukot.py" osa="operaatiot"}
```

```{.tuloste tiedosto="esimerkit/04-joukot.odotettu" rivit="1-7"}
```

![Esimerkin joukot Vennin kaaviona. Leikkaus on ympyröiden yhteinen
alue, yhdiste molempien peittämä alue ja komplementti kaikki sen
ulkopuolella perusjoukossa $U$.](kuvat/venn-joukot.png){width=55%}

Joukko-opin lait ovat propositiologiikan lakeja: $x \in A \cup B$
tarkoittaa $x \in A \lor x \in B$, joten esimerkiksi De Morganin laki
$(A \cup B)' = A' \cap B'$ seuraa suoraan logiikan vastaavasta.
Pythonin `set` toteuttaa operaatiot hajautuksella: jäsenyystesti ja
lisäys vievät keskimäärin saman ajan joukon koosta riippumatta, toisin
kuin listassa, jossa `in` käy läpi kaikki alkiot.

## Potenssijoukko ja karteesinen tulo

Joukon $A$ **potenssijoukko** $\mathcal{P}(A)$ on sen kaikkien
osajoukkojen joukko. Jokaisesta alkiosta päätetään erikseen, kuuluuko
se osajoukkoon, joten $\lvert \mathcal{P}(A) \rvert = 2^{\lvert A
\rvert}$. Tiedoston oikeuksien yhdistelmät ovat potenssijoukko:

```{.python tiedosto="esimerkit/04-joukot.py" osa="potenssijoukko"}
```

```{.tuloste tiedosto="esimerkit/04-joukot.odotettu" rivit="8-16"}
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

```{.tuloste tiedosto="esimerkit/04-joukot.odotettu" rivit="17-"}
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

```{.tuloste tiedosto="esimerkit/04-funktiot.odotettu" rivit="1-4"}
```

![Esimerkin neljä funktiota nuolikaavioina. Injektiossa jokaiseen
maalijoukon alkioon tulee enintään yksi nuoli, surjektiossa vähintään
yksi ja bijektiossa täsmälleen yksi. Korostetut maalijoukon alkiot
rikkovat ehdon: niihin tulee kaksi nuolta tai ei
yhtään.](kuvat/funktiot.png){width=92%}

Funktio $x \mapsto 3x \bmod 8$ sekoittaa luvut 0–7 mutta säilyttää
ne kaikki, kun taas $x \mapsto 2x \bmod 8$ menettää tietoa: parittomat
luvut eivät ole saavutettavissa, ja kaksi syötettä kuvautuu aina
samaan. Ero johtuu siitä, onko kertoimella yhteisiä tekijöitä
modulin kanssa (luku *Modulaariaritmetiikka*).

Funktiot $f: A \to B$ ja $g: B \to C$ voidaan **yhdistää**:
$(g \circ f)(x) = g(f(x))$, eli ensin sovelletaan $f$ ja tulokseen $g$.
Ohjelmassa yhdistäminen on sisäkkäinen kutsu `g(f(x))` tai käsittelyketju,
jossa jokainen vaihe saa edellisen tuloksen. Kahden injektion yhdiste
on injektio ja kahden bijektion bijektio, joten purettavista vaiheista
koottu ketju on purettavissa. Käänteisfunktio määritellään yhdistämisen
avulla: $f^{-1} \circ f$ on **identiteettifunktio**, joka palauttaa
syötteensä sellaisenaan.

## Kardinaliteetti ja hajautus

Äärellisille joukoille pätee: jos on olemassa injektio $A \to B$,
niin $\lvert A \rvert \le \lvert B \rvert$. Kääntäen: jos
$\lvert A \rvert > \lvert B \rvert$, mikään funktio $A \to B$ ei ole
injektio. Hajautusfunktio kuvaa valtavan avainjoukon pieneen
lokerojoukkoon, joten **törmäykset ovat väistämättömiä**, ja
hajautustaulun on varauduttava niihin:

```{.python tiedosto="esimerkit/04-funktiot.py" osa="hajautus"}
```

```{.tuloste tiedosto="esimerkit/04-funktiot.odotettu" rivit="5-5"}
```

Sama periaate pätee kryptografisiin tiivisteisiin: SHA-256 kuvaa
mielivaltaisen pitkät syötteet 256 bittiin, joten törmäyksiä on
olemassa äärettömästi. Tiivisteen turvallisuus perustuu siihen, ettei
niitä osata löytää (taito *Kryptografia*).

Bijektion käänteisfunktio on purku. Funktio $x \mapsto 3x \bmod 8$
kumoutuu kertomalla kolmella, koska $3 \cdot 3 = 9 \equiv 1$:

```{.python tiedosto="esimerkit/04-funktiot.py" osa="kaanteis"}
```

```{.tuloste tiedosto="esimerkit/04-funktiot.odotettu" rivit="6-"}
```

Äärettömillä joukoilla kardinaliteetti mitataan bijektioilla:
luonnolliset luvut ja kokonaisluvut ovat ”yhtä suuria”, koska niiden
välillä on bijektio ($0, -1, 1, -2, 2, \ldots$). Reaalilukuja on
Cantorin diagonaaliargumentin mukaan aidosti enemmän. Tietojenkäsittelyn
kannalta tärkeä seuraus: ohjelmia on numeroituvasti ääretön määrä
(ne ovat äärellisiä merkkijonoja), mutta funktioita
$\mathbb{N} \to \{0, 1\}$ ylinumeroituvasti, joten useimpia
funktioita ei voi laskea millään ohjelmalla.

## Kasvunopeus ja O-merkintä

Algoritmin työmäärä on funktio syötteen koosta: $n$ alkion listan
läpikäynti vie $n$ askelta, kaikkien parien vertailu $n(n-1)/2$.
Tarkka askelmäärä riippuu koneesta ja toteutuksesta, joten funktioita
verrataan sen mukaan, kuinka nopeasti ne kasvavat, kun $n$ kasvaa.
Vakiokertoimet ja hitaammin kasvavat termit jätetään pois.

Funktio $f$ on **enintään kertaluokkaa** $g$, merkitään
$f(n) = O(g(n))$ (”iso O”), jos on vakiot $c > 0$ ja $n_0$, joilla

$$f(n) \le c \cdot g(n) \quad \text{kaikilla } n \ge n_0.$$

Määritelmä on kvanttorilauseke: *on olemassa* $c$ ja $n_0$ niin, että
epäyhtälö pätee *kaikilla* suurilla $n$. Väite todistetaan antamalla
vakiot. Esimerkiksi $3n^2 + 10n + 5 = O(n^2)$, koska $10n + 5 \le n^2$,
kun $n \ge 11$, joten vakiot $c = 4$ ja $n_0 = 11$ kelpaavat:

```{.python tiedosto="esimerkit/04-kasvu.py" osa="raja"}
```

```{.tuloste tiedosto="esimerkit/04-kasvu.odotettu" rivit="6-7"}
```

Iso O on yläraja. Alarajalle ja tarkalle kertaluokalle on omat
merkintänsä:

| Merkintä | Lue | Merkitys |
|----------|-----|----------|
| $f = O(g)$ | enintään kertaluokkaa $g$ | $f(n) \le c\,g(n)$ suurilla $n$ |
| $f = \Omega(g)$ | vähintään kertaluokkaa $g$ | $f(n) \ge c\,g(n)$ suurilla $n$ |
| $f = \Theta(g)$ | täsmälleen kertaluokkaa $g$ | sekä $O(g)$ että $\Omega(g)$ |

Arkipuheessa sanotaan usein ”algoritmi on $O(n^2)$”, vaikka
tarkoitetaan $\Theta(n^2)$. Tavallisimmat kertaluokat ovat vakio
$O(1)$, logaritminen $O(\log n)$, lineaarinen $O(n)$, $O(n \log n)$,
neliöllinen $O(n^2)$, kuutiollinen $O(n^3)$ ja eksponentiaalinen
$O(2^n)$. Logaritmin kantaluku ei vaikuta kertaluokkaan, koska
kantaluvun vaihto on vakiolla kertomista. Taulukko näyttää, miksi
kertaluokka ratkaisee enemmän kuin vakiokerroin:

```{.python tiedosto="esimerkit/04-kasvu.py" osa="taulukko"}
```

```{.tuloste tiedosto="esimerkit/04-kasvu.odotettu" rivit="1-5"}
```

![Kasvunopeudet logaritmisilla akseleilla. Potenssifunktiot ovat
suoria, joiden kulmakerroin on eksponentti; eksponenttifunktio $2^n$
nousee niistä jokaisen yli.](kuvat/kasvu.png){width=62%}

Kun $n$ kymmenkertaistuu, lineaarinen työ kymmenkertaistuu,
neliöllinen satakertaistuu ja eksponentiaalinen karkaa käsistä.
Kertaluokan näkee myös mittaamalla. Tehtävä ”onko listassa kaksi samaa
alkiota” ratkeaa vertaamalla kaikki parit tai muistamalla nähdyt
alkiot joukossa:

```{.python tiedosto="esimerkit/04-kasvu.py" osa="mittaus"}
```

```{.tuloste tiedosto="esimerkit/04-kasvu.odotettu" rivit="8-"}
```

Parivertailun askelmäärä satakertaistuu, kun $n$ kymmenkertaistuu
($\Theta(n^2)$), ja joukkoa käyttävän kymmenkertaistuu ($\Theta(n)$,
kun joukon jäsenyystesti on keskimäärin vakioaikainen). Kymmenellä
tuhannella alkiolla ero on viisituhatkertainen. Algoritmien
analyysi jatkuu luvussa *Rekursio ja rekursioyhtälöt* ja taidoissa
*Tietorakenteet* ja *Algoritmit*.

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
- **Arvioi kertaluokka ennen optimointia.** Sisäkkäinen silmukka koko
  aineiston yli on neliöllinen. Tuhannella alkiolla se ei haittaa,
  miljoonalla se ei valmistu. Kertaluokan vaihto (lista → joukko,
  parivertailu → avain) voittaa vakiokertoimen viilauksen.

## Itsearviointi

- Osaat käyttää joukko-operaatioita ja selittää niiden yhteyden
  propositiologiikkaan.
- Osaat laskea potenssijoukon ja karteesisen tulon koon ja tunnistaa
  ne ohjelmointitehtävissä.
- Osaat tunnistaa, onko äärellinen funktio injektio, surjektio vai
  bijektio, ja muodostaa bijektion käänteisfunktion.
- Osaat perustella kardinaliteetilla, miksi hajautusfunktiolla on
  väistämättä törmäyksiä.
- Osaat määritellä merkinnät $O$, $\Omega$ ja $\Theta$, osoittaa
  yksinkertaisen funktion kertaluokan vakioilla $c$ ja $n_0$ ja
  päätellä kertaluokan askelmäärien kasvusta.
