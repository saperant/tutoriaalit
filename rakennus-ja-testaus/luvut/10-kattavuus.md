# Kattavuus

Testit kertovat, toimiiko testattu koodi. Ne eivät kerro, mitä jäi
testaamatta. *Kattavuusmittaus* (*code coverage*) laskee, mitkä rivit
ja haarat testiajo suoritti. Se ei mittaa testien laatua: rivi voi
tulla suoritetuksi ilman, että yksikään tarkistus koskee sen tulosta.
Se kertoo kuitenkin varmasti, mitä *ei* testattu, ja se on hyödyllisin
tieto, jonka kattavuus antaa.

## gcov ja gcovr

GCC:n kattavuusmittaus koostuu kolmesta osasta. Valitsin `--coverage`
lisää käännökseen laskurit, jotka kasvavat jokaisen peruslohkon
suorituksessa, ja kirjoittaa koodin rakenteen tiedostoon `.gcno`.
Ohjelma kirjoittaa laskurit lopussa tiedostoon `.gcda`. `gcov` yhdistää
nämä lähdekoodiin, ja `gcovr` kokoaa tuloksen raportiksi koko
projektista. Clangilla vastaava on `-fprofile-instr-generate
-fcoverage-mapping` ja `llvm-cov`.

Esimerkin testit ovat tavallisen näköiset, mutta niistä puuttuu kaksi
tapausta:

```{.c tiedosto="esimerkit/09-kattavuus/testit.c"}
```

Komentosarja kääntää kirjaston ja testit kattavuuslaskureilla, ajaa
testit ja raportoi kirjaston rivikattavuuden. Toisella kerralla
mukana ovat myös puuttuneet tapaukset:

```{.bash tiedosto="esimerkit/09-kattavuus/aja.sh" osa="kattavuus"}
```

```{.tuloste tiedosto="esimerkit/09-kattavuus.odotettu"}
```

Raportti kertoo puuttuvat rivit numeroina. Rivi 17 on yhden arvon
sarjan erikoistapaus ja rivi 37 parillisen pituuden mediaani:

```{.c tiedosto="esimerkit/lahde/tilasto.c"}
```

Kumpikin on juuri sellainen rajatapaus, jossa virheet piilevät.
Parillisen pituuden mediaanissa on kaksi indeksiä, joista toinen on
helppo kirjoittaa väärin, ja yhden arvon hajonnassa jakaja olisi nolla
ilman erikoistapausta. 90 prosentin kattavuus kuulostaa hyvältä, mutta
puuttuvat 10 prosenttia ovat koodin vaikein osa.

`--filter lahde/` rajaa raportin projektin omaan koodiin, jotta testit
itse eivät nosta lukua. `--object-directory` kertoo, missä
`.gcda`-tiedostot ovat, ja `--gcov-executable` valitsee kääntäjää
vastaavan gcov-version: GCC 14:n tuottamat tiedostot vaativat GCC 14:n
gcovin.

## Rivit, haarat ja ehdot

Rivikattavuus on karkein mittari. Rivi `return sivu > RAJA ? -1 :
NELIO(sivu);` on katettu, vaikka testi kokeilisi vain toista haaraa.
`gcovr --txt-metric branch` raportoi haarakattavuuden: kumpikin haara
jokaisesta ehdosta. Tiukin tavallinen mittari on MC/DC (*modified
condition/decision coverage*), jossa jokaisen ehdon osan on osoitettu
vaikuttavan tulokseen. Ilmailun ja autoteollisuuden turvallisuusstandardit
(DO-178C, ISO 26262) vaativat sitä kriittisimmälle koodille, ja GCC 14
osaa mitata sen valitsimella `-fcondition-coverage`.

Optimointi sotkee rivien ja konekoodin vastaavuuden, joten kattavuus
mitataan valitsimella `-O0`. Raportti kannattaa tuottaa myös HTML:nä
(`--html-details kattavuus/index.html`), jolloin jokainen tiedosto
näkyy värikoodattuna: punainen rivi on suorittamaton. CI tallentaa sen
artefaktiksi, kuten luvussa 12 tehdään.

## Kynnys ja sen asettaminen

`gcovr --fail-under-line 90` palauttaa virheen, jos kattavuus jää alle
kynnyksen. Kynnys estää kattavuuden hiljaisen laskun, mutta se on
helppo asettaa väärin:

- **Liian korkea kynnys** houkuttelee kirjoittamaan testejä, jotka
  suorittavat rivejä tarkistamatta mitään. 100 prosentin vaatimus
  pakottaa testaamaan myös koodia, jota ei voi järkevästi testata,
  kuten tulostusvirheiden käsittelyä.
- **Kiinteä kynnys koko projektille** piilottaa kriittisen moduulin
  puutteet keskiarvoon. Kynnyksen voi asettaa tiedostokohtaisesti tai
  vaatia, ettei muutos laske kattavuutta (*diff coverage*).
- **Kynnys ilman tarkastelua** on pelkkä luku. Arvokkain käyttö on
  lukea, mitkä rivit jäivät kattamatta, ja päättää jokaisesta, onko se
  hyväksyttävää.

Kattavuudelle täydentävä työkalu on *mutaatiotestaus* (esimerkiksi
Mull C- ja C++-koodille): se muuttaa koodia pienin askelin (`<` muotoon
`<=`, `+` muotoon `-`) ja tarkistaa, huomaavatko testit muutoksen.
Selviytynyt mutantti on rivi, joka on katettu mutta jota mikään
tarkistus ei oikeasti testaa.

## Käytännössä

- **Lue puuttuvat rivit, älä pelkkää lukua.** Kattamattomat rivit
  ovat lähes aina rajatapauksia ja virhepolkuja, eli juuri sitä, mitä
  testien kuuluu kokeilla.
- **Mittaa vain omaa koodia.** Testit, vendoroidut kirjastot ja
  generoitu koodi rajataan pois, muuten luku ei kerro mitään.
- **Haarakattavuus rivikattavuuden lisäksi.** Yhden rivin ehtolauseke
  voi olla katettu, vaikka vain toinen haara on testattu.
- **Kynnys estää laskun, ei takaa laatua.** Kohtuullinen kynnys CI:ssä
  ja muutoskohtainen tarkastelu katselmoinnissa toimivat paremmin kuin
  100 prosentin vaatimus.
- **Sama kääntäjäversio mittaukseen ja raporttiin.** Väärä gcov ei
  osaa lukea toisen version tiedostoja ja antaa virheen tai, pahempaa,
  väärän tuloksen.

## Itsearviointi

- Osaat mitata C-koodin rivikattavuuden valitsimella `--coverage` ja
  raportoida sen gcovrilla vain projektin omasta koodista.
- Osaat lukea kattavuusraportista puuttuvat rivit ja kirjoittaa niille
  testit.
- Osaat kertoa rivi-, haara- ja MC/DC-kattavuuden erot.
- Osaat asettaa kattavuuskynnyksen CI:hin ja perustella sen tason.
