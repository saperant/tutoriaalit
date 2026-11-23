# Jäljitys ja mittaus: trace add execution näyttää proseduurin kutsut,
# trace add variable muuttujan kirjoitukset, time keskimääräisen ajan.

proc kerroin {luku} { expr {$luku * 2} }
proc laske {luvut} {
    set s 0
    foreach x $luvut { incr s [kerroin $x] }
    return $s
}

# @alku kutsut
proc nayta_kutsu {komento tapahtuma} {
    puts "  -> $komento"
}
proc nayta_paluu {komento koodi tulos tapahtuma} {
    puts "  <- [lindex $komento 0] = $tulos (koodi $koodi)"
}
trace add execution kerroin enter nayta_kutsu
trace add execution kerroin leave nayta_paluu
puts "summa [laske {1 2}]"
trace remove execution kerroin enter nayta_kutsu
trace remove execution kerroin leave nayta_paluu
# @loppu kutsut

# @alku muuttuja
# Kuka muuttaa globaalia asetusta? info level näyttää kirjoittajan.
proc vahdi {nimi indeksi toiminto} {
    upvar 1 $nimi arvo
    set kutsuja [expr {[info level] > 1 ? [lindex [info level -1] 0] \
                           : "päätaso"}]
    puts "  $nimi = $arvo ($kutsuja)"
}
set jakso 10.0
trace add variable jakso write vahdi
proc nopeuta {} { set ::jakso 2.5 }
set jakso 5.0
nopeuta
# @loppu muuttuja

# @alku time
set t [time {laske {1 2 3 4 5 6 7 8}} 1000]
puts "laske: [expr {[lindex $t 0] < 1000 ? "alle ms" : "hidas"}]\
      / kutsu (1000 toistoa)"
# @loppu time
