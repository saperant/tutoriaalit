# Työkalut ja testaus {.runko-tyokalut}

Tcl-skriptien laadunvarmistus on usein pelkkää käsin kokeilua
työkalun konsolissa. Tämä luku näyttää, miten logiikkaa testataan
automaattisesti, miten virhettä jäljitetään ja mitä apuvälineitä on.

## Interaktiivinen käyttö

- `tclsh` ilman argumentteja on interaktiivinen tulkki. `rlwrap tclsh`
  lisää rivinmuokkauksen ja historian.
- `info commands kuvio`, `info procs`, `info args proc`, `info body
  proc` ja `info vars` kertovat tulkin tilan. EDA-työkalun konsolissa
  `info commands get_*` löytää komennot.
- `source tiedosto.tcl` lataa skriptin uudelleen ajossa olevaan
  tulkkiin, mikä nopeuttaa kokeilua.
- `parray taulukko` tulostaa taulukon ja `puts [dict get …]` sanakirjan
  osan.

## Yksikkötestit: tcltest

`tcltest` kuuluu Tcl:n perusasennukseen. Testi on komento `test nimi
kuvaus -body {…} -result odotettu`. Valitsimet `-setup` ja `-cleanup`
valmistelevat ja siivoavat, `-returnCodes error` odottaa virhettä, ja
`-errorCode` tarkistaa virhekoodin. Oletuksena tulos vertaillaan
tarkasti (`-match exact`); `-match glob` ja `-match regexp` sallivat
kuviot.

Testattava kirjasto on oma tiedostonsa. Se ei kutsu työkalun komentoja,
joten sen voi testata pelkällä tclsh:lla:

```{.tcl tiedosto="esimerkit/12-testit/vaylat.tcl"}
```

```{.tcl tiedosto="esimerkit/12-testit/main.tcl" osa="testit"}
```

`cleanupTests` tulostaa yhteenvedon ja nollaa laskurit, joten
epäonnistuneiden määrä luetaan ennen sitä:

```{.tcl tiedosto="esimerkit/12-testit/main.tcl" osa="lopetus"}
```

```{.tuloste tiedosto="esimerkit/12-testit.odotettu"}
```

Testi `jasenna-3` löysi tätä lukua kirjoitettaessa virheen: `\w` sisältää
numerot, joten numerolla alkava nimi kelpasi aluksi. Epäonnistunut testi
tulostaa testin rungon sekä odotetun ja saadun tuloksen.

Suuremmassa projektissa testit ovat tiedostoissa `*.test`, ja
`all.tcl` ajaa ne komennolla `tcltest::runAllTests`. Valitsimet
`-match nimi*` ja `-verbose bpe` valitsevat ajettavat testit ja
tulosteen tarkkuuden.

## Jäljitys

`trace add execution` kutsuu käsittelijää ennen proseduurin kutsua ja
sen jälkeen, ja `trace add variable` aina, kun muuttujaa luetaan tai
kirjoitetaan. Niillä selvitetään, kuka kutsuu ja mitä, muuttamatta
tutkittavaa koodia. `info level -1` kertoo kutsujan.

```{.tcl tiedosto="esimerkit/12-jaljitys.tcl" osa="kutsut"}
```

```{.tcl tiedosto="esimerkit/12-jaljitys.tcl" osa="muuttuja"}
```

## Mittaus

`time {skripti} n` ajaa skriptin `n` kertaa ja palauttaa keskimääräisen
ajan mikrosekunteina. Ensimmäinen kutsu sisältää proseduurin
kääntämisen tavukoodiksi, joten mittaa useampi toisto.

```{.tcl tiedosto="esimerkit/12-jaljitys.tcl" osa="time"}
```

```{.tuloste tiedosto="esimerkit/12-jaljitys.odotettu"}
```

Laajempaan profilointiin sopii `trace add execution … enterstep`,
mutta se hidastaa ajoa paljon. Yleensä riittää mitata epäillyt
proseduurit `time`-komennolla ja tarkistaa luvun 5 hinnat.

## Muut työkalut

| Työkalu | Käyttö |
|---------|--------|
| Nagelfar | Staattinen tarkistin: syntaksi, argumenttimäärät, aaltosulkeeton `expr`. Tuntee myös EDA-työkalujen komentoja lisätiedostoilla. |
| tclint | Muotoilija ja tarkistin (Python-pohjainen, EDA-yhteisön kehittämä) |
| tkcon | Parempi interaktiivinen konsoli |
| Tcllib | `cmdline`, `json`, `csv`, `logger`, `struct`-tietorakenteet |
| tclsh `-encoding` | Skriptitiedoston merkistö, jos se ei ole järjestelmän oletus |

Staattinen tarkistus kannattaa ajaa CI:ssä samoin kuin muidenkin
kielten koodille. Kun työkalun komentoja ei voi ajaa CI:ssä,
logiikan testit ja tarkistin ovat ainoa automaattinen varmistus.

## Käytännössä

- **Testattava logiikka erilleen työkalun komennoista.** Jäsentimet,
  laskenta ja nimien käsittely testataan tclsh:lla CI:ssä. Työkalun
  komentoja kutsuvat ohuet proseduurit testataan työkalussa.
- **Testaa virhetapaukset** `-returnCodes error -errorCode …`:lla.
  Virheellinen syöte on EDA-skripteissä yleistä.
- **Paluuarvo testiajosta.** `cleanupTests` ei aseta sitä, joten lue
  laskuri ja kutsu `exit`.
- **Jäljitä, älä lisää tulosteita.** `trace` ei muuta tutkittavaa koodia
  eikä unohdu tuotantoon.
- **Staattinen tarkistus CI:hin.** Nagelfar tai tclint löytää
  aaltosulkeettomat lausekkeet ja väärät argumenttimäärät ennen ajoa.

## Itsearviointi

- Osaat kirjoittaa tcltest-testejä onnistuville ja virhetapauksille ja
  palauttaa CI:lle oikean paluuarvon.
- Osaat jäljittää proseduurin kutsut ja muuttujan kirjoitukset
  `trace`-komennolla.
- Osaat mitata koodin keston `time`-komennolla luotettavasti.
- Osaat jakaa EDA-skriptin testattavaan logiikkaan ja ohueen
  työkalukerrokseen.
