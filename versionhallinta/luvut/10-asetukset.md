# Koukut, .gitignore ja .gitattributes

Kolme tiedostotyyppiä sovittaa Gitin projektin tarpeisiin: koukut
ajavat tarkistuksia, `.gitignore` kertoo, mitä ei versioida, ja
`.gitattributes` kertoo, miten tiedostoja käsitellään. Koukkuja lukuun
ottamatta ne ovat versionhallinnassa, joten ne koskevat jokaista
kehittäjää.

## Koukut

Koukku on ohjelma, jonka Git ajaa tietyssä kohdassa. `pre-commit` ajetaan
ennen commitin luomista, `commit-msg` saa viestin tiedostona, ja
`pre-push` ajetaan ennen lähettämistä. Jos koukku päättyy muuhun kuin
nollaan, operaatio keskeytyy. Oletuspaikka `.git/hooks` ei ole
versionhallinnassa. Asetus `core.hooksPath` ottaa käyttöön
versioidun hakemiston, jolloin koko tiimi käyttää samoja koukkuja:

```{.bash tiedosto="esimerkit/10-koukut.sh" osa="koukut"}
```

```{.bash tiedosto="esimerkit/10-koukut.sh" osa="kokeilu"}
```

```{.tuloste tiedosto="esimerkit/10-koukut.odotettu"}
```

`git diff --cached --check` on valmis tarkistus rivinloppujen
välilyönneille ja unohtuneille konfliktimerkinnöille. Koukut ovat apu,
eivät vartija: `git commit --no-verify` ohittaa ne, ja jokaisen on
otettava `core.hooksPath` itse käyttöön (tai se asetetaan projektin
asennusskriptissä). Pakolliset tarkistukset ajetaan siksi CI:ssä, ja
koukut antavat palautteen jo ennen sitä. *pre-commit*-kehys hallitsee
koukkuja ja niiden työkaluja asetustiedostolla. Salaisuusskannerit
koukkuina käsitellään taidossa *Tietoturva kehitystyössä*.

## .gitignore

`.gitignore` kertoo, mitä seuraamattomia tiedostoja Git ei näytä eikä
lisää. Rivit ovat glob-kuvioita: `/` lopussa rajaa hakemistoihin, `/`
alussa repositorion juureen, `**` mihin tahansa syvyyteen, ja `!`
palauttaa aiemmin ohitetun:

```{.bash tiedosto="esimerkit/10-ignore.sh" osa="ignore"}
```

`git check-ignore -v` kertoo, mikä sääntö ohittaa tiedoston. Se on paras
työkalu, kun tiedosto ei näy tai näkyy odottamatta. `.gitignore` koskee
vain seuraamattomia tiedostoja. Jo versionhallinnassa oleva tiedosto
seurataan yhä, kunnes se poistetaan seurannasta:

```{.bash tiedosto="esimerkit/10-ignore.sh" osa="seurattu"}
```

```{.tuloste tiedosto="esimerkit/10-ignore.odotettu"}
```

Projektin `.gitignore` sisältää projektin tuotokset (käännöshakemistot,
riippuvuudet, lokit). Henkilökohtaiset editori- ja käyttöjärjestelmä-
tiedostot (`.idea/`, `.DS_Store`) kuuluvat omaan globaaliin tiedostoon
(`core.excludesFile`). Repositoriokohtaiset paikalliset poikkeukset
menevät tiedostoon `.git/info/exclude`.

## .gitattributes

`.gitattributes` liittää tiedostoihin attribuutteja kuvioiden perusteella.
Tärkeimmät:

| Attribuutti | Merkitys |
|-------------|----------|
| `text`, `eol=lf` | Rivinvaihdot normalisoidaan; työhakemistoon LF |
| `binary` | Sama kuin `-text -diff -merge`: ei muunnoksia eikä rividiffiä |
| `-diff` | Ei tekstidiffiä (esim. generoidut tiedostot) |
| `merge=binary` | Ei rivikohtaista yhdistämistä, konflikti koko tiedostosta |
| `export-ignore` | Ei mukaan `git archive` -arkistoon |
| `filter=lfs` | Sisältö Git LFS:ään (asettaa `git lfs track`) |

```{.bash tiedosto="esimerkit/10-attribuutit.sh" osa="attribuutit"}
```

Rivinvaihdot ovat yleisin syy attribuutteihin. Windows-editori tallentaa
CRLF:n, ja ilman sääntöä jokainen rivi näyttää muuttuneen. `text eol=lf`
tallentaa repositorioon aina LF:n:

```{.bash tiedosto="esimerkit/10-attribuutit.sh" osa="crlf"}
```

```{.tuloste tiedosto="esimerkit/10-attribuutit.odotettu"}
```

`git ls-files --eol` kertoo rivinvaihdot repositoriossa (`i/`) ja
työhakemistossa (`w/`). Tiedosto, jossa on CRLF, tallentui LF:nä, ja se
muunnetaan työhakemistossa seuraavalla kerralla, kun Git kirjoittaa sen.
`export-ignore` jätti testihakemiston pois julkaisuarkistosta.

## Käytännössä

- **`.gitattributes` jokaiseen projektiin**, jossa on kehittäjiä usealla
  käyttöjärjestelmällä. Rivi `* text=auto eol=lf` ratkaisee suurimman osan
  ongelmista. Windowsin skriptit (`*.bat`, `*.cmd`) tarvitsevat CRLF:n.
- **Koukut nopeiksi.** Yli muutaman sekunnin `pre-commit` ohitetaan
  ennen pitkää. Raskaat tarkistukset kuuluvat `pre-push`iin tai CI:hin.
- **`.gitignore` ennen ensimmäistä committia.** Vahingossa commitoitu
  `node_modules` tai `.env` jää historiaan, vaikka se myöhemmin poistetaan.
- **Mallipohjat.** GitHubin `gitignore`-kokoelma sisältää valmiit
  pohjat useimmille kielille ja työkaluille.

## Itsearviointi

- Osaat kirjoittaa pre-commit- ja commit-msg-koukun ja jakaa ne tiimille
  `core.hooksPath`illa, ja tiedät, miksi koukku ei korvaa CI:tä.
- Osaat kirjoittaa `.gitignore`-säännöt, selvittää `check-ignore -v`:llä,
  mikä sääntö vaikuttaa, ja poistaa jo seuratun tiedoston seurannasta.
- Osaat normalisoida rivinvaihdot ja merkitä binääri- ja generoidut
  tiedostot `.gitattributes`illa.
