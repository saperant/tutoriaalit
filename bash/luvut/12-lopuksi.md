# Lopuksi {.runko-kaytannot .runko-lahteet}

## Mallit ja idiomit

| Malli | Mitä ratkaisee | Luku |
|--------------------------------|------------------------------------|----|
| tiukka tila `set -euo pipefail` | virheet pysäyttävät skriptin | 7 |
| siivousansa `trap siivoa EXIT` | väliaikaiset resurssit vapautuvat aina | 7 |
| `main "$@"` viimeisenä | skripti luetaan kokonaan ennen ajoa, funktiot testattavissa | 1, 8 |
| predikaattifunktio | validointi luettavasti ja testattavasti | 4 |
| tulos tulosteena, onnistuminen paluuarvona | `if x=$(f); then` | 4 |
| nimiviittaus `local -n` | taulukon palautus ilman alikuorta | 4 |
| komento taulukkona | ehdolliset argumentit ilman `eval`:ia | 5 |
| laskenta avaimittain `declare -A` | ryhmittely ja tilastot | 5 |
| `while IFS= read -r` | rivien lukeminen muuttamatta niitä | 6 |
| kirjoita–nimeä uudelleen | atominen tiedoston päivitys | 6 |
| latausvartija ja etuliitteet | kirjastot ilman nimiavaruuksia | 8 |
| `kaytto` ja `kuole` | yhtenäinen komentorivirajapinta | 8 |
| rajoitettu rinnakkaisuus `wait -n` | rinnakkaiset työt hallitusti | 9 |
| `flock` | päällekkäisten ajojen esto | 9 |
| varmista-funktio | idempotentti asennus | 10 |
| `aja`-kääre | kuivaharjoitus ja lokitus | 10 |
| versiohakemisto ja linkki | atominen julkaisu ja paluu | 10 |
| uudelleenyritys eksponentiaalisella viiveellä | tilapäiset verkkovirheet | 10 |

## Nyrkkisäännöt

1. Lainaa jokainen laajennus: `"$x"`, `"$(…)"`, `"${a[@]}"`.
2. `--` ennen muuttujasta tulevia operandeja.
3. `[[ ]]` merkkijonoille, `(( ))` luvuille, `[ ]` vain POSIX-`sh`:ssa.
4. `printf '%s\n'` datalle, `echo` vakioteksteille.
5. `local` jokaiselle funktion muuttujalle ja esittely erikseen
   komentokorvauksesta.
6. Tiedostonimet globilla tai `find -print0`:lla, ei koskaan `ls`:stä.
7. Lista on taulukko, komento on taulukko.
8. `mktemp` ja `trap … EXIT` jokaiselle väliaikaiselle tiedostolle.
9. Data vakiotulosteeseen, viestit virhetulosteeseen, virheestä nollasta
   poikkeava paluuarvo.
10. Kiinteä lokaali (`LC_ALL=C`), kun tuloste on toisen ohjelman syötettä
    tai järjestys ratkaisee.
11. ShellCheck ilman varoituksia; jokainen vaiennus perusteltu.
12. Ei `eval`:ia. Jos sitä tuntuu tarvitsevan, taulukko, nimiviittaus tai
    `printf %q` ratkaisee ongelman.

## Turvallisuus

Skripti, joka käsittelee muiden käyttäjien syötettä, tiedostoja tai
ympäristöä, on hyökkäyspinta. Tavallisimmat aukot:

- **Lainaamaton laajennus** voi muuttaa yhden argumentin moneksi tai
  tiedostolistaksi (luku 3).
- **`eval` ja `bash -c "… $x"`** suorittavat datan koodina. Data
  välitetään argumentteina: `bash -c 'komento "$1"' _ "$x"` (luku 9).
- **Aritmeettinen injektio.** Aritmeettinen lauseke ja tavallisen
  taulukon indeksi laajentavat sisältönsä uudelleen, joten syöte
  `a[$(komento)]` muodossa `$(( syote ))` tai `[[ $syote -eq 0 ]]`
  suorittaa komennon. Luku validoidaan säännöllisellä lausekkeella
  (`^[0-9]+$`) ennen aritmetiikkaa.
- **Asetustiedoston `source`** suorittaa tiedoston (luku 8).
- **Arvattavat väliaikaistiedostot** `/tmp`:ssä ovat symbolilinkkihyökkäyksen
  kohde; `mktemp` korjaa tämän (luku 6).
- **Salaisuudet** eivät kuulu komentoriville, jonka muut käyttäjät
  näkevät `ps`:llä, eivätkä jäljitykseen. Ne välitetään
  ympäristömuuttujina tai tiedostoina, joiden oikeudet ovat 0600.
- **`PATH` ja `cd`.** Pääkäyttäjänä ajettava skripti asettaa `PATH`:n
  itse, ja epäonnistunut `cd` lopettaa skriptin (`cd -- "$h" || exit`),
  jotta seuraavat komennot eivät kohdistu väärään hakemistoon.

## Milloin vaihtaa toiseen kieleen

Bash on oikea valinta, kun skripti enimmäkseen ajaa muita ohjelmia.
Vaihda Pythoniin tai Go:hon, kun

- skriptissä on yli noin 200 riviä omaa logiikkaa tai funktioita, jotka
  eivät aja komentoja,
- tarvitaan sisäkkäisiä tietorakenteita, liukulukuja tai päivämäärälaskentaa,
- käsitellään JSONia, YAMLia, XML:ää tai lainattua CSV:tä enemmän kuin
  yhdellä `jq`-kutsulla,
- virheenkäsittely vaatii eri toimia eri virheille,
- skriptin on toimittava myös Windowsissa,
- tai suorituskyky ratkaisee ja ulkoisia komentoja ajetaan silmukassa.

Raja ei ole ehdoton. Hyvä käytäntö on pitää Bash ohuena ohjauskerroksena,
joka kutsuu Python-ohjelmaa tai `awk`:ia raskaaseen työhön. Taitopuun
taito *Python työkaluohjelmointiin* jatkaa tästä.

## Kun käytössä on vain sh

Pienissä konteissa (Alpine, BusyBox) ja joissakin käynnistysskripteissä
Bashia ei ole, ja skripti kirjoitetaan POSIX-`sh`:lle. Tämän tutoriaalin
periaatteet pätevät, mutta osa rakenteista on korvattava:

| Bash | POSIX `sh` |
|------|------------|
| `[[ $a == v* ]]` | `case $a in v*) … ;; esac` |
| `[[ -n $a && -f $t ]]` | `[ -n "$a" ] && [ -f "$t" ]`; lainaus on pakollinen |
| Taulukko `a=(x y)`, `"${a[@]}"` | Positioparametrit: `set -- x y`, `"$@"` |
| `local x` | Ei standardissa, mutta toimii dashissa ja BusyBoxissa |
| `${x//a/b}`, `${x^^}` | `sed`, `tr`; `${x#alku}` ja `${x%loppu}` toimivat |
| `<<< "$x"`, `< <(komento)` | Here-dokumentti, putki tai väliaikaistiedosto |
| `set -o pipefail` | Vasta POSIX 2024:ssä; puuttuu esimerkiksi dashin versiosta 0.5.12 |
| `source t`, `function f` | `. t`, `f() { …; }` |

Skripti aloitetaan rivillä `#!/bin/sh`, ja `shellcheck --shell=sh`
ilmoittaa Bash-rakenteista. Testaa skripti sillä kuorella, jolla se
ajetaan: Debianin ja Ubuntun `/bin/sh` on `dash`, Alpinen BusyBoxin
`ash`.

## Lähteet ja jatkolukeminen

- **GNU Bash Reference Manual** (<https://www.gnu.org/software/bash/manual/>)
  on Bashin virallinen ja kattava kuvaus. `man bash` sisältää saman
  tiiviimmin, ja `help komento` kertoo sisäänrakennetun komennon käytön.
- **POSIX Shell Command Language**
  (<https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html>)
  määrittelee siirrettävän `sh`-kielen.
- **Greg's Wiki** (<https://mywiki.wooledge.org/>): *BashGuide*,
  *BashFAQ* ja *BashPitfalls* ovat yhteisön kokoamia, tarkkoja ohjeita
  Bashin sudenkuoppiin. Tämän tutoriaalin monet säännöt ovat peräisin
  sieltä.
- **ShellCheckin wiki** (<https://www.shellcheck.net/wiki/>) selittää
  jokaisen varoituksen esimerkein.
- **Google Shell Style Guide**
  (<https://google.github.io/styleguide/shellguide.html>) on laajalti
  käytetty tyyliopas, joka myös suosittelee vaihtamaan kieltä, kun skripti
  kasvaa.
- **Kirjat:** Arnold Robbinsin ja Nelson Beeben *Classic Shell Scripting*
  käsittelee Unixin työkaluja ja siirrettävää skriptausta. Carl Albingin
  ja JP Vossenin *bash Cookbook* on ratkaisukokoelma Bashin tyypillisiin
  tehtäviin.

### Työkalut ja kirjastot

- **ShellCheck** (<https://github.com/koalaman/shellcheck>): staattinen
  analyysi.
- **shfmt** (<https://github.com/mvdan/sh>): muotoilu ja jäsennin.
- **bats-core** (<https://github.com/bats-core/bats-core>) sekä
  **bats-assert** ja **bats-file**: testaus.
- **jq** (<https://jqlang.org>): JSONin käsittely komentorivillä.
- **Miller** (<https://miller.readthedocs.io>): CSV:n, TSV:n ja JSONin
  käsittely kuten `awk`.
- **GNU Parallel** (<https://www.gnu.org/software/parallel/>):
  monipuolinen rinnakkaisajo, myös etäkoneilla.

### Mihin tästä eteenpäin

Taitopuussa Bash on esitietona taidolle *Käännösjärjestelmät, testaus ja
CI*, jossa skriptejä käytetään käännösten ja testien automatisointiin.
*Säiliöt ja pilvi-infrastruktuuri* ja *Sulautettu Linux* käyttävät
Bashia konttien käynnistysskripteissä ja järjestelmän alustuksessa, ja
*EDA-työkaluketjujen automatisointi* laitesuunnittelun työkaluketjuissa.

## Lisenssi

Tämä tutoriaali ja sen esimerkkikoodit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0,
<https://creativecommons.org/licenses/by-sa/4.0/deed.fi>). Teosta saa
kopioida, levittää ja muokata, kunhan alkuperäinen lähde mainitaan ja
muokatut versiot jaetaan samalla lisenssillä.
