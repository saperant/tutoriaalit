# Parametrisoitu synteesikulku: argumenttien käsittely, vaiheet,
# lokitus, raporttien tarkistus ja paluuarvo CI:lle.
#
# Käyttö: tclsh main.tcl -top NIMI -clock JAKSO_NS
#                        [-strategy area|default|perf] [-out HAK]

set hakemisto [file dirname [file normalize [info script]]]
source [file join $hakemisto tyokalu.tcl]

# @alku argumentit
proc jasenna_argumentit {argv maaritys} {
    set tulos [dict create]
    dict for {nimi m} $maaritys {
        if {[dict exists $m oletus]} {
            dict set tulos $nimi [dict get $m oletus]
        }
    }
    if {[llength $argv] % 2} {
        throw {KAYTTO} "valitsimelta puuttuu arvo"
    }
    foreach {valitsin arvo} $argv {
        set nimi [string trimleft $valitsin -]
        if {![dict exists $maaritys $nimi]} {
            throw {KAYTTO} "tuntematon valitsin $valitsin"
        }
        set tyyppi [dict get $maaritys $nimi tyyppi]
        if {[string match {enum *} $tyyppi]} {
            if {$arvo ni [lrange $tyyppi 1 end]} {
                throw {KAYTTO} "$valitsin: sallitut [lrange $tyyppi 1 end]"
            }
        } elseif {![string is $tyyppi -strict $arvo]} {
            throw {KAYTTO} "$valitsin: odotettiin $tyyppi, saatiin '$arvo'"
        }
        dict set tulos $nimi $arvo
    }
    dict for {nimi m} $maaritys {
        if {![dict exists $tulos $nimi]} {
            throw {KAYTTO} "pakollinen valitsin -$nimi puuttuu"
        }
    }
    return $tulos
}
# @loppu argumentit

# @alku vaiheet
proc vaihe {nimi runko} {
    puts "== $nimi"
    set alku [clock milliseconds]
    try {
        uplevel 1 $runko
    } on error {viesti valinnat} {
        puts "VIRHE vaiheessa $nimi: $viesti"
        return -options $valinnat $viesti
    }
    # Kesto lokiin, ei tulosteeseen: tuloste pysyy vertailukelpoisena.
    puts $::loki "$nimi [expr {[clock milliseconds] - $alku}] ms"
}

proc aja_kulku {asetukset} {
    set out [dict get $asetukset out]
    file mkdir $out
    set ::loki [open [file join $out kulku.log] w]
    try {
        vaihe lue {
            tyokalu::read_hdl rtl/alu.sv rtl/regs.sv rtl/top.sv
        }
        vaihe syntetisoi {
            tyokalu::synthesize [dict get $asetukset top] \
                [dict get $asetukset strategy]
        }
        vaihe raportoi {
            set ajoitus [tyokalu::report_timing [dict get $asetukset clock]]
            set ala [tyokalu::report_area]
            set f [open [file join $out ajoitus.rpt] w]
            puts $f $ajoitus
            close $f
        }
    } finally {
        close $::loki
    }
    regexp {WNS (\S+)} $ajoitus - wns
    regexp {area: (\d+)} $ala - pinta
    return [dict create wns $wns ala $pinta]
}
# @loppu vaiheet

# @alku paaohjelma
set maaritys {
    top      {tyyppi alnum}
    clock    {tyyppi double}
    strategy {tyyppi {enum area default perf} oletus default}
    out      {tyyppi print oletus build}
}
try {
    set asetukset [jasenna_argumentit $argv $maaritys]
} trap KAYTTO {viesti} {
    puts stderr "virhe: $viesti"
    puts stderr "käyttö: tclsh main.tcl -top NIMI -clock NS"
    puts stderr "         \[-strategy area|default|perf\] \[-out HAK\]"
    exit 2
}

set tulos [aja_kulku $asetukset]
puts [format "top %s, strategia %s: WNS %s ns, pinta-ala %s" \
          [dict get $asetukset top] [dict get $asetukset strategy] \
          [dict get $tulos wns] [dict get $tulos ala]]
# CI:lle: 0 ajoitus kunnossa, 1 ajoitus ei täyty.
exit [expr {[dict get $tulos wns] < 0}]
# @loppu paaohjelma
