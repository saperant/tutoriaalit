# Listat, sanakirjat ja merkkijonot {.runko-kokoelmat}

Tcl:n kokoelmat ovat lista, sanakirja (`dict`) ja assosiatiivinen
taulukko (`array`). Listat ja sanakirjat ovat arvoja: niitä voi
välittää, palauttaa ja sisäkkäistää. Taulukko on muuttujien kokoelma,
eikä sitä voi välittää arvona. Uudessa koodissa käytetään sanakirjaa,
ellei tarvita taulukon erityispiirteitä (`trace` alkioittain, vanhat
rajapinnat).

## Listat

| Tehtävä | Komento |
|---------|---------|
| Luonti ja pituus | `list a b`, `llength $l` |
| Alkio, osa | `lindex $l 0`, `lindex $l end`, `lrange $l 1 end-1` |
| Lisäys muuttujaan | `lappend l x y` |
| Muokkaus | `lset l 2 x`, `lreplace $l 0 1`, `linsert $l 0 x` |
| Haku | `lsearch -exact`, `-glob`, `-regexp`, `-all`, `-inline` |
| Jäsenyys | `expr {$x in $l}`, `ni` |
| Lajittelu | `lsort -integer`, `-real`, `-dictionary`, `-index`, `-unique` |
| Muunnos | `lmap x $l {…}`, `lreverse`, `lrepeat`, `concat` |
| Merkkijonosta ja -jonoksi | `split $s ,`, `join $l ", "` |
| Purku | `lassign $l a b c` |

Pinni- ja tiedostonimissä on numeroita. Oletuslajittelu vertaa merkki
kerrallaan, joten `data[10]` tulee ennen `data[2]`-alkiota.
`-dictionary` lajittelee numerot lukuina.

```{.tcl tiedosto="esimerkit/06-listat.tcl" osa="lajittelu"}
```

```{.tcl tiedosto="esimerkit/06-listat.tcl" osa="haku"}
```

Lista listoista on Tcl:n tapa esittää taulukkomuotoista dataa.
`lsort -index` lajittelee alkion mukaan, ja `lindex` ottaa useita
indeksejä sisäkkäisiin listoihin:

```{.tcl tiedosto="esimerkit/06-listat.tcl" osa="sisakkaiset"}
```

`lmap` on `foreach`, joka kerää rungon tulokset. `continue` jättää
alkion pois, joten sama komento suodattaa ja muuntaa:

```{.tcl tiedosto="esimerkit/06-listat.tcl" osa="lmap"}
```

```{.tuloste tiedosto="esimerkit/06-listat.odotettu"}
```

## Sanakirjat

Sanakirja on lista, jossa avaimet ja arvot vuorottelevat. Se säilyttää
lisäysjärjestyksen. Arvo voi olla toinen sanakirja, ja `dict set`,
`dict get` ja `dict exists` ottavat avainpolun:
`dict set kellot clk_core jakso 2.5`.

| Tehtävä | Komento |
|---------|---------|
| Luonti | `dict create k1 v1 k2 v2` |
| Luku ja olemassaolo | `dict get $d k`, `dict exists $d k` |
| Muokkaus muuttujaan | `dict set d k v`, `dict unset d k` |
| Laskuri ja lista | `dict incr d k`, `dict lappend d k v` |
| Läpikäynti | `dict for {k v} $d {…}`, `dict keys`, `dict values` |
| Suodatus | `dict filter $d key *_X1`, `dict filter $d value …` |
| Yhdistäminen | `dict merge $oletus $annetut` |
| Sisäkkäinen muokkaus | `dict update d k v {…}`, `dict with d {…}` |

Esimerkki laskee porttitason netlistasta solut lohkoittain.
Pinta-alaa ei tallenneta laskuriin, vaan se johdetaan
tulostusvaiheessa lukumääristä ja kirjaston tiedoista. Näin data ei
voi olla ristiriidassa itsensä kanssa.

```{.tcl tiedosto="esimerkit/06-solut.tcl" osa="kirjasto"}
```

```{.tcl tiedosto="esimerkit/06-solut.tcl" osa="jasennys"}
```

```{.tcl tiedosto="esimerkit/06-solut.tcl" osa="tulostus"}
```

Syöte ja tuloste:

```{.tuloste tiedosto="esimerkit/06-solut.syote"}
```

```{.tuloste tiedosto="esimerkit/06-solut.odotettu"}
```

`dict update` sitoo avaimen arvon paikalliseen muuttujaan ja
kirjoittaa sen takaisin lohkon jälkeen. Puuttuva avain luodaan, ja
`dict incr` aloittaa laskurin nollasta.

## Merkkijonot

`string`-komento kokoaa merkkijono-operaatiot. Indeksit ovat merkkejä,
ja `end-1` toimii kuten listoissa. `file`-komento käsittelee
tiedostopolkuja, ja sen apufunktiot sopivat myös muihin polkuihin.

```{.tcl tiedosto="esimerkit/06-merkkijonot.tcl" osa="string"}
```

Hierarkkinen nimi jaetaan tasoiksi `split`-komennolla ja kootaan
`join`-komennolla:

```{.tcl tiedosto="esimerkit/06-merkkijonot.tcl" osa="hierarkia"}
```

`string map` korvaa useita merkkijonoja yhdellä kierroksella. Se
sopii mallipohjiin ja merkkien siivoukseen:

```{.tcl tiedosto="esimerkit/06-merkkijonot.tcl" osa="map"}
```

Säännölliset lausekkeet ovat Tcl:ssä ARE-muotoa (*advanced regular
expressions*), ja ne kirjoitetaan aina aaltosulkeisiin, jotta `[`, `$`
ja `\` eivät korvaudu. `regexp` asettaa osumat muuttujiin, `-all
-inline` palauttaa kaikki osumat listana, ja `regsub` korvaa:

```{.tcl tiedosto="esimerkit/06-merkkijonot.tcl" osa="regexp"}
```

```{.tuloste tiedosto="esimerkit/06-merkkijonot.odotettu"}
```

## Käytännössä

- **Sanakirja tietueeksi, lista järjestykseksi.** Tietueen kentät
  nimetään sanakirjassa; samanmuotoiset rivit ovat lista
  sanakirjoista tai listoista.
- **`lsort -dictionary`** kaikelle, mitä ihminen lukee: pinnit,
  instanssit ja tiedostonimet.
- **Johda, älä tallenna:** summat ja tunnusluvut lasketaan
  perustiedoista silloin, kun niitä tarvitaan.
- **Koristele, lajittele, riisu:** kun lajitteluavain on laskettava,
  muodosta lista `{avain alkio}`, lajittele `-index 0` ja pura. Se on
  nopeampi ja selkeämpi kuin `lsort -command`.
- **Säännöllinen lauseke aina aaltosulkeisiin.** Ankkuroi se (`^…$`),
  kun validoit koko syötteen.
- **`dict exists` ennen `dict get`-kutsua,** jos avain voi puuttua.
  Tcl 8.6:ssa ei ole `dict getdef`-komentoa (tuli versiossa 8.7/9.0).

## Itsearviointi

- Osaat hakea, lajitella, suodattaa ja muuntaa listoja ja valita
  oikean lajittelutavan pinninimille.
- Osaat rakentaa sisäkkäisen sanakirjan syötteestä ja käydä sen läpi.
- Osaat jäsentää työkalun tulosteen säännöllisillä lausekkeilla ja
  `string`-komennoilla.
- Osaat perustella, milloin käytät listaa, sanakirjaa tai taulukkoa.
