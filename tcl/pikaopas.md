---
title: Tcl
subtitle: Pikaopas kokeneelle kehittäjälle · Tcl 8.6 · EDA-skriptaus
---

# Korvaussäännöt

| Merkintä | Merkitys |
|----------|----------|
| `a b c` | komento `a`, argumentit `b` ja `c` |
| `"… $x [k] \n"` | yksi sana, korvaukset tehdään |
| `{… $x [k]}` | yksi sana, ei korvauksia |
| `[komento]` | komennon tulos |
| `$x`, `${x y}`, `$a(k)` | muuttuja, erikoisnimi, taulukko |
| `{*}$lista` | alkiot erillisiksi sanoiksi |
| `\` rivin lopussa | jatkorivi |
| `;#` | kommentti rivin lopussa |

- Korvaus tehdään kerran; tulos on aina yksi sana.
- `expr {…}`, `if {…}`: aina aaltosulkeet (nopeus, turvallisuus).
- `{u0/data[3]}`: hakasulkeelliset nimet aaltosulkeisiin.
- `08` on virheellinen oktaaliluku (8.6): `scan $x %d`.

# Proseduurit

```{.tcl tiedosto="esimerkit/pikaopas.tcl" osa="proc"}
```

- `return -code error "viesti"`: virhe kutsujan rivillä.
- `upvar 1 $nimi v`: kutsujan muuttuja; `global x`, `variable x`.
- `uplevel 1 $runko`: koodi kutsujan kontekstissa.
- `apply {{x} {expr {$x*2}}} 3`: nimetön funktio.

# Ohjaus

| Rakenne | Muoto |
|---------|-------|
| Ehto | `if {…} {…} elseif {…} {…} else {…}` |
| Silmukat | `while {…} {…}`, `for {set i 0} {$i<$n} {incr i} {…}` |
| Läpikäynti | `foreach {a b} $l {…}`, `foreach x $l y $m {…}` |
| Valinta | `switch -glob -- $x {a* {…} default {…}}` |
| Kerääminen | `lmap x $l {…}` (`continue` suodattaa) |
| Paluukoodit | 0 ok, 1 error, 2 return, 3 break, 4 continue |

# Lausekkeet

| Asia | Muoto |
|------|-------|
| Jako | `7/2` = 3, `-7/2` = -4, `7/2.0` = 3.5 |
| Vertailu | `==` lukuina, `eq`/`ne` merkkijonoina |
| Jäsenyys | `$x in $l`, `$x ni $l` |
| Funktiot | `int round abs min max sqrt pow double entier` |
| Ehto | `$a > 0 ? "pos" : "ei"` |
| Muotoilu | `format "%-8s %6.2f %08b %X" …` |
| Jäsennys | `scan $s "%s %f" nimi arvo` (palauttaa määrän) |
| Validointi | `string is integer -strict $x` |

# Kokoelmat

```{.tcl tiedosto="esimerkit/pikaopas.tcl" osa="kokoelmat"}
```

| Lista | Sanakirja |
|-------|-----------|
| `llength lindex lrange` | `dict get exists size keys values` |
| `lappend lset` (muuttuja) | `dict set unset incr lappend` (muuttuja) |
| `lsort -dictionary -real -index -unique` | `dict for {k v} $d {…}` |
| `lsearch -exact -glob -all -inline` | `dict filter $d key *_X1` |
| `split join concat lreverse` | `dict merge $oletus $annetut` |
| `lassign $l a b` | `dict update d k v {…}` |

Merkkijonot: `string length range index first map match trim
toupper is`, `regexp {re} $s - a b`, `regexp -all -inline`,
`regsub -all {re} $s {\1}`.

# Virheet

```{.tcl tiedosto="esimerkit/pikaopas.tcl" osa="virheet"}
```

- `catch {…} viesti valinnat` palauttaa paluukoodin.
- `dict get $valinnat -errorcode`, `-errorinfo` (pino).
- Tcl:n koodit: `POSIX ENOENT …`, `ARITH DIVZERO …`,
  `CHILDSTATUS pid koodi`, `TCL LOOKUP DICT avain`.

# Nimiavaruudet ja oliot

```{.tcl tiedosto="esimerkit/pikaopas.tcl" osa="nimiavaruus"}
```

```{.tcl tiedosto="esimerkit/pikaopas.tcl" osa="oo"}
```

- `superclass`, `next`, `mixin`, `oo::objdefine`, `$o destroy`.
- Paketti: `package provide p 1.0`; käyttö: `lappend auto_path
  $hak; package require p 1.0`.
- Oma hakemisto: `file dirname [file normalize [info script]]`.

# Tiedostot ja prosessit

```{.tcl tiedosto="esimerkit/pikaopas.tcl" osa="tiedosto"}
```

- `file join dirname tail extension rootname exists mkdir rename
  delete`, `glob -directory $d *.rpt`.
- `exec … 2>@1`: virhevirta tulosteeseen; muuten se on virhe.
- `trap CHILDSTATUS {v o}`: lapsen paluuarvo
  `[lindex [dict get $o -errorcode] 2]`.
- `open |[list ohjelma arg] r` + `fileevent $k readable cb` +
  `vwait`: rinnakkaiset ajot.

# Tapahtumat ja korutiinit

- `after ms {…}`, `after idle {…}`, `after cancel $id`.
- `vwait muuttuja`: pyöritä silmukkaa, kunnes muuttuja asetetaan.
- `coroutine c proc args`; sisällä `yield arvo`,
  `[info coroutine]` jatkamiskomento.

# Hinnat

| Kallista | Halpaa |
|----------|--------|
| aaltosulkeeton `expr` (n. 20×) | `expr {…}` tavukoodina |
| lista vs. merkkijono silmukassa | sama esitys koko ajan |
| `set l [lreplace $l …]` (kopio) | `lset`, `lappend`, K-yhdistelmä |
| `set s "$s x"` | `append s x` |
| päätason silmukka | silmukka proseduurissa |
| `exec`, työkalun raportit | yksi haku, käsittely Tcl:ssä |

# Työkalut

| Tarkoitus | Komento |
|-----------|---------|
| Ajo | `tclsh8.6 skripti.tcl arg…` (`$argv`, `$argc`) |
| Versio | `info patchlevel`, `package require Tcl 8.6` |
| Tutkiminen | `info commands get_*`, `info body p`, `info args p` |
| Testit | `package require tcltest`, `test n d -body {…} -result r` |
| Jäljitys | `trace add execution p enter cb`, `trace add variable` |
| Mittaus | `time {…} 1000` (µs/kerta) |
| Tarkistus | `nagelfar skripti.tcl`, `tclint skripti.tcl` |
| Eräajo | `vivado -mode batch -source x.tcl -tclargs …` |
