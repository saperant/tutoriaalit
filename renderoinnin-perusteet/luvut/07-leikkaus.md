# Leikkaus

Perspektiivijako olettaa, että $w$ on positiivinen eli piste on
kameran edessä. Kolmio, jonka yksi kärki on kameran takana, rikkoo
oletuksen: jako negatiivisella $w$:llä peilaa kärjen keskipisteen
toiselle puolelle, ja kolmio piirtyy väärään paikkaan tai ei
ollenkaan. Kärki, jonka $w$ on nolla, ei projisoidu mihinkään.
Lattiat, seinät ja maasto ulottuvat jatkuvasti kameran taakse, joten
tapaus on arkipäivää.

Ratkaisu on **leikkaus** (clipping): kolmiosta leikataan pois osa,
joka on lähitason takana, ennen perspektiivijakoa.

## Leikkausavaruus

Leikkaus tehdään leikkausavaruudessa, jossa koordinaatit ovat vielä
homogeenisia. Näkökartio on siellä yksinkertainen: piste on näkyvissä,
kun

$$-w \le x \le w, \qquad -w \le y \le w, \qquad -w \le z \le w.$$

Ehdot ovat lineaarisia, joten jokainen leikkaustaso on
leikkausavaruudessa tavallinen taso, ja kärkien välinen interpolointi
on oikein. Perspektiivijaon jälkeen näin ei olisi, ja kameran takana
olevaa kärkeä ei voisi enää edes esittää järkevästi. Lähitaso on ehto
$z + w \ge 0$: suure $z + w$ on etumerkillinen etäisyys tasosta
(skaalattuna), positiivinen näkyvällä puolella.

## Sutherland–Hodgman

Monikulmion leikkaus yhtä tasoa vastaan on yksinkertainen: kuljetaan
monikulmion reunat läpi, säilytetään sisäpuolella olevat kärjet, ja
jokaisen tason ylittävän reunan kohdalle lisätään uusi kärki. Tämä on
**Sutherlandin–Hodgmanin** algoritmi (1974). Useampaa tasoa vastaan
leikataan toistamalla sama tasoittain.

```{.cpp tiedosto="esimerkit/yhteinen/putki.hpp" osa="leikkaus"}
```

Uuden kärjen paikka on kohdassa $t = d_a / (d_a - d_b)$, jossa $d$ on
etäisyys tasosta. Samalla parametrilla interpoloidaan kaikki kärjen
muut arvot, joten leikattu kärki saa oikean värin ja
tekstuurikoordinaatin:

```{.cpp tiedosto="esimerkit/yhteinen/putki.hpp" osa="tulos"}
```

Jos lähitason takana on yksi kärki, tuloksena on nelikulmio; jos
kaksi, pienempi kolmio; jos kaikki kolme, ei mitään. Nelikulmio
jaetaan kahdeksi kolmioksi viuhkana. Yhden tason leikkaus tuottaa
enintään yhden lisäkärjen, joten kuuden tason leikkaus voi tuottaa
enintään yhdeksänkulmion.

## Kolmio kameran takana

Seuraava esimerkki leikkaa lattiakolmion, jonka kärki $c$ on kameran
takana, ja piirtää sen leikkauksen kanssa ja ilman:

```{.cpp tiedosto="esimerkit/07-leikkaus.cpp" osa="kolmio"}
```

```{.cpp tiedosto="esimerkit/07-leikkaus.cpp" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/07-leikkaus.odotettu"}
```

Kärjen $c$ arvo $w$ on negatiivinen, ja $z + w < 0$ kertoo, että se on
lähitason takana. Leikkaus korvaa sen kahdella kärjellä, jotka ovat
täsmälleen lähitasolla ($z + w = 0$, $w$ on lähitason etäisyys 0,5).
Leikattu nelikulmio täyttää ruudun alaosan, kuten lattian kuuluukin.
Ilman leikkausta kärki $c$ peilautuu ylös horisontin taakse, ja
kolmiosta piirtyy vain kapea suikale. Peilautuminen kääntää myös
kolmion kiertosuunnan, joten takapintojen karsinta hylkäisi sen
kokonaan. Siksi karsinta on esimerkissä pois, jotta virheellinen
kolmio näkyy.

## Hylkäys ja suojakaista

Kaikkia kuutta tasoa ei kannata leikata. Kolmio, jonka kaikki kärjet
ovat saman tason ulkopuolella, hylätään kokonaan ilman leikkausta:

```{.cpp tiedosto="esimerkit/yhteinen/putki.hpp" osa="hylkaa"}
```

Kolmiot, jotka ylittävät vain ruudun sivu-, ylä- tai alareunan,
piirretään leikkaamatta: rasteroija käy läpi vain ruudun sisällä olevat
pikselit, joten ruudun ulkopuolinen osa ei maksa mitään. Tätä kutsutaan
**suojakaistaksi** (guard band). Näytönohjaimet leikkaavat sivutasoja
vastaan vain, jos koordinaatit kasvaisivat kiinteän pilkun
esitysalueen yli. Tässä toteutuksessa 64-bittiset kokonaisluvut
riittävät tavallisille kohtauksille, ja ainoa todella leikattava taso
on lähitaso. Kaukotason takana olevat pikselit hylätään syvyystestissä,
koska niiden syvyys on yli 1.

Leikkaus muuttaa myös tilastoja: kolmio voi muuttua kahdeksi
kolmioksi, ja kuvan kolmiomäärä on eri kuin mallin. Lattia, joka
ulottuu kameran taakse, leikataan joka ruudulla.

## Käytännössä

- **Leikkaa ennen perspektiivijakoa.** Leikkausavaruudessa tasot ovat
  lineaarisia ja interpolointi oikein; jaon jälkeen tieto kameran
  takana olemisesta on menetetty.
- **Hylkää kokonaan ulkona olevat kolmiot halvalla testillä** ja
  leikkaa vain lähitasoa vastaan; muuten luota suojakaistaan.
- **Interpoloi kaikki kärjen arvot leikkauskohtaan.** Unohtunut arvo
  näkyy värin tai tekstuurin hyppäyksenä kameran lähellä.
- **Lähitaso on kompromissi.** Liian kaukana se leikkaa lähellä olevat
  esineet (seinän läpi näkeminen), liian lähellä se syö syvyyden
  tarkkuuden.

## Itsearviointi

- Osaat selittää, mitä tapahtuu, jos kameran takana olevaa kärkeä ei
  leikata.
- Osaat kirjoittaa näkökartion ehdot leikkausavaruudessa ja
  lähitason ehdon $z + w \ge 0$.
- Osaat leikata monikulmion tasoa vastaan Sutherlandin–Hodgmanin
  algoritmilla ja interpoloida uusien kärkien arvot.
- Osaat kertoa, miksi sivutasoja ei yleensä leikata (suojakaista).
