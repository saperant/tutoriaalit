# Ehdot, silmukat ja funktiot {.runko-ohjaus}

Bashin ohjausrakenteet perustuvat komentojen paluuarvoihin. Tämä luku
käy läpi testit, ehtorakenteet, silmukat ja funktiot sekä tavat, joilla
funktio välittää tuloksensa kutsujalle.

## Paluuarvo on totuusarvo

Jokainen komento palauttaa kokonaisluvun 0–255, joka on luettavissa
muuttujasta `$?`. Nolla tarkoittaa onnistumista, muut arvot epäonnistumista.
`if`, `while`, `&&` ja `||` ajavat komennon ja haarautuvat sen paluuarvon
mukaan:

- `komento && toinen` ajaa toisen, jos ensimmäinen onnistui
- `komento || toinen` ajaa toisen, jos ensimmäinen epäonnistui
- `! komento` kääntää paluuarvon

Testit ovat komentoja, jotka palauttavat 0 tai 1:

- **`[[ … ]]`** on Bashin ehtolauseke: merkkijonojen ja tiedostojen
  testit, glob-vertailu `==` ja säännöllinen lauseke `=~`. Sen sisällä
  muuttujia ei jaeta sanoiksi, ja `&&`, `||` ja sulut toimivat.
- **`(( … ))`** on aritmeettinen ehto: `(( n > 0 && n <= 10 ))`.
- **`[ … ]`** eli `test` on POSIX-komento. Sen argumentit jaetaan kuten
  minkä tahansa komennon, joten `[ -n $x ]` on tosi myös tyhjällä `x`:llä
  (luku 11). Bash-skriptissä sitä ei tarvita.

Tavallisimmat testit ovat `-f` (tavallinen tiedosto), `-d` (hakemisto),
`-e` (olemassa), `-s` (ei tyhjä), `-r`/`-w`/`-x` (oikeudet), `-n` ja `-z`
(merkkijono ei tyhjä / tyhjä) sekä `-v nimi` (muuttuja on asetettu).
Lukuja verrataan `(( ))`:ssa, sillä `[[ ]]`:n `<` vertaa merkkijonoja
aakkosjärjestyksessä.

## Ehdot ja validointi

Funktio, joka vain testaa, on predikaatti: sen paluuarvo on viimeisen
komennon paluuarvo, eikä `return`-lausetta tarvita.

```{.bash tiedosto="esimerkit/04-validointi.sh" osa="funktiot"}
```

`=~` vertaa säännölliseen lausekkeeseen (POSIX ERE). Lauseke kirjoitetaan
lainaamatta, koska lainattu oikea puoli tulkitaan kirjaimelliseksi
merkkijonoksi. Monimutkainen lauseke kannattaa tallentaa ensin muuttujaan:
`kuvio='^[a-z]+$'; [[ $x =~ $kuvio ]]`.

`case` vertaa arvoa glob-kuvioihin ja on selkein tapa käsitellä
luettelomaisia vaihtoehtoja:

```{.bash tiedosto="esimerkit/04-validointi.sh" osa="case"}
```

Pääohjelma lukee rivejä ja validoi jokaisen. `elif`-ketjun ehdot ovat
funktiokutsuja, ja viimeisessä ehdossa sijoitus `taso=$(…)` onnistuu tai
epäonnistuu sen komennon mukaan, jonka tuloste kaapattiin.

```{.bash tiedosto="esimerkit/04-validointi.sh" osa="kaytto"}
```

Osuman alaryhmät ovat taulukossa `BASH_REMATCH`:

```{.bash tiedosto="esimerkit/04-validointi.sh" osa="rematch"}
```

Syötteellä

```{.tuloste tiedosto="esimerkit/04-validointi.syote"}
```

tuloste on

```{.tuloste tiedosto="esimerkit/04-validointi.odotettu"}
```

## Silmukat

`for nimi in sanat` käy läpi sanalistan ja `while komento` toistaa niin
kauan kuin komento onnistuu. Tiedostojen läpikäyntiin käytetään globia
eikä `ls`-komennon tulostetta, koska glob tuottaa jokaisen nimen yhtenä
sanana nimen sisällöstä riippumatta:

```{.bash tiedosto="esimerkit/04-silmukat.sh" osa="glob"}
```

Ilman `nullglob`-asetusta kuvio, joka ei täsmää mihinkään, jää
sellaisenaan, ja silmukka ajetaan kerran arvolla `data/*.json`.
Asetus kannattaa kytkeä skriptin alussa tai tarkistaa jokainen arvo
`[[ -e ]]`:llä.

Alihakemistot käydään läpi `find`-komennolla. Nollatavu on ainoa
merkki, jota tiedostonimessä ei voi olla, joten `-print0` ja
`read -d ''` käsittelevät myös rivinvaihdon sisältävät nimet oikein.
Silmukka luetaan prosessikorvauksesta `< <(…)` eikä putkesta, jotta
`maara` säilyy (luku 2):

```{.bash tiedosto="esimerkit/04-silmukat.sh" osa="find"}
```

Laskuri-silmukalle on C:n kaltainen muoto:

```{.bash tiedosto="esimerkit/04-silmukat.sh" osa="cstyle"}
```

```{.tuloste tiedosto="esimerkit/04-silmukat.odotettu"}
```

`break` ja `continue` toimivat kuten muissa kielissä ja ottavat
valinnaisen sisäkkäisyystason (`break 2`). Aaltosulkulaajennus
`{1..10}` tuottaa lukujonon, mutta sen rajat eivät voi olla muuttujia.

## Funktiot

Funktio määritellään `nimi() { … }` ja kutsutaan kuten komentoa.
Argumentit ovat `$1`, `$2`, …, kaikki yhdessä `"$@"` ja niiden määrä
`$#`. Funktiolla on kolme tapaa välittää tietoa kutsujalle:

1. **Paluuarvo** (`return n`) kertoo onnistumisen. Se ei ole tulos.
2. **Tuloste** kaapataan komentokorvauksella `x=$(funktio)`. Tämä on
   tavallisin tapa palauttaa arvo.
3. **Nimiviittaus** (`local -n`, Bash 4.3) antaa funktion muokata
   kutsujan muuttujaa tai taulukkoa.

```{.bash tiedosto="esimerkit/04-funktiot.sh" osa="tuloste"}
```

Funktio tulostaa tuloksen ja palauttaa 1, jos osiota ei löydy. Kutsuja
tarkistaa onnistumisen ja kaappaa tuloksen samalla rivillä:

```{.bash tiedosto="esimerkit/04-funktiot.sh" osa="kaytto"}
```

Komentokorvaus poistaa tulosteen lopusta rivinvaihdot ja ajaa funktion
alikuoressa, joten funktion muuttujamuutokset eivät näy kutsujalle.
Taulukon palauttamiseen ja muokkaamiseen käytetään nimiviittausta:

```{.bash tiedosto="esimerkit/04-funktiot.sh" osa="nimiviittaus"}
```

Nimiviittauksen nimi ei saa olla sama kuin kutsujan muuttujan, koska
viittaus osoittaisi itseensä. Kirjastofunktiot käyttävät siksi
viittauksille erottuvia nimiä, kuten `_kohde` (luku 8).

Ilman `local`-määrettä kaikki muuttujat ovat globaaleja. `local`
näkyvyys on *dynaaminen*: funktion paikallinen muuttuja näkyy myös
funktioille, joita se kutsuu.

```{.bash tiedosto="esimerkit/04-funktiot.sh" osa="local"}
```

```{.tuloste tiedosto="esimerkit/04-funktiot.odotettu"}
```

### Sudenkuoppa: `local x=$(komento)`

`local` on komento, ja sen paluuarvo korvaa komentokorvauksen paluuarvon.
Rivi `local asetus=$(lue_asetus)` onnistuu aina, joten virhe jää
huomaamatta. ShellCheck varoittaa tästä (SC2155):

```{.bash tiedosto="esimerkit/04-local.ei-kaanny.sh"}
```

```{.tuloste tiedosto="esimerkit/04-local.odotettu"}
```

Sama koskee komentoja `export` ja `readonly`. Esittely ja sijoitus
kirjoitetaan erikseen aina, kun oikea puoli on komentokorvaus.

## Käytännössä

- **Predikaattifunktiot validointiin.** `on_kelvollinen_portti "$p"`
  on luettavampi kuin säännöllinen lauseke ehdossa, ja sen voi testata
  erikseen (luku 11).
- **`[[ ]]` merkkijonoille, `(( ))` luvuille.** `[ ]`:ta käytetään vain
  POSIX-skripteissä.
- **`case` luetteloille.** Valitsimet, alikomennot ja ympäristöt
  käsitellään `case`:lla; `*)`-haara käsittelee tuntemattomat arvot.
- **Tulos tulosteena, onnistuminen paluuarvona.** `if x=$(f); then` on
  Bashin vastine Pythonin funktiolle, joka palauttaa arvon tai heittää
  poikkeuksen.
- **`local` jokaiselle funktion muuttujalle** ja esittely erikseen, kun
  arvo tulee komentokorvauksesta.
- **`main`-funktio.** Skriptin logiikka funktioihin ja viimeiseksi riviksi
  `main "$@"`. Funktioita voi silloin testata lataamalla skriptin ilman,
  että pääohjelma käynnistyy (luku 11).
- **Glob tai `find -print0`, ei `ls`.** Tiedostonimissä voi olla mitä
  tahansa merkkejä nollatavua ja kauttaviivaa lukuun ottamatta.
- **Hinta:** `$(funktio)` luo alikuoren jokaisella kutsulla. Tuhansia
  kertoja ajettavassa silmukassa tulos kannattaa välittää
  nimiviittauksella tai `printf -v`:llä.

## Itsearviointi

- Osaat kirjoittaa predikaattifunktion, joka validoi syötteen
  säännöllisellä lausekkeella ja aritmeettisella ehdolla.
- Osaat käydä tiedostot läpi globilla ja `find -print0`:lla niin, että
  välilyönnit ja rivinvaihdot nimissä eivät riko silmukkaa.
- Osaat palauttaa funktiosta arvon tulosteena, onnistumisen paluuarvona
  ja taulukon nimiviittauksella.
- Osaat selittää, miksi `local x=$(komento)` peittää virheen ja miten sen
  korjaa.
