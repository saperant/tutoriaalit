# Proseduurit ja ohjausrakenteet {.runko-ohjaus}

Tcl:n ohjausrakenteet ovat komentoja, jotka saavat koodilohkot
argumentteina. Samalla mekanismilla voi kirjoittaa omia
ohjausrakenteita. Tämä luku näyttää proseduurien argumenttimallit,
viittausparametrit ja omat ohjausrakenteet.

## Proseduurit

`proc nimi argumentit runko` määrittelee komennon. Argumenttilistan
alkio `{nimi oletus}` antaa oletusarvon, ja viimeinen alkio `args`
kerää loput argumentit listaksi. Proseduuri palauttaa `return`-arvon
tai viimeisen komennon tuloksen.

```{.tcl tiedosto="esimerkit/04-proseduurit.tcl" osa="oletus"}
```

```{.tcl tiedosto="esimerkit/04-proseduurit.tcl" osa="args"}
```

EDA-työkalujen komennot käyttävät nimettyjä valitsimia
(`-period 2.5 -name clk`). Saman rajapinnan saa omaan proseduuriin
kokoamalla oletukset sanakirjaksi ja yhdistämällä annetut arvot
komennolla `dict merge`. Tuntemattomat valitsimet hylätään, jotta
kirjoitusvirhe ei jää huomaamatta:

```{.tcl tiedosto="esimerkit/04-proseduurit.tcl" osa="valitsimet"}
```

Useampi tulos palautetaan listana, joka puretaan `lassign`-komennolla:

```{.tcl tiedosto="esimerkit/04-proseduurit.tcl" osa="palautus"}
```

```{.tuloste tiedosto="esimerkit/04-proseduurit.odotettu"}
```

`return -code error` palauttaa virheen kutsujan kohdalta. Silloin
virheilmoitus osoittaa väärin kutsuneeseen riviin eikä proseduurin
sisälle.

## Ohjausrakenteet

`if`/`elseif`/`else`, `while`, `for` ja `foreach` toimivat kuten
muissakin kielissä. `foreach` voi ottaa useita muuttujia kerralla,
mikä sopii tasaisen listan läpikäyntiin. `switch` vertaa merkkijonoja
tarkasti, kuvioilla (`-glob`) tai säännöllisillä lausekkeilla
(`-regexp`). Merkintä `-` haaran rungon paikalla jakaa saman rungon
seuraavan haaran kanssa, ja `--` päättää valitsimet, jos arvo voi
alkaa viivalla.

```{.tcl tiedosto="esimerkit/04-ohjaus.tcl" osa="perus"}
```

## Viittausparametrit: `upvar`

Argumentit välitetään arvoina. Kun proseduurin on muutettava kutsujan
muuttujaa, sille annetaan muuttujan *nimi*, ja `upvar` sitoo
paikallisen nimen kutsujan muuttujaan. Tcl:n omat komennot `incr`,
`lappend` ja `dict set` toimivat samoin.

```{.tcl tiedosto="esimerkit/04-ohjaus.tcl" osa="upvar"}
```

```{.dot otsikko="Kutsukehykset esimerkin ensimmäisen kutsun aikana. upvar 1 sitoo proseduurin paikallisen nimen yhtä tasoa ylempänä olevaan muuttujaan."}
digraph {
  rankdir=LR; node [shape=box];
  subgraph cluster_0 {
    label="taso 0: päätaso"; labeljust=l; style=dashed;
    kirjastot [label="kirjastot = work"];
  }
  subgraph cluster_1 {
    label="taso 1: lisaa_jos_puuttuu"; labeljust=l; style=dashed;
    nimi [label="listamuuttuja = kirjastot"];
    arvo [label="arvo = ieee"];
    lista [label="lista"];
  }
  lista -> kirjastot [label="upvar 1"];
}
```

Seuraavan osion `uplevel 1` käyttää samaa pinoa toisin päin: se
suorittaa annetun koodin ylemmän tason kehyksessä.

## Omat ohjausrakenteet: `uplevel`

`uplevel 1 $runko` suorittaa koodin kutsujan kontekstissa, jolloin
rungon muuttujat ovat kutsujan muuttujia. `catch` palauttaa
paluukoodin: 0 onnistui, 1 virhe, 2 `return`, 3 `break`, 4 `continue`.
Esimerkin `yrita` toistaa runkoa, kunnes se onnistuu. Tällaisella
rakenteella voi odottaa esimerkiksi varattua lisenssipalvelinta.

```{.tcl tiedosto="esimerkit/04-ohjaus.tcl" osa="oma"}
```

`break` lopettaa yrittämisen. Muut koodit, kuten rungon `return`,
välitetään kutsujalle `return -options` -komennolla, ja `-level`
kasvatetaan, jotta ne vaikuttavat kutsujan kontekstissa. Ilman tätä
käsittelyä `return` rungossa palaisi vain `yrita`-proseduurista.

## Nimettömät funktiot

`apply` kutsuu nimetöntä funktiota, joka on lista `{argumentit runko}`.
Sitä käytetään takaisinkutsuissa ja `lmap`-, `lsort -command`- ja
tapahtumakäsittelijöissä.

```{.tcl tiedosto="esimerkit/04-ohjaus.tcl" osa="apply"}
```

```{.tuloste tiedosto="esimerkit/04-ohjaus.odotettu"}
```

## Kommentit ja aaltosulkeet

Tulkki laskee aaltosulkeet ennen kuin se tietää, mikä rivi on
kommentti. Kommentoitu koodirivi, jossa on avaava aaltosulje, rikkoo
koko proseduurin:

```{.tcl tiedosto="esimerkit/04-kommentti.kaatuu.tcl"}
```

```{.tuloste tiedosto="esimerkit/04-kommentti.virhe"}
```

Poista vanha koodi kommentoimisen sijaan, tai kommentoi lohko
rakenteella `if 0 {…}`, jonka aaltosulkeet ovat parilliset.

## Käytännössä

- **Nimetyt valitsimet ja oletukset `dict merge` -mallilla** tekevät
  omista proseduureista samannäköisiä kuin työkalun komennot. Hylkää
  tuntemattomat valitsimet.
- **`return -code error` virheelliselle kutsulle** osoittaa vian
  kutsujan riville. Sisäiselle vialle sopii `error` tai `throw`.
- **`upvar` vain, kun muokataan kutsujan muuttujaa.** Palauta muuten
  arvo: se on helpompi testata ja ymmärtää.
- **Oma ohjausrakenne `uplevel`-komennolla** on Tcl:n tapa välttää
  toisto: uudelleenyritys, ajanotto, resurssin avaus ja sulkeminen
  (`with_file`-malli). Käsittele kaikki paluukoodit.
- **`switch -- $arvo`**: `--` estää arvon tulkinnan valitsimeksi.
- **Pidä logiikka proseduureissa**, ei päätasolla: tavukoodi on
  nopeampaa, ja proseduurin voi testata (luku 12).

## Itsearviointi

- Osaat kirjoittaa proseduurin, jossa on oletusarvoja ja nimettyjä
  valitsimia, ja validoida valitsimet.
- Osaat muokata kutsujan muuttujaa `upvar`-komennolla.
- Osaat kirjoittaa oman ohjausrakenteen `uplevel`- ja `catch`-komennoilla
  ja välittää rungon `break`-, `continue`- ja `return`-koodit oikein.
- Osaat selittää, miksi pariton aaltosulje kommentissa rikkoo
  proseduurin.
