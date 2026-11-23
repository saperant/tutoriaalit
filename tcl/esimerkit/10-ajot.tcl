# Rinnakkaiset työkaluajot tapahtumasilmukalla: jokainen ajo on oma
# prosessi, jonka tulostetta luetaan fileevent-takaisinkutsulla.
# Simuloidut "työkaluajot" ovat tämän saman skriptin lapsiprosesseja.

# @alku lapsi
if {[lindex $argv 0] eq "lapsi"} {
    lassign $argv - nimi kesto
    after $kesto                     ;# "synteesi" kestää kesto ms
    puts "$nimi: slack [format %.2f [expr {0.5 - $kesto / 400.0}]]"
    exit [expr {$nimi eq "dsp" ? 2 : 0}]
}
# @loppu lapsi

# @alku kaynnistys
set kesken 0
proc kaynnista {nimi kesto} {
    global kesken
    set komento [list [info nameofexecutable] [info script] \
                     lapsi $nimi $kesto]
    set kanava [open |[list {*}$komento 2>@1] r]
    fconfigure $kanava -blocking 0 -buffering line
    fileevent $kanava readable [list lue $kanava $nimi]
    incr kesken
}
# @loppu kaynnistys

# @alku lukeminen
proc lue {kanava nimi} {
    global kesken tulokset
    if {[gets $kanava rivi] >= 0} {
        dict lappend tulokset $nimi $rivi
        return
    }
    if {![eof $kanava]} return       ;# rivi ei ole vielä kokonainen
    # Estävä tila takaisin, jotta close raportoi lapsen paluuarvon.
    fconfigure $kanava -blocking 1
    if {[catch {close $kanava} viesti valinnat]} {
        set koodi [dict get $valinnat -errorcode]
        dict lappend tulokset $nimi "VIRHE: paluuarvo [lindex $koodi 2]"
    }
    incr kesken -1
}
# @loppu lukeminen

# @alku paaohjelma
set tulokset [dict create]
set alku [clock milliseconds]
foreach {nimi kesto} {alu 300 fifo 100 dsp 200 regs 250} {
    kaynnista $nimi $kesto
}
# vwait pyörittää tapahtumasilmukkaa, kunnes muuttuja muuttuu.
while {$kesken > 0} { vwait kesken }
set kesto [expr {[clock milliseconds] - $alku}]

foreach nimi [lsort [dict keys $tulokset]] {
    puts [join [dict get $tulokset $nimi] "; "]
}
puts "rinnakkain: [expr {$kesto < 800 ? "kyllä" : "ei"}]"
# @loppu paaohjelma
