# Testattava kirjasto: väylänimien jäsentäminen ja laajentaminen.

namespace eval ::vaylat {}

# "data[7:0]" -> {data 7 0}; yksittäinen signaali "clk" -> {clk {} {}}
proc ::vaylat::jasenna {nimi} {
    if {[regexp {^([A-Za-z_]\w*)\[(\d+):(\d+)\]$} $nimi - perus msb lsb]} {
        return [list $perus [scan $msb %d] [scan $lsb %d]]
    }
    if {[regexp {^[A-Za-z_]\w*$} $nimi]} {
        return [list $nimi {} {}]
    }
    throw [list VAYLA NIMI $nimi] "virheellinen väylänimi: $nimi"
}

# "data[2:0]" -> {data[2] data[1] data[0]}
proc ::vaylat::laajenna {nimi} {
    lassign [jasenna $nimi] perus msb lsb
    if {$msb eq ""} { return [list $perus] }
    set askel [expr {$msb >= $lsb ? -1 : 1}]
    set tulos {}
    for {set i $msb} {$i != $lsb + $askel} {incr i $askel} {
        lappend tulos "$perus\[$i\]"
    }
    return $tulos
}
