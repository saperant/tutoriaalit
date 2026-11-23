# Työkalut: ShellCheck, jäljitys ja testaus {.runko-tyokalut}

Bash-skriptiä ei käännetä, joten virheet löytyvät oletuksena vasta
ajossa, usein tuotannossa ja harvinaisella syötteellä. Tämä luku käy
läpi työkalut, jotka siirtävät virheiden löytämisen aikaisemmaksi:
staattisen analyysin, jäljityksen ja yksikkötestit. Testauksen ja CI:n
yleiset periaatteet käsitellään taitopuun taidossa *Käännösjärjestelmät,
testaus ja CI*.

## ShellCheck

ShellCheck lukee skriptin ja varoittaa yleisistä virheistä:
lainaamattomista laajennuksista, `set -e`:n aukoista, väärin kirjoitetuista
testeistä, siirrettävyysongelmista ja käyttämättömistä muuttujista.
Jokaisella varoituksella on tunnus, kuten SC2086, ja wikisivu, joka
selittää ongelman ja korjauksen.

```{.bash tiedosto="esimerkit/11-tarkistin.ei-kaanny.sh" osa="virheet"}
```

```{.tuloste tiedosto="esimerkit/11-tarkistin.odotettu"}
```

Kukin `@virhe`-rivi on tyypillinen virhe, jonka korjattu versio on sen
alla:

- **SC2045:** `ls`-tulosteen läpikäynti jakaa nimet välilyönneistä.
- **SC2086:** lainaamaton muuttuja komennon argumenttina.
- **SC2070:** `[ -n $x ]` on tyhjällä `x`:llä `[ -n ]`, joka on aina
  tosi. Ehto toimi siis väärin juuri silloin, kun sen piti estää jotain.

ShellCheckin käyttö:

```text
shellcheck skripti.sh             # yksi tiedosto
shellcheck -x main.sh lib/*.sh    # -x seuraa source-komentoja
shellcheck -S warning *.sh        # vain varoitukset ja virheet
shellcheck -f gcc *.sh            # editorin ymmärtämä muoto
```

Varoituksen voi vaientaa kommentilla `# shellcheck disable=SC2086`
seuraavalta komennolta tai, tiedoston alussa ennen ensimmäistä komentoa,
koko tiedostosta. Vaiennus perustellaan aina kommentilla, kuten tämän
tutoriaalin tarkoituksella virheellisissä esimerkeissä. Projektin
yhteiset asetukset kirjoitetaan tiedostoon `.shellcheckrc`.

Editorilaajennukset (VS Code, Vim, Emacs) näyttävät ShellCheckin
varoitukset kirjoitettaessa. CI:ssä ShellCheck ajetaan kaikille
skripteille, ja varoitus estää yhdistämisen.

## Muotoilu: shfmt

`shfmt` muotoilee skriptit yhtenäisesti, kuten `gofmt` tai `black`.
`shfmt -d -i 4 -ci *.sh` näyttää erot neljän välilyönnin sisennykseen,
ja `-w` kirjoittaa muutokset. Yhtenäinen muotoilu tekee
koodikatselmoinneista sisällön eikä tyylin tarkastelua.

## Syntaksi ja jäljitys

`bash -n skripti.sh` jäsentää skriptin ajamatta sitä ja löytää
syntaksivirheet, kuten puuttuvan `fi`:n. `bash -x skripti.sh` tai
skriptin sisällä `set -x` tulostaa jokaisen komennon laajennusten
jälkeen ennen sen suorittamista. Jäljitys näyttää, mitä argumentteja
komento todella sai, mikä ratkaisee useimmat lainausongelmat.

Muuttuja `PS4` määrää jäljitysrivin etuliitteen. Kun siihen lisätään
funktion nimi ja rivinumero, pitkästäkin jäljestä näkee, mistä rivi on
peräisin. `BASH_XTRACEFD` (4.1) ohjaa jäljen omaan tiedostoonsa, jolloin
se ei sekoitu skriptin virhetulosteeseen:

```{.bash tiedosto="esimerkit/11-jaljitys.sh" osa="jaljitys"}
```

```{.tuloste tiedosto="esimerkit/11-jaljitys.odotettu"}
```

Plusmerkkien määrä kertoo sisäkkäisyyden: komentokorvauksen sisällä
suoritetut rivit ovat tasolla kaksi. Rivinumerot viittaavat
esimerkkitiedostoon. Jäljitys paljastaa myös salaisuudet, kuten
komentoriville annetut salasanat, joten CI-lokeissa se kytketään päälle
vain rajatuissa kohdissa.

## Profilointi

Hidas skripti on lähes aina hidas samasta syystä: silmukassa
käynnistetään ulkoisia komentoja (luku 2). Kokonaisaika mitataan
komennolla `time skripti.sh`, ja *user*- ja *sys*-ajan suuri osuus
kertoo prosessien käynnistyksestä. Tarkempi kuva saadaan jäljityksellä,
jossa `PS4` sisältää aikaleiman: `PS4='+ $EPOCHREALTIME ${LINENO}: '`.
`EPOCHREALTIME` (5.0) on mikrosekuntitarkka kellonaika, ja peräkkäisten
rivien erotus kertoo, mihin aika kului.

## Testaus batsilla

bats-core (*Bash Automated Testing System*) on Bash-skriptien
testikehys. Testitiedosto on Bash-skripti, jossa `@test`-lohkot ovat
testejä. Testi onnistuu, jos sen kaikki komennot onnistuvat; jokainen
rivi on siis väite.

Testattava koodi on kirjasto, jonka funktiot ovat puhtaita: ne lukevat
argumentit ja tulostavat tuloksen. Hinnoittelukirjasto käsittelee
rahamäärät sentteinä:

```{.bash tiedosto="esimerkit/11-bats/hinta.sh" osa="kirjasto"}
```

```{.bash tiedosto="esimerkit/11-bats/hinta.bats"}
```

`setup` suoritetaan ennen jokaista testiä, ja `load` lataa kirjaston
testitiedoston hakemistosta. `run` ajaa komennon niin, että sen
epäonnistuminen ei kaada testiä, ja tallentaa paluuarvon muuttujaan
`status` ja tulosteen muuttujaan `output`. Ilman `run`:ia epäonnistuva
komento päättää testin epäonnistuneena, mikä on oikein komennoille,
joiden pitää onnistua.

Testit ajetaan komennolla `bats hinta.bats` tai hakemistolle
`bats testit/`. Esimerkin pääohjelma ajaa ne TAP-muodossa, jota
CI-järjestelmät osaavat lukea:

```{.bash tiedosto="esimerkit/11-bats/main.sh"}
```

```{.tuloste tiedosto="esimerkit/11-bats.odotettu"}
```

Kokonaisen skriptin testaamiseen on kaksi tapaa:

- **Funktiot.** Skripti kirjoitetaan niin, että sen voi ladata
  käynnistämättä pääohjelmaa (`[[ ${BASH_SOURCE[0]} == "$0" ]] &&
  main "$@"`, luku 8), ja testit kutsuvat funktioita suoraan.
- **Mustana laatikkona.** `run ./skripti.sh -k 3 lahde` ajaa skriptin,
  ja testi tarkistaa paluuarvon, tulosteen ja syntyneet tiedostot.
  Testi luo syötteet väliaikaiseen hakemistoon (`$BATS_TEST_TMPDIR`), jotta
  testit eivät riipu toisistaan.

Ulkoiset riippuvuudet, kuten `curl` tai `systemctl`, korvataan testeissä
*tynkäkomennoilla*: testi luo hakemistoon samannimisen skriptin, joka
tulostaa ennalta määrätyn vastauksen, ja lisää hakemiston `PATH`:n
alkuun. Kirjastot `bats-assert` ja `bats-file` tarjoavat luettavampia
väitteitä, kuten `assert_output --partial`.

## Käytännössä

- **ShellCheck jokaiselle skriptille**, editorissa ja CI:ssä. Varoitukset
  ovat virheitä, ja jokainen vaiennus on perusteltu kommentissa.
- **`bash -n` ja shfmt** CI:n ensimmäisinä vaiheina; ne ovat nopeita.
- **`set -x` ja kuvaava `PS4`** vianetsintään. Jälki omaan tiedostoonsa
  `BASH_XTRACEFD`:llä, ja salaisuudet pois jäljityksen piiristä.
- **Logiikka puhtaisiin funktioihin**, jotka voi testata batsilla. Komentoja
  ajava ohjauskoodi pidetään ohuena.
- **Testit eristettyinä:** väliaikainen hakemisto, tynkäkomennot `PATH`:n
  alussa, kiinteä lokaali ja aika.
- **Mittaa ennen optimointia.** `time` ja aikaleimattu jäljitys
  kertovat, mikä silmukka käynnistää liikaa prosesseja.

## Itsearviointi

- Osaat ajaa ShellCheckin monitiedostoiselle skriptille, tulkita sen
  varoitukset ja vaientaa perustellun poikkeuksen.
- Osaat jäljittää skriptin suorituksen niin, että jäljestä näkee
  funktion ja rivin ja että jälki menee omaan tiedostoonsa.
- Osaat kirjoittaa bats-testin, joka tarkistaa funktion tulosteen ja
  paluuarvon `run`:n avulla.
- Osaat jäsentää skriptin niin, että sen funktiot voi testata ilman
  pääohjelman ajamista.
