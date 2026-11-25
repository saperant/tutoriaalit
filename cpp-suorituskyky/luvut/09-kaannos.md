# Käännös: sisällyttäminen, LTO, PGO ja käännösaika

C++:n abstraktiot ovat halpoja vain, jos kääntäjä näkee niiden läpi.
Malli tai `inline`-funktio otsakkeessa on näkyvissä jokaisessa
käännösyksikössä, mutta toisessa `.cpp`-tiedostossa määritelty funktio
ei ole. Tämä luku käsittelee sisällyttämisen edellytykset C++:n
kannalta, linkitysaikaisen ja profiiliohjatun optimoinnin,
käännösaikaisen laskennan sekä hinnan, jonka sama näkyvyys perii
käännösajassa. Optimointitasot ja `-march` ovat taidossa
*Suorituskyvyn analyysi ja optimointi*.

## `inline` ja ODR

Avainsana `inline` ei nykyään tarkoita "sisällytä tämä kutsukohtaan".
Se tarkoittaa, että funktion määritelmä saa esiintyä useassa
käännösyksikössä, kunhan kaikki määritelmät ovat samat (*yhden
määritelmän sääntö*, engl. one definition rule, ODR). Linkkeri valitsee
niistä yhden. Luokan sisällä määritellyt jäsenfunktiot, mallit,
`constexpr`-funktiot ja C++17:n `inline`-muuttujat ovat
automaattisesti `inline`.

Sisällyttämisestä päättää kääntäjä, ja sen edellytys on, että rungon
näkee:

```{.cpp tiedosto="esimerkit/09-lto/tuote.hpp" osa="vertailut"}
```

```{.cpp tiedosto="esimerkit/09-lto/tuote.cpp" osa="erillinen"}
```

```{.cpp tiedosto="esimerkit/09-lto/main.cpp" osa="lajittelu"}
```

```{.tuloste tiedosto="esimerkit/09-lto.odotettu"}
```

Kaksi lajittelua ovat lähdekoodissa samat. Ensimmäisessä jokainen
vertailu on funktiokutsu toiseen käännösyksikköön; toisessa vertailu on
yksi käsky sisällytettynä lajittelun silmukkaan.

ODR-rikkomus, eli eri sisältöiset määritelmät samalla nimellä eri
käännösyksiköissä, on määrittelemätöntä käyttäytymistä, jota kääntäjän
ei tarvitse havaita. Tyypillinen syy on otsake, jonka sisältö riippuu
makrosta, joka on eri käännösyksiköissä eri. GCC:n LTO-käännös
varoittaa monista tällaisista (`-Wodr`), samoin AddressSanitizerin
`detect_odr_violation`.

## Linkitysaikainen optimointi

*LTO* (engl. link-time optimization) tallentaa objektitiedostoihin
kääntäjän välikielen ja optimoi linkityksessä koko ohjelman kerralla.
Toisen käännösyksikön funktio voidaan silloin sisällyttää:

```{.dot otsikko="Mitä optimoija näkee. Ilman LTO:ta jokainen käännösyksikkö optimoidaan erikseen, ja toisen yksikön funktio on pelkkä kutsu. LTO:ssa optimointi tehdään linkityksessä, jolloin koko ohjelma on näkyvissä."}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.45;
  subgraph cluster_ei {
    label="ilman LTO:ta"; color="#C9CED6"; style=rounded;
    a1 [label="a.cpp", fillcolor="#FFFFFF"]; b1 [label="b.cpp", fillcolor="#FFFFFF"];
    oa1 [label="optimointi\n→ a.o"]; ob1 [label="optimointi\n→ b.o"];
    l1 [label="linkitys:\nkutsut jäävät"];
    a1 -> oa1 -> l1; b1 -> ob1 -> l1;
  }
  subgraph cluster_lto {
    label="-flto"; color="#C9CED6"; style=rounded;
    a2 [label="a.cpp", fillcolor="#FFFFFF"]; b2 [label="b.cpp", fillcolor="#FFFFFF"];
    oa2 [label="välikieli\n→ a.o"]; ob2 [label="välikieli\n→ b.o"];
    l2 [label="linkitys:\nkoko ohjelman\noptimointi", fillcolor="#F3E2C7"];
    a2 -> oa2 -> l2; b2 -> ob2 -> l2;
  }
}
```

```{.makefile tiedosto="esimerkit/Makefile" osa="lto"}
```

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-lto.txt"}
```

Ilman LTO:ta erillinen vertailu maksaa kaksinkertaisen määrän käskyjä;
LTO:n kanssa molemmat versiot ovat samat, eikä kutsuja ole konekoodissa
lainkaan. Ajat miljoonan tuotteen lajittelussa:

```{.tuloste tiedosto="esimerkit/tulokset/09-lto.txt"}
```

```{.tuloste tiedosto="esimerkit/tulokset/09-lto-kylla.txt"}
```

C++-ohjelmissa LTO:lla on kaksi erityistä hyötyä. Kääntäjä voi
devirtualisoida, kun se näkee koko luokkahierarkian (luku 3), ja se
voi poistaa mallien käyttämättömät instanssit ja yhdistää samanlaiset.
`-flto=auto` jakaa työn usealle prosessille; Clangin ThinLTO
(`-flto=thin`) on suurissa projekteissa nopeampi linkittää.
CMakessa LTO otetaan käyttöön ominaisuudella
`INTERPROCEDURAL_OPTIMIZATION`.

## Profiiliohjattu optimointi

*PGO* (engl. profile-guided optimization) kääntää ohjelman ensin
instrumentoituna (`-fprofile-generate`), ajaa sen edustavalla kuormalla
ja kääntää uudelleen profiilin kanssa (`-fprofile-use`). Menetelmä ja
esimerkki ovat taidossa *Suorituskyvyn analyysi ja optimointi*.
C++-ohjelmissa PGO hyödyttää erityisesti kahta asiaa:

- **Spekulatiivinen devirtualisointi.** Profiili kertoo, mikä
  virtuaalifunktio kutsukohdassa yleensä on, ja kääntäjä lisää
  sille suoran polun, kuten luvun 3 avoimelle luokalle.
- **Sisällyttämisen valinta.** Mallit ja otsakkeiden funktiot tuottavat
  paljon sisällytettävää. Profiili kertoo, mitkä kutsukohdat ovat
  kuumia, joten kylmät jätetään sisällyttämättä ja koodin kasvu
  rajoittuu.

## Käännösaikainen laskenta

`constexpr`- ja `consteval`-funktiot siirtävät laskennan
käännökseen. *Moderni C++* esittelee kielen säännöt; suorituskyvyn
kannalta tärkeää on, mitä valmiiseen ohjelmaan jää:

```{.cpp tiedosto="esimerkit/09-constexpr.cpp" osa="taulukko"}
```

```{.cpp tiedosto="esimerkit/09-constexpr.cpp" osa="ajonaikainen"}
```

```{.tuloste tiedosto="esimerkit/09-constexpr.odotettu"}
```

```{.makefile tiedosto="esimerkit/Makefile" osa="constexpr"}
```

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-constexpr.txt"}
```

Ohjelmassa on vain taulukko vakiodatana (`r` eli vain luku), ei sen
laskevaa funktiota. `consteval` takaa tämän: jos kutsua ei voi laskea
käännösaikana, käännös epäonnistuu. Pelkkä `constexpr` sallii laskennan
myös ajon aikana, jolloin kääntäjä saa valita. `static_assert` testaa
funktion jo käännöksessä. Käännösaikaisen laskennan hinta on
käännösaika ja muisti: kääntäjän tulkki on satoja kertoja hitaampi kuin
käännetty koodi, ja kääntäjät rajoittavat askelten määrää
(`-fconstexpr-ops-limit`).

## Otsakkeiden hinta

Näkyvyys maksetaan käännösajassa. Jokainen `#include` tuo
käännösyksikköön koko otsakkeen ja sen otsakkeet, ja kääntäjä
jäsentää ne joka kerta uudelleen:

```{.makefile tiedosto="esimerkit/Makefile" osa="otsakkeet"}
```

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-otsakkeet.txt"}
```

`<cstdio>` on muutama sata riviä, `<print>` ja `<iostream>` lähes
viisikymmentätuhatta. Sadan tiedoston projekti, jonka jokainen tiedosto
ottaa mukaan `<format>`in, jäsentää viisi miljoonaa riviä
standardikirjastoa. Keinoja:

- **Ota mukaan vain tarvittava**, ja käytä otsakkeissa
  ennakkoesittelyjä (`class Tietokanta;`) ja `<iosfwd>`ia.
- **Piilota toteutus**: *pimpl*-malli tai erillinen käännösyksikkö
  pitää raskaat otsakkeet poissa rajapinnasta. Hinta on, ettei
  toteutusta voi sisällyttää ilman LTO:ta: tämä on luvun alun
  kauppa toisin päin.
- **Esikäännetyt otsakkeet** (CMaken `target_precompile_headers`)
  jäsentävät yleiset otsakkeet kerran.
- **Modulit** (C++20, `import std;` C++23:sta) korvaavat tekstuaalisen
  sisällyttämisen käännetyllä rajapinnalla. Kääntäjätuki on valmistunut
  vähitellen (GCC 15, Clang 18 libc++:n kanssa, MSVC).

Käännösajan voi mitata: Clangin `-ftime-trace` kirjoittaa
liekkikuvaajana avattavan JSON-tiedoston, ja työkalu ClangBuildAnalyzer
kokoaa niistä projektin kalleimmat otsakkeet ja mallit.

## Käytännössä

- **Pienet, kuumat funktiot otsakkeeseen**, suuret ja harvoin
  kutsutut `.cpp`-tiedostoon. Mallit ovat otsakkeissa joka tapauksessa.
- **Ota LTO käyttöön julkaisukäännöksissä.** Hyöty on usein
  kymmeniä prosentteja ilman koodimuutoksia, ja se korjaa
  käännösyksikköjaon suorituskykyhaitat.
- **`consteval` taulukoille ja vakioille**, `static_assert`
  tarkistuksille. Laskenta tapahtuu kerran käännöksessä eikä joka
  käynnistyksessä.
- **Mittaa käännösaika** kuten ajonaika, ja karsi raskaimmat
  otsakkeet rajapinnoista.
- **Älä riko ODR:ää makroilla.** Sama otsake on jäsennettävä joka
  käännösyksikössä samoin asetuksin.

## Itsearviointi

- Osaat selittää, mitä `inline` tarkoittaa ODR:n kannalta ja mikä on
  sisällyttämisen edellytys.
- Osaat osoittaa konekoodista ja käskymääristä, että LTO sisällyttää
  toisen käännösyksikön funktion.
- Osaat siirtää laskennan käännökseen `consteval`illa ja varmistaa,
  ettei laskevaa koodia jää ohjelmaan.
- Osaat mitata otsakkeiden hinnan ja nimetä keinot käännösajan
  lyhentämiseen.
