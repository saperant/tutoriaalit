# Ympäristö ja kuoren asetukset

Ohjelman käytös riippuu argumenttien lisäksi ympäristöstä: mistä
komennot etsitään, mikä on lokaali, mihin väliaikaistiedostot
kirjoitetaan ja millä asetuksilla palvelu käynnistyy. Moni "toimii
minun koneellani" -ongelma on ympäristöero. Tämä luku käy läpi
ympäristömuuttujat, komentojen etsinnän ja kuoren asetustiedostot.

## Kuoren muuttujat ja ympäristömuuttujat

Kuoren muuttuja (`TILA=kehitys`) on vain kuoren omassa käytössä.
`export` tekee siitä ympäristömuuttujan, jonka kaikki kuoren
käynnistämät ohjelmat perivät. Muoto `NIMI=arvo komento` asettaa
muuttujan vain yhden komennon ympäristöön. Ympäristö periytyy vain
vanhemmalta lapselle: lapsi ei voi muuttaa vanhempansa ympäristöä.

```{.bash tiedosto="esimerkit/10-muuttujat.sh" osa="muuttujat"}
```

```{.tuloste tiedosto="esimerkit/10-muuttujat.odotettu"}
```

`env -i` käynnistää komennon tyhjällä ympäristöllä, mikä on hyvä tapa
selvittää, riippuuko vika ympäristöstä. `env` ja `printenv` listaavat
ympäristön, ja käynnissä olevan prosessin ympäristön voi lukea
tiedostosta `/proc/PID/environ`.

| Muuttuja | Merkitys |
|----------|----------|
| `PATH` | Hakemistot, joista komennot etsitään |
| `HOME`, `USER`, `SHELL` | Kotihakemisto, käyttäjä, kirjautumiskuori |
| `LANG`, `LC_ALL`, `LC_*` | Lokaali: kieli, lajittelu, numero- ja aikamuodot |
| `TZ` | Aikavyöhyke (`TZ=Europe/Helsinki date`) |
| `EDITOR`, `PAGER` | Ohjelmat, joita muut työkalut käynnistävät |
| `TMPDIR` | Väliaikaistiedostojen hakemisto |
| `http_proxy`, `https_proxy`, `no_proxy` | Välityspalvelin |

Ohjelmat lukevat asetuksiaan ympäristömuuttujista yhä useammin.
Kontit ja pilvipalvelut välittävät asetukset näin (*twelve-factor
app*). Salaisuudet ympäristössä näkyvät kuitenkin samalle käyttäjälle
tiedostossa `/proc/PID/environ` ja voivat päätyä lokeihin.

## PATH ja komennon etsintä

Kun komennon nimessä ei ole kauttaviivaa, kuori etsii sen
järjestyksessä: alias, funktio, sisäinen komento ja lopuksi `PATH`-
muuttujan hakemistot vasemmalta oikealle. Ensimmäinen osuma voittaa.
Omat työkalut lisätään oman hakemiston kautta, tavallisesti
`~/.local/bin` tai `~/bin`:

```{.bash tiedosto="esimerkit/10-path.sh" osa="path"}
```

Järjestys tarkoittaa, että aiempi hakemisto *varjostaa* myöhemmät.
`type -a` näyttää kaikki osumat. Kuori muistaa löytämänsä polut, ja
`hash -r` tyhjentää muistin, kun `PATH` tai tiedostot muuttuvat:

```{.bash tiedosto="esimerkit/10-path.sh" osa="varjostus"}
```

```{.tuloste tiedosto="esimerkit/10-path.odotettu"}
```

Varjostus on hyödyllinen, kun esimerkiksi uudempi kääntäjäversio
otetaan käyttöön ilman järjestelmän versioon koskemista. Versioiden
hallintatyökalut (`pyenv`, `nvm`, `rustup`) perustuvat siihen. Se on
myös tietoturvariski: kirjoitettava hakemisto `PATH`-muuttujan alussa,
tai `.` siinä, antaa kenelle tahansa mahdollisuuden korvata `ls`.

## Lokaali

Lokaali määrää kielen, merkistön, lajittelujärjestyksen sekä luku- ja
aikamuodot. `LC_ALL` ohittaa kaikki muut. Sama komento voi antaa eri
tuloksen eri koneilla:

```{.bash tiedosto="esimerkit/10-lokaali.sh" osa="lokaali"}
```

```{.bash tiedosto="esimerkit/10-lokaali.sh" osa="versiot"}
```

```{.tuloste tiedosto="esimerkit/10-lokaali.odotettu"}
```

C-lokaalissa lajittelu on tavujärjestys (isot kirjaimet ensin) ja
merkki on tavu, joten `Ä` lasketaan kahdeksi. UTF-8-lokaalissa merkit
lasketaan oikein. Suomalaisessa lokaalissa `fi_FI.UTF-8` myös
lajittelu noudattaa suomen aakkosia (å, ä ja ö z:n jälkeen), ja
desimaalierotin on pilkku. Se rikkoo helposti skriptit, jotka
jäsentävät lukuja. Versionumerot lajitellaan `sort -V`:llä.

Nyrkkisääntö: skripteissä ja automaatiossa `LC_ALL=C` (tai
`C.UTF-8`, kun tarvitaan merkkejä), käyttäjälle näkyvässä tulosteessa
käyttäjän oma lokaali. Käytettävissä olevat lokaalit näkyvät komennolla
`locale -a`.

## Kuoren asetustiedostot

Bash lukee eri tiedostot sen mukaan, onko kuori kirjautumiskuori ja
onko se vuorovaikutteinen:

| Tilanne | Luettavat tiedostot |
|---------|---------------------|
| Kirjautuminen (konsoli, `ssh`) | `/etc/profile`, sitten ensimmäinen tiedostoista `~/.bash_profile`, `~/.bash_login`, `~/.profile` |
| Vuorovaikutteinen muu kuori (pääteikkuna) | `/etc/bash.bashrc`, `~/.bashrc` |
| Skripti | Ei mitään (paitsi `$BASH_ENV`) |

Käytäntö Debianissa ja Ubuntussa: `~/.profile` asettaa ympäristön (kuten
`PATH`) ja lukee lopuksi tiedoston `~/.bashrc`. Tiedosto `~/.bashrc`
sisältää vuorovaikutteisen käytön asetukset:

```{.bash tiedosto="esimerkit/10-bashrc.sh" osa="bashrc"}
```

Muutos tulee voimaan uudessa kuoressa tai komennolla
`source ~/.bashrc`. Aliakset ovat vain vuorovaikutteiseen käyttöön.
Skriptit eivät näe niitä, eikä skripti saa nojata käyttäjän
asetuksiin.

Hyödyllisiä vuorovaikutteisia toimintoja ovat historian haku Ctrl+R,
edellisen komennon viimeinen argumentti `Alt+.` (tai `!$`), rivin
alkuun Ctrl+A ja loppuun Ctrl+E sekä täydennys sarkaimella.

## Käytännössä

- **`export` vain, kun lapsiprosessin pitää nähdä arvo.** Muuten
  kuoren muuttuja riittää.
- **`NIMI=arvo komento`** kokeiluun ja yksittäisiin ajoihin: ei
  pysyvää muutosta, ei siivottavaa.
- **Lisää `PATH`-muuttujaan, älä korvaa**: `PATH="$HOME/.local/bin:$PATH"`.
  Älä koskaan lisää `.`-hakemistoa.
- **Kiinnitä lokaali automaatiossa** (`LC_ALL=C`). Lajittelun,
  desimaalierottimen ja virheilmoitusten kielen vaihtelu rikkoo
  vertailut ja jäsentimet.
- **Vianetsintä ympäristöstä**: vertaa `env | sort` toimivalla ja
  toimimattomalla koneella. Kokeile `env -i`:llä, ja muista, että cron
  ja systemd ajavat ohjelmia hyvin suppealla ympäristöllä.
- **Pidä asetustiedostot versionhallinnassa** (*dotfiles*). Uuden
  koneen käyttöönotto on silloin muutaman minuutin työ.

## Itsearviointi

- Osaat selittää kuoren muuttujan ja ympäristömuuttujan eron ja
  asettaa muuttujan yhden komennon ajaksi.
- Osaat lisätä omia työkaluja `PATH`-muuttujaan ja selvittää, mikä
  ohjelma nimellä todella käynnistyy.
- Osaat kertoa, miten lokaali vaikuttaa lajitteluun ja merkkien
  laskentaan, ja kiinnittää sen automaatiossa.
- Osaat sijoittaa asetukset oikeaan tiedostoon (`~/.profile` tai
  `~/.bashrc`) ja tiedät, miksi skriptit eivät näe aliaksia.
