# Ohjausrakenteet, upvar ja omat ohjausrakenteet uplevelillä.

# @alku perus
set portit {clk in 1 rst_n in 1 data in 32 valid out 1}
foreach {nimi suunta leveys} $portit {
    switch -glob -- $nimi {
        clk* - *_clk { set laji kello }
        rst*         { set laji nollaus }
        default      { set laji data }
    }
    puts [format "%-6s %-4s %3d %s" $nimi $suunta $leveys $laji]
}
# @loppu perus

# @alku upvar
# upvar sitoo paikallisen nimen kutsujan muuttujaan: proseduuri voi
# muokata kutsujan listaa paikallaan.
proc lisaa_jos_puuttuu {listamuuttuja arvo} {
    upvar 1 $listamuuttuja lista
    if {$arvo ni $lista} { lappend lista $arvo }
    return [llength $lista]
}
set kirjastot {work}
lisaa_jos_puuttuu kirjastot ieee
lisaa_jos_puuttuu kirjastot work
puts $kirjastot
# @loppu upvar

# @alku oma
# Oma ohjausrakenne: ajaa rungon kutsujan kontekstissa, kunnes se
# onnistuu tai yritykset loppuvat. Rungon break ja continue toimivat.
proc yrita {kertaa runko} {
    for {set i 1} {$i <= $kertaa} {incr i} {
        set koodi [catch {uplevel 1 $runko} tulos valinnat]
        switch $koodi {
            0 { return $tulos }
            1 { puts "yritys $i epäonnistui: $tulos" }
            3 { return }                          ;# break
            default {
                dict incr valinnat -level
                return -options $valinnat $tulos
            }
        }
    }
    return -code error "kaikki $kertaa yritystä epäonnistuivat"
}

set lisenssit 0
set tulos [yrita 3 {
    incr lisenssit
    if {$lisenssit < 3} { error "lisenssipalvelin varattu" }
    format "lisenssi saatu yrityksellä %d" $lisenssit
}]
puts $tulos
# @loppu oma

# @alku apply
# Nimetön funktio on lista {argumentit runko}; apply kutsuu sitä.
set nelio {{x} { expr {$x * $x} }}
puts [lmap x {1 2 3 4} { apply $nelio $x }]
# @loppu apply
