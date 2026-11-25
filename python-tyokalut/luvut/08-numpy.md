# NumPy mittausdatalle

Mittaus- ja simulaatiodataa on usein miljoonia näytteitä. Python-lista
ja silmukka käsittelevät ne yksi kerrallaan tulkin kautta, mikä on
hidasta. NumPyn taulukko on yhtenäinen muistialue, jossa on yhtä
tietotyyppiä, ja sen operaatiot tehdään käännetyssä koodissa koko
taulukolle kerralla. Tämä luku käsittelee sen, mitä työkalun
kirjoittaja tarvitsee. Matriisilaskenta on taidon *Lineaarialgebra*
ja signaalinkäsittely taidon *Signaalit ja järjestelmät* asia.

## Tietotyypit ja muoto

Taulukolla on muoto (`shape`) ja tietotyyppi (`dtype`). Tietotyyppi
päättää muistinkäytön ja aritmetiikan. Kokonaisluvut kiertävät
ylivuodossa hiljaa kuten C:ssä, joten raakalukemat muunnetaan
leveämpään tyyppiin ennen laskentaa:

```{.python tiedosto="esimerkit/08-taulukot.py" osa="tyypit"}
```

Taito *Miten tietokone laskee* käsittelee kahden komplementin ja
liukulukujen tarkkuuden syvemmin.

## Binääritietueet suoraan taulukoksi

Luvun 5 binäärimuodot luetaan suurina määrinä NumPyn *rakenteisella
tietotyypillä*: kentät nimetään ja tyypitetään tavujärjestyksineen,
ja `frombuffer` tulkitsee tavut taulukoksi kopioimatta:

```{.python tiedosto="esimerkit/08-tietueet.py" osa="dtype"}
```

```{.python tiedosto="esimerkit/08-tietueet.py" osa="lue"}
```

```{.tuloste tiedosto="esimerkit/08-tietueet.odotettu"}
```

`frombuffer`in tulos on vain luku -näkymä alkuperäisiin tavuihin.
Muokattava kopio tehdään `copy()`lla. Suurilla tiedostoilla
`np.memmap` kuvaa tiedoston muistiin, eikä sitä tarvitse lukea
kokonaan.

## Vektorointi ja broadcast

AD-muuntimen raakalukemat muunnetaan jännitteiksi kanavakohtaisella
kertoimella ja siirtymällä. Silmukkaa ei tarvita: lauseke koskee koko
taulukkoa. *Broadcast* venyttää pienemmän taulukon isomman muotoon.
Muoto `(3,)` kohdistuu sarakkeisiin ja muoto `(3, 1)` riveihin:

```{.python tiedosto="esimerkit/08-taulukot.py" osa="vektorointi"}
```

Sääntö: muotoja verrataan oikealta, ja ulottuvuudet sopivat, jos ne
ovat samat tai toinen on 1. Kun broadcast tuottaa yllättävän muodon,
tarkista `shape` ennen ja jälkeen.

## Maskit ja näkymät

Vertailu tuottaa totuusarvotaulukon (maskin), jolla valitaan,
lasketaan ja yhdistellään. Nousevat reunat löytyvät vertaamalla
taulukkoa itsensä siirrettyyn versioon:

```{.python tiedosto="esimerkit/08-taulukot.py" osa="maskit"}
```

Viipale on *näkymä* samaan muistiin. Kopioita ei synny, joten viipaleen
muuttaminen muuttaa alkuperäistä. Indeksilista ja maski tekevät
kopion:

```{.python tiedosto="esimerkit/08-taulukot.py" osa="nakymat"}
```

```{.tuloste tiedosto="esimerkit/08-taulukot.odotettu"}
```

## Signaalin analyysi

Tyypillinen työkalutehtävä: mittaussignaalista lasketaan tunnusluvut,
löydetään häiriöpiikit ja tarkistetaan taajuus. Testisignaali
tuotetaan toistettavasti siemenellä:

```{.python tiedosto="esimerkit/08-analyysi.py" osa="signaali"}
```

`default_rng(siemen)` on suositeltu satunnaislukugeneraattori. Sama
siemen tuottaa saman jonon, joten testit ja raportit toistuvat.
Vanha `np.random.seed` muuttaa globaalia tilaa, mikä rikkoo
rinnakkaiset testit.

```{.python tiedosto="esimerkit/08-analyysi.py" osa="analyysi"}
```

- `np.convolve` laskee liukuvan keskiarvon ilman silmukkaa.
- `sliding_window_view` tekee ikkunoista näkymän kopioimatta.
  Piikki tunnistetaan vertaamalla näytettä paikalliseen mediaaniin,
  jota yksittäinen piikki ei siirrä toisin kuin keskiarvoa.
- `np.fft.rfft` laskee reaalisignaalin spektrin, ja `rfftfreq` antaa
  sitä vastaavat taajuudet.

```{.tuloste tiedosto="esimerkit/08-analyysi.odotettu"}
```

![Esimerkin signaali, liukuva keskiarvo ja tunnistetut häiriöpiikit
sekä spektri, jonka huippu on 50 Hz:n kohdalla. Yhden jakson pituinen
liukuva keskiarvo poistaa 50 Hz:n komponentin lähes kokonaan; piikit
näkyvät siinä pieninä askelina.](kuvat/analyysi.png){width=92%}

Kuvan tuottaa `kuvat/piirra.py` samoilla funktioilla ja samalla
siemenellä. Kuvaajien piirtäminen on seuraavan luvun aihe.

## Käytännössä

- **Ei Python-silmukkaa taulukon alkioiden yli.** Jos sellainen on
  tarpeen, tehtävälle on yleensä valmis funktio (`cumsum`, `diff`,
  `where`, `searchsorted`, `bincount`).
- **Tietotyyppi tietoisesti.** Raakadata pienessä kokonaislukutyypissä,
  laskenta `float64`:ssä. `float32` puolittaa muistin mutta kuluttaa
  tarkkuutta summissa.
- **Toistettava satunnaisuus:** `default_rng(siemen)` ja generaattori
  parametrina, ei globaalia tilaa.
- **Tarkista muoto.** Väärin suunnattu broadcast tuottaa virheettömästi
  väärän tuloksen. `assert x.shape == (n, 3)` rajapinnoissa maksaa
  vähän.
- **Pandas taulukkomaiselle datalle.** Kun datassa on nimettyjä
  sarakkeita, eri tyyppejä ja ryhmittelyä, pandas tai Polars on
  NumPyä kätevämpi. Ne rakentuvat samoille taulukoille.
- **Sudenkuoppa:** `a == b` liukuluvuilla. Vertaa `np.isclose`lla tai
  `np.allclose`lla.

## Itsearviointi

- Osaat valita tietotyypin ja välttää kokonaislukujen hiljaisen
  ylivuodon.
- Osaat kirjoittaa vektoroidun laskennan broadcastilla ja ennustaa
  tuloksen muodon.
- Osaat käyttää maskeja ja erottaa näkymän kopiosta.
- Osaat lukea binääritietueet rakenteisella tietotyypillä ja
  `frombuffer`illa.
