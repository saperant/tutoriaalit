# Osoittimet

*Osoitin* on muuttuja, jonka arvo on toisen olion muistiosoite.
Osoittimet ovat C:n keskeisin ja samalla vaarallisin ominaisuus. Niiden
avulla funktiot voivat muuttaa kutsujan muuttujia, taulukoita voi
käsitellä tehokkaasti ja dynaamisesti varattua muistia voi käyttää.

## Perusteet

Osoitintyyppi kirjoitetaan tähdellä: `int *p` on osoitin
`int`-tyyppiseen olioon. Operaattori `&` antaa olion osoitteen ja
operaattori `*` *dereferoi* osoittimen eli antaa olion, johon osoitin
osoittaa:

```{.c tiedosto="esimerkit/04-osoittimet.c" osa="perusteet"}
```

*Tyhjä osoitin* ei osoita mihinkään olioon. C23:ssa se kirjoitetaan
`nullptr`; vanhemmassa koodissa käytetään makroa `NULL`. Tyhjän
osoittimen dereferointi on määrittelemätöntä käyttäytymistä, ja
käytännössä ohjelma yleensä kaatuu. Samoin on alustamattoman
osoittimen ja jo tuhoutuneeseen olioon osoittavan osoittimen laita.

## Osoittimet parametreina

Koska C välittää argumentit arvoina, funktio voi muuttaa kutsujan
muuttujaa vain, jos se saa muuttujan osoitteen. Edellisen luvun
toimimaton `vaihda`-funktio korjautuu näin:

```{.c tiedosto="esimerkit/04-osoittimet.c" osa="vaihda"}
```

Samaa tekniikkaa käytetään, kun funktion on palautettava useampi arvo.
Paluuarvo kertoo tällöin usein onnistumisesta ja varsinaiset tulokset
kirjoitetaan *tulosparametreihin*:

```{.c tiedosto="esimerkit/04-osoittimet.c" osa="jako"}
```

```{.c tiedosto="esimerkit/04-osoittimet.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/04-osoittimet.odotettu"}
```

## Osoitinaritmetiikka

Osoittimeen voi lisätä kokonaisluvun. Lisäys tehdään alkioina, ei
tavuina: jos `p` osoittaa `int`-taulukon alkioon, `p + 1` osoittaa
seuraavaan `int`-alkioon. Lauseke `p[i]` tarkoittaa täsmälleen samaa
kuin `*(p + i)`. Kahden saman taulukon alkioon osoittavan osoittimen
erotus on niiden välisten alkioiden määrä, tyyppiä `ptrdiff_t`.

Taulukon nimi muuntuu useimmissa lausekkeissa osoittimeksi taulukon
ensimmäiseen alkioon. Taulukon voi siksi käydä läpi osoittimella:

```{.c tiedosto="esimerkit/04-aritmetiikka.c" osa="aritmetiikka"}
```

Osoittimen saa siirtää taulukon viimeisen alkion *ohi* yhden alkion
verran (`t + 5`), mutta sitä ei saa dereferoida. Kauemmas siirtäminen
on määrittelemätöntä käyttäytymistä, vaikka osoitinta ei käytettäisi.

Taulukko ja osoitin eivät kuitenkaan ole sama asia. `sizeof` antaa
taulukolle koko taulukon koon, osoittimelle vain osoittimen koon:

```{.c tiedosto="esimerkit/04-aritmetiikka.c" osa="koko"}
```

```{.tuloste tiedosto="esimerkit/04-aritmetiikka.odotettu"}
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

```{.c tiedosto="esimerkit/04-const.ei-kaanny.c"}
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

```{.c tiedosto="esimerkit/04-funktio-osoittimet.c" osa="laskin"}
```

Funktio-osoittimet ja `void *` yhdessä mahdollistavat yleiskäyttöiset
funktiot. Standardikirjaston `qsort` järjestää minkä tahansa taulukon,
kun sille annetaan alkion koko ja vertailufunktio. Vertailufunktio
saa alkioiden osoitteet `void *`-tyyppisinä ja palauttaa negatiivisen
luvun, nollan tai positiivisen luvun:

```{.c tiedosto="esimerkit/04-funktio-osoittimet.c" osa="vertailu"}
```

```{.c tiedosto="esimerkit/04-funktio-osoittimet.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/04-funktio-osoittimet.odotettu"}
```

Merkkijonotaulukon alkiot ovat osoittimia, joten vertailufunktio saa
osoittimia osoittimiin (`const char *const *`). Lauseke
`sizeof t / sizeof t[0]` laskee taulukon alkioiden määrän; se toimii
vain todelliselle taulukolle, ei osoittimelle.
