# Osoittimet {.runko-muisti}

*Osoitin* on muuttuja, jonka arvo on toisen olion muistiosoite.
Osoittimet ovat C:n keskeisin ja samalla vaarallisin ominaisuus. Niiden
avulla funktiot voivat muuttaa kutsujan muuttujia, taulukoita voi
käsitellä tehokkaasti ja dynaamisesti varattua muistia voi käyttää.

## Perusteet

Osoitintyyppi kirjoitetaan tähdellä: `int *p` on osoitin
`int`-tyyppiseen olioon. Operaattori `&` antaa olion osoitteen ja
operaattori `*` *dereferoi* osoittimen eli antaa olion, johon osoitin
osoittaa:

```{.c tiedosto="esimerkit/05-osoittimet.c" osa="perusteet"}
```

```{.dot otsikko="Osoitin `p` on oma muuttujansa, jonka arvo on muuttujan `luku` osoite. Osoitteet ovat esimerkkejä; todelliset vaihtelevat ajokerrasta toiseen."}
digraph {
  rankdir=LR; nodesep=0.4; ranksep=0.9;
  node [shape=plain, style=""];
  p [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left"><i>int *p</i></td></tr>
    <tr><td port="v" bgcolor="#EEF1F6" width="110">0x7ffc1000</td></tr>
    <tr><td border="0" align="left"><font point-size="8">osoite 0x7ffc1008</font></td></tr></table>>];
  x [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left"><i>int luku</i></td></tr>
    <tr><td port="v" bgcolor="#EEF1F6" width="110">42</td></tr>
    <tr><td border="0" align="left"><font point-size="8">osoite 0x7ffc1000</font></td></tr></table>>];
  p:v:e -> x:v:w [label="  *p  "];
}
```

Sijoitus `*p = 7` kirjoittaa siis nuolen päässä olevaan laatikkoon,
kun taas `p = &toinen` kääntäisi nuolen osoittamaan toiseen muuttujaan.

*Tyhjä osoitin* ei osoita mihinkään olioon. C23:ssa se kirjoitetaan
`nullptr`; vanhemmassa koodissa käytetään makroa `NULL`. Tyhjän
osoittimen dereferointi on määrittelemätöntä käyttäytymistä, ja
käytännössä ohjelma yleensä kaatuu. Samoin on alustamattoman
osoittimen ja jo tuhoutuneeseen olioon osoittavan osoittimen laita.

## Osoittimet parametreina

Koska C välittää argumentit arvoina, funktio voi muuttaa kutsujan
muuttujaa vain, jos se saa muuttujan osoitteen. Edellisen luvun
toimimaton `vaihda`-funktio korjautuu näin:

```{.c tiedosto="esimerkit/05-osoittimet.c" osa="vaihda"}
```

Samaa tekniikkaa käytetään, kun funktion on palautettava useampi arvo.
Paluuarvo kertoo tällöin usein onnistumisesta ja varsinaiset tulokset
kirjoitetaan *tulosparametreihin*:

```{.c tiedosto="esimerkit/05-osoittimet.c" osa="jako"}
```

```{.c tiedosto="esimerkit/05-osoittimet.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/05-osoittimet.odotettu"}
```

## Olion elinaika

Osoitin on käyttökelpoinen vain niin kauan kuin olio, johon se
osoittaa, on olemassa. C-ohjelman oliot sijaitsevat kolmenlaisessa
muistissa, ja muistialue määrää olion elinajan:

- **Staattinen muisti**: globaalit ja `static`-muuttujat sekä
  merkkijonoliteraalit. Ne ovat olemassa koko ohjelman ajan.
- **Pino** (*stack*): funktioiden paikalliset muuttujat ja parametrit.
  Ne luodaan funktioon tultaessa ja tuhotaan siitä poistuttaessa.
  Pinon koko on rajallinen, tyypillisesti muutamia megatavuja.
- **Keko** (*heap*): dynaamisesti varattu muisti. Ohjelma varaa sen
  ajon aikana ja vapauttaa sen itse (luku 8).

Funktio ei siksi saa palauttaa osoitinta paikalliseen muuttujaansa:
muuttuja tuhoutuu funktion palatessa, ja osoitin jää osoittamaan
pinon kohtaan, jonka seuraava funktiokutsu ottaa käyttöön. Kääntäjä
huomaa yksinkertaisimmat tapaukset:

```{.c tiedosto="esimerkit/05-elinaika.ei-kaanny.c"}
```

Toiseen suuntaan osoittimen välittäminen on turvallista: kutsujan
muuttuja on olemassa koko kutsun ajan, joten edellä `vaihda(&a, &b)` ja
tulosparametrit toimivat. Jos datan on elettävä sen luonutta funktiota
pidempään, se on joko staattista, kutsujan antamassa muistissa tai
varattu keosta.

## Osoitinaritmetiikka

Osoittimeen voi lisätä kokonaisluvun. Lisäys tehdään alkioina, ei
tavuina: jos `p` osoittaa `int`-taulukon alkioon, `p + 1` osoittaa
seuraavaan `int`-alkioon. Lauseke `p[i]` tarkoittaa täsmälleen samaa
kuin `*(p + i)`. Kahden saman taulukon alkioon osoittavan osoittimen
erotus on niiden välisten alkioiden määrä, tyyppiä `ptrdiff_t`.

Taulukon nimi muuntuu useimmissa lausekkeissa osoittimeksi taulukon
ensimmäiseen alkioon. Taulukon voi siksi käydä läpi osoittimella:

```{.c tiedosto="esimerkit/05-aritmetiikka.c" osa="aritmetiikka"}
```

```{.dot otsikko="Osoitinaritmetiikka lasketaan alkioina: `p + 2` on kahden `int`-alkion eli kahdeksan tavun päässä. `t + 5` osoittaa viimeisen alkion ohi; sitä saa verrata mutta ei dereferoida."}
digraph {
  rankdir=TB; nodesep=0.15; ranksep=0.35;
  node [shape=plain, style=""];
  t [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0"><font point-size="8">t[0]<br/>+0</font></td><td border="0"><font point-size="8">t[1]<br/>+4</font></td><td border="0"><font point-size="8">t[2]<br/>+8</font></td><td border="0"><font point-size="8">t[3]<br/>+12</font></td><td border="0"><font point-size="8">t[4]<br/>+16</font></td><td border="0"><font point-size="8"> <br/>+20 tavua</font></td></tr>
    <tr><td port="c0" bgcolor="#EEF1F6" width="48">10</td><td port="c1" bgcolor="#EEF1F6" width="48">20</td><td port="c2" bgcolor="#EEF1F6" width="48">30</td><td port="c3" bgcolor="#EEF1F6" width="48">40</td><td port="c4" bgcolor="#EEF1F6" width="48">50</td><td port="c5" width="48" style="dashed"><font point-size="8">ei alkiota</font></td></tr></table>>];
  p [label="p = t"]; p2 [label="p + 2"]; loppu [label="loppu = t + 5"];
  t:c0:s -> p [dir=back]; t:c2:s -> p2 [dir=back];
  t:c5:s -> loppu [dir=back, style=dashed];
}
```

Osoittimen saa siirtää taulukon viimeisen alkion *ohi* yhden alkion
verran (`t + 5`), mutta sitä ei saa dereferoida. Kauemmas siirtäminen
on määrittelemätöntä käyttäytymistä, vaikka osoitinta ei käytettäisi.

Taulukko ja osoitin eivät kuitenkaan ole sama asia. `sizeof` antaa
taulukolle koko taulukon koon, osoittimelle vain osoittimen koon:

```{.c tiedosto="esimerkit/05-aritmetiikka.c" osa="koko"}
```

```{.tuloste tiedosto="esimerkit/05-aritmetiikka.odotettu"}
```

## `const` ja osoittimet

`const` voi koskea joko osoitettua dataa tai osoitinta itseään sen
mukaan, kummalle puolelle tähteä se kirjoitetaan:

| Esittely | Datan muutos | Osoittimen siirto |
|----------|--------------|-------------------|
| `int *p` | sallittu | sallittu |
| `const int *p` | kielletty | sallittu |
| `int *const p` | sallittu | kielletty |
| `const int *const p` | kielletty | kielletty |

Funktion parametri `const int *t` on lupaus kutsujalle: funktio lukee
dataa mutta ei muuta sitä. Kääntäjä valvoo lupausta:

```{.c tiedosto="esimerkit/05-const.ei-kaanny.c"}
```

Osoitinparametrit kannattaa merkitä `const`-määreellä aina, kun funktio
ei muuta dataa. Se dokumentoi rajapintaa ja estää vahinkoja.

## `void *` ja funktio-osoittimet

`void *` on yleinen osoitin, joka voi osoittaa mihin tahansa
datatyyppiin. Sitä ei voi dereferoida suoraan, vaan se muunnetaan ensin
oikeaksi osoitintyypiksi. C:ssä muunnos `void *`-tyypistä muihin
osoitintyyppeihin tapahtuu automaattisesti.

Osoitin voi osoittaa myös funktioon. Funktio-osoittimen tyypissä
näkyvät paluuarvo ja parametrit: `int (*f)(int, int)` on osoitin
funktioon, joka ottaa kaksi `int`-arvoa ja palauttaa `int`:n. Funktion
nimi muuntuu automaattisesti osoittimeksi, ja osoittimen kautta
funktiota kutsutaan kuten tavallista funktiota.

```{.c tiedosto="esimerkit/05-funktio-osoittimet.c" osa="laskin"}
```

Funktio-osoittimet ja `void *` yhdessä mahdollistavat yleiskäyttöiset
funktiot. Standardikirjaston `qsort` järjestää minkä tahansa taulukon,
kun sille annetaan alkion koko ja vertailufunktio. Vertailufunktio
saa alkioiden osoitteet `void *`-tyyppisinä ja palauttaa negatiivisen
luvun, nollan tai positiivisen luvun:

```{.c tiedosto="esimerkit/05-funktio-osoittimet.c" osa="vertailu"}
```

```{.c tiedosto="esimerkit/05-funktio-osoittimet.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/05-funktio-osoittimet.odotettu"}
```

Merkkijonotaulukon alkiot ovat osoittimia, joten vertailufunktio saa
osoittimia osoittimiin (`const char *const *`). Lauseke
`sizeof t / sizeof t[0]` laskee taulukon alkioiden määrän; se toimii
vain todelliselle taulukolle, ei osoittimelle.

## Käytännössä

- **`const`-oikeellisuus alusta asti.** Jokainen osoitinparametri on
  `const`, ellei funktio muuta dataa. `const` leviää: jos sitä ei käytetä
  alusta asti, sen lisääminen myöhemmin vaatii muutoksia koko koodiin.
- **Osoitin ei saa elää kohdettaan pidempään.** Funktio ei palauta
  eikä tallenna osoitinta paikalliseen muuttujaansa. Rajapinnan
  kuvaukseen kirjoitetaan, kuinka kauan funktiolle annetun tai sen
  palauttaman osoittimen on oltava voimassa.
- **Tulosparametri ja paluuarvo.** Funktio palauttaa onnistumisen
  (`bool` tai virhekoodi) ja kirjoittaa tuloksen tulosparametriin vain
  onnistuessaan. Kutsuja ei näin koskaan saa puolivalmista tulosta.
- **Tyhjät osoittimet rajapinnan reunalla.** Julkinen funktio tarkistaa
  `nullptr`-argumentit tai dokumentoi esiehdon ja tarkistaa sen
  `assert`-makrolla (luku 11). Sisäiset apufunktiot eivät toista
  tarkistusta jokaisella tasolla.
- **Takaisinkutsuun kuuluu kontekstiosoitin.** Hyvin suunniteltu
  takaisinkutsu on muotoa `void (*f)(void *konteksti, ...)`, ja kutsuja
  antaa kontekstin mukaan. Standardin `qsort` ei anna kontekstia, mikä
  houkuttelee globaaleihin muuttujiin; omat rajapinnat kannattaa
  suunnitella toisin.
- **Vertailufunktio ilman ylivuotoa:** `(x > y) - (x < y)`, ei `x - y`.

## Itsearviointi

- Osaat kirjoittaa funktion, joka palauttaa tuloksen tulosparametrin
  kautta ja kertoo onnistumisen paluuarvolla.
- Osaat lukea `const`-määreiset osoitintyypit ja selittää, mikä niissä on
  vakio.
- Osaat käydä taulukon läpi osoitinaritmetiikalla rajoja ylittämättä.
- Osaat kertoa, missä muistialueessa olio sijaitsee ja kuinka kauan
  siihen osoittava osoitin on käyttökelpoinen.
- Osaat välittää funktio-osoittimen takaisinkutsuna ja perustella, miksi
  takaisinkutsulle annetaan kontekstiosoitin.
