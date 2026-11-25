# Testivetoinen kehitys

Testivetoisessa kehityksessä (*test-driven development*, TDD) koodia
kirjoitetaan lyhyissä kierroksissa, joissa on kolme vaihetta:

1. **Punainen:** kirjoita yksi pieni testi, joka epäonnistuu.
2. **Vihreä:** kirjoita yksinkertaisin koodi, jolla testi menee läpi.
3. **Refaktorointi:** siisti koodi ja testit. Testit pysyvät vihreinä.

```{.dot otsikko="TDD:n kierros kestää minuutteja, ei tunteja"}
digraph {
  rankdir=LR; ranksep=0.3;
  p [label="Punainen\nuusi testi\nepäonnistuu", fillcolor="#F4C7C3"];
  v [label="Vihreä\nyksinkertaisin\ntoteutus", fillcolor="#CDE8C5"];
  r [label="Refaktorointi\nrakenne\nparanee"];
  p -> v [label="vähän\nkoodia"];
  v -> r [label="testit\nturvana"];
  r -> p [label="seuraava vaatimus"];
}
```

Jokaisella vaiheella on oma tehtävänsä. Punainen vaihe pakottaa
päättämään, miltä koodin käyttö näyttää, ennen kuin toteutus on
olemassa. Lisäksi se todistaa, että testi osaa epäonnistua: testi, joka
ei ole koskaan ollut punainen, voi olla vihreä väärästä syystä. Vihreä
vaihe pitää askeleen pienenä. Refaktorointi on se vaihe, jossa
suunnittelu tapahtuu, ja se jää helpoimmin tekemättä.

Tässä luvussa rakennetaan ostoskorin hinnoittelu kahdeksassa vaiheessa.
Jokainen vaihe on oma hakemistonsa (`esimerkit/02-tdd/`), joten kierrosta
voi seurata tiedosto tiedostolta.

## Ensimmäinen testi ennen koodia

Kori laskee ostosten summan. Yksinkertaisin tapaus on tyhjä kori:

```{.python tiedosto="esimerkit/02-tdd/1-punainen/test_kori.py"}
```

Moduulia `kori` ei ole, joten testi ei edes käynnisty:

```{.tuloste tiedosto="esimerkit/02-tdd/1-punainen/odotettu"}
```

Testi on silti jo tehnyt työtä. Se päätti luokan nimen, sen, että kori
luodaan ilman argumentteja, ja sen, että summa kysytään metodilla
`summa()`. Rajapinta suunniteltiin käyttäjän näkökulmasta, koska testi
on koodin ensimmäinen käyttäjä.

Testissä on kolme osaa tyhjällä rivillä erotettuna: **alkutilanne**,
**toiminto** ja **väite** (*arrange, act, assert*). Sama rakenne toistuu
kaikissa tämän tutoriaalin testeissä.

Yksinkertaisin koodi, jolla testi menee läpi, palauttaa vakion:

```{.python tiedosto="esimerkit/02-tdd/2-vihrea/kori.py"}
```

```{.tuloste tiedosto="esimerkit/02-tdd/2-vihrea/odotettu"}
```

Vakion palauttaminen näyttää huijaukselta, mutta se on rehellinen
kuvaus tilanteesta: testit eivät vaadi enempää. Jos toteutus tuntuu
liian tyhmältä, puuttuu testi.

## Kolmiointi

Toinen testi pakottaa yleistämään. Kun kaksi esimerkkiä vaatii eri
tuloksen, vakio ei enää riitä. Tätä kutsutaan **kolmioinniksi**: yleinen
ratkaisu päätellään kahdesta tai useammasta pisteestä.

```{.python tiedosto="esimerkit/02-tdd/3-punainen/test_kori.py" osa="uusi"}
```

Testi käyttää metodia `lisaa`, jota ei ole. Sille kirjoitetaan ensin
tynkä, joka ei tee mitään:

```{.python tiedosto="esimerkit/02-tdd/3-punainen/kori.py" osa="tynka"}
```

Tyngän ansiosta testi epäonnistuu *oikeasta syystä*: väite ei pidä,
eikä syy ole puuttuva metodi tai kirjoitusvirhe testissä.

```{.tuloste tiedosto="esimerkit/02-tdd/3-punainen/odotettu"}
```

Virheilmoitus kannattaa lukea joka kerta. Jos se on jotain muuta kuin
odotit, testi ei testaa sitä, mitä luulet.

Nyt toteutus on helppo kirjoittaa:

```{.python tiedosto="esimerkit/02-tdd/4-vihrea/kori.py" osa="kori"}
```

```{.tuloste tiedosto="esimerkit/02-tdd/4-vihrea/odotettu"}
```

## Refaktorointi

Koodi toimii, mutta rivi on nimetön pari `(hinta, maara)`, ja tuotteen
nimi heitetään pois. Vihreiden testien turvin rakennetta voi muuttaa:
rivistä tehdään oma tyyppinsä, joka osaa laskea hintansa.

```{.python tiedosto="esimerkit/02-tdd/5-refaktorointi/kori.py" osa="rivi"}
```

Testeihin ei kosketa. Ne menevät läpi ennen muutosta ja sen jälkeen,
ja juuri se tekee muutoksesta refaktoroinnin.

Tässä näkyy, miksi testit kannattaa kirjoittaa julkista rajapintaa
vasten. Jos testi olisi tarkistanut listan `_rivit` sisällön, se olisi
hajonnut, vaikka kori toimii täsmälleen kuten ennen.

## Vaatimus testeinä

Seuraava vaatimus tulee kaupalta: *kun samaa tuotetta ostaa vähintään
kymmenen kappaletta, rivin hinnasta saa kymmenen prosentin alennuksen.*

Testiä kirjoittaessa joutuu kysymään asioita, joihin lause ei vastaa.
Koskeeko alennus yhdeksää kappaletta? Entä kun kymmenen prosenttia ei
ole tasasenttejä? Vastaukset kirjataan testeiksi, jolloin niistä tulee
osa määrittelyä:

```{.python tiedosto="esimerkit/02-tdd/6-punainen/test_kori.py" osa="alennus"}
```

Kolmas testi kirjaa päätöksen, jota alkuperäisessä vaatimuksessa ei
ollut: alennus pyöristetään ylöspäin eli asiakkaan eduksi. Päätös
kysyttiin kaupalta, ei arvattu.

```{.tuloste tiedosto="esimerkit/02-tdd/6-punainen/odotettu"}
```

Kaksi testiä on punaisena. Yhdeksän kappaleen testi on vihreä jo nyt,
koska nykyinen koodi ei anna alennusta kenellekään. Se on silti
hyödyllinen: se vartioi rajaa, kun alennus toteutetaan.

```{.python tiedosto="esimerkit/02-tdd/7-vihrea/kori.py" osa="hinta"}
```

```{.tuloste tiedosto="esimerkit/02-tdd/7-vihrea/odotettu"}
```

## Myös testit refaktoroidaan

Toteutuksessa on taikalukuja ja pyöristyskaava ilman nimeä. Säännölle
annetaan nimi, vakioille merkitys ja pyöristykselle oma funktio:

```{.python tiedosto="esimerkit/02-tdd/8-refaktorointi/kori.py" osa="saanto"}
```

Kolme alennustestiä ovat samaa muotoa, joten ne yhdistetään taulukoksi.
Jokaisella rivillä on tunniste, joka kertoo, mitä sääntöä rivi vartioi:

```{.python tiedosto="esimerkit/02-tdd/8-refaktorointi/test_kori.py" osa="taulukko"}
```

```{.tuloste tiedosto="esimerkit/02-tdd/8-refaktorointi/odotettu"}
```

Taulukko paljastaa hinnoittelusta jotain, mitä vaatimuksen kirjoittaja
ei ehkä tarkoittanut: yhdeksän ja kymmenen viiden euron tuotetta maksavat
saman verran. Testi ei ota kantaa siihen, onko se toivottua, mutta se
tekee asian näkyväksi ajoissa.

Koodia ja testejä ei pidä muuttaa samalla askeleella. Kun rakennat koodia
uudelleen, testit pysyvät paikallaan ja vartioivat. Kun siistit testejä,
koodi pysyy paikallaan, ja testin voi hetkeksi rikkoa tahallaan
nähdäkseen, että se yhä osaa epäonnistua.

## Käytännössä

- **Askeleen koko on säädettävä.** Tässä luvussa askeleet ovat
  tarkoituksella pieniä. Tutussa koodissa vihreän vaiheen voi kirjoittaa
  suoraan valmiiksi; kun yllätyt punaisesta testistä, lyhennä askelta.
- **Yksi kierros kestää minuutteja.** Jos testi on ollut punaisena
  puoli tuntia, askel on liian suuri. Peru muutos ja valitse pienempi
  testi.
- **Testilista pitää ajatukset koossa.** Kun kesken työn keksit uuden
  tapauksen ("entä negatiivinen määrä?"), kirjoita se listaan äläkä
  hyppää siihen. Lista on TDD:n huomaamattomin työkalu.
- **Tee commit jokaisen vihreän jälkeen.** Silloin epäonnistuneen
  kokeilun voi perua yhdellä komennolla (taito *Versionhallinta (Git)*).
- **Testin nimi on lause.** `test_alennus_pyoristetaan_asiakkaan_eduksi`
  kertoo säännön; `test_alennus_3` ei kerro mitään, kun testi
  puolen vuoden päästä hajoaa.
- **Testaa käytöstä, älä rakennetta.** Testi, joka tuntee luokan
  yksityiset kentät, estää juuri sen refaktoroinnin, jota varten testit
  kirjoitettiin.

## Itsearviointi

- Osaat selittää, mitä kukin TDD:n kolmesta vaiheesta tuottaa ja mitä
  menetetään, jos vaihe jätetään väliin.
- Osaat kirjoittaa epäonnistuvan testin ennen toteutusta ja varmistaa,
  että se epäonnistuu oikeasta syystä.
- Osaat edetä kolmioimalla: toteutus yleistyy vasta, kun testit sitä
  vaativat.
- Osaat refaktoroida koodia ja testejä erikseen niin, että testit
  pysyvät koko ajan vihreinä.
- Osaat muuttaa epämääräisen vaatimuksen testeiksi ja tunnistaa
  kysymykset, joihin vaatimus ei vastaa.
