# Merkkijonot ja tiedostot

Suuri osa ohjelmoinnista on tekstin käsittelyä: nimiä, osoitteita,
lokitiedostoja ja CSV-tiedostoja. Tässä luvussa käsitellään
merkkijonojen tärkeimmät operaatiot ja tiedostojen lukeminen ja
kirjoittaminen.

## Merkkijonot

Merkkijono on muuttumaton jono merkkejä. Siihen pätevät samat
indeksit ja viipaleet kuin listaan, mutta metodit palauttavat aina
uuden merkkijonon eivätkä muuta alkuperäistä.

```{.python tiedosto="esimerkit/06-tunnus.py"}
```

```{.tuloste tiedosto="esimerkit/06-tunnus.odotettu"}
```

| Metodi | Tulos |
|--------|-------|
| `s.strip()` | poistaa välilyönnit ja rivinvaihdot alusta ja lopusta |
| `s.lower()`, `s.upper()`, `s.title()` | kirjainkoko |
| `s.split()`, `s.split(";")` | pilkkoo listaksi välilyönneistä tai erottimesta |
| `";".join(lista)` | yhdistää listan merkkijonot erottimella |
| `s.replace(a, b)` | korvaa kaikki osajonot `a` osajonolla `b` |
| `s.startswith(a)`, `s.endswith(a)` | alkaako tai päättyykö |
| `a in s`, `s.find(a)` | sisältyykö, missä kohdassa (`-1`: ei löydy) |
| `s.partition(a)` | jakaa kolmeen osaan ensimmäisen `a`:n kohdalta |
| `s.isdigit()`, `s.isalpha()` | koostuuko numeroista, kirjaimista |

`str.maketrans` ja `translate` korvaavat monta merkkiä kerralla.
Funktion `kayttajatunnus` dokumentaatiomerkkijono on konkreettinen
syöte ja tulos. Esimerkki kertoo funktion toiminnan nopeammin kuin
sanallinen kuvaus.

Esimerkki tekee myös oletuksen, joka kannattaa huomata: nimessä on
vähintään yksi osa. Tyhjällä nimellä `osat[0]` aiheuttaisi virheen.
Ammattilainen kirjaa tällaiset oletukset ja päättää, tarkistetaanko ne
(luku *Virheet ja poikkeukset*).

## Tiedostojen lukeminen ja kirjoittaminen

Tiedosto avataan funktiolla `open` `with`-lauseessa. `with` sulkee
tiedoston automaattisesti lohkon lopussa, myös virhetilanteessa, joten
tiedostoa ei voi unohtaa auki.

```{.python tiedosto="esimerkit/06-muistio.py"}
```

```{.tuloste tiedosto="esimerkit/06-muistio.odotettu"}
```

- Tila `"w"` (*write*) luo tiedoston tai tyhjentää olemassa olevan,
  `"a"` (*append*) lisää loppuun ja oletustila `"r"` lukee.
- `encoding="utf-8"` määrää merkistökoodauksen. Ilman sitä Python
  käyttää käyttöjärjestelmän oletusta, joka voi Windowsissa olla eri
  kuin Linuxissa, ja ääkköset rikkoutuvat.
- Tiedostoa voi lukea rivi kerrallaan `for`-silmukalla. Rivin lopussa
  on rivinvaihto, jonka `rstrip()` poistaa.
- `enumerate(tiedosto, start=1)` antaa jokaisen rivin lisäksi sen
  järjestysnumeron.
- `print(..., file=tiedosto)` tulostaa tiedostoon.

Tiedoston koko on 50 tavua, vaikka tekstissä on 47 merkkiä: UTF-8 tallentaa
ääkköset kahtena tavuna.

Standardikirjaston `pathlib.Path` edustaa tiedostopolkua. Sillä voi
lukea pienen tiedoston kerralla (`read_text`), yhdistää polkuja
(`Path("data") / "kulut.csv"`) ja kysyä tiedoston tietoja (`exists()`,
`stat()`).

## CSV-tiedostot

CSV (*comma-separated values*) on yleisin taulukkomuotoisen datan
siirtomuoto. Suomalaisissa ohjelmissa erottimena on usein puolipiste,
koska pilkku on desimaalierotin. Standardikirjaston `csv`-moduli
jäsentää CSV:n oikein, myös lainausmerkeissä olevat erottimet:

```{.python tiedosto="esimerkit/06-saa.py"}
```

Syöte ja tuloste:

```{.tuloste tiedosto="esimerkit/06-saa.syote"}
```

```{.tuloste tiedosto="esimerkit/06-saa.odotettu"}
```

`csv.DictReader` lukee otsikkorivin ja palauttaa jokaisen rivin
sanakirjana, jonka avaimet ovat sarakkeiden nimet. Koodi viittaa
sarakkeeseen nimellä (`rivi["lampotila"]`), joten se toimii, vaikka
sarakkeiden järjestys muuttuisi.

Ohjelma kaatuu, jos jokin lämpötila puuttuu tai on virheellinen, tai
jos syötteessä ei ole yhtään havaintoa (nollalla jakaminen). Seuraava
luku korjaa tämän.

## Käytännössä

- **`with open(...)` ja `encoding="utf-8"` aina.** Molemmat
  ehkäisevät virheitä, jotka näkyvät vasta toisella koneella tai
  kuormituksessa.
- **Älä jäsennä CSV:tä `split(",")`-kutsulla.** Ensimmäinen
  lainausmerkeissä oleva pilkku rikkoo sen. Käytä `csv`-modulia, ja
  JSONille `json`-modulia.
- **Viittaa sarakkeisiin nimellä, ei indeksillä.** `rivi["pvm"]` on
  luettavampi ja kestää sarakkeiden lisäämisen.
- **Normalisoi syöte heti luettaessa.** Poista välilyönnit, yhtenäistä
  kirjainkoko ja desimaalierotin ennen kuin data kulkee ohjelmassa
  eteenpäin. Muun koodin ei tarvitse silloin varautua eri muotoihin.
- **Kokoa teksti f-merkkijonolla tai `join`-metodilla**, ei
  `+`-operaattorilla silmukassa.
- **Polut `pathlib`-modulilla**, ei merkkijonoja yhdistelemällä, jotta
  koodi toimii sekä Windowsissa että Linuxissa.

## Itsearviointi

- Osaat siistiä ja pilkkoa merkkijonon ja koota merkkijonon osista.
- Osaat lukea ja kirjoittaa tekstitiedoston oikealla
  merkistökoodauksella `with`-lauseessa.
- Osaat lukea CSV-tiedoston `csv.DictReader`illa ja laskea siitä
  yhteenvedon.
- Osaat kertoa, millä syötteillä oma ohjelmasi kaatuu.
