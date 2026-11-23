# Oliot: TclOO {.runko-omat-tyypit}

Tcl:ssä ei ole tietuetyyppejä. Tiedon rakenne esitetään sanakirjoilla
(luku 6), ja tilaa ja käyttäytymistä yhdistävät oliot tehdään
TclOO-järjestelmällä, joka on ollut kielen ytimessä versiosta 8.6
alkaen. Vanhemmissa skripteissä näkyy myös [incr Tcl], XOTcl ja
nimiavaruuksilla tehdyt "oliot" (luku 9).

## Luokka ja olio

`oo::class create Nimi {…}` määrittelee luokan. Luokan rungossa
`variable` luettelee olion muuttujat, `constructor` alustaa ne, ja
`method` määrittelee metodit. Metodin sisällä `my metodi` kutsuu saman
olion metodia. Isolla alkukirjaimella alkava metodi on yksityinen.

Esimerkki mallintaa oheislaitteen rekisterikarttaa: kantaosoite,
rekisterien siirtymät ja arvot, jotka katkaistaan 32-bittisiksi.

```{.tcl tiedosto="esimerkit/07-rekisterit.tcl" osa="luokka"}
```

Virheet heitetään virhekoodin kanssa (`-errorcode`), jotta kutsuja voi
käsitellä tuntemattoman rekisterin muista virheistä erillään (luku 8).

## Periytyminen ja `next`

`superclass` periyttää luokan. `next` kutsuu yliluokan samannimistä
metodia tai konstruktoria. Ajastin on rekisterikartta, jolla on
kiinteät rekisterit ja oma metodi:

```{.tcl tiedosto="esimerkit/07-rekisterit.tcl" osa="periytyminen"}
```

## Mixin

Mixin on luokka, jonka metodit lisätään olion tai luokan eteen
metodien hakujärjestyksessä. `next` jatkaa varsinaiseen metodiin. Näin
lokitus, ajanotto tai tarkistukset lisätään muuttamatta alkuperäistä
luokkaa:

```{.tcl tiedosto="esimerkit/07-rekisterit.tcl" osa="mixin"}
```

```{.tcl tiedosto="esimerkit/07-rekisterit.tcl" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-rekisterit.odotettu"}
```

Olio on komento: `$ajastin kaynnista 1000` kutsuu metodia. `new` antaa
oliolle yksilöllisen nimen, `create nimi` kiinteän nimen. Olio elää,
kunnes se tuhotaan `destroy`-metodilla tai sen nimiavaruus poistetaan;
Tcl ei kerää olioita roskana. `info object` ja `info class`
kertovat olion ja luokan rakenteen.

## Muut piirteet

- `filter` ohjaa kaikki olion metodikutsut yhden metodin kautta
  (esim. kutsulokiin).
- `oo::objdefine` lisää yksittäiselle oliolle metodeja tai mixinejä.
- `forward` ohjaa metodin suoraan komentoon:
  `forward loki puts stderr`.
- `oo::define` muuttaa luokkaa ajonaikana. Muutos koskee myös
  olemassa olevia olioita.
- Luokkamuuttujia ei ole sellaisenaan. Jaettu tila sijoitetaan luokan
  nimiavaruuteen tai erilliseen olioon.

## Käytännössä

- **Sanakirja datalle, olio tilalle.** Jos rakenne on vain dataa, joka
  välitetään ja tallennetaan, käytä sanakirjaa. Olio sopii, kun
  arvoon liittyy invariantteja (rekisterien rajat) tai resurssi
  (avoin tiedosto, työkalun istunto).
- **Koostaminen ja mixinit periytymisen sijaan.** Syvä luokkahierarkia
  on Tcl:ssäkin hauras; mixin lisää poikkileikkaavan toiminnon
  (lokitus, ajanotto) yhteen paikkaan.
- **Tuhoa oliot.** Oliot eivät vapaudu automaattisesti. Käytä
  `try … finally {$olio destroy}` tai luo olio nimiavaruuteen, joka
  poistetaan kerralla.
- **Yksityiset metodit isolla alkukirjaimella** pitävät julkisen
  rajapinnan pienenä.
- **Virhekoodi jokaiseen heitettyyn virheeseen**, jotta kutsuja voi
  valita käsittelyn ilman viestitekstin vertailua.

## Itsearviointi

- Osaat määritellä TclOO-luokan konstruktoreineen, metodeineen ja
  yksityisine metodeineen.
- Osaat periyttää luokan ja kutsua yliluokan metodia `next`-komennolla.
- Osaat lisätä oliolle toiminnallisuutta mixinillä muuttamatta luokkaa.
- Osaat valita sanakirjan ja olion välillä ja huolehtia olion
  tuhoamisesta.
