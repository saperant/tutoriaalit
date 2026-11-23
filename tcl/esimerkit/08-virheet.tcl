# Virheet: throw ja -errorcode, try/trap/on/finally, virheen
# välittäminen eteenpäin ja catch-komennon valinnat.

# @alku heitto
proc lue_raportti {polku} {
    if {![file exists $polku]} {
        throw [list RAPORTTI PUUTTUU $polku] "raporttia ei ole: $polku"
    }
    set f [open $polku r]
    try {
        set rivit [split [read $f] \n]
    } finally {
        close $f                     ;# suljetaan myös virheen sattuessa
    }
    if {![llength [lsearch -all -regexp $rivit {^Slack}]]} {
        throw {RAPORTTI MUOTO} "$polku: ei ajoitustietoja"
    }
    return $rivit
}
# @loppu heitto

# @alku try
proc tarkista {polku} {
    try {
        lue_raportti $polku
        return "ok"
    } trap {RAPORTTI PUUTTUU} {viesti} {
        return "ohitetaan: $viesti"
    } trap {POSIX} {viesti valinnat} {
        return "käyttöjärjestelmä: [dict get $valinnat -errorcode]"
    } on error {viesti valinnat} {
        # Tuntematon virhe: lisätään tietoa ja heitetään eteenpäin.
        dict append valinnat -errorinfo "\n    (tarkistettiin $polku)"
        return -options $valinnat "tarkistus epäonnistui: $viesti"
    }
}
# @loppu try

# @alku kaytto
set f [open tyhja.rpt w]
close $f
puts [tarkista puuttuva.rpt]
if {[catch {tarkista tyhja.rpt} viesti valinnat]} {
    puts $viesti
    puts "koodi: [dict get $valinnat -errorcode]"
    set pino [split [dict get $valinnat -errorinfo] \n]
    puts [string trim [lsearch -inline -glob $pino *tarkistettiin*]]
}
# @loppu kaytto

# @alku koodit
# catch palauttaa paluukoodin: 0 ok, 1 error, 2 return, 3 break,
# 4 continue. -errorcode NONE tarkoittaa, ettei koodia annettu.
puts [catch {expr {1 / 0}} v o]:[dict get $o -errorcode]
puts [catch {error "pelkkä viesti"} v o]:[dict get $o -errorcode]
puts [catch {break}]
# @loppu koodit
