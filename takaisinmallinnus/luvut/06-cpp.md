# C++-ohjelmien takaisinmallinnus

C++-ohjelman konekielessä on samat rakenteet kuin C-ohjelmassa, mutta
lisäksi kielen mekanismit: koristellut nimet, virtuaalitaulut,
ajonaikainen tyyppitieto (RTTI), poikkeustaulut ja vakiokirjaston
tyyppien sisäinen asettelu. Kun ne tunnistaa, luokkahierarkian voi
palauttaa melko tarkasti.

Luku olettaa, että C++ on tuttu lähdekoodin tasolla (*Moderni C++*).
Lyhyt kertaus luvussa tarvittavista käsitteistä: *virtuaalifunktio* on
jäsenfunktio, jonka toteutus valitaan ajon aikana olion todellisen
luokan mukaan, ja *puhdas virtuaalifunktio* (`= 0`) tekee luokasta
abstraktin. *Purkaja* (*destructor*) ajetaan, kun olio tuhotaan.
`std::unique_ptr` on osoitin, joka omistaa kohteensa ja vapauttaa sen
itse, `dynamic_cast` tarkistaa olion tyypin ajon aikana, ja poikkeus
(`throw`, `catch`) siirtää suorituksen kutsupinoa ylöspäin lähimpään
sieppaajaan. Esimerkin kohde on pieni muotohierarkia:

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

```{.dot otsikko="`Ympyra`-olio, sen virtuaalitaulu ja tyyppitieto edellisen tulosteen mukaan. Olion ensimmäinen sana osoittaa taulun paikkaan 2, ja `call [rax+0x10]` lukee paikan 4."}
digraph {
  rankdir=LR; nodesep=0.4; ranksep=0.7;
  node [shape=plain, style=""];
  olio [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0" colspan="2" align="left"><i>Ympyra-olio (keossa)</i></td></tr>
    <tr><td border="0"><font point-size="8">+0</font></td><td port="vptr" bgcolor="#EEF1F6" width="80">vptr</td></tr>
    <tr><td border="0"><font point-size="8">+8</font></td><td>sade_</td></tr>
  </table>>];
  vt [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0" colspan="2" align="left"><i>vtable for Ympyra (.data.rel.ro)</i></td></tr>
    <tr><td border="0"><font point-size="8">[0]</font></td><td align="left">0 (siirtymä olion alkuun)</td></tr>
    <tr><td border="0"><font point-size="8">[1]</font></td><td port="ti" align="left">typeinfo for Ympyra</td></tr>
    <tr><td border="0"><font point-size="8">[2]</font></td><td port="p2" bgcolor="#EEF1F6" align="left">~Ympyra (täydellinen)</td></tr>
    <tr><td border="0"><font point-size="8">[3]</font></td><td bgcolor="#EEF1F6" align="left">~Ympyra (poistava)</td></tr>
    <tr><td border="0"><font point-size="8">[4]</font></td><td bgcolor="#EEF1F6" align="left">Ympyra::pinta_ala</td></tr>
    <tr><td border="0"><font point-size="8">[5]</font></td><td bgcolor="#EEF1F6" align="left">Ympyra::nimi</td></tr>
  </table>>];
  ti [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0" align="left"><i>typeinfo for Ympyra</i></td></tr>
    <tr><td align="left">__si_class_type_info</td></tr>
    <tr><td align="left">nimi "6Ympyra"</td></tr>
    <tr><td port="kanta" align="left">typeinfo for Muoto</td></tr>
  </table>>];
  olio:vptr:e -> vt:p2:w;
  vt:ti:e -> ti:w;
}
```

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

```{.dot otsikko="libstdc++:n `std::string` on 32 tavua. Lyhyen merkkijonon data on olion omassa puskurissa, pitkän keossa, ja puskurin paikalla on kapasiteetti."}
digraph {
  nodesep=0.3; ranksep=0.35;
  node [shape=plain, style=""];
  lyhyt [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0" align="left" width="50"><i>lyhyt</i></td><td border="0"><font point-size="8">+0</font></td><td border="0"><font point-size="8">+8</font></td><td border="0" colspan="2"><font point-size="8">+16 … +31</font></td></tr>
    <tr><td border="0"> </td><td bgcolor="#EEF1F6" width="110">data-osoitin<br/><font point-size="8">= olio + 16</font></td><td width="70">pituus 3</td><td colspan="2" width="180">"abc\\0"<br/><font point-size="8">16 tavun puskuri</font></td></tr>
  </table>>];
  pitka [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0" align="left" width="50"><i>pitka</i></td><td border="0"><font point-size="8">+0</font></td><td border="0"><font point-size="8">+8</font></td><td border="0"><font point-size="8">+16</font></td><td border="0"><font point-size="8">+24</font></td></tr>
    <tr><td border="0"> </td><td port="d" bgcolor="#EEF1F6" width="110">data-osoitin</td><td width="70">pituus 40</td><td width="100">kapasiteetti 40</td><td width="80">ei käytössä</td></tr>
  </table>>];
  keko [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0" align="left" width="50"><i>keko</i></td><td width="180">"xxxx…x\\0"<br/><font point-size="8">41 tavua</font></td></tr>
  </table>>];
  lyhyt -> pitka [style=invis];
  pitka:d:s -> keko:n;
}
```

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
