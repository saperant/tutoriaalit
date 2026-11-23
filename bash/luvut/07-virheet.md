# Virheiden käsittely {.runko-virheet}

Bashissa ei ole poikkeuksia. Jokainen komento palauttaa paluuarvon, ja
oletuksena skripti jatkaa seuraavaan riviin, vaikka edellinen komento
epäonnistui. Luotettava skripti joko tarkistaa jokaisen komennon tai
pyytää Bashia pysähtymään virheeseen, ja siivoaa jälkensä kaikissa
tapauksissa. Tämä luku käy läpi molemmat ja niiden rajat.

## Paluuarvot

| Arvo | Merkitys |
|------|----------|
| 0 | onnistui |
| 1 | yleinen virhe |
| 2 | väärä käyttö, esim. virheellinen valitsin (sopimus) |
| 126 | komento löytyi, mutta sitä ei voi suorittaa |
| 127 | komentoa ei löytynyt |
| 128 + n | prosessi päättyi signaaliin n: 130 = INT (Ctrl-C), 141 = PIPE, 143 = TERM |

Skriptin paluuarvo on `exit`-komennon argumentti tai viimeisen komennon
paluuarvo. Kutsuva ohjelma, kuten CI-järjestelmä tai `make`, päättää sen
perusteella, onnistuiko vaihe. Siksi virheen jälkeen skriptin on
päätyttävä nollasta poikkeavaan arvoon.

Eksplisiittinen tarkistus kirjoitetaan `||`-operaattorilla:

- `cd -- "$hakemisto" || exit 1`
- `mkdir -p -- "$kohde" || return`, jolloin funktio palauttaa `mkdir`:n
  paluuarvon
- `komento || kuole "viesti"`, jossa `kuole` tulostaa viestin
  virhetulosteeseen ja lopettaa (luku 8)

## Tiukka tila: `set -euo pipefail`

Tutoriaalin skriptit alkavat rivillä `set -euo pipefail`:

- **`-e`** (*errexit*) lopettaa skriptin, kun komento epäonnistuu.
- **`-u`** (*nounset*) tekee asettamattoman muuttujan käytöstä virheen.
- **`-o pipefail`** tekee putken paluuarvoksi viimeisen epäonnistuneen
  komennon paluuarvon eikä vain viimeisen komennon.

`-u` löytää kirjoitusvirheet muuttujien nimissä. Ilman sitä
virheellinen nimi laajenee tyhjäksi, ja polku `"$hakemisto/$vanha"`
muuttuu muotoon `/$vanha`:

```{.bash tiedosto="esimerkit/07-asettamaton.kaatuu.sh"}
```

```{.tuloste tiedosto="esimerkit/07-asettamaton.virhe"}
```

Kun muuttuja saa tarkoituksella puuttua, se luetaan oletuksen kanssa:
`${VALINNAINEN:-}`. Samoin `"$@"` ja tyhjä taulukko `"${a[@]}"` ovat
sallittuja Bash 4.4:stä alkaen.

`pipefail` korjaa putken, jonka alkupää epäonnistuu. Ilman sitä
`curl … | tar -x` onnistuu, vaikka lataus katkesi, koska vain `tar`:n
paluuarvo lasketaan. `PIPESTATUS`-taulukko kertoo jokaisen putken osan
paluuarvon. Se on luettava heti putken jälkeen, koska seuraava komento
korvaa sen:

```{.bash tiedosto="esimerkit/07-pipefail.sh" osa="vertailu"}
```

```{.bash tiedosto="esimerkit/07-pipefail.sh" osa="pipestatus"}
```

`pipefail`:llä on yksi tunnettu sivuvaikutus. Kun putken loppupää lopettaa
lukemisen aikaisin, kuten `head`, alkupää saa kirjoittaessaan
SIGPIPE-signaalin ja päättyy arvoon 141. Tulos on oikea, mutta putki
epäonnistuu:

```{.bash tiedosto="esimerkit/07-pipefail.sh" osa="sigpipe"}
```

```{.tuloste tiedosto="esimerkit/07-pipefail.odotettu"}
```

Ratkaisuja ovat `head`-tyyppisten putkien välttäminen tiukassa tilassa
(esim. `sed -n 1,2p` lukee koko syötteen) tai paluuarvon 141 salliminen
kyseisessä kohdassa.

## Missä `set -e` ei toimi

`set -e` ei ole poikkeusmekanismi. Se ei laukea

- `if`-, `while`- tai `until`-ehdossa,
- `&&`- tai `||`-listan muussa kuin viimeisessä komennossa,
- `!`-alkuisessa komennossa,
- ja, mikä yllättää useimmat, **missään funktiossa, jota kutsutaan
  näistä kohdista**.

```{.bash tiedosto="esimerkit/07-set-e.sh" osa="ansa"}
```

`cp` epäonnistui, mutta funktio jatkoi ja palautti `echo`:n paluuarvon 0.
Funktio, joka voi epäonnistua ja jota kutsutaan ehdossa, tarkistaa siksi
omat komentonsa itse:

```{.bash tiedosto="esimerkit/07-set-e.sh" osa="korjaus"}
```

```{.tuloste tiedosto="esimerkit/07-set-e.odotettu"}
```

Muita aukkoja:

- `local x=$(komento)` ja `export x=$(komento)` peittävät paluuarvon
  (luku 4).
- Komentokorvaus ei peri `-e`:tä ilman asetusta
  `shopt -s inherit_errexit` (4.4). Pikaoppaan pohja kytkee sen.
- Prosessikorvauksen `<(…)` paluuarvoa ei tarkisteta koskaan.

`set -e` on turvaverkko, ei virheenkäsittelyn suunnitelma. Kohdat, joissa
virhe on odotettavissa (puuttuva tiedosto, verkkovirhe), käsitellään
eksplisiittisesti `if`:llä tai `||`:llä.

## Siivous: `trap … EXIT`

Skriptin väliaikaiset resurssit (tiedostot, hakemistot, lukot,
taustaprosessit) vapautetaan *ansalla*. `trap komento EXIT` suoritetaan,
kun skripti päättyy millä tahansa tavalla: normaalisti, `exit`-komennolla
tai `set -e`:n pysäyttämänä. Tämä vastaa muiden kielten `finally`-lohkoa
tai RAII:ta.

```{.bash tiedosto="esimerkit/07-siivous.sh" osa="ansa"}
```

```{.bash tiedosto="esimerkit/07-siivous.sh" osa="tyo"}
```

```{.tuloste tiedosto="esimerkit/07-siivous.odotettu"}
```

Ansa asetetaan heti resurssin luomisen jälkeen. Siivousfunktio tallentaa
ensimmäiseksi `$?`:n, jotta se voi raportoida ja tarvittaessa palauttaa
alkuperäisen paluuarvon. Bash ajaa EXIT-ansan myös INT- ja TERM-
signaalien jälkeen, kun skripti lopetetaan Ctrl-C:llä tai `kill`:llä.
`kill -9` (SIGKILL) ohittaa kaikki ansat.

Kullekin signaalille voi olla vain yksi ansa. Uusi `trap … EXIT`
korvaa edellisen, joten kirjastot eivät aseta EXIT-ansaa itse vaan
tarjoavat siivousfunktion, jota pääohjelman ansa kutsuu.

## Virheen paikka: `trap … ERR`

ERR-ansa suoritetaan, kun komento epäonnistuu samoissa kohdissa, joissa
`set -e` laukeaisi. Se sopii virheilmoitukseen, josta näkee rivin ja
komennon:

```{.bash tiedosto="esimerkit/07-virherivi.kaatuu.sh"}
```

```{.tuloste tiedosto="esimerkit/07-virherivi.virhe"}
```

Valitsin `-E` (*errtrace*) periyttää ERR-ansan funktioihin,
komentokorvauksiin ja alikuoriin; ilman sitä funktion sisäinen virhe
ei laukaisisi ansaa. Ansan argumentit lainataan yksinkertaisilla
lainausmerkeillä, jotta `$LINENO` ja `$BASH_COMMAND` laajennetaan
vasta virheen hetkellä. `BASH_LINENO`- ja `FUNCNAME`-taulukoista voi
koota myös kutsupinon.

## Käytännössä

- **`set -euo pipefail` jokaisen skriptin alkuun**, ja tarvittaessa
  `shopt -s inherit_errexit`. Se on turvaverkko, jonka aukot tunnetaan.
- **Odotetut virheet eksplisiittisesti.** `if ! komento; then … fi` tai
  `komento || kuole "…"`. Virheilmoitus kertoo, mitä yritettiin ja millä
  arvolla.
- **Funktio, jota kutsutaan ehdossa, tarkistaa omat komentonsa**
  (`|| return`), koska `set -e` ei toimi sen sisällä.
- **`trap siivoa EXIT` heti resurssin luomisen jälkeen.** Yksi ansa,
  joka siivoaa kaiken, ja kirjastoissa siivousfunktio ilman omaa ansaa.
- **Virheilmoitukset virhetulosteeseen ja nollasta poikkeava
  paluuarvo.** Käyttövirheestä arvo 2, muista 1.
- **`set -E` ja ERR-ansa** pitkissä skripteissä, kuten CI-vaiheissa,
  joissa virheen rivi säästää aikaa.
- **Varo `pipefail`:n ja `head`:n yhdistelmää.** SIGPIPE (141) ei ole
  virhe, kun loppupää lopetti tarkoituksella.
- **Hinta:** tiukka tila ei maksa ajossa mitään, mutta se tekee
  ehdottomaksi säännön, että tarkoituksella epäonnistuva komento
  merkitään (`|| true`, `if`). Tämä on dokumentaatiota, ei kustannus.

## Itsearviointi

- Osaat selittää, mitä `set -e`, `set -u` ja `set -o pipefail` tekevät
  ja miksi kukin on tarpeen.
- Osaat luetella tilanteet, joissa `set -e` ei pysäytä skriptiä, ja
  kirjoittaa funktion, joka toimii oikein myös ehdossa kutsuttuna.
- Osaat siivota väliaikaiset tiedostot `trap … EXIT`:llä niin, että
  siivous tapahtuu myös virheen ja Ctrl-C:n jälkeen.
- Osaat kirjoittaa ERR-ansan, joka kertoo epäonnistuneen komennon ja
  rivin.
- Osaat lukea putken jokaisen osan paluuarvon `PIPESTATUS`:sta.
