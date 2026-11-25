# Muistinvaraukset

Dynaaminen muistinvaraus on C++-ohjelman yleisin piilokustannus.
Yksi `operator new` maksaa glibc:n varaajalla tyypillisesti 20–100
nanosekuntia, monisäikeisessä kilpailussa enemmän, ja jokainen varaus
hajottaa dataa eri puolille kekoa. Standardikirjasto varaa usein
huomaamatta: vektori kasvaessaan, merkkijono pidentyessään ja
solmusäiliö jokaista alkiota kohden. Yleiset keinot, kuten areenat ja
sivuvirheet, käsitellään taidossa *Suorituskyvyn analyysi ja
optimointi*. Tässä luvussa mitataan standardikirjaston omat
varaukset ja keinot vähentää niitä sekä älykkäiden osoittimien hinta.

## `reserve`

`std::vector` kasvattaa kapasiteettiaan geometrisesti, jotta
`push_back` on keskimäärin vakioaikainen. libstdc++ kaksinkertaistaa
kapasiteetin:

```{.cpp tiedosto="esimerkit/06-reserve.cpp" osa="kapasiteetti"}
```

Tuhat alkiota tarvitsee yksitoista varausta, ja jokainen kasvu siirtää
kaikki vanhat alkiot. Kun lopullinen koko tiedetään tai voidaan arvioida,
`reserve` tekee yhden varauksen:

```{.cpp tiedosto="esimerkit/06-reserve.cpp" osa="reserve"}
```

Merkkijonojen yhdistäminen `+`-operaattorilla tuottaa välituloksia.
libstdc++ käyttää väliaikaisen merkkijonon puskuria uudelleen, kun se
riittää, mutta kasvu varaa silti. `reserve` ja `append` tekevät yhden
varauksen:

```{.cpp tiedosto="esimerkit/06-reserve.cpp" osa="merkkijono"}
```

```{.tuloste tiedosto="esimerkit/06-reserve.odotettu"}
```

`reserve` ei pienennä kapasiteettia, eikä vektori pienene, kun alkioita
poistetaan. `shrink_to_fit` pyytää pienentämään (pyyntö ei ole
sitova), ja `clear` säilyttää kapasiteetin, mikä on yleensä haluttua:
uudelleen täytetty vektori ei varaa uudelleen. Silmukassa luotu
vektori kannattaa siksi usein siirtää silmukan ulkopuolelle ja
tyhjentää kierrosten välillä.

## Lyhyen merkkijonon optimointi

`std::string` on 32 tavun olio, jossa on osoitin, pituus ja joko
kapasiteetti tai sisäinen puskuri. Lyhyt merkkijono tallennetaan
olion sisään ilman varausta (engl. small string optimization, SSO):

```{.dot otsikko="libstdc++:n `std::string` kahdessa tilassa (periaatekuva). Lyhyen merkkijonon osoitin osoittaa olion omaan puskuriin; pitkän merkkijonon merkit ovat keossa, ja samassa kohdassa oliota on kapasiteetti."}
digraph {
  rankdir=TB; nodesep=0.6; ranksep=0.45;
  node [shape=plain, style=""];
  lyhyt [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="3"><i>"tunniste" (8 merkkiä): ei varausta</i></td></tr>
    <tr><td port="p" bgcolor="#EEF1F6">osoitin (8)</td><td bgcolor="#EEF1F6">pituus 8 (8)</td><td port="b" bgcolor="#F3E2C7">puskuri: tunniste\\0 (16)</td></tr></table>>];
  pitka [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="3"><i>24 merkkiä: yksi varaus</i></td></tr>
    <tr><td port="p" bgcolor="#EEF1F6">osoitin (8)</td><td bgcolor="#EEF1F6">pituus 24 (8)</td><td bgcolor="#EEF1F6">kapasiteetti 24 (8) + käyttämätön (8)</td></tr></table>>];
  keko [shape=box, style="rounded,filled", fillcolor="#FFFFFF", label="keko: 25 tavua"];
  lyhyt:p:s -> lyhyt:b:s;
  pitka:p:s -> keko;
}
```

```{.cpp tiedosto="esimerkit/06-sso.cpp" osa="sso"}
```

```{.cpp tiedosto="esimerkit/06-sso.cpp" osa="nimet"}
```

```{.tuloste tiedosto="esimerkit/06-sso.odotettu"}
```

libstdc++:ssa raja on 15 merkkiä, libc++:ssa 22 ja MSVC:ssä 15.
Lyhyet tunnisteet, avainsanat ja numerot eivät siis varaa lainkaan,
mutta 16 merkin URL tai sähköpostiosoite varaa. Raja vaikuttaa myös
siirtoon: lyhyen merkkijonon siirto kopioi merkit, koska niitä ei voi
"varastaa" osoittimena. Siksi näkymä lyhyen merkkijonon sisältöön
mitätöityy, kun merkkijono siirtyy (luku 7).

## Polymorfiset muistiresurssit

C++17:n `std::pmr` (polymorphic memory resources) erottaa varausstrategian
säiliön tyypistä. `std::pmr::vector<T>` on `std::vector<T,
std::pmr::polymorphic_allocator<T>>`, ja allokaattori saa
rakennettaessa osoittimen muistiresurssiin. Kirjasto tarjoaa kolme
resurssia:

| Resurssi | Strategia | Sopii |
|--------------------------|------------------------------------|--------------------------|
| `monotonic_buffer_resource` | Varaa peräkkäin, ei vapauta yksittäin | Lyhytikäinen työ, jäsennys, pyyntö |
| `unsynchronized_pool_resource` | Poolit kokoluokittain, yksi säie | Solmusäiliöt yhdessä säikeessä |
| `synchronized_pool_resource` | Sama lukolla | Jaettu usean säikeen kesken |

Monotoninen resurssi pinossa olevan puskurin päällä on varaajista
nopein: varaus on osoittimen siirto, ja vapautus tapahtuu kerralla,
kun resurssi tuhoutuu. Ylävirraksi annettu `null_memory_resource`
heittää `std::bad_alloc`in, jos puskuri loppuu, joten keosta ei varata
vahingossa:

```{.cpp tiedosto="esimerkit/06-pmr.cpp" osa="monotoninen"}
```

Merkkijonot ovat `std::pmr::string`-tyyppisiä, ja vektori antaa niille
saman resurssin automaattisesti (engl. uses-allocator construction).
Poolin ja oman laskevan resurssin avulla nähdään, kuinka harvoin
pooli pyytää muistia ylävirralta:

```{.cpp tiedosto="esimerkit/06-pmr.cpp" osa="laskeva"}
```

```{.cpp tiedosto="esimerkit/06-pmr.cpp" osa="pooli"}
```

```{.cpp tiedosto="esimerkit/06-pmr.cpp" osa="testi"}
```

```{.tuloste tiedosto="esimerkit/06-pmr.odotettu"}
```

Tuhat `std::map`-lisäystä on tuhat varausta, pooli tekee kahdeksan.
Ajoissa:

```{.tuloste tiedosto="esimerkit/tulokset/06-pmr.txt"}
```

`pmr`:n hinta on virtuaalikutsu jokaista varausta kohden (resurssi on
kantaluokka, jonka `do_allocate` on virtuaalinen) ja 8 tavua
lisää jokaisessa säiliössä. Lisäksi `std::pmr::string` ja
`std::string` ovat eri tyyppejä: rajapinnan, joka ottaa `const
std::string&`, kutsuminen `pmr`-merkkijonolla kopioi. Rajapinnoissa
`std::string_view` ratkaisee tämän (luku 7).

## Oma allokaattori

Allokaattori on tyyppi, jolla on `value_type`, `allocate` ja
`deallocate`; loput `std::allocator_traits` täydentää. Areena, josta
varataan peräkkäin ja joka vapautetaan kerralla, on muutaman rivin työ:

```{.cpp tiedosto="esimerkit/06-areena.cpp" osa="areena"}
```

```{.cpp tiedosto="esimerkit/06-areena.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/06-areena.odotettu"}
```

Areenan tuhannesta listasolmusta jokainen vie 24 tavua (kaksi
osoitinta ja `int` tasattuna), eikä yhtään varausta tehdä keosta
areenan oman puskurin jälkeen. Oma allokaattori on osa säiliön tyyppiä,
joten `std::list<int, AreenaAllokaattori<int>>` ei ole sama tyyppi kuin
`std::list<int>`. Tämä on syy, miksi `pmr` tehtiin: sama säiliötyyppi,
vaihdettava strategia. Omaa allokaattoria kannattaa käyttää, kun
virtuaalikutsukin on liikaa tai kun allokaattorin pitää kantaa tietoa,
kuten NUMA-solmua tai jaetun muistin osoitetta.

## Älykkäiden osoittimien hinta

`std::unique_ptr` on osoittimen kokoinen, ja sen käyttö kääntyy samaksi
koodiksi kuin paljas osoitin ja `delete`. `std::shared_ptr` maksaa
kolmessa kohdassa: se on kahden osoittimen kokoinen, se tarvitsee
*ohjauslohkon* (viitelaskurit ja poistaja), ja jokainen kopio päivittää
laskuria atomisesti.

```{.cpp tiedosto="esimerkit/06-osoittimet.cpp" osa="luonti"}
```

Kalleinta on huomaamaton kopio. Funktio, joka ottaa `shared_ptr`in
arvona, ottaa osuuden omistuksesta, vaikka se vain lukisi oliota:

```{.cpp tiedosto="esimerkit/06-osoittimet.cpp" osa="valitys"}
```

```{.cpp tiedosto="esimerkit/06-osoittimet.cpp" osa="testi"}
```

```{.tuloste tiedosto="esimerkit/06-osoittimet.odotettu"}
```

```{.makefile tiedosto="esimerkit/Makefile" osa="osoittimet"}
```

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-osoittimet.txt"}
```

Arvona välitys tekee neljä kertaa niin monta käskyä kuin viittaus, ja
käskymäärä aliarvioi eron: laskurin kasvatus ja vähennys ovat atomisia
operaatioita, ja jos sama osoitin kopioidaan usean säikeen kuumassa
silmukassa, laskurin välimuistirivi kiertää ytimeltä toiselle (ks.
*Rinnakkaisohjelmointi*). Rajapinnan sääntö seuraa suoraan mittauksesta:
funktio, joka vain käyttää oliota, ottaa `const T&`:n tai `T*`:n;
`shared_ptr` arvona kuuluu funktiolle, joka säilyttää osoittimen.

`unique_ptr`in nollakustannuksella on kaksi rajaa. Oma poistaja, jolla
on tilaa (esimerkiksi funktio-osoitin), kasvattaa olion kokoa; tilaton
poistaja, kuten lambda ilman sieppauksia, ei kasvata. Lisäksi Itaniumin
ABI:ssa `unique_ptr` välitetään arvona muistin kautta eikä
rekisterissä, koska sillä on purkaja, joten arvona otettu `unique_ptr`
on hieman paljasta osoitinta kalliimpi parametri.

## Muut keinot

- **Varaajan vaihto.** jemalloc, tcmalloc ja mimalloc ovat glibc:n
  varaajaa nopeampia monisäikeisissä ohjelmissa, ja ne otetaan käyttöön
  linkittämällä tai `LD_PRELOAD`illa ilman koodimuutoksia.
- **Solmujen siirto** (`extract` ja `insert` C++17:stä alkaen) siirtää
  alkion kartasta toiseen varaamatta.
- **`std::array` ja `std::inplace_vector`** (C++26) säilyttävät alkiot
  olion sisällä, kun enimmäiskoko tiedetään.

## Käytännössä

- **Laske varaukset kuumasta polusta.** Pyyntöä, kehystä tai riviä
  kohden tehtyjen varausten määrä on hyvä mittari ja helppo
  regressiotesti.
- **Käytä `reserve`a**, kun koko tiedetään, ja käytä säiliöitä
  uudelleen `clear`illa silmukoissa.
- **Pidä tunnisteet lyhyinä** tai tallenna ne numeroina: alle 16
  merkin merkkijonot eivät varaa libstdc++:ssa.
- **`pmr` ja monotoninen resurssi** lyhytikäiselle työlle, jonka
  kaikki tulokset hylätään kerralla, kuten pyynnön käsittely tai
  jäsennys.
- **`shared_ptr` vain jaettuun omistukseen.** Luo se
  `make_shared`illa, välitä lukijoille viittaus olioon ja kopioi
  osoitin vain, kun kopio todella säilytetään.
- **Poolit solmusäiliöille**, joista lisätään ja poistetaan paljon.
  Vielä parempi on usein vaihtaa solmusäiliö vektoriin (luku 8).

## Itsearviointi

- Osaat ennustaa ja mitata vektorin ja merkkijonon kasvun varaukset ja
  vähentää ne `reserve`lla.
- Osaat selittää lyhyen merkkijonon optimoinnin ja sen rajan
  libstdc++:ssa ja libc++:ssa.
- Osaat kertoa, mitä `shared_ptr` maksaa luotaessa ja kopioitaessa, ja
  valita funktion parametrin tyypin sen mukaan, säilyttääkö funktio
  osoittimen.
- Osaat käyttää `monotonic_buffer_resource`- ja
  `unsynchronized_pool_resource`-resursseja ja kirjoittaa oman
  muistiresurssin.
- Osaat kirjoittaa yksinkertaisen allokaattorin ja selittää, miksi
  `pmr` on usein parempi valinta.
