# Tekstin etsiminen: grep ja säännölliset lausekkeet

Lokit, asetukset, lähdekoodi ja komentojen tulosteet ovat tekstiä.
`grep` tulostaa rivit, jotka vastaavat hahmoa, ja on siksi yleisin
työkalu vianetsinnässä. Tämä luku käy läpi grepin tärkeimmät
valitsimet ja säännölliset lausekkeet siinä laajuudessa kuin
komentorivillä tarvitaan.

## Perusvalitsimet

Esimerkkien aineisto on sovelluksen loki:

```{.bash tiedosto="esimerkit/05-perus.sh" osa="aineisto"}
```

| Valitsin | Merkitys |
|----------|----------|
| `-i` | Kirjainkoko ei merkitse |
| `-v` | Rivit, jotka *eivät* vastaa |
| `-c` | Osumien määrä tiedostoittain |
| `-n` | Rivinumerot |
| `-w` | Vain kokonaiset sanat |
| `-x` | Vain kokonaiset rivit |
| `-l`, `-L` | Vain tiedostonimet, joissa osuma on tai ei ole |
| `-o` | Vain osuva osa, kukin omalle rivilleen |
| `-q` | Ei tulostetta, vain paluuarvo |
| `-m N` | Lopeta N osuman jälkeen |
| `-A N`, `-B N`, `-C N` | N riviä osuman jälkeen, ennen, molemmin puolin |
| `-E`, `-F`, `-P` | Laajennettu lauseke, kiinteä merkkijono, Perl-lauseke |

```{.bash tiedosto="esimerkit/05-perus.sh" osa="perus"}
```

```{.bash tiedosto="esimerkit/05-perus.sh" osa="sana"}
```

```{.tuloste tiedosto="esimerkit/05-perus.odotettu"}
```

`-c` ja `-ci` antavat eri tuloksen, koska yhdessä rivissä taso on
kirjoitettu pienillä kirjaimilla. Lokitiedostoja tutkiessa kannattaa
aloittaa väljästä hausta ja tarkentaa. Toinen putki rajaa ensin
GET-pyynnöt ja sitten virhekoodit 4xx ja 5xx rivin lopusta.

## Säännölliset lausekkeet

grep tuntee kaksi POSIX-murretta. Perusmuodossa (BRE) merkit `?`, `+`,
`{`, `|` ja `(` ovat tavallisia merkkejä, ja erikoismerkityksen saa
kenoviivalla. Laajennetussa muodossa (ERE, `grep -E`) ne ovat
erikoismerkkejä ilman kenoviivaa. ERE on luettavampi, ja sitä
kannattaa käyttää aina, kun lausekkeessa on muutakin kuin tekstiä ja
`.*`.

| Lauseke | Vastaa |
|---------|--------|
| `.` | Mitä tahansa merkkiä |
| `[abc]`, `[^abc]`, `[0-9]` | Merkkiä joukosta, joukon ulkopuolelta, väliltä |
| `[[:digit:]]`, `[[:space:]]`, `[[:alpha:]]` | Merkkiluokkaa |
| `^`, `$` | Rivin alkua, loppua |
| `\b`, `\<`, `\>` | Sanan rajaa (GNU) |
| `*`, `+`, `?` | 0 tai useampaa, 1 tai useampaa, 0 tai 1 kertaa edellistä |
| `{n}`, `{n,m}` | Täsmälleen n kertaa, n–m kertaa |
| `( )` | Ryhmää |

Pystyviiva erottaa vaihtoehdot: `(GET|POST) /api` vastaa kumpaakin
pyyntöä. Lausekkeet kirjoitetaan yksinkertaisiin lainausmerkkeihin, jottei kuori
tulkitse merkkejä `$`, `*` ja `\` itse.

## Kenttien poimiminen

`-o` tulostaa vain osuvan osan, mikä tekee grepistä poimintatyökalun.
Esimerkki etsii epäonnistuneiden kirjautumisten IP-osoitteet ja laskee
yleisimmät. Tällainen putki on tyypillinen ensimmäinen askel, kun
epäillään salasanojen arvausta:

```{.bash tiedosto="esimerkit/05-poiminta.sh" osa="poiminta"}
```

Lausekkeen pisteet ovat helppo ohittaa. `10.0.0.5` osuu myös
osoitteisiin `10.0.0.51` ja `10a0b0c5`. Sanaraja `-w` estää
pidemmän osoitteen osuman, ja `-F` tekee koko hahmosta kirjaimellisen:

```{.bash tiedosto="esimerkit/05-poiminta.sh" osa="tarkka"}
```

```{.tuloste tiedosto="esimerkit/05-poiminta.odotettu"}
```

`-F` on myös nopein tapa hakea suurta määrää kiinteitä merkkijonoja:
`grep -F -f kielletyt.txt loki` hakee kaikki tiedoston rivit kerralla.

## Konteksti

Virheilmoitus on harvoin yksinään ymmärrettävä. Rivit ennen ja jälkeen
kertovat, mitä oltiin tekemässä:

```{.bash tiedosto="esimerkit/05-konteksti.sh" osa="konteksti"}
```

```{.tuloste tiedosto="esimerkit/05-konteksti.odotettu"}
```

`-m1 -n` vastaa kysymykseen "missä on ensimmäinen ongelma?". Käännöksen
lokissa ensimmäinen virhe on usein ainoa todellinen, ja myöhemmät ovat
sen seurauksia.

## Hakemistopuun läpikäynti

`grep -r` käy hakemiston läpi rekursiivisesti. `--include` rajaa
tiedostotyypit ja `--exclude-dir` ohittaa hakemistot, kuten
riippuvuudet ja versionhallinnan:

```{.bash tiedosto="esimerkit/05-rekursiivinen.sh" osa="rekursiivinen"}
```

```{.tuloste tiedosto="esimerkit/05-rekursiivinen.odotettu"}
```

Tehtävä on tavallinen palvelinsiirrossa: missä asetuksissa vanha osoite
vielä on, ja missä ei? `-L` kertoo tiedostot, joista osuma puuttuu.

Lähdekoodin hakuun on grepiä nopeampia työkaluja: `git grep` hakee
vain versionhallinnassa olevista tiedostoista, ja `ripgrep` (`rg`)
noudattaa oletuksena `.gitignore`-tiedostoa ja käyttää useita säikeitä.
Valitsimet ovat pitkälti samat.

## Käytännössä

- **Väljästä tarkkaan.** Aloita `grep -i`:llä ja tarkenna, kun näet,
  miltä rivit näyttävät. Lokitasot ja virheilmoitukset kirjoitetaan
  harvoin johdonmukaisesti.
- **`-E` tai `-F`, ei perusmuotoa**: laajennettu lauseke on luettavampi
  ja `-F` estää pisteiden ja hakasulkeiden tahattoman tulkinnan.
- **`grep | sort | uniq -c | sort -rn`** on lokianalyysin perusputki:
  poimi, lajittele, laske, järjestä. Seuraava luku kokoaa sen osat.
- **`grep -q` ehdoissa**: `if grep -q '^kaisa:' /etc/passwd` ei tulosta
  mitään ja lopettaa ensimmäiseen osumaan.
- **Paluuarvo 1 ei ole virhe** vaan "ei osumia". Skripteissä se pitää
  erottaa arvosta 2, joka tarkoittaa esimerkiksi puuttuvaa tiedostoa.
- **Rakenteinen loki (JSON) käsitellään `jq`:lla**, ei grepillä,
  kun kenttien järjestys tai sisäkkäisyys vaihtelee.
- **Pakatut lokit**: `zgrep` ja `zcat | grep` lukevat `.gz`-tiedostoja
  purkamatta niitä levylle.

## Itsearviointi

- Osaat rajata lokista rivit tason, komponentin ja kentän arvon
  perusteella ja laskea osumat.
- Osaat kirjoittaa laajennetun säännöllisen lausekkeen, jossa on
  merkkijoukkoja, toistoja ja vaihtoehtoja, ja tiedät, milloin
  tarvitaan `-F` tai `-w`.
- Osaat poimia kentän arvot `grep -o`:lla ja laskea yleisimmät.
- Osaat hakea hakemistopuusta tiedostotyypin mukaan ja ohittaa
  riippuvuushakemistot.
