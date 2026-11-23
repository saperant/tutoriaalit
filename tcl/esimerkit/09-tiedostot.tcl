# Tiedostot ja ulkoiset ohjelmat: koodaus, atominen kirjoitus,
# hakemistot ja exec.

# @alku kirjoitus
# Kirjoitetaan väliaikaiseen tiedostoon ja nimetään lopuksi: lukija
# ei koskaan näe puolikasta tiedostoa.
proc kirjoita_atomisesti {polku sisalto} {
    set tmp $polku.tmp[pid]
    set f [open $tmp w]
    try {
        fconfigure $f -encoding utf-8 -translation lf
        puts -nonewline $f $sisalto
    } finally {
        close $f
    }
    file rename -force $tmp $polku
}

proc lue {polku} {
    set f [open $polku r]
    try {
        fconfigure $f -encoding utf-8
        return [read $f]
    } finally {
        close $f
    }
}
# @loppu kirjoitus

# @alku hakemistot
file mkdir [file join build raportit]
foreach nimi {ajoitus pinta-ala teho} {
    kirjoita_atomisesti [file join build raportit $nimi.rpt] \
        "# $nimi\nyhteenveto: ok\n"
}
foreach polku [lsort [glob -directory [file join build raportit] *.rpt]] {
    puts "[file tail $polku]: [file size $polku] tavua,\
          [lindex [split [lue $polku] \n] 0]"
}
puts "[file extension alu.sv] [file rootname alu.sv]"
# @loppu hakemistot

# @alku exec
# exec ajaa ohjelman ilman komentotulkkia: argumentit ovat Tcl-sanoja,
# eikä lainaus- tai välilyöntiongelmia synny.
puts [exec sort -r << "alu\nregs\nfifo"]
# Nollasta poikkeava paluuarvo on Tcl-virhe, jonka koodi kertoo syyn.
try {
    exec sh -c {echo "synteesi epäonnistui" >&2; exit 3}
} trap CHILDSTATUS {viesti valinnat} {
    set status [lindex [dict get $valinnat -errorcode] 2]
    puts "paluuarvo $status: $viesti"
}
# Virhevirran tulostus ei kaada, kun se ohjataan tulosteeseen.
puts [exec sh -c {echo varoitus >&2; echo valmis} 2>@1]
# @loppu exec
