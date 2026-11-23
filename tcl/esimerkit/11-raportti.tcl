# Jäsentää ajoitusraportin tilakoneella. Muoto on yksinkertaistettu,
# mutta rakenne (otsikko, polkulohkot, yhteenveto) on EDA-työkalujen
# raporteille tyypillinen.

# @alku jasennin
proc jasenna_ajoitus {kanava} {
    set polut {}
    set polku {}
    set yhteenveto {}
    set rivinro 0
    while {[gets $kanava rivi] >= 0} {
        incr rivinro
        switch -regexp -matchvar m -- $rivi {
            {^Path (\d+)$} {
                if {[dict size $polku]} { lappend polut $polku }
                set polku [dict create nro [lindex $m 1]]
            }
            {^\s+(Startpoint|Endpoint):\s+(\S+)$} {
                dict set polku [string tolower [lindex $m 1]] \
                    [lindex $m 2]
            }
            {^\s+Slack:\s+(-?\d+\.\d+) ns} {
                dict set polku slack [lindex $m 1]
            }
            {^Summary: WNS (\S+) TNS (\S+) failing (\d+)$} {
                lassign $m - wns tns n
                set yhteenveto [dict create wns $wns tns $tns failing $n]
            }
            {^\s*(\S.*)?$} {
                # Otsikot, viivat ja tyhjät rivit ohitetaan.
            }
        }
    }
    if {[dict size $polku]} { lappend polut $polku }
    foreach p $polut {
        foreach kentta {startpoint endpoint slack} {
            if {![dict exists $p $kentta]} {
                throw {RAPORTTI MUOTO} \
                    "polulta [dict get $p nro] puuttuu $kentta"
            }
        }
    }
    if {![dict size $yhteenveto]} {
        throw {RAPORTTI MUOTO} "yhteenveto puuttuu ($rivinro riviä)"
    }
    return [list $polut $yhteenveto]
}
# @loppu jasennin

# @alku tarkistus
lassign [jasenna_ajoitus stdin] polut yhteenveto
set tns 0.0
# Koristele, lajittele, riisu: lajitteluavain listan ensimmäiseksi.
set avaimin [lmap p $polut {list [dict get $p slack] $p}]
foreach pari [lsort -real -index 0 $avaimin] {
    lassign $pari s p
    if {$s < 0} { set tns [expr {$tns + $s}] }
    puts [format "%7.3f  %-22s -> %s" $s \
              [dict get $p startpoint] [dict get $p endpoint]]
}
# Raportin oma yhteenveto tarkistetaan: jäsennysvirhe paljastuu heti.
if {abs($tns - [dict get $yhteenveto tns]) > 0.0005} {
    puts stderr "TNS ei täsmää: laskettu $tns,\
                 raportissa [dict get $yhteenveto tns]"
    exit 1
}
puts [format "WNS %.3f ns, TNS %.3f ns" [dict get $yhteenveto wns] $tns]
# @loppu tarkistus
