# opetus-sta: pieni ajoitusanalysaattori, joka käyttäytyy kuten kaupalliset
# EDA-työkalut: sen komennot ovat Tcl-komentoja, ja käyttäjän skripti
# ajetaan eräajona.
#
#   tclsh opetus_sta.tcl -source skripti.tcl [-- argumentit]
#
# Paluuarvo: 0 kun skripti meni läpi, 1 kun skriptissä oli virhe ja
# 2 kun komentorivi oli väärin. Netlista luetaan BLIF-muodossa, jonka
# Yosys kirjoittaa komennolla write_blif.

# Viivemalli (ns): kiikun kello->Q, portin viive ja kiikun asetusaika.
set ::KELLO_Q 0.35
set ::PORTTI 0.18
set ::ASETUS 0.12

# @alku lue
proc read_blif {polku} {
    array unset ::portti
    array unset ::kiikku
    set ::tulot {}
    set ::lahdot {}
    set f [open $polku]
    set rivit [split [read $f] \n]
    close $f
    set n [llength $rivit]
    for {set i 0} {$i < $n} {incr i} {
        set sanat [lindex $rivit $i]
        switch -- [lindex $sanat 0] {
            .inputs  { lappend ::tulot {*}[lrange $sanat 1 end] }
            .outputs { lappend ::lahdot {*}[lrange $sanat 1 end] }
            .names {
                set tulo [lrange $sanat 1 end-1]
                set kansi [lindex $rivit [expr {$i + 1}]]
                # Yksi tulo ja kansi "1 1" on pelkkä johdin.
                set johdin [expr {[llength $tulo] == 1
                                  && $kansi eq "1 1"}]
                set ::portti([lindex $sanat end]) [list $tulo $johdin]
            }
            .subckt {
                set liitos [dict create]
                foreach pari [lrange $sanat 2 end] {
                    lassign [split $pari =] nasta verkko
                    dict set liitos $nasta $verkko
                }
                set ::kiikku([dict get $liitos Q]) [dict get $liitos D]
            }
        }
    }
    return [expr {[array size ::portti] + [array size ::kiikku]}]
}
# @loppu lue

proc create_clock {args} {
    set ::kello [lindex $args end]
    set ::jakso [dict get [lrange $args 0 end-1] -period]
}

proc get_cells {{kuvio *}} {
    lsort [array names ::kiikku $kuvio]
}

# Saapumisaika verkolle: palauttaa {aika syvyys lähtö}.
proc saapuminen {verkko} {
    if {[info exists ::muisti($verkko)]} { return $::muisti($verkko) }
    if {[info exists ::kiikku($verkko)]} {
        set tulos [list $::KELLO_Q 0 $verkko]
    } elseif {[info exists ::portti($verkko)]} {
        lassign $::portti($verkko) tulot johdin
        set tulos {0.0 0 vakio}
        foreach t $tulot {
            set s [saapuminen $t]
            if {[lindex $s 0] >= [lindex $tulos 0]} { set tulos $s }
        }
        if {!$johdin} {
            lassign $tulos aika syvyys lahto
            set tulos [list [expr {$aika + $::PORTTI}] \
                           [expr {$syvyys + 1}] $lahto]
        }
    } else {
        set tulos [list 0.0 0 $verkko]
    }
    set ::muisti($verkko) $tulos
    return $tulos
}

# @alku raportti
proc report_timing {args} {
    if {![info exists ::jakso]} {
        error "report_timing: kelloa ei ole määritelty (create_clock)"
    }
    array unset ::muisti
    set pahin {-1 0 {} {}}
    foreach {q d} [array get ::kiikku] {
        lassign [saapuminen $d] aika syvyys lahto
        if {$aika > [lindex $pahin 0]} {
            set pahin [list $aika $syvyys $lahto $q]
        }
    }
    lassign $pahin aika syvyys lahto loppu
    set vaadittu [expr {$::jakso - $::ASETUS}]
    set slack [expr {$vaadittu - $aika}]
    set tila [expr {$slack >= 0 ? "MET" : "VIOLATED"}]
    set teksti [join [list \
        "Ajoitusraportti (opetus-sta)" \
        [format "Kello: %s  jakso %.2f ns" $::kello $::jakso] \
        "Lähtö: $lahto (kiikku)" \
        "Loppu: $loppu (kiikku)" \
        "Polun syvyys: $syvyys" \
        [format "  saapumisaika   %6.2f" $aika] \
        [format "  vaadittu aika  %6.2f" $vaadittu] \
        [format "  slack          %6.2f (%s)" $slack $tila]] \n]
    if {[dict exists $args -file]} {
        set f [open [dict get $args -file] w]
        puts $f $teksti
        close $f
    } else {
        puts $teksti
    }
    return $tila
}
# @loppu raportti

# @alku eraajo
proc kaytto {} {
    puts stderr "käyttö: opetus_sta.tcl -source skripti.tcl \[-- arg...\]"
    exit 2
}

set erotin [lsearch -exact $argv --]
if {$erotin >= 0} {
    set ::skriptin_argv [lrange $argv [expr {$erotin + 1}] end]
    set argv [lrange $argv 0 [expr {$erotin - 1}]]
} else {
    set ::skriptin_argv {}
}
if {[llength $argv] != 2 || [lindex $argv 0] ne "-source"} { kaytto }
set skripti [lindex $argv 1]

puts "opetus-sta 1.0: ajetaan [file tail $skripti]"
if {[catch {uplevel #0 [list source $skripti]} viesti valinnat]} {
    # Virheen rivinumero löytyy pinojäljestä: (file "x.tcl" line 5).
    regexp {line (\d+)\)} [dict get $valinnat -errorinfo] - rivi
    puts "Error: $viesti ([file tail $skripti], rivi $rivi)"
    exit 1
}
puts "opetus-sta: valmis"
exit 0
# @loppu eraajo
