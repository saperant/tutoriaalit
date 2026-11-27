# Optimoinnit

**Optimointi** on muunnos, joka säilyttää ohjelman merkityksen ja
tekee siitä nopeamman tai pienemmän. Nimi on harhaanjohtava: kääntäjä
ei tuota optimaalista koodia (se on yleisesti ratkeamatonta), vaan
parantaa koodia joukolla paikallisia sääntöjä ja analyysejä. Jokainen
optimointi on pieni, ja teho syntyy niiden yhdistelmästä: yksi
muunnos paljastaa mahdollisuuden toiselle.

Tämän luvun optimoinnit ovat **passeja** (*pass*): kukin käy funktion
läpi, muuttaa sitä ja kertoo, muuttuiko jotain. Ajuri ajaa passeja
kierroksittain, kunnes mikään passi ei enää muuta funktiota:

```{.cpp tiedosto="esimerkit/kide/optimointi.cpp" osa="optimoi"}
```

## Vakioiden laskostus

**Vakioiden laskostus** (*constant folding*) laskee käännösaikana
operaation, jonka operandit tunnetaan. Se käyttää samaa
aritmetiikan määrittelyä kuin tulkki (luku 2), joten `7 / 0` laskostuu
samaksi kuin suoritin sen laskisi:

```{.cpp tiedosto="esimerkit/kide/optimointi.cpp" osa="laskostus"}
```

Laskostus on vaarallisimpia optimointeja, koska kääntäjä laskee
*isäntäkoneella* kohdekoneen aritmetiikkaa. Ristiinkääntäjässä
isäntä ja kohde voivat erota sanan pituudessa, tavujärjestyksessä ja
liukulukujen pyöristyksessä. GCC käyttää siksi mielivaltaisen tarkkuuden
aritmetiikkaa (GMP ja MPFR) laskostaessaan.

## Paikallinen arvonumerointi

**Arvonumerointi** (*value numbering*) käy peruslohkon läpi ja pitää
kirjaa siitä, mitä kunkin rekisterin arvosta tiedetään: onko se vakio,
onko se kopio toisesta rekisteristä, ja mitkä lausekkeet on jo
laskettu mihinkin rekisteriin. Kun rekisteriin kirjoitetaan, kaikki sitä
koskeva tieto vanhenee:

```{.cpp tiedosto="esimerkit/kide/optimointi.cpp" osa="numerointi"}
```

Tiedon avulla jokainen käsky sievennetään. Sievennys tekee neljä
klassista optimointia:

- **kopioiden eteneminen** (*copy propagation*): kun `x = y`, myöhemmät
  `x`:n käytöt korvataan `y`:llä,
- **vakioiden eteneminen** (*constant propagation*) ja laskostus,
- **algebralliset sievennykset**: `x + 0`, `x * 1`, `x * 0`,
- **yhteisten alilausekkeiden poisto** (*common subexpression
  elimination*): jos `a + b` on jo laskettu rekisteriin `%1` eikä
  kumpikaan operandi ole muuttunut, uusi laskenta korvataan kopiolla.

Sievennyksen alku korvaa operandit kopioiden lähteillä ja muuttaa
tunnetun ehdon haarat hypyiksi. Loppuosa laskostaa, sieventää ja etsii
yhteiset alilausekkeet:

```{.cpp tiedosto="esimerkit/kide/optimointi.cpp" osa="sievenna"}
```

Vaihdannaisten operaatioiden operandit järjestetään, jotta `a + b` ja
`b + a` tunnistetaan samaksi. Ehdollinen haara, jonka ehto tunnetaan,
muuttuu hypyksi; se avaa tien saavuttamattoman koodin poistolle.

Algebrallisissa sievennyksissä on oltava tarkka. `x * 0 = 0` pätee
kokonaisluvuille mutta ei liukuluvuille (`NaN * 0` on `NaN`), ja
`x / x = 1` ei päde, kun `x` on nolla. Jokainen sääntö on todistettava
kielen semantiikasta, ei koulumatematiikasta. Alive2-työkalu on
löytänyt LLVM:n sievennyssäännöistä kymmeniä virheitä tarkistamalla
ne SMT-ratkaisijalla.

## Kuolleen koodin poisto

Käsky on **kuollut**, jos sen tulosta ei lueta ja sillä ei ole
sivuvaikutuksia. Elävyysanalyysi (luku 10) kertoo lohkon lopussa
elävät rekisterit, ja lohko käydään taaksepäin:

```{.cpp tiedosto="esimerkit/kide/optimointi.cpp" osa="kuollut"}
```

Kutsuja ja tulostuksia ei poisteta, vaikka niiden tulosta ei
käytettäisi, koska kutsuttu funktio voi tulostaa. Tuotantokääntäjät
analysoivat funktioiden sivuvaikutukset (GCC:n `pure`- ja
`const`-attribuutit, LLVM:n `memory(none)`), ja silloin
sivuvaikutuksettoman funktion kutsunkin voi poistaa.

## Ohjausvuon siistiminen

Kun haara muuttuu hypyksi, graafiin jää tyhjiä lohkoja ja hyppyketjuja.
Siistiminen ohjaa hypyt tyhjien lohkojen ohi, muuttaa haaran, jonka
molemmat kohteet ovat samat, hypyksi, yhdistää lohkon ja sen ainoan
seuraajan, jos seuraajalla ei ole muita edeltäjiä, ja poistaa lohkot,
joihin ei enää pääse (syvyyshaku alkulohkosta).

## Kopioiden yhdistäminen

Alentaminen tuottaa sijoituksesta kaksi käskyä: `%6 = add i, %5` ja
`i = %6`. Jos `%6` ei ole elävä kopion jälkeen, laskennan voi
kirjoittaa suoraan kohteeseen: `i = add i, %5`. Passi laskee
elävyyden jokaisen käskyn jälkeen kulkemalla lohkon taaksepäin ja
etsii laskenta–kopio-pareja, joissa välitulos kuolee kopioon.

Tämä on yksinkertainen muoto **yhdistämisestä** (*coalescing*), jonka
rekisterien varaajat tekevät yleisemmin: kaksi rekisteriä, joiden
elinajat eivät leikkaa ja jotka on yhdistetty kopiolla, saavat saman
fyysisen rekisterin, ja kopio katoaa.

## Passit yhdessä

Funktion `nelio` passit (`--vaihe=passit`):

```{.rust tiedosto="esimerkit/naytteet/vakiot.kide"}
```

```{.tuloste tiedosto="esimerkit/naytteet/passit-nelio.txt"}
```

Ensin poistetaan `return`-lauseen jälkeinen saavuttamaton lohko.
Arvonumerointi huomaa, että `%2` laskee saman kuin `%1`, ja korvaa sen
kopiolla; kertolasku käyttää nyt kahdesti `%1`:tä, ja kuolleen koodin
poisto poistaa kopion. Pääohjelmassa yhdistelmä on vielä tehokkaampi.
Ilman optimointeja:

```{.tuloste tiedosto="esimerkit/naytteet/ir-vakiot-O0.txt"}
```

Optimoituna:

```{.tuloste tiedosto="esimerkit/naytteet/ir-vakiot.txt"}
```

Vakioiden eteneminen laskee `ala = 42`, laskostus tekee ehdosta
`42 > 40` toden, haaran sieventäminen tekee siitä hypyn, siistiminen
poistaa `else`-haaran (ja sen mukana kutsun `nelio`), ja kuolleen koodin
poisto poistaa muuttujat `leveys` ja `korkeus`. Mikään yksittäinen
passi ei olisi tehnyt tätä yksin. Tämä on **vaiheiden järjestyksen
ongelma** (*phase ordering problem*): yksi optimointi luo tilaisuuksia
toiselle, eikä mikään kiinteä järjestys ole kaikille ohjelmille paras.
Kide toistaa passeja kiintopisteeseen asti; tuotantokääntäjät ajavat
kiinteän, huolella viritetyn putken, jossa sama passi voi esiintyä
monta kertaa (LLVM:n `-O2`-putkessa on satoja passeja).

## Mitä Kidestä puuttuu

Tämän luvun passit ovat tason `-O1` sisältö, ja niiden arvonumerointi
toimii lohko kerrallaan. Koko funktion yli toimivat vakioiden
eteneminen, arvonumerointi ja kuolleen koodin poisto tehdään
SSA-muodossa tasolla `-O2` (luvut 13 ja 14).
Tärkeimmät optimoinnit, joita Kide ei tee millään tasolla:

| Optimointi | Ajatus |
|------------|--------|
| upottaminen (*inlining*) | kutsu korvataan funktion rungolla; avaa muut optimoinnit kutsun yli |
| silmukasta riippumattoman koodin siirto | silmukassa muuttumaton laskenta siirretään silmukan eteen |
| induktiomuuttujat ja voiman vähennys | `i * 8` silmukassa muuttuu yhteenlaskuksi |
| häntärekursion poisto | rekursiivinen kutsu viimeisenä muuttuu hypyksi |
| silmukoiden avaus ja vektorointi | useampi kierros kerralla, SIMD-käskyt |
| osittaisen redundanssin poisto | lauseke, joka on laskettu vain osalla poluista, lasketaan muillakin ja käytetään uudelleen |

Upottaminen on niistä tärkein: se poistaa kutsun kustannuksen ja tuo
kutsujan ja kutsutun koodin saman optimoinnin piiriin. Luvussa 18
nähdään GCC:n muuttavan kertomafunktion rekursion silmukaksi.

## Käytännössä

- **Optimointi on merkityksen säilyttävä muunnos.** Jokaisen säännön
  on oltava todistettavasti oikein kielen semantiikassa, myös
  reunatapauksissa (ylivuoto, nolla, NaN).
- **Pienet passit, toistettuina.** Yksinkertaiset passit on helppo
  testata, ja niiden yhdistelmä on tehokas. Tulosta välikieli
  jokaisen passin jälkeen, kun etsit vikaa.
- **Sivuvaikutukset rajaavat kaiken.** Kutsua, muistiin kirjoitusta tai
  tulostusta ei poisteta eikä siirretä ilman analyysiä, joka todistaa
  sen turvalliseksi.
- **Mittaa.** Optimointi, joka ei nopeuta todellisia ohjelmia, on
  pelkkää kääntäjän monimutkaisuutta (taito *Suorituskyvyn analyysi ja
  optimointi*).

## Itsearviointi

- Osaat toteuttaa paikallisen arvonumeroinnin, joka tekee kopioiden ja
  vakioiden etenemisen, laskostuksen ja yhteisten alilausekkeiden
  poiston.
- Osaat poistaa kuolleen koodin elävyysanalyysin avulla ja kertoa,
  miksi kutsuja ei poisteta.
- Osaat selittää, miten optimoinnit ruokkivat toisiaan, ja mitä
  vaiheiden järjestyksen ongelma tarkoittaa.
- Osaat arvioida algebrallisen sievennyksen oikeellisuuden kielen
  semantiikan perusteella.
