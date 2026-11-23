# Ohjausrakenteet ja funktiot {.runko-ohjaus}

Go:ssa on kolme ohjausrakennetta: `if`, `for` ja `switch`, sekä
`select` kanaville (luku 10) ja `defer` siivoukseen. Sulkuja ehdon
ympärillä ei kirjoiteta, ja aaltosulut ovat pakollisia.

## if ja switch

`if` voi alkaa alustuslauseella, jonka muuttujat näkyvät vain ehdossa ja
sen haaroissa. Tämä on yleisin tapa käsitellä funktion palauttama
lisätieto tai virhe:

```{.go tiedosto="esimerkit/04-ohjaus.go" osa="if"}
```

`switch` ei valu seuraavaan haaraan (`fallthrough` on erikseen
kirjoitettava ja harvinainen). Haarassa voi olla useita arvoja, ja
ehdoton `switch` korvaa `if`–`else if`-ketjun:

```{.go tiedosto="esimerkit/04-ohjaus.go" osa="switch"}
```

## for

`for` on Go:n ainoa silmukka. Sillä on kolme muotoa: C:n kolmiosainen
silmukka, pelkkä ehto (kuten `while`) ja ehdoton ikuinen silmukka.
`range` käy läpi viipaleen, merkkijonon, kartan, kanavan,
kokonaisluvun (1.22) tai iteraattorifunktion (1.23, luku 6).

```{.go tiedosto="esimerkit/04-ohjaus.go" osa="for"}
```

Nimetty `break` tai `continue` kohdistuu ulompaan silmukkaan ilman
lippumuuttujaa. `goto` on olemassa, mutta sitä ei käytetä.

## Funktiot

Funktiolla voi olla monta paluuarvoa. Nimetyt paluuarvot ovat
dokumentaatiota ja tavallisia muuttujia, jotka alustetaan nolla-arvoon.
Variadinen parametri `...T` on funktion sisällä viipale:

```{.go tiedosto="esimerkit/04-ohjaus.go" osa="funktiot"}
```

```{.tuloste tiedosto="esimerkit/04-ohjaus.odotettu"}
```

Parametrit välitetään aina arvona. Arvo voi olla osoitin, viipale tai
kartta, jolloin kutsuttu funktio pääsee käsiksi samaan dataan (luku 5).
Ylikuormitusta ja oletusparametreja ei ole; niiden sijaan käytetään eri
nimisiä funktioita, asetusrakennetta tai funktionaalisia optioita
(luku 7).

## defer

`defer` lykkää kutsun funktion loppuun. Lykätyt kutsut suoritetaan
käänteisessä järjestyksessä, myös paniikin sattuessa. Argumentit
lasketaan heti `defer`-lauseessa, ei vasta suoritushetkellä:

```{.go tiedosto="esimerkit/04-defer.go" osa="jarjestys"}
```

`defer` on Go:n tapa vapauttaa resurssit: tiedosto suljetaan ja lukko
vapautetaan heti avaamisen jälkeen kirjoitetulla rivillä, joten
yksikään paluupolku ei unohda sitä. Kirjoitettavan tiedoston
`Close` voi kuitenkin epäonnistua, koska käyttöjärjestelmä voi kirjoittaa
puskurin levylle vasta sulkiessa. Virhe otetaan talteen nimettyyn
paluuarvoon:

```{.go tiedosto="esimerkit/04-defer.go" osa="tallenna"}
```

```{.tuloste tiedosto="esimerkit/04-defer.odotettu"}
```

`errors.Join` yhdistää kirjoitus- ja sulkemisvirheen; se palauttaa
`nil`, jos molemmat ovat `nil`. Lukemista varten avatun tiedoston
`defer f.Close()` riittää sellaisenaan.

## Funktiot arvoina ja sulkeumat

Funktiot ovat arvoja, ja funktioliteraali sulkee sisäänsä ympäröivät
muuttujat (*sulkeuma*). Pieni strategia ilmaistaan funktiotyyppinä eikä
rajapintana:

```{.go tiedosto="esimerkit/04-sulkeumat.go" osa="tyyppi"}
```

```{.go tiedosto="esimerkit/04-sulkeumat.go" osa="laskuri"}
```

Go 1.22 muutti silmukkamuuttujan merkityksen: jokaisella kierroksella on
oma muuttujansa. Aiemmin kaikki sulkeumat ja goroutinet jakoivat saman
muuttujan ja näkivät sen viimeisen arvon, mikä oli Go:n tunnetuin
sudenkuoppa. Vanhassa koodissa näkyy siksi korjausrivi `nimi := nimi`.

```{.go tiedosto="esimerkit/04-sulkeumat.go" osa="silmukka"}
```

```{.tuloste tiedosto="esimerkit/04-sulkeumat.odotettu"}
```

## Esimerkki: tilakone

Tilakone jäsentää lainausmerkkejä sisältävän CSV-rivin. Tila on
luetellun tyypin arvo, ja `switch` valitsee käsittelyn tilan ja merkin
mukaan. `range` merkkijonon yli antaa Unicode-merkit (`rune`), joten
monitavuiset merkit käsitellään oikein.

```{.go tiedosto="esimerkit/04-tilakone.go"}
```

```{.tuloste tiedosto="esimerkit/04-tilakone.odotettu"}
```

Oikeassa ohjelmassa käytetään `encoding/csv`-pakettia. Tilakonemalli on
kuitenkin yleinen protokollien ja tiedostomuotojen jäsentimissä.

## Käytännössä

- **Varhainen paluu.** Virhetapaus käsitellään heti ja palataan;
  onnistunut polku jatkuu vasemmassa reunassa ilman `else`-haaraa.
  Go-koodi luetaan ylhäältä alas: sisennys tarkoittaa poikkeustilannetta.
- **`if err := f(); err != nil`** rajaa virhemuuttujan näkyvyyden
  ehtoon. Jos arvoa tarvitaan myöhemmin, esittele se ennen `if`-lausetta.
- **`defer` heti resurssin saamisen jälkeen**, ei funktion lopussa.
  Tämä on Go:n vastine RAII:lle ja `with`-lauseelle.
- **Ei `defer`-kutsuja pitkässä silmukassa.** Ne ajetaan vasta
  funktion lopussa, joten tiedostokahvat kertyvät. Siirrä silmukan runko
  omaan funktioonsa.
- **Pienet funktiot, vähän parametreja.** Jos parametreja on yli neljä
  tai viisi, kokoa ne rakenteeseen. Sama tyyppi peräkkäin
  (`func f(a, b, c string)`) johtaa helposti väärään järjestykseen.
- **Nimetyt paluuarvot vain dokumentaatioksi tai `defer`-käsittelyyn.**
  Paljas `return` pitkässä funktiossa heikentää luettavuutta.
- **Hinta.** Funktiokutsu on halpa, ja kääntäjä laajentaa pienet
  funktiot inline-koodiksi. Sulkeuma, joka pakenee funktiosta, varaa
  kaapatut muuttujat keosta.

## Itsearviointi

- Osaat käyttää `if`- ja `switch`-lauseiden alustuslausetta ja
  ehdotonta `switch`-lausetta.
- Osaat kirjoittaa `for`-silmukan eri muodot ja käyttää nimettyä
  `break`-lausetta.
- Osaat käyttää `defer`-lausetta resurssin vapauttamiseen ja ottaa
  sulkemisvirheen talteen nimettyyn paluuarvoon.
- Osaat kertoa, milloin `defer`-kutsun argumentit lasketaan ja missä
  järjestyksessä kutsut suoritetaan.
- Osaat käyttää funktioita arvoina ja sulkeumina ja kertoa, mitä Go
  1.22 muutti silmukkamuuttujissa.
