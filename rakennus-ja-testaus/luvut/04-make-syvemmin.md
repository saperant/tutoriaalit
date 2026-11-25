# Make syvemmin

Edellisen luvun Makefile toimi, mutta siinä oli kolme puutetta, jotka
jokainen kasvava projekti kohtaa: otsakeriippuvuudet puuttuivat,
jokaiselle tiedostolle oli oma sääntönsä, ja käännöstuotteet
sekoittuivat lähdekoodiin. Tässä luvussa ne korjataan. Lopputulos on
Makefile, jonka rakennetta voi käyttää sellaisenaan C-projektin
pohjana.

## Muuttujat ja niiden sijoitus

Makessa on neljä sijoitusoperaattoria, ja niiden ero on merkittävä:

| Operaattori | Merkitys |
|-------------|----------|
| `=` | laiska: arvo lasketaan joka käyttökerralla uudelleen |
| `:=` | välitön: arvo lasketaan kerran, sijoitushetkellä |
| `?=` | oletus: sijoitetaan vain, jos muuttujalla ei ole arvoa |
| `+=` | lisää loppuun |

Välitön sijoitus `:=` on turvallisin oletus: arvo ei muutu
yllättäen, ja raskas `$(shell ...)` tai `$(wildcard ...)` ajetaan vain
kerran. Laiskaa sijoitusta tarvitaan, kun arvo viittaa muuttujaan, joka
määritellään vasta myöhemmin. Uuden Makefilen muuttujat:

```{.makefile tiedosto="esimerkit/04-make-syvemmin/Makefile" osa="muuttujat"}
```

`$(wildcard lahde/*.c)` etsii lähdetiedostot, joten uutta tiedostoa ei
tarvitse lisätä Makefileen. Korvauslauseke
`$(LAHTEET:$(LAHDE)/%.c=$(RAKENNUS)/%.o)` muuttaa jokaisen polun
`lahde/x.c` muotoon `build/x.o`. Monessa projektissa tiedostot
luetellaan silti käsin, jotta hakemistoon unohtunut kokeilutiedosto ei
päädy ohjelmaan. Kumpikin on perusteltu valinta, kunhan se on
tietoinen.

Varoitusliput ovat omassa muuttujassaan `PAKOLLISET`, ja `CFLAGS`
saa arvon `?=`-operaattorilla. Käyttäjä voi siis vaihtaa optimoinnin
(`make CFLAGS=-O0`) ilman, että varoitukset ja kielistandardi katoavat.
Komentorivillä annettu muuttuja ohittaa Makefilen sijoitukset, joten
jos kaikki liput olisivat muuttujassa `CFLAGS`, yksi komentorivin
arvo poistaisi ne kaikki.

## Mallisäännöt ja automaattiset riippuvuudet

Mallisääntö kuvaa, miten minkä tahansa tietyn muotoisen kohteen saa
tehtyä. Merkki `%` vastaa samaa merkkijonoa kohteessa ja
riippuvuudessa:

```{.makefile tiedosto="esimerkit/04-make-syvemmin/Makefile" osa="saannot"}
```

Säännöissä on kolme tärkeää yksityiskohtaa.

**Automaattiset riippuvuudet.** Valitsin `-MMD` pyytää kääntäjää
kirjoittamaan käännöksen ohessa tiedoston `build/x.d`, jossa on
Make-sääntö: objektitiedosto riippuu lähteestä ja kaikista
otsakkeista, jotka kääntäjä luki. Järjestelmäotsakkeet jätetään pois
(`-MD` ottaisi nekin). `-MP` lisää jokaiselle otsakkeelle tyhjän
säännön, jotta poistettu otsake ei kaada rakennusta virheeseen `No rule
to make target`. Rivi `-include $(OBJEKTIT:.o=.d)` lukee tiedostot
Makefileen; miinusmerkki ohittaa ne, joita ei vielä ole. Ensimmäisellä
kerralla riippuvuuksia ei tarvita, koska kaikki käännetään joka
tapauksessa.

**Järjestysriippuvuus.** Pystyviivan jälkeinen `$(RAKENNUS)` on
riippuvuus, jonka on oltava olemassa ennen kohdetta, mutta jonka
muutosaika ei tee kohteesta vanhentunutta. Tavallisena riippuvuutena
hakemisto pakottaisi kaikki objektit uudelleen käännettäviksi aina,
kun hakemistoon lisätään tiedosto, koska hakemiston muutosaika
päivittyy silloin.

**Hiljainen tuloste.** Pitkät käännöskomennot hukuttavat varoitukset,
joten sääntö tulostaa vain lyhyen rivin, ja varsinainen komento
piilotetaan `@`-merkillä. Muuttuja `Q` on tyhjä, kun käyttäjä antaa
`V=1`, jolloin komennot näkyvät kokonaan. Sama käytäntö on
esimerkiksi Linuxin ytimen rakennusjärjestelmässä. CI:ssä komennot
kannattaa näyttää kokonaan, koska lokista halutaan nähdä tarkat liput.

Esimerkki kokeilee rakennusta, katsoo kääntäjän kirjoittaman
riippuvuustiedoston ja muuttaa otsaketta:

```{.bash tiedosto="esimerkit/04-make-syvemmin/aja.sh"}
```

```{.tuloste tiedosto="esimerkit/04-make-syvemmin.odotettu"}
```

Nyt otsakkeen muutos kääntää molemmat sitä lukevat tiedostot. Sama
näkyy riippuvuusverkosta, joka on piirretty Maken tietokannasta
ensimmäisen rakennuksen jälkeen samalla skriptillä kuin edellisessä
luvussa. Kääntäjän kirjoittamat `.d`-tiedostot ovat tuoneet verkkoon
otsakkeen ja kaksi uutta kaarta:

```{.dot tiedosto="esimerkit/04-make-syvemmin/verkko.dot" otsikko="Riippuvuusverkko, kun kääntäjän kirjoittamat `.d`-tiedostot on luettu mukaan. Otsakkeesta `lahde/tilasto.h` lähtee kaari kumpaankin objektitiedostoon."}
```

`make -n V=1` näyttää täydet komennot ajamatta niitä; siitä näkee
myös lippujen järjestyksen: `CPPFLAGS`, pakolliset liput ja
käyttäjän `CFLAGS`. Käyttäjän `-O0` tulee viimeisenä ja voittaa
siksi aiemmat optimointitasot. Varoitukset pysyvät mukana.

## Rinnakkainen rakennus

`make -j4` ajaa enintään neljä komentoa yhtä aikaa. Make ajaa
rinnakkain vain sellaiset kohteet, joiden välillä ei ole riippuvuutta,
joten oikein kuvattu Makefile on automaattisesti rinnakkaistettavissa.
Väärin kuvattu ei ole: jos kaksi sääntöä kirjoittaa samaan
tiedostoon tai jos jokin sääntö tarvitsee tiedoston, jota se ei
mainitse riippuvuutena, rakennus toimii peräkkäin mutta satunnaisesti
rikki rinnakkain. Tyypillinen esimerkki on käännöshakemisto, jota
mikään sääntö ei luo ennen objekteja; tässä siitä huolehtii
järjestysriippuvuus.

Rinnakkaisuus kannattaa testata puhtaalta pöydältä, kuten esimerkki
tekee (`make siivoa`, sitten `make -j4`), koska vain silloin kaikki
säännöt kilpailevat keskenään. Prosessorien määrän saa komennolla
`nproc`. Jos Makefile kutsuu toista Makea (`$(MAKE) -C alihakemisto`),
kutsussa on käytettävä muuttujaa `$(MAKE)`, ei sanaa `make`. Silloin
alimake jakaa saman työpaikkavarannon (*jobserver*) eikä käynnistä
omia neljää rinnakkaista työtään jokaiselle alihakemistolle.

## Rekursiivinen vai yksi Makefile

Suurissa projekteissa on kaksi tapaa jakaa Makefile. Rekursiivisessa
mallissa jokaisella hakemistolla on oma Makefile, ja ylempi kutsuu
alempia. Malli on helppo ymmärtää, mutta Make näkee kerrallaan vain
yhden hakemiston riippuvuudet: hakemistojen välinen riippuvuus on
kirjoitettava käsin järjestykseksi, ja rinnakkaisuus kärsii. Peter
Millerin artikkeli *Recursive Make Considered Harmful* (1998) kuvasi
ongelman, ja sen ratkaisu on yksi Makefile, joka lukee hakemistojen
osat `include`-direktiivillä. Silloin Make näkee koko riippuvuusgraafin.
Kun projekti kasvaa tähän kokoon, CMake ja Ninja ovat yleensä parempi
valinta.

## Käytännössä

- **`-MMD -MP` jokaiseen C-Makefileen.** Automaattiset riippuvuudet
  ovat kaksi lippua ja yksi `-include`-rivi. Ilman niitä Makefile on
  rikki ensimmäisestä otsakemuutoksesta alkaen.
- **Käännöstuotteet omaan hakemistoonsa.** `build/` pitää lähdepuun
  siistinä, `siivoa` on yksi `rm -rf`, ja `.gitignore` tarvitsee
  yhden rivin. Samasta lähteestä voi rakentaa useita versioita eri
  hakemistoihin.
- **Pakolliset liput erillään käyttäjän lipuista.** Käyttäjän
  `CFLAGS` ei saa poistaa varoituksia, standardia tai `-MMD`:tä.
- **Testaa `make -j` puhtaalta pöydältä.** Rinnakkaisuuden virheet
  ovat puuttuvia riippuvuuksia, ja ne näkyvät vain, kun kaikki säännöt
  ajetaan samaan aikaan.
- **`$(MAKE)`, ei `make`.** Alimaken kutsu muuttujan kautta välittää
  valitsimet ja jakaa työpaikat.

## Itsearviointi

- Osaat valita sijoitusoperaattorin (`=`, `:=`, `?=`, `+=`) ja
  perustella valinnan.
- Osaat kirjoittaa mallisäännön, joka kääntää lähteet erilliseen
  käännöshakemistoon, ja selittää järjestysriippuvuuden tarpeen.
- Osaat ottaa käyttöön kääntäjän tuottamat riippuvuudet (`-MMD -MP`
  ja `-include`) ja lukea `.d`-tiedoston.
- Osaat kertoa, miksi Makefile voi toimia peräkkäin mutta ei
  rinnakkain, ja miten sen testaa.
