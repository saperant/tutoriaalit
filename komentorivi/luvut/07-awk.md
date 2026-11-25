# Raportit awkilla

`awk` on pieni ohjelmointikieli kenttiin jaetun tekstin käsittelyyn.
Siinä missä `cut` ja `sort` tekevät yhden asian, awk laskee, ryhmittelee,
suodattaa ehdoilla ja muotoilee tulosteen yhdellä kertaa. Se on
komentorivin raporttityökalu: kun putkeen tarvittaisiin summia,
keskiarvoja tai ehtoja useasta kentästä, awk on yleensä oikea valinta.

## Ohjelman rakenne

Awk-ohjelma on joukko sääntöjä muotoa `ehto { toiminto }`. Jokaiselle
syötteen riville suoritetaan toiminnot niistä säännöistä, joiden ehto
on tosi. Puuttuva ehto on aina tosi, ja puuttuva toiminto tulostaa
rivin. `BEGIN` ajetaan ennen syötettä ja `END` sen jälkeen.

| Nimi | Merkitys |
|------|----------|
| `$0` | Koko rivi |
| `$1`, `$2`, …, `$NF` | Kentät, viimeinen kenttä |
| `NR`, `NF` | Rivin numero, kenttien määrä |
| `FS`, `-F,` | Kenttäerotin; oletus on välilyönnit ja sarkaimet |
| `-v nimi=arvo` | Muuttuja komentoriviltä |
| `a[k]` | Assosiatiivinen taulukko; `for (k in a)` käy avaimet läpi |
| `printf` | Muotoiltu tuloste kuten C:ssä |

Muuttujia ei esitellä: tuntematon muuttuja on tyhjä merkkijono ja
lukuna nolla. Siksi `summa[k] += $4` toimii ilman alustusta.

## Ryhmittely ja koosteet

Sovelluksen vasteaikaloki, jossa kentät ovat metodi, polku, tilakoodi
ja aika millisekunteina:

```{.bash tiedosto="esimerkit/07-vasteajat.sh" osa="aineisto"}
```

Raportti laskee jokaiselle päätepisteelle pyyntöjen määrän, keskiarvon
ja maksimin. Kolme taulukkoa samalla avaimella korvaa SQL:n
`GROUP BY`-kyselyn:

```{.bash tiedosto="esimerkit/07-vasteajat.sh" osa="awk"}
```

Ehdot voivat vertailla kenttiä lukuina. Kynnysarvo annetaan
`-v`-valitsimella. Kuoren muuttujaa ei pidä upottaa ohjelmatekstiin,
koska lainaukset menevät helposti rikki ja arvo voi muuttaa ohjelmaa:

```{.bash tiedosto="esimerkit/07-vasteajat.sh" osa="ehto"}
```

```{.tuloste tiedosto="esimerkit/07-vasteajat.odotettu"}
```

`hitaat + 0` tulostaa nollan myös silloin, kun yhtään riviä ei
löytynyt ja muuttuja on tyhjä. `for (a in n)` käy avaimet läpi
määrittelemättömässä järjestyksessä, joten tulos lajitellaan `sort`-
komennolla.

## CSV-raportti

Myyntiraportti tuoteryhmittäin: otsikkorivi ohitetaan ehdolla
`NR > 1`, ja `END`-lohkossa lasketaan osuudet, kun kokonaissumma on
tiedossa.

```{.bash tiedosto="esimerkit/07-raportti.sh" osa="aineisto"}
```

```{.bash tiedosto="esimerkit/07-raportti.sh" osa="raportti"}
```

```{.tuloste tiedosto="esimerkit/07-raportti.odotettu"}
```

Raportin rivi `kaikki` on kirjoitettu ilman ääkkösiä tarkoituksella.
Ubuntun oletus-awk (`mawk`) laskee leveydet tavuina, joten
`%-14s` jättäisi rivin `YHTEENSÄ` yhden merkin vajaaksi. GNU awk
(`gawk`) osaa UTF-8:n.

## Tila rivien välillä

Awk-muuttujat säilyvät riviltä toiselle, joten ohjelma voi muistaa,
missä kohtaa tiedostoa ollaan. INI-tiedoston osion arvon haku on
tyypillinen esimerkki: otsikkorivi asettaa tilan, ja arvorivit
tulkitaan sen mukaan. Kenttäerotin on säännöllinen lauseke
`' *= *'`, joten välilyönnit yhtäsuuruusmerkin ympärillä eivät päädy
kenttiin. Pieni kuorifunktio tekee haun uudelleenkäytettäväksi
(funktioista enemmän taidossa *Bash-skriptaus*):

```{.bash tiedosto="esimerkit/07-osiot.sh" osa="osio"}
```

```{.tuloste tiedosto="esimerkit/07-osiot.odotettu"}
```

`exit` ensimmäisessä osumassa lopettaa lukemisen. `END`-lohko ajetaan
silti, ja se asettaa paluuarvon: 1, jos avainta ei löytynyt. Näin
funktio toimii ehdoissa kuten `grep -q`.

## awk, sed vai jokin muu?

| Tehtävä | Työkalu |
|---------|---------|
| Rivien valinta hahmolla | `grep` |
| Korvaus rivin sisällä | `sed` |
| Kenttien valinta, kun erotin on yksiselitteinen | `cut` |
| Laskenta, ryhmittely, ehdot kentistä, muotoiltu raportti | `awk` |
| Liitokset ja monimutkaiset kyselyt | SQL (`sqlite3`, DuckDB) |
| JSON | `jq` |
| Logiikkaa yli 10–20 riviä | Python |

## Käytännössä

- **Yksi awk korvaa usein putken** `grep | cut | sort | uniq -c`,
  mutta lyhyt putki on usein luettavampi. Valitse lukijan mukaan.
- **Ohjelma yksinkertaisiin lainausmerkkeihin, arvot `-v`:llä.** Näin
  kuori ei koske `$1`-viittauksiin, eikä data päädy ohjelmakoodiksi.
- **Lajittele tulos** `for (k in a)`-silmukan jälkeen; järjestys ei ole
  määritelty.
- **Kirjoita siirrettävää awkia**: Ubuntussa oletus on `mawk`, jossa ei
  ole GNU-laajennuksia kuten `gensub` ja `asort`. Aikafunktiot
  (`strftime`, `systime`) ovat mawkin nykyversioissa, mutta puuttuvat
  vanhoista. Jos tarvitset laajennuksia, kutsu `gawk`-komentoa nimellä.
- **Liukuluvut**: awk laskee kaksoistarkkuudella. Rahasummat
  kannattaa laskea sentteinä tai pyöristää vasta tulostuksessa
  (`%.2f`).
- **Pitkä awk-ohjelma omaan tiedostoon** (`awk -f raportti.awk`), kun se
  kasvaa yli muutaman rivin, tai siirry Pythoniin.

## Itsearviointi

- Osaat kirjoittaa awk-ohjelman, joka ryhmittelee rivit avaimen mukaan
  ja laskee määrän, summan, keskiarvon ja maksimin.
- Osaat käyttää ehtoja, `BEGIN`- ja `END`-lohkoja ja `-v`-muuttujia
  sekä muotoilla tulosteen `printf`:llä.
- Osaat ylläpitää tilaa rivien välillä, esimerkiksi tulkita
  osioihin jaetun asetustiedoston.
- Osaat valita tehtävään sopivan työkalun: grep, sed, cut, awk, SQL
  tai Python.
