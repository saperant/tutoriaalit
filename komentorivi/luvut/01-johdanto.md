# Johdanto {.runko-johdanto}

Komentorivi on edelleen tehokkain tapa käyttää Linux-järjestelmää.
Palvelimilla, konteissa, sulautetuissa laitteissa ja CI-putkissa
graafista käyttöliittymää ei yleensä ole. Kehittäjän työkaluketju, kuten
kääntäjät, versionhallinta, paketinhallinta ja testit, on rakennettu
komentoriville. Komentorivin hyöty ei ole yksittäisissä komennoissa
vaan niiden yhdistämisessä: pienistä työkaluista kootaan putki, joka
ratkaisee tehtävän, johon ei ole valmista ohjelmaa.

Tämä tutoriaali opettaa Linuxin käyttöä komentoriviltä: tiedostot ja
oikeudet, putket, tekstinkäsittelyn työkalut, prosessit, ympäristön,
paketit ja palvelut sekä etäkäytön. Esitietoja ei tarvita. Skriptien
kirjoittaminen, eli funktiot, virheenkäsittely ja luotettavat
automaatiot, opetetaan taidossa *Bash-skriptaus*, joka rakentuu tämän
päälle.

## Pääte, kuori ja komennot

Kolme käsitettä sekoitetaan usein:

- **Pääte** (*terminal*, esim. GNOME Terminal, Windows Terminal, iTerm2)
  on ohjelma, joka näyttää tekstiä ja välittää näppäilyt. Etäyhteydessä
  pääte on omalla koneella, mutta kaikki muu tapahtuu palvelimella.
- **Kuori** (*shell*, esim. Bash, Zsh, dash) lukee komentorivin, tekee
  laajennukset (muuttujat, jokerimerkit), käynnistää ohjelmat ja
  yhdistää ne putkiksi. Tässä tutoriaalissa kuori on Bash.
- **Komennot** ovat useimmiten erillisiä ohjelmia (`/usr/bin/grep`),
  osa kuoren sisäisiä komentoja (`cd`, `export`), joita ei voi toteuttaa
  erillisenä ohjelmana, koska ne muuttavat kuoren omaa tilaa.

Komento `type` kertoo, mikä nimi on, ja paluuarvo kertoo, onnistuiko
komento. Paluuarvo 0 tarkoittaa onnistumista, muu arvo epäonnistumista.
Kuoren `&&` ja `||` ketjuttavat komentoja paluuarvon perusteella:

```{.bash tiedosto="esimerkit/01-komento.sh" osa="tyyppi"}
```

```{.bash tiedosto="esimerkit/01-komento.sh" osa="paluuarvo"}
```

```{.tuloste tiedosto="esimerkit/01-komento.odotettu"}
```

`grep` palauttaa 1, kun osumia ei ole, ja 2 virheessä. `ls` palauttaa
2 vakavassa virheessä. Arvot on dokumentoitu kunkin komennon
ohjesivulla, ja niiden varaan voi rakentaa ehtoja.

## Komennon anatomia

```text
grep  -r -n  --include='*.c'  'malloc'  lahde/
^     ^       ^                ^         ^
|     |       |                |         operandi
|     |       |                hahmo (operandi)
|     |       pitkä valitsin arvon kanssa
|     lyhyet valitsimet, yhdistettävissä: -rn
komento
```

Lyhyet valitsimet alkavat yhdellä viivalla ja voidaan yhdistää
(`-rn`). Pitkät valitsimet (`--include`) ovat GNU-työkalujen tapa ja
selkeämpiä skripteissä. Erotin `--` päättää valitsimet: kaikki sen
jälkeen on operandeja, vaikka alkaisi viivalla (`rm -- -r`).

## Ohjeiden löytäminen

| Komento | Mitä antaa |
|---------|-----------|
| `man grep` | Täydellinen ohjesivu; `/sana` hakee, `n` seuraava, `q` lopettaa |
| `grep --help` | Valitsimet tiiviisti |
| `help cd` | Bashin sisäisten komentojen ohje |
| `man -k salasana` | Hakee ohjesivujen kuvauksista |
| `type -a nimi` | Mikä nimi on ja mistä se löytyy |
| `info coreutils` | GNU-työkalujen laaja käsikirja |

Ohjesivut on jaettu osioihin: 1 komennot, 5 tiedostomuodot, 8
ylläpitokomennot. `man 5 passwd` näyttää tiedoston `/etc/passwd`
muodon, `man passwd` komennon. Ohjesivun luku kannattaa aloittaa
osiosta *EXAMPLES*, jos sellainen on.

## Linux, GNU, POSIX ja muut

Linux on ydin. Käyttäjän näkemät työkalut tulevat useimmiten
GNU-projektista (coreutils, grep, sed, findutils, Bash). Muissa
ympäristöissä on samannimisiä työkaluja, joiden valitsimet eroavat:

- **macOS ja BSD:t**: BSD-versiot. Esimerkiksi `sed -i` vaatii macOS:ssä
  argumentin (`sed -i '' ...`), eikä `find -printf` ole käytettävissä.
  GNU-työkalut saa Homebrew'lla (`gsed`, `gfind`).
- **Alpine ja sulautetut järjestelmät**: BusyBox, jossa työkalut ovat
  suppeampia. Alpine-kontin `/bin/sh` ei ole Bash.
- **POSIX** määrittelee yhteisen ytimen. Skripti, jonka on toimittava
  kaikkialla, käyttää vain POSIX-valitsimia.

Tämä tutoriaali käyttää GNU-työkaluja Ubuntu 24.04:ssä ja mainitsee
GNU-laajennukset, kun ne ovat olennaisia.

## Mihin komentorivi ei sovellu

Putket ovat tehokkaita rivipohjaiselle tekstille. Ne sopivat huonosti

- rakenteiseen dataan: JSON:lle on `jq`, CSV:lle, jossa kentissä on
  lainattuja pilkkuja, tarvitaan oikea jäsennin (esim. Python)
- logiikkaan, jossa on paljon tilaa ja haaroja: kun komentorivi kasvaa
  yli muutaman rivin, se kuuluu skriptiin tai ohjelmaan
- binääridataan ja suuriin laskentoihin.

## Tutoriaalin esimerkit

Jokainen esimerkki on Bash-skripti, joka luo tarvitsemansa aineiston
väliaikaiseen hakemistoon, ajaa näytetyt komennot ja jonka tuloste
verrataan odotettuun. Tekstissä näytetään vain olennaiset komennot.
Skriptin alussa asetetaan `LC_ALL=C`, jotta lajittelu ja viestit ovat
samat kaikilla koneilla (luku *Ympäristö ja kuoren asetukset*).
Komennot, joita ei voi ajaa testiympäristössä, kuten `apt install`,
`systemctl` ja oikea `ssh`-yhteys, näytetään ilman tulostetta.

Kehityskontti `.devcontainer/komentorivi` sisältää samat työkalut.
Esimerkit ajetaan komennolla `make testaa`.
