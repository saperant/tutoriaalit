# Proseduurit: oletusarvot, vaihteleva määrä argumentteja,
# nimetyt valitsimet ja useamman arvon palauttaminen.

# @alku oletus
proc jakso_ns {taajuus_mhz {tarkkuus 3}} {
    return [format "%.${tarkkuus}f" [expr {1000.0 / $taajuus_mhz}]]
}
puts [jakso_ns 300]
puts [jakso_ns 300 1]
# @loppu oletus

# @alku args
proc summa {args} {
    set s 0
    foreach x $args { set s [expr {$s + $x}] }
    return $s
}
puts [summa 1 2 3 4]
# @loppu args

# @alku valitsimet
# EDA-työkalujen tapaan nimetyt valitsimet: oletukset ja annetut
# arvot yhdistetään dict merge -komennolla.
proc luo_kello {nimi args} {
    set oletus {-jakso 10.0 -kayttosuhde 0.5 -vaihe 0.0}
    if {[llength $args] % 2} {
        return -code error "valitsimilta puuttuu arvo: $args"
    }
    foreach avain [dict keys $args] {
        if {![dict exists $oletus $avain]} {
            return -code error "tuntematon valitsin $avain, sallitut:\
                [join [dict keys $oletus] {, }]"
        }
    }
    set v [dict merge $oletus $args]
    set nousu [dict get $v -vaihe]
    set lasku [expr {$nousu + [dict get $v -jakso]
                     * [dict get $v -kayttosuhde]}]
    return [list $nimi [dict get $v -jakso] $nousu $lasku]
}
puts [luo_kello clk_core -jakso 2.5]
catch {luo_kello clk -taajuus 100} viesti
puts $viesti
# @loppu valitsimet

# @alku palautus
# Useampi arvo palautetaan listana ja puretaan lassign-komennolla.
proc min_max {luvut} {
    set j [lsort -real $luvut]
    return [list [lindex $j 0] [lindex $j end]]
}
lassign [min_max {3.2 -1.5 7.0 0.25}] pienin suurin
puts "pienin $pienin, suurin $suurin"
# @loppu palautus
