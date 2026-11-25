# C:stä C++:aan

Tämä luku on tarkoitettu lukijalle, joka osaa C:n mutta ei C++:aa.
Siinä esitellään ne C++:n peruspiirteet, joiden varaan kaikki myöhemmät
luvut rakentuvat: viittaukset, funktioiden kuormitus, nimiavaruudet sekä
standardikirjaston merkkijono, vektori ja iteraattorit. Luokat
käsitellään seuraavassa luvussa. Vanhempaa C++:aa osaava voi lukea
luvun lopun *Itsearviointi*-osion ja siirtyä eteenpäin.

Lähes kaikki C-koodi on myös kelvollista C++:aa, mutta idiomaattinen
C++ näyttää erilaiselta. Taulukoiden, `char*`-merkkijonojen ja
`malloc`-kutsujen tilalla käytetään tyyppejä, jotka hallitsevat
muistinsa itse, ja osoitinparametrien tilalla useimmiten viittauksia.

## Viittaukset

*Viittaus* (`T&`) on toinen nimi olemassa olevalle oliolle. Se
alustetaan aina luotaessa, eikä sitä voi myöhemmin siirtää osoittamaan
toiseen olioon: sijoitus viittaukseen sijoittaa viitattuun olioon.

```{.cpp tiedosto="esimerkit/03-viittaukset.cpp" osa="alias"}
```

Viittaus on toteutukseltaan osoitin, mutta sitä käytetään kuin
tavallista muuttujaa ilman `*`- ja `&`-operaattoreita, eikä se voi olla
tyhjä. Tärkein käyttö on parametrien välitys. C:ssä funktio, joka
muuttaa kutsujan muuttujaa tai välttää suuren rakenteen kopioinnin,
ottaa osoittimen. C++:ssa vaihtoehtoja on kolme:

```{.cpp tiedosto="esimerkit/03-viittaukset.cpp" osa="parametrit"}
```

```{.cpp tiedosto="esimerkit/03-viittaukset.cpp" osa="kutsut"}
```

```{.tuloste tiedosto="esimerkit/03-viittaukset.odotettu"}
```

Funktio `nollaa_kopio` muutti vain omaa kopiotaan. *Vakioviittaus*
`const T&` on yleisin tapa välittää olio, jota funktio vain lukee:
mitään ei kopioida, ja kääntäjä estää muuttamisen. Vakioviittaukseen
kelpaa myös väliaikainen arvo, kuten `tulosta(Mittaus{"T2", 3.0})`.

| Parametri | Kopioi | Voi muuttaa kutsujan oliota | Käyttö |
|-----------|--------|-----------------------------|--------|
| `T` | kyllä | ei | pienet tyypit, kuten `int` ja `double` |
| `const T&` | ei | ei | suuren olion lukeminen |
| `T&` | ei | kyllä | kutsujan olion muuttaminen |
| `T*` | ei | kyllä | kun arvo voi puuttua (`nullptr`) |

Viittaus ei pidennä olion elinaikaa. Funktio ei saa palauttaa
viittausta paikalliseen muuttujaansa, koska muuttuja tuhoutuu funktion
päättyessä (ks. roikkuva viittaus luvussa
[C++ kokeneelle](#c-kokeneelle)).

## Kuormitus ja oletusargumentit

C:ssä jokaisella funktiolla on oma nimensä (`abs`, `labs`, `fabs`).
C++:ssa samannimisiä funktioita voi olla useita, kunhan niiden
parametrit eroavat. Kääntäjä valitsee *kuormitetuista* (*overloaded*)
funktioista sen, jonka parametrit sopivat argumentteihin parhaiten.
Pelkkä paluutyyppi ei riitä erottamaan funktioita.

```{.cpp tiedosto="esimerkit/03-funktiot.cpp" osa="kuormitus"}
```

Parametrille voi antaa *oletusargumentin*, jolloin sen voi jättää
kutsusta pois. Oletusargumentit ovat parametriluettelon lopussa:

```{.cpp tiedosto="esimerkit/03-funktiot.cpp" osa="oletus"}
```

```{.cpp tiedosto="esimerkit/03-funktiot.cpp" osa="kutsut"}
```

## Nimiavaruudet

C:ssä kirjaston nimet erotetaan etuliitteellä (`sqlite3_open`).
C++:ssa nimet ryhmitellään *nimiavaruuksiin*. Standardikirjaston nimet
ovat nimiavaruudessa `std`, ja niihin viitataan operaattorilla `::`,
esimerkiksi `std::string`. Oman nimiavaruuden voi määritellä itse, ja
nimiavaruuksia voi olla sisäkkäin:

```{.cpp tiedosto="esimerkit/03-funktiot.cpp" osa="nimiavaruus"}
```

```{.cpp tiedosto="esimerkit/03-funktiot.cpp" osa="nimet"}
```

Esittely `using nimiavaruus::nimi;` tuo yhden nimen käyttöön ilman
etuliitettä. Direktiivi `using namespace std;` toisi kaikki
standardikirjaston nimet kerralla. Sitä ei käytetä otsikkotiedostoissa
eikä tämän tutoriaalin esimerkeissä, koska nimien yhteentörmäykset
ovat vaikeita huomata.

Edellisten ohjelmien tuloste:

```{.tuloste tiedosto="esimerkit/03-funktiot.odotettu"}
```

Vakio `tuuma` on määritelty avainsanalla `constexpr`, joka korvaa C:n
`#define`-vakiot tyypitetyllä, käännösaikana lasketulla arvolla (luku
[Käännösaikainen laskenta](#käännösaikainen-laskenta)).

## Merkkijonot: `std::string`

C:n merkkijono on nollaan päättyvä `char`-taulukko, jonka muistin
ohjelmoija varaa ja vapauttaa itse. `std::string` omistaa merkkinsä:
se varaa muistin, kasvaa tarvittaessa ja vapauttaa muistin, kun
muuttuja poistuu näkyvyysalueelta.

```{.cpp tiedosto="esimerkit/03-merkkijono.cpp" osa="perus"}
```

Merkkijono on *arvo* kuten `int`. Sijoitus kopioi sisällön, ja
vertailuoperaattorit vertaavat sisältöä eivätkä osoitteita, joten
`strcpy`- ja `strcmp`-kutsuja ei tarvita:

```{.cpp tiedosto="esimerkit/03-merkkijono.cpp" osa="arvo"}
```

Jäsenfunktiot kutsutaan pisteellä kuten rakenteen kentät. `find`
palauttaa löytökohdan indeksin tai arvon `std::string::npos`, ja
`substr` palauttaa osamerkkijonon uutena merkkijonona:

```{.cpp tiedosto="esimerkit/03-merkkijono.cpp" osa="haku"}
```

```{.cpp tiedosto="esimerkit/03-merkkijono.cpp" osa="muunnos"}
```

```{.tuloste tiedosto="esimerkit/03-merkkijono.odotettu"}
```

Kun merkkijono on annettava C-funktiolle, `c_str()` palauttaa
nollaan päättyvän `const char*`-osoittimen. Funktion parametrina
merkkijono otetaan vakioviittauksena `const std::string&` tai näkymänä
`std::string_view` (luku
[Standardikirjaston sanastotyypit](#standardikirjaston-sanastotyypit)).

## Dynaaminen taulukko: `std::vector`

`std::vector<T>` on kasvava taulukko, jonka alkiot ovat tyyppiä `T`.
Se korvaa C:n `malloc`–`realloc`–`free`-ketjun. Kulmasulkeissa oleva
tyyppi on *malliargumentti*: `std::vector` on *malli* (*template*),
josta kääntäjä tuottaa oman tyyppinsä jokaiselle alkiotyypille.

```{.cpp tiedosto="esimerkit/03-vektori.cpp" osa="perus"}
```

Vektori-olio itse on pieni: siinä on osoitin keosta varattuun
taulukkoon sekä tieto alkioiden määrästä (`size`) ja varatusta tilasta
(`capacity`). Alkiot ovat muistissa peräkkäin kuten C:n taulukossa.

```{.dot otsikko="Vektori omistaa keosta varatun taulukon. Kun tila loppuu, `push_back` varaa suuremman taulukon ja siirtää alkiot sinne."}
digraph {
  rankdir=LR; nodesep=0.3;
  node [shape=box, fontsize=11];
  subgraph cluster_pino {
    label="pino: std::vector<double> arvot"; fontsize=11; style=rounded;
    v [shape=plain, label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
      <tr><td port="p">osoitin</td></tr>
      <tr><td>koko = 4</td></tr>
      <tr><td>kapasiteetti = 4</td></tr></table>>];
  }
  subgraph cluster_keko {
    label="keko"; fontsize=11; style=rounded;
    t [shape=plain, label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
      <tr><td port="a">2.5</td><td>3.0</td><td>1.5</td><td>8.0</td></tr></table>>];
  }
  v:p -> t:a;
}
```

Vektorikin on arvo: sijoitus kopioi kaikki alkiot, ja muisti vapautuu
automaattisesti. Funktiolle vektori välitetään siksi yleensä
vakioviittauksena, kuten funktiossa `summa`.

```{.cpp tiedosto="esimerkit/03-vektori.cpp" osa="kopio"}
```

```{.cpp tiedosto="esimerkit/03-vektori.cpp" osa="summa"}
```

Silmukka `for (double x : arvot)` on *aluepohjainen `for`* (*range-based
for*, lyhyesti range-for), joka käy säiliön alkiot läpi alusta loppuun.
Operaattori `[]` ei tarkista indeksiä: virheellinen indeksi on
määrittelemätöntä käyttäytymistä kuten C:ssä. Jäsenfunktio `at`
tarkistaa indeksin.

## Iteraattorit ja range-for

*Iteraattori* on osoittimen yleistys: olio, joka osoittaa säiliön
alkioon. `*it` antaa alkion ja `++it` siirtyy seuraavaan. Jokaisella
säiliöllä on jäsenfunktiot `begin()` ja `end()`. Näistä `end()`
osoittaa viimeisen alkion *jälkeen*, joten väli on puoliavoin, kuten
C:n silmukassa `for (p = t; p != t + n; ++p)`.

```{.cpp tiedosto="esimerkit/03-vektori.cpp" osa="iteraattorit"}
```

Iteraattorin tyyppi on pitkä (`std::vector<double>::iterator`), joten
se jätetään kääntäjän pääteltäväksi avainsanalla `auto` (luku
[Kielen perusteet modernisti](#kielen-perusteet-modernisti)). Range-for
on lyhennysmerkintä samalle `begin`–`end`-silmukalle. Silmukkamuuttuja
on kopio alkiosta, ellei sitä esitellä viittauksena.

Iteraattorit yhdistävät säiliöt ja algoritmit. `std::sort` ja
`std::find` eivät tiedä, mitä säiliötä ne käsittelevät. Ne saavat
iteraattoriparin, joka rajaa käsiteltävän välin, ja `std::find`
palauttaa iteraattorin löytyneeseen alkioon tai välin loppuun. Samat
algoritmit toimivat siksi vektorille, merkkijonolle ja C-taulukolle.
Uudempi tapa kutsua algoritmeja suoraan säiliölle esitellään luvussa
[Algoritmit ja ranges](#algoritmit-ja-ranges).

Iteraattori on voimassa vain niin kauan kuin säiliön muisti pysyy
paikallaan. `push_back` voi siirtää alkiot uuteen taulukkoon, jolloin
vanhat iteraattorit, osoittimet ja viittaukset alkioihin *mitätöityvät*
(esimerkki luvussa [C++ kokeneelle](#c-kokeneelle)).

## Poikkeukset lyhyesti

C-funktio ilmoittaa virheestä paluuarvolla. C++:ssa funktio voi myös
*heittää poikkeuksen* lauseella `throw`. Suoritus siirtyy lähimpään
`try`-lohkoon, jonka `catch`-haara sopii poikkeuksen tyyppiin, ja matkan
varrella olevat paikalliset oliot tuhotaan. Standardikirjasto käyttää
poikkeuksia: `at` heittää poikkeuksen `std::out_of_range` ja
epäonnistunut `std::stoi` poikkeuksen `std::invalid_argument`.

```{.cpp tiedosto="esimerkit/03-vektori.cpp" osa="poikkeus"}
```

```{.tuloste tiedosto="esimerkit/03-vektori.odotettu"}
```

Poikkeus siepataan vakioviittauksena. Sieppaamaton poikkeus päättää
ohjelman. Poikkeusten oikea käyttö ja vaihtoehdot käsitellään luvussa
[Virheenkäsittely](#virheenkäsittely).

## Käytännössä

- **`std::string` ja `std::vector` oletuksena.** `char*`-puskureita,
  C-taulukoita ja `malloc`-kutsuja käytetään vain C-rajapintojen
  reunalla. Standardityypit vapauttavat muistinsa itse ja tietävät
  kokonsa.
- **Lukuparametri vakioviittauksena.** Merkkijonot, vektorit ja muut
  suuret oliot otetaan parametriksi `const T&`:nä. Arvona välitetään
  perustyypit ja muut muutaman tavun kokoiset tyypit.
- **Viittaus, kun arvo on aina olemassa; osoitin, kun se voi puuttua.**
  Viittausparametrille ei tarvita `NULL`-tarkistusta. Osoitin kertoo
  lukijalle, että `nullptr` on mahdollinen arvo.
- **Muuttava viittausparametri näkyy vain esittelyssä.** Kutsu
  `nollaa(m)` ei paljasta, että `m` muuttuu. Funktion nimi kertoo
  muutoksesta, ja tulos palautetaan mieluummin paluuarvona.
- **Range-for, kun indeksiä ei tarvita.** Silmukka ei voi ylittää
  säiliön rajoja. Alkiot otetaan `const auto&`:na, jos ne ovat
  kopioitavaksi suuria.
- **Kuormitetut funktiot tekevät saman asian.** Kuormitus on tarkoitettu
  saman operaation versioille eri tyypeillä. Jos toiminta eroaa,
  funktioille annetaan eri nimet.
- **Nimiavaruus jokaiselle kirjastolle.** Oma koodi sijoitetaan
  projektin nimiavaruuteen, ja `std::`-etuliite kirjoitetaan näkyviin.

## Itsearviointi

- Osaat selittää viittauksen ja osoittimen erot ja valita parametrille
  tyypin `T`, `const T&`, `T&` tai `T*`.
- Osaat kirjoittaa kuormitetun funktion ja funktion, jolla on
  oletusargumentteja.
- Osaat käyttää `std::string`iä ja `std::vector`ia: lisätä, hakea,
  kopioida ja välittää ne funktiolle ilman kopiointia.
- Osaat käydä säiliön läpi iteraattoreilla ja range-for-silmukalla ja
  kertoa, milloin iteraattori mitätöityy.
- Osaat siepata standardikirjaston heittämän poikkeuksen.
