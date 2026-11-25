# Johdanto {.runko-johdanto}

Bash on Unix-järjestelmien komentotulkki ja samalla ohjelmointikieli,
jolla automatisoidaan komentojen ajamista: asennuksia, käännöksiä,
varmuuskopioita, julkaisuja ja jatkuvan integraation vaiheita. Bash-skripti
on liimaa, joka yhdistää muita ohjelmia. Sen vahvuus on, että komentorivillä
kokeiltu komento siirtyy skriptiin sellaisenaan. Heikkous on, että kieli
on kasvanut vuosikymmenten kuluessa kerros kerrallaan ja sisältää ansoja,
joihin kokenutkin ohjelmoija kompastuu.

Tämä tutoriaali opettaa kirjoittamaan Bash-skriptejä, jotka toimivat myös
silloin, kun tiedostonimessä on välilyönti, komento epäonnistuu tai skripti
keskeytetään kesken ajon.

## Historia

- **1979** Stephen Bournen *Bourne shell* (`sh`) julkaistiin Unixin
  versiossa 7. Sen syntaksi (`if … fi`, `case … esac`, putket ja
  uudelleenohjaukset) on edelleen kaikkien Unix-kuorten perusta.
- **1989** Brian Fox kirjoitti GNU-projektille vapaan korvaajan, *Bourne
  Again Shellin*. Chet Ramey on ylläpitänyt Bashia 1990-luvun alusta.
- **1992** POSIX standardoi kuoren kielen (nykyisin IEEE Std 1003.1,
  *Shell and Utilities*). Bash noudattaa standardia ja laajentaa sitä.
- **2009** Bash 4.0 toi assosiatiiviset taulukot, `mapfile`-komennon ja
  kirjainkoon muunnokset. Versio 4.3 (2014) lisäsi nimiviittaukset ja
  `wait -n`:n.
- **2019–2025** Bash 5.x: `EPOCHREALTIME`, `wait -p`, parannuksia
  virheilmoituksiin ja suorituskykyyn. Versio 5.3 julkaistiin 2025.

Tämä tutoriaali käyttää Bash 5.2:ta, joka on esimerkiksi Ubuntu 24.04:n
ja Debian 12:n oletusversio. Kunkin ominaisuuden vähimmäisversio
mainitaan, kun se on uudempi kuin 4.0.

## Mihin Bash sopii ja mihin ei

Bash sopii, kun työ on pääosin muiden ohjelmien ajamista:

- asennus- ja käyttöönottoskriptit, konttien käynnistysskriptit
  (*entrypoint*) ja CI-putkien vaiheet
- tiedostojen siirtely, pakkaaminen ja varmuuskopiointi
- komentoriviohjelmien yhdistäminen putkiksi (`find`, `grep`, `sort`,
  `awk`, `curl`, `jq`)
- kehittäjän apuskriptit, joiden on toimittava missä tahansa
  Linux-koneessa ilman asennuksia

Bash ei sovi, kun ohjelmassa on omaa logiikkaa:

- **Tietorakenteet.** Kieli tuntee vain merkkijonot, yksiulotteiset
  taulukot ja assosiatiiviset taulukot. Sisäkkäisiä rakenteita ei ole.
- **Laskenta.** Aritmetiikka on kokonaislukuaritmetiikkaa, eikä
  liukulukuja ole.
- **Rakenteiset tiedostomuodot.** JSONia, XML:ää tai CSV:tä lainattuine
  kenttineen ei voi jäsentää luotettavasti Bashilla itsellään.
- **Koko.** Kun skriptissä on satoja rivejä omaa logiikkaa, virheiden
  käsittely ja testaus tulevat kalliiksi. Luvussa 12 on nyrkkisäännöt
  siihen, milloin vaihtaa Pythoniin.

## Kuoret ja standardit

| Kuori | Missä | Huomio |
|-------|-------|--------|
| POSIX `sh` | standardi | pienin yhteinen nimittäjä; ei taulukoita eikä `[[ ]]`:ta |
| `dash` | Debianin ja Ubuntun `/bin/sh` | nopea, lähes puhdas POSIX |
| BusyBox `ash` | Alpine-kontit, sulautettu Linux | POSIX ja muutama laajennus |
| `bash` | lähes kaikki Linux-jakelut | tämän tutoriaalin kieli |
| `bash` 3.2 | macOS:n `/bin/bash` | vanha versio lisenssisyistä; asenna uudempi |
| `zsh` | macOS:n oletuskuori vuodesta 2019 | interaktiivinen käyttö; eri semantiikka |

Skriptin ensimmäinen rivi (*shebang*) valitsee tulkin. Tutoriaalin
skriptit alkavat rivillä `#!/usr/bin/env bash`, joka hakee Bashin
polusta. Jos skripti alkaa rivillä `#!/bin/sh`, se ajetaan Debianissa
dashilla, eivätkä Bashin laajennukset toimi. Skriptin kieli on siis
päätettävä tietoisesti: POSIX-`sh`, kun skriptin on toimittava
pienimmissäkin ympäristöissä, ja Bash muualla.

## Esitiedot ja rajaus

Esitietoina ovat taidot *Komentorivi ja Linux* (tiedostot, oikeudet,
prosessit, putket ja uudelleenohjaukset interaktiivisessa käytössä) ja
*Ohjelmoinnin perusteet (Python)* (muuttujat, ehdot, silmukat ja
funktiot). Bashin omat piirteet, kuten lainaus, laajennukset, paluuarvot
ja virheiden käsittely, käydään läpi alusta.

Tutoriaali ei opeta komentorivin perustyökaluja uudelleen: ne ovat
taidossa *Komentorivi ja Linux*. Käännösten, testien ja jatkuvan
integraation automatisointi on taidossa *Käännösjärjestelmät, testaus ja
CI*, ja suuremmat työkalut kirjoitetaan Pythonilla (taito *Python
työkaluohjelmointiin*).

Toisessa kielessä kokenut lukija aloittaa luvusta 2, joka kokoaa Bashin
ajattelutavan, hinnat ja sudenkuopat. Jokaisen luvun lopussa on
itsearviointi, jonka perusteella luvun voi ohittaa.

## Työkalut

- **ShellCheck** (<https://www.shellcheck.net>) on skriptien staattinen
  analysaattori. Se löytää lainausvirheet, sudenkuopat ja
  siirrettävyysongelmat ennen ajoa. Tutoriaalin kaikki esimerkit läpäisevät
  sen ilman varoituksia. Luku 11 käsittelee sitä tarkemmin.
- **shfmt** muotoilee skriptit yhtenäisesti.
- **bats-core** on Bash-skriptien testikehys (luku 11).
- **`bash -n`** tarkistaa syntaksin ajamatta skriptiä, ja **`bash -x`**
  näyttää jokaisen komennon ennen sen suorittamista.

Kehityskontissa ovat valmiina Bash 5.2, ShellCheck ja bats. Skripti
tarkistetaan ja ajetaan näin:

```text
shellcheck lokiyhteenveto.sh
bash lokiyhteenveto.sh < palvelu.log
```

## Ensimmäinen ohjelma

Ensimmäinen skripti tiivistää palvelun lokin: se laskee rivit
lokitasoittain ja kertoo, millä riveillä virheet ovat. Lokirivi on muotoa
`aikaleima TASO viesti`.

```{.bash tiedosto="esimerkit/01-lokiyhteenveto.sh"}
```

Syötteellä

```{.tuloste tiedosto="esimerkit/01-lokiyhteenveto.syote"}
```

skripti tulostaa

```{.tuloste tiedosto="esimerkit/01-lokiyhteenveto.odotettu"}
```

Lyhyessäkin skriptissä on monta tämän tutoriaalin teemaa:

- `set -euo pipefail` pysäyttää skriptin virheeseen ja asettamattoman
  muuttujan käyttöön (luku 7).
- `while IFS= read -r rivi` on rivien lukemisen idiomi: `IFS=` säilyttää
  rivin alun ja lopun välilyönnit ja `-r` kenoviivat (luku 6).
- `read -r _ taso _ <<< "$rivi"` jakaa rivin sanoiksi ja ottaa talteen
  vain toisen. Alaviiva on sovittu nimi hylättävälle arvolle.
- `local -A maarat` on assosiatiivinen taulukko ja `virheet+=(…)` lisää
  alkion taulukkoon (luku 5).
- `main "$@"` viimeisenä rivinä: koko logiikka on funktioissa, ja
  skripti suoritetaan vasta, kun Bash on lukenut sen kokonaan. Näin
  kesken ajon muokattu tiedosto ei sotke käynnissä olevaa ajoa.

## Esimerkkien testaus

Kaikki tutoriaalin koodi on peräisin hakemiston `esimerkit` tiedostoista.
Testaaja tarkistaa jokaisen ShellCheckillä varoitukset virheinä, ajaa sen
tyhjässä väliaikaisessa hakemistossa ja vertaa tulostetta tiedostoon,
josta myös tekstin tulosteet on poimittu.

Osa esimerkeistä näyttää virheellistä koodia. Tiedosto
`nimi.ei-kaanny.sh` ei saa läpäistä ShellCheckiä sellaisenaan, mutta sen
on läpäistävä ja toimittava, kun rivit, joilla on merkintä `@virhe`,
poistetaan. Tiedoston `nimi.kaatuu.sh` on päätyttävä virheeseen, ja
virhetulosteen on sisällettävä odotettu ilmoitus.
