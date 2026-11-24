# C++-ohjelmien takaisinmallinnus

C++-ohjelman konekielessä on samat rakenteet kuin C-ohjelmassa, mutta
lisäksi kielen mekanismit: koristellut nimet, virtuaalitaulut,
ajonaikainen tyyppitieto (RTTI), poikkeustaulut ja vakiokirjaston
tyyppien sisäinen asettelu. Kun ne tunnistaa, luokkahierarkian voi
palauttaa melko tarkasti. Esimerkin kohde on pieni muotohierarkia:

```{.cpp tiedosto="esimerkit/05-cpp/muodot.cpp" osa="luokat"}
```

## Koristellut nimet

Itanium C++ ABI koristelee (*mangle*) nimet niin, että nimiavaruus,
luokka, parametrien tyypit ja `const` tallentuvat symboliin.
*Objektitiedostot, linkitys ja ABI* (luku 13) selittää säännöt; tässä
tärkeintä on, että ne palautuvat työkalulla `c++filt`:

```{.bash tiedosto="esimerkit/05-cpp/aja.sh" osa="nimet"}
```

```{.tuloste tiedosto="esimerkit/05-cpp/odotettu" osa="t1"}
```

Parametrien tyypit tulevat siis symbolitaulusta ilmaiseksi, mikä on
C-ohjelmaan verrattuna suuri etu. Purkajalla on kolme muotoa:
`D0` (*deleting destructor*) purkaa ja vapauttaa muistin, `D1`
(*complete object*) purkaa koko olion ja `D2` (*base object*) vain
kantaluokan osan. Erikoissymbolit alkavat `_ZT`:llä: `_ZTV` on
virtuaalitaulu (*vtable*), `_ZTI` tyyppitieto (*typeinfo*) ja `_ZTS`
tyypin nimi merkkijonona.

## Virtuaalitaulut

Jokaisella virtuaalifunktioita sisältävällä oliolla on ensimmäisenä
kenttänään osoitin luokkansa virtuaalitauluun (*vptr*). Taulu on
`.data.rel.ro`-osiossa, ja paikkariippumattomassa ohjelmassa sen
osoitteet ovat dynaamisia relokaatioita. Skripti `vtaulu.py` lukee
taulun paikat relokaatioista ja nimeää ne symbolitaulun avulla:

```{.bash tiedosto="esimerkit/05-cpp/aja.sh" osa="vtaulu"}
```

```{.tuloste tiedosto="esimerkit/05-cpp/odotettu" osa="t2"}
```

Itanium-ABI:n mukainen taulu alkaa kahdella kentällä: siirtymä olion
alkuun (*offset to top*, nollasta poikkeava moniperinnässä) ja
osoitin tyyppitietoon. Olion vptr osoittaa paikkaan 2, josta
virtuaalifunktiot alkavat esittelyjärjestyksessä: kaksi purkajaa,
`pinta_ala` ja `nimi`. `Suorakulmio` ei korvaa `nimi`-funktiota, joten
sen taulussa on `Muoto::nimi`. `Muoto` on abstrakti (puhdas
virtuaalifunktio), eikä sen taulua tarvita, koska `Muoto`-olioita ei
luoda: kääntäjä on jättänyt sen pois.

Virtuaalikutsu on konekielessä kaksi epäsuoraa latausta ja epäsuora
kutsu:

```{.tuloste tiedosto="esimerkit/05-cpp/odotettu" osa="t3"}
```

`mov rdi,[rbx]` lataa olion osoitteen (`unique_ptr`:n sisältö), `mov
rax,[rdi]` sen vptr:n ja `call [rax+0x10]` kutsuu kolmatta virtuaalifunktiota
(`0x10 / 8 = 2` paikkaa vptr:n jälkeen): `pinta_ala`. Kun siirtymä ja
taulut tunnetaan, epäsuora kutsu voidaan ratkaista kaikiksi mahdollisiksi
kohteiksi: `Ympyra::pinta_ala` tai `Suorakulmio::pinta_ala`. Ghidra
tekee tämän, jos rakenteen tyyppi on asetettu.

## RTTI ja periytyminen

Tyyppitieto paljastaa luokkahierarkian. `__si_class_type_info`
tarkoittaa yksinkertaista periytymistä yhdestä kantaluokasta, ja sen
kolmas kenttä osoittaa kantaluokan tyyppitietoon; `__class_type_info`
on luokka ilman kantaluokkia ja `__vmi_class_type_info` moniperintä.
Edellisestä tulosteesta luetaan suoraan, että `Ympyra` ja
`Suorakulmio` periytyvät `Muoto`:sta. Tyypin nimi (`6Ympyra`) on
koristelun tyyppiosa, ja se säilyy riisutussakin ohjelmassa, koska
`dynamic_cast` ja `typeid` tarvitsevat sitä. Vain `-fno-rtti` poistaa
sen.

## Poikkeukset

```{.cpp tiedosto="esimerkit/05-cpp/muodot.cpp" osa="kaytto"}
```

```{.bash tiedosto="esimerkit/05-cpp/aja.sh" osa="poikkeukset"}
```

```{.tuloste tiedosto="esimerkit/05-cpp/odotettu" osa="t4"}
```

Poikkeuksen heitto on kutsu `__cxa_throw`, sieppaus alkaa kutsulla
`__cxa_begin_catch`, ja `dynamic_cast` on kutsu `__dynamic_cast`.
Sieppauslohkoihin ei hypätä tavallisilla hypyillä: niiden osoitteet ovat
poikkeustauluissa. `.eh_frame` kertoo, miten kunkin funktion
pinokehys puretaan, ja `.gcc_except_table` sisältää funktioiden
*laskeutumisalustat* (*landing pads*), eli sieppaus- ja siivouskoodin
osoitteet. Disassembleri, joka ei lue näitä tauluja, ei löydä
sieppauslohkoja; Ghidra ja IDA lukevat. `.eh_frame` on hyödyllinen
myös C-ohjelmissa, kuten luku 7 näyttää.

## Vakiokirjaston tyypit muistissa

Kun ohjelma käsittelee `std::string`- ja `std::vector`-olioita, niiden
sisäinen asettelu pitää tunnistaa muistista ja konekielestä. gdb:n
skripti lukee asettelun libstdc++:n oliosta suoraan muistista:

```{.text tiedosto="esimerkit/05-cpp/asettelu.gdb" osa="asettelu"}
```

```{.tuloste tiedosto="esimerkit/05-cpp/odotettu" osa="t5"}
```

| Tyyppi (libstdc++, x86-64) | Koko | Kentät |
|----------------------------|------|--------|
| `std::string` | 32 | data-osoitin, pituus, 16 tavun puskuri tai kapasiteetti |
| `std::vector<T>` | 24 | alku, loppu, varatun alueen loppu |
| `std::unique_ptr<T>` | 8 | osoitin |
| `std::shared_ptr<T>` | 16 | osoitin, viitelaskurilohko |

Lyhyt merkkijono (enintään 15 merkkiä) on olion omassa puskurissa:
data-osoitin osoittaa olion sisään (*small string optimization*).
Pitkän merkkijonon data on keossa, ja puskurin paikalla on kapasiteetti.
Vektorin koko lasketaan konekielessä vähentämällä alku lopusta ja
jakamalla alkion koolla, eli tuttu `sar rax,0x3` tai taikaluku. LLVM:n
libc++ ja MSVC:n kirjasto järjestävät kentät toisin, joten kirjasto on
tunnistettava ensin (`nm -D` näyttää `GLIBCXX`- tai `__1`-versiot).

## Käytännössä

- **Pura nimet ensimmäiseksi.** `nm -C` ja `c++filt` antavat
  parametrien tyypit, luokat ja nimiavaruudet.
- **Rakenna luokkahierarkia tyyppitiedosta ja virtuaalitauluista**:
  `_ZTI`-symbolit kertovat periytymisen, `_ZTV`-taulut virtuaalifunktiot
  järjestyksessä.
- **Ratkaise virtuaalikutsut siirtymästä.** `call [rax+N]` on taulun
  paikka `N / 8`; kaikki taulut, joissa paikka on, ovat mahdollisia
  kohteita.
- **Muista poikkeustaulut.** Sieppauskoodi löytyy `.gcc_except_table`-
  taulusta, ei hypyistä.
- **Tunnista kirjaston tyypit asettelusta**: 32 tavun olio, jonka
  ensimmäinen kenttä osoittaa olion sisään, on `std::string`.

## Itsearviointi

- Osaat purkaa koristellut nimet ja tunnistaa purkajien muodot.
- Osaat rekonstruoida virtuaalitaulun ja ratkaista virtuaalikutsun
  mahdolliset kohteet.
- Osaat päätellä luokkahierarkian RTTI:stä.
- Osaat tunnistaa libstdc++:n `std::string`- ja `std::vector`-olioiden
  asettelun muistissa.
