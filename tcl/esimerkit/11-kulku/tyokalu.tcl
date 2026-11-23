# Simuloitu EDA-työkalu. Oikeassa työkalussa nämä komennot ovat
# valmiina tulkissa; tässä ne ovat tavallisia proseduureja, jotta
# kulkua voi ajaa ja testata pelkällä tclsh:lla.

namespace eval ::tyokalu {
    variable suunnitelma [dict create]
}

proc ::tyokalu::read_hdl {args} {
    variable suunnitelma
    foreach tiedosto $args {
        if {[file extension $tiedosto] ni {.sv .v .vhd}} {
            throw [list TYOKALU HDL $tiedosto] \
                "tuntematon lähdetiedosto: $tiedosto"
        }
        dict lappend suunnitelma lahteet $tiedosto
    }
}

proc ::tyokalu::synthesize {top strategia} {
    variable suunnitelma
    if {![dict exists $suunnitelma lahteet]} {
        throw {TYOKALU TILA} "synthesize: lähteitä ei ole luettu"
    }
    # Strategia vaikuttaa simuloituun viiveeseen ja pinta-alaan.
    set viive [dict get {area 2.61 default 2.38 perf 2.12} $strategia]
    dict set suunnitelma top $top
    dict set suunnitelma viive $viive
    dict set suunnitelma ala [dict get {area 812 default 905 perf 1043} \
                                  $strategia]
}

proc ::tyokalu::report_timing {jakso} {
    variable suunnitelma
    set slack [expr {$jakso - [dict get $suunnitelma viive]}]
    return [format "Summary: WNS %.3f TNS %.3f failing %d" $slack \
                [expr {min($slack, 0.0)}] [expr {$slack < 0}]]
}

proc ::tyokalu::report_area {} {
    variable suunnitelma
    return "Total cell area: [dict get $suunnitelma ala]"
}
