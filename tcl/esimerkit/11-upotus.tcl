# Tulkki tulkin sisällä: isäntäohjelma ("työkalu") ajaa käyttäjän
# rajoiteskriptin turvallisessa lapsitulkissa, jolle se antaa vain
# omat komentonsa. Sama rakenne on C-ohjelmassa, joka upottaa Tcl:n.

# @alku komennot
# Työkalun omat komennot: tavallisia proseduureja isäntätulkissa.
set kellot [dict create]

proc luo_kello {nimi jakso} {
    if {![string is double -strict $jakso] || $jakso <= 0} {
        throw {RAJOITE JAKSO} "$nimi: jakson on oltava positiivinen luku"
    }
    dict set ::kellot $nimi $jakso
    return $nimi
}

proc viesti {teksti} { puts "  skripti: $teksti" }
# @loppu komennot

# @alku ajo
proc aja_rajoitteet {skripti} {
    set lapsi [interp create -safe]
    try {
        # Lapsi näkee isännän proseduurit näillä nimillä. Muuta se ei
        # isännästä näe: ei muuttujia, tiedostoja eikä prosesseja.
        interp alias $lapsi create_clock {} luo_kello
        interp alias $lapsi puts {} viesti
        # Katkaise skripti, joka ei pääty.
        interp limit $lapsi command -value 500
        interp eval $lapsi $skripti
        return "ok"
    } on error {virhe} {
        return "virhe: $virhe"
    } finally {
        interp delete $lapsi
    }
}
# @loppu ajo

# @alku kaytto
puts [aja_rajoitteet {
    set perus 2.5
    create_clock clk_core $perus
    create_clock clk_io [expr {$perus * 4}]
    puts "kellot määritelty"
}]
puts "kellot: $kellot"

puts [aja_rajoitteet {create_clock clk_neg -1}]
puts [aja_rajoitteet {exec rm -rf /tmp/tulokset}]
puts [aja_rajoitteet {set f [open /etc/passwd]}]
puts [aja_rajoitteet {while 1 {incr i}}]
puts "kellot: $kellot"
# @loppu kaytto
