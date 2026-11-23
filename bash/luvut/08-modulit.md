# Argumentit, kirjastot ja skriptin rakenne {.runko-modulit}

Skriptin rajapinta on sen komentorivi: argumentit, valitsimet,
ympäristömuuttujat, paluuarvo ja tulosteet. Tämä luku käy läpi
valitsimien jäsentämisen, skriptin jakamisen kirjastoihin ja rakenteen,
jolla pitkäkin skripti pysyy luettavana.

## Lyhyet valitsimet: getopts

`getopts` on Bashin sisäänrakennettu valitsinjäsennin. Se tukee POSIXin
lyhyitä valitsimia: `-v`, arvolliset `-k 14` ja `-k14`, yhdistetyt
`-vn` sekä `--` valitsimien loppuna. Skriptin rajapinta alkaa
käyttöohjeesta ja virheilmoitusfunktiosta:

```{.bash tiedosto="esimerkit/08-getopts.sh" osa="kaytto"}
```

Käyttöohje on here-dokumentti, joka tulostetaan vakiotulosteeseen, kun
sitä pyydetään (`-h`), ja virhetulosteeseen virheen yhteydessä.
`${0##*/}` on skriptin nimi ilman polkua.

```{.bash tiedosto="esimerkit/08-getopts.sh" osa="jasennys"}
```

Valitsinmerkkijonossa kaksoispiste kirjaimen perässä tarkoittaa arvoa,
joka tulee muuttujaan `OPTARG`. Alun kaksoispiste valitsee *hiljaisen
tilan*: `getopts` ei tulosta omia virheilmoituksiaan, vaan asettaa
muuttujaan `:` (arvo puuttuu) tai `?` (tuntematon valitsin), ja skripti
kirjoittaa ilmoituksen itse. Silmukan jälkeen `shift` poistaa käsitellyt
valitsimet, ja `"$@"` sisältää vain operandit.

Arvot validoidaan heti jäsentämisen jälkeen, ennen kuin mitään tehdään:

```{.bash tiedosto="esimerkit/08-getopts.sh" osa="validointi"}
```

Argumenteilla

```{.tuloste tiedosto="esimerkit/08-getopts.argumentit"}
```

(yksi argumentti riviä kohti) tuloste on

```{.tuloste tiedosto="esimerkit/08-getopts.odotettu"}
```

## Pitkät valitsimet

`getopts` ei tue pitkiä valitsimia (`--kohde`). Ulkoinen `getopt`-
ohjelma tukee, mutta vain GNU-versio, eikä se ole macOS:ssä tai
BusyBoxissa samanlainen. Siirrettävä tapa on jäsentää argumentit itse
`while`- ja `case`-rakenteella:

```{.bash tiedosto="esimerkit/08-pitkat.sh" osa="silmukka"}
```

```{.bash tiedosto="esimerkit/08-pitkat.sh" osa="validointi"}
```

```{.tuloste tiedosto="esimerkit/08-pitkat.odotettu"}
```

Silmukka tukee muotoja `--kohde=X` ja `--kohde X`. `--` lopettaa
valitsimien käsittelyn, joten viivalla alkava tiedostonimi
`--outo-nimi.txt` päätyi lähteisiin. Pakollinen valitsin ja sallitut
arvot tarkistetaan `case`:lla, jonka tyhjä haara `testi|tuotanto) ;;`
hyväksyy arvon.

## Ympäristömuuttujat asetuksina

Valitsimien lisäksi skripti voi lukea asetuksia ympäristöstä:
`LOKI_TASO=debug ./skripti.sh`. Käytäntö on lukea ne kerran skriptin
alussa oletusarvon kanssa (`${LOKI_TASO:-info}`) ja dokumentoida ne
käyttöohjeessa. Ympäristömuuttujat sopivat asetuksiin, jotka ovat samat
useassa ajossa, kuten CI-järjestelmän muuttujat. Valitsimet sopivat
asetuksiin, jotka vaihtelevat ajoittain.

## Kirjastot: source

`source tiedosto` (POSIX-nimeltään `.`) suorittaa tiedoston nykyisessä
kuoressa, jolloin sen funktiot ja muuttujat tulevat käyttöön. Tämä on
Bashin modulijärjestelmä. Siinä ei ole nimiavaruuksia, joten kirjaston
nimet erotetaan etuliitteellä tai alaviivalla (`_LOKI_TASOT`).

Pääohjelma lataa kirjastot omasta hakemistostaan, jotta skriptin voi
käynnistää mistä tahansa. `${BASH_SOURCE[0]}` on käynnissä olevan
tiedoston polku:

```{.bash tiedosto="esimerkit/08-kirjasto/main.sh" osa="lataus"}
```

Kommentti `# shellcheck source-path=SCRIPTDIR` tiedoston alussa kertoo
ShellCheckille, mistä ladattavat tiedostot löytyvät, jotta se voi
tarkistaa myös niiden käytön.

Kirjasto suojautuu kaksoislataukselta *latausvartijalla*, vastaavasti kuin
C:n otsikkotiedostot:

```{.bash tiedosto="esimerkit/08-kirjasto/loki.sh" osa="suoja"}
```

```{.bash tiedosto="esimerkit/08-kirjasto/loki.sh" osa="tasot"}
```

Lokikirjasto kirjoittaa **virhetulosteeseen**, jotta loki ei sekoitu
skriptin varsinaiseen tulosteeseen. Taso valitaan ympäristömuuttujalla
`LOKI_TASO`, ja aikaleiman voi kiinnittää muuttujalla `LOKI_AIKA`
testejä varten. `declare -g` luo globaalin muuttujan, vaikka kirjasto
ladattaisiin funktion sisältä.

Toinen kirjasto lukee asetustiedoston `AVAIN=arvo`-rivit assosiatiiviseen
taulukkoon:

```{.bash tiedosto="esimerkit/08-kirjasto/asetukset.sh" osa="lue"}
```

Asetustiedostoa ei ladata `source`:lla, vaikka se olisi Bash-syntaksia.
`source` suorittaisi tiedoston koodina, jolloin asetustiedostoon kirjoitettu
`$(rm -rf ~)` suoritettaisiin. Rivi riviltä jäsentävä lukija käsittelee
arvon tekstinä:

```{.bash tiedosto="esimerkit/08-kirjasto/main.sh" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/08-kirjasto.odotettu"}
```

Esimerkki ohjaa virhetulosteen vakiotulosteeseen (`exec 2>&1`), jotta
lokirivit näkyvät tulosteessa. Oikeassa skriptissä virrat pidetään
erillään.

## Skriptin rakenne

Kun skripti kasvaa yli muutaman kymmenen rivin, vakiintunut rakenne
helpottaa lukemista:

1. shebang, lyhyt kuvaus ja käyttöesimerkki kommenttina
2. `set -euo pipefail` ja `shopt`-asetukset
3. vakiot (`readonly`) ja ympäristömuuttujista luetut asetukset
4. kirjastojen lataus
5. funktiot: apufunktiot ensin, `main` viimeisenä
6. viimeinen rivi `main "$@"`

Kun skriptin funktioita halutaan testata, viimeinen rivi kirjoitetaan
muotoon `[[ ${BASH_SOURCE[0]} == "$0" ]] && main "$@"`. Ehto on tosi
vain, kun tiedosto ajetaan, ei kun se ladataan `source`:lla, joten testi
voi ladata skriptin ja kutsua sen funktioita (luku 11).

## Käytännössä

- **`kaytto`- ja `kuole`-funktiot** jokaiseen skriptiin, joka ottaa
  argumentteja. `-h` tulostaa ohjeen vakiotulosteeseen ja paluuarvolla 0,
  käyttövirhe virhetulosteeseen ja paluuarvolla 2.
- **getopts lyhyille valitsimille, `while`/`case` pitkille.** Ulkoista
  `getopt`:ia ei käytetä siirrettävissä skripteissä.
- **Validoi heti jäsentämisen jälkeen.** Virheellinen argumentti
  havaitaan ennen kuin mitään on muutettu.
- **`--` operandien eteen** omissa ja kutsuttavissa komennoissa.
- **Kirjastot `source`:lla skriptin omasta hakemistosta**, latausvartija
  ja etuliitteelliset nimet. Kirjasto ei aseta `set`-valitsimia, ei
  `trap`-ansoja eikä tulosta mitään latautuessaan.
- **Asetustiedostoa ei suoriteta.** Data luetaan jäsentämällä, ei
  `source`:lla, ellei tiedosto ole yhtä luotettu kuin skripti itse.
- **Loki virhetulosteeseen**, tasot ympäristömuuttujalla.
- **Hinta:** `source` on halpa, mutta jokainen ladattu funktio jää
  kuoren muistiin. Satoja funktioita sisältävä kirjasto on merkki siitä,
  että työkalu kannattaa kirjoittaa toisella kielellä.

## Itsearviointi

- Osaat jäsentää lyhyet valitsimet getoptsilla hiljaisessa tilassa ja
  tuottaa omat virheilmoitukset.
- Osaat jäsentää pitkät valitsimet muodoissa `--nimi=arvo` ja
  `--nimi arvo` sekä tukea `--`-erotinta.
- Osaat jakaa skriptin kirjastoihin, jotka ladataan skriptin omasta
  hakemistosta riippumatta käynnistyshakemistosta.
- Osaat lukea asetustiedoston suorittamatta sitä.
- Osaat kirjoittaa skriptin niin, että sen funktiot voi ladata testiin
  käynnistämättä pääohjelmaa.
