# Tekstinkäsittelyn työkalut

Unixin tekstityökalut tekevät kukin yhden asian riveille: valitsevat,
leikkaavat, lajittelevat, laskevat tai muuntavat. Yhdessä niistä
syntyy raportteja ja muunnoksia, joihin muuten kirjoitettaisiin
ohjelma. Työkalut olettavat rivipohjaista tekstiä, jossa kentät
erotetaan välilyönnillä, sarkaimella tai pilkulla.

| Komento | Tehtävä |
|---------|---------|
| `head -n N`, `tail -n N` | Ensimmäiset tai viimeiset N riviä |
| `tail -n +2` | Kaikki paitsi ensimmäinen rivi (otsikko pois) |
| `tail -f loki` | Seuraa kasvavaa tiedostoa |
| `wc -l`, `wc -c` | Rivien, tavujen määrä |
| `cut -d, -f2,3` | Kentät erottimen mukaan |
| `sort`, `sort -n`, `sort -h` | Lajittelu: teksti, luku, `2K`-muoto |
| `sort -t, -k3,3nr` | Kentän 3 mukaan numeerisesti laskevasti |
| `sort -u`, `uniq`, `uniq -c` | Duplikaatit pois, toistojen laskenta |
| `tr 'a-z' 'A-Z'`, `tr -d '\r'` | Merkkien vaihto ja poisto |
| `paste -sd,` | Rivit yhdeksi riviksi erottimella |
| `join -t,` | Kahden lajitellun tiedoston liitos avaimella |
| `sed 's/a/b/'` | Muokkaus rivi kerrallaan |

## Laskeminen ja lajittelu

Pääsyloki on yleinen aineisto: jokainen HTTP-pyyntö on rivi, jossa on
asiakkaan osoite, aika, pyyntö, tilakoodi ja koko.

```{.bash tiedosto="esimerkit/06-yleisimmat.sh" osa="aineisto"}
```

`cut -d' '` jakaa rivin välilyönneistä. Osoite on kenttä 1, polku
kenttä 7 ja tilakoodi kenttä 9:

```{.bash tiedosto="esimerkit/06-yleisimmat.sh" osa="asiakkaat"}
```

```{.bash tiedosto="esimerkit/06-yleisimmat.sh" osa="tilakoodit"}
```

```{.bash tiedosto="esimerkit/06-yleisimmat.sh" osa="virhepolut"}
```

```{.tuloste tiedosto="esimerkit/06-yleisimmat.odotettu"}
```

`uniq` poistaa vain *peräkkäiset* toistot, joten sitä edeltää aina
`sort`. Toinen `sort` järjestää määrän mukaan: `-k1,1nr` lajittelee
kentän 1 numeerisesti laskevaan järjestykseen ja `-k2` ratkaisee tasapelit
nimen mukaan. Ilman tasapelisääntöä samanarvoisten rivien järjestys voi
vaihdella, mikä tekee raporteista ja testeistä epävakaita.

`-k1,1` rajaa avaimen kenttään 1. Pelkkä `-k1` tarkoittaisi kenttää 1
rivin loppuun asti, mikä on tavallinen virhe.

## sed

`sed` (*stream editor*) lukee rivin kerrallaan ja muokkaa sitä
komentojen mukaan. Tavallisin komento on korvaus `s/hahmo/korvaus/`,
jonka lopussa `g` korvaa kaikki rivin osumat. Ennen komentoa voi olla
*osoite*, joka rajaa rivit: numero (`3`), väli (`3,5`), hahmo (`/^#/`)
tai GNU:n askel (`2~3` joka kolmas rivi alkaen toisesta). `d` poistaa
rivin ja `p` tulostaa sen. `-n` estää muiden rivien tulostuksen.

Asetustiedostosta näkee nopeasti voimassa olevat arvot, kun kommentit ja
tyhjät rivit poistetaan:

```{.bash tiedosto="esimerkit/06-sed.sh" osa="kommentit"}
```

`-i` muokkaa tiedostoa paikallaan. Pääte `-i.bak` säilyttää
alkuperäisen, ja `diff` näyttää muutoksen:

```{.bash tiedosto="esimerkit/06-sed.sh" osa="paikallaan"}
```

`-E` ottaa käyttöön laajennetut lausekkeet, joissa ryhmät `( )`
viitataan korvauksessa `\1`, `\2` ja niin edelleen. Esimerkki muuntaa
suomalaisen päivämäärän ISO-muotoon. Huomaa, että tulos ei ole täysin
oikein: kuukautta ja päivää ei täydennetä nollalla. Tällaiseen
tarvitaan `awk` tai `date`:

```{.bash tiedosto="esimerkit/06-sed.sh" osa="ryhmat"}
```

```{.bash tiedosto="esimerkit/06-sed.sh" osa="osoitteet"}
```

```{.tuloste tiedosto="esimerkit/06-sed.odotettu"}
```

Jos hahmossa tai korvauksessa on kauttaviivoja, erottimeksi käy mikä
tahansa merkki: `sed 's|/usr/local|/opt|'`.

## CSV ja liitokset

Yksinkertainen CSV, jonka kentissä ei ole lainattuja pilkkuja, onnistuu
perustyökaluilla. Esimerkissä on asiakkaat ja tilaukset kahdessa
tiedostossa:

```{.bash tiedosto="esimerkit/06-csv.sh" osa="aineisto"}
```

Otsikkorivi ohitetaan `tail -n +2`:lla. `sort -t,` määrää erottimen:

```{.bash tiedosto="esimerkit/06-csv.sh" osa="lajittelu"}
```

`join` liittää kaksi tiedostoa yhteisen avaimen mukaan, samoin kuin
SQL:n liitos. Molempien syötteiden on oltava lajiteltuja avaimen
mukaan. `-1 1 -2 2` kertoo avainkentät ja `-o` tulostettavat kentät
muodossa *tiedosto.kenttä*:

```{.bash tiedosto="esimerkit/06-csv.sh" osa="join"}
```

```{.bash tiedosto="esimerkit/06-csv.sh" osa="cut"}
```

```{.tuloste tiedosto="esimerkit/06-csv.odotettu"}
```

Kun liitoksia tai ryhmittelyjä tarvitaan enemmän, siirry SQL:ään.
Esimerkiksi `sqlite3` tai DuckDB lukee CSV-tiedoston suoraan
tauluksi (taito *SQL ja relaatiotietokannat*).

## Rivinvaihdot ja näkymättömät merkit

Windowsissa luodun tiedoston rivit päättyvät merkkeihin CR LF. Linuxin
työkaluille CR on rivin viimeinen merkki, joten `^kaisa$` ei osu, ja
skripti antaa virheen `$'\r': command not found`. `cat -A` näyttää
näkymättömät merkit (`^M` on CR, `$` rivin loppu, `^I` sarkain):

```{.bash tiedosto="esimerkit/06-rivinvaihdot.sh" osa="nakyviin"}
```

```{.bash tiedosto="esimerkit/06-rivinvaihdot.sh" osa="korjaus"}
```

```{.tuloste tiedosto="esimerkit/06-rivinvaihdot.odotettu"}
```

Muita näkymättömiä ongelmia ovat UTF-8:n tavujärjestysmerkki tiedoston
alussa ja sarkaimen ja välilyöntien sekoittuminen. `cat -A` ja
`od -c | head` paljastavat ne.

## Koostaminen: putken rakentaminen

Kaikki edellä yhdistyy, kun kysymys on uusi: mitä funktioita
lähdekoodissa kutsutaan eniten? Putki rakennetaan vaiheittain: poimi
nimet, siivoa, suodata avainsanat, laske, järjestä.

```{.bash tiedosto="esimerkit/06-tunnisteet.sh" osa="tunnisteet"}
```

```{.tuloste tiedosto="esimerkit/06-tunnisteet.odotettu"}
```

`grep -vxE` poistaa rivit, jotka ovat kokonaan jokin luetelluista
avainsanoista. Putki ei ole jäsennin. Se ei ymmärrä kommentteja tai
merkkijonoja, mutta vastaa kysymykseen sekunneissa, ja se riittää usein.

## Käytännössä

- **`LC_ALL=C` lajitteluun skripteissä.** Lokaali vaikuttaa `sort`-,
  `uniq`- ja `join`-komentojen järjestykseen, ja eri lokaalilla
  lajitellut tiedostot eivät kelpaa `join`- ja `comm`-komennoille.
  Kiinteä lokaali tekee tuloksesta toistettavan.
- **Tasapelisääntö aina, kun järjestys näkyy**: `sort -k1,1nr -k2`.
- **`sort -u` korvaa `sort | uniq`**, mutta `uniq -c` tarvitsee
  erillisen `sort`-vaiheen.
- **`sed -i` vasta testauksen jälkeen.** Aja korvaus ensin ilman
  valitsinta `-i` ja katso tulos, tai käytä `-i.bak`. Versionhallinnassa
  olevissa tiedostoissa `git diff` toimii tarkistuksena.
- **Tunne työkalujen rajat**: CSV, jossa on lainauksia, JSON ja XML
  vaativat jäsentimen (Pythonin `csv`-moduuli tai `mlr`, `jq`,
  `xmllint`). Rikkinäinen tulos ilman virheilmoitusta on vaarallisempi
  kuin hidas työkalu.
- **Suuret tiedostot**: putket ovat virtoja ja käsittelevät gigatavujen
  lokeja vakiomuistilla. `sort` käyttää tarvittaessa levyä
  (`-S` muistin koko, `--parallel`).

## Itsearviointi

- Osaat laskea lokista yleisimmät arvot `cut`-, `sort`- ja
  `uniq -c` -komennoilla ja tehdä järjestyksestä toistettavan.
- Osaat poistaa kommentit, vaihtaa arvon tiedostossa paikallaan ja
  käyttää ryhmiä `sed -E`:n korvauksessa.
- Osaat liittää kaksi CSV-tiedostoa `join`-komennolla ja tiedät,
  milloin on siirryttävä SQL:ään tai oikeaan jäsentimeen.
- Osaat tunnistaa ja korjata Windowsin rivinvaihdot.
- Osaat rakentaa uuden putken vaiheittain välituloksia tarkastellen.
