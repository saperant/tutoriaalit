# Lukee kellomäärittelyt muodossa "nimi jakso_ns" ja tulostaa
# taajuudet. Virheelliset rivit raportoidaan, eikä ajo pysähdy niihin.

proc lue_kellot {kanava} {
    set kellot [dict create]
    set rivinro 0
    while {[gets $kanava rivi] >= 0} {
        incr rivinro
        set rivi [string trim $rivi]
        if {$rivi eq "" || [string index $rivi 0] eq "#"} {
            continue
        }
        if {[scan $rivi "%s %f %s" nimi jakso ylim] != 2 || $jakso <= 0} {
            puts stderr "rivi $rivinro ohitettu: $rivi"
            continue
        }
        dict set kellot $nimi $jakso
    }
    return $kellot
}

set kellot [lue_kellot stdin]
dict for {nimi jakso} $kellot {
    puts [format "%-10s %6.3f ns %8.2f MHz" $nimi $jakso \
              [expr {1000.0 / $jakso}]]
}
