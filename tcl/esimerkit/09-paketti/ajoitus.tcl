# Ajoitusraportin apufunktiot nimiavaruudessa ja komentokokoelmana
# (ensemble): ajoitus jasenna, ajoitus yhteenveto.

package require Tcl 8.6

namespace eval ::ajoitus {
    namespace export jasenna yhteenveto
    namespace ensemble create

    # Nimiavaruuden muuttuja: yhteinen tila kaikille proseduureille.
    variable raja 0.0
}

proc ::ajoitus::jasenna {teksti} {
    set polut {}
    foreach rivi [split $teksti \n] {
        if {[regexp {^(\S+)\s+(-?[\d.]+)$} [string trim $rivi] - p s]} {
            lappend polut [list $p $s]
        }
    }
    return $polut
}

proc ::ajoitus::yhteenveto {polut} {
    variable raja
    set rikkojat [lmap p $polut {
        if {[lindex $p 1] >= $raja} continue
        set p
    }]
    set wns [expr {[llength $polut]
        ? [tcl::mathfunc::min {*}[lmap p $polut {lindex $p 1}]] : 0.0}]
    return [dict create polkuja [llength $polut] \
                rikkojia [llength $rikkojat] wns $wns]
}

package provide ajoitus 1.0
