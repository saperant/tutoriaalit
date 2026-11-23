# Pikaoppaan koodi: jokainen osa on testattu tällä tiedostolla.

# @alku proc
proc luo {nimi {leveys 1} args} {     ;# oletus ja loput argumentit
    set v [dict merge {-suunta in} $args]
    return [list $nimi $leveys [dict get $v -suunta]]
}
lassign [luo data 8 -suunta out] n w s
# @loppu proc
puts "$n $w $s"

# @alku kokoelmat
set l {c a b}
lappend l d                          ;# muokkaa muuttujaa paikallaan
set j [lsort -dictionary $l]
set i [lsearch -exact $l b]          ;# -1, jos ei löydy
set p [lmap x $l {string toupper $x}]
set d [dict create clk 2.5 axi 4.0]
dict set d ddr 1.25
dict incr laskuri INV_X1             ;# puuttuva avain alkaa nollasta
dict for {k v} $d { set _ $k }
set e [dict exists $d clk]
# @loppu kokoelmat
puts "$j $i $p [dict get $d ddr] $e"

# @alku virheet
proc lue {polku} {
    if {![file exists $polku]} {
        throw [list LUKU PUUTTUU $polku] "ei tiedostoa $polku"
    }
}
try {
    lue x.rpt
} trap {LUKU PUUTTUU} {viesti} {
    set tulos "puuttuu"
} on error {viesti valinnat} {
    return -options $valinnat $viesti  ;# heitä eteenpäin
} finally {
    # siivous aina
}
# @loppu virheet
puts $tulos

# @alku nimiavaruus
namespace eval ::lib {
    namespace export tee
    namespace ensemble create        ;# kutsu: lib tee ...
    variable laskuri 0
}
proc ::lib::tee {} { variable laskuri; incr laskuri }
# @loppu nimiavaruus
lib tee
puts [lib tee]

# @alku oo
oo::class create Laskuri {
    variable n
    constructor {} { set n 0 }
    method lisaa {{k 1}} { incr n $k }
}
set c [Laskuri new]
$c lisaa 5
# @loppu oo
puts [$c lisaa]

# @alku tiedosto
set f [open tulos.txt w]
try {
    fconfigure $f -encoding utf-8
    puts $f "rivi"
} finally { close $f }
set f [open tulos.txt]
set rivit [split [string trimright [read $f]] \n]
close $f
set out [exec sort << "b\na"]        ;# virhe, jos paluuarvo != 0
# @loppu tiedosto
puts "$rivit [join [split $out \n] ,]"
file delete tulos.txt
