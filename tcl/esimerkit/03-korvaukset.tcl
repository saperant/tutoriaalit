# Tcl:n kolme korvausta ja kaksi ryhmittelytapaa.

set solu "u_alu"
set leveys 8

# @alku korvaukset
# Muuttujakorvaus ($) ja komentokorvaus ([]) lainausmerkeissä:
puts "solu $solu, leveys [expr {$leveys * 2}] bittiä"
# Aaltosulkeet estävät kaikki korvaukset:
puts {solu $solu, leveys [expr {$leveys * 2}] bittiä}
# Kenoviiva estää yksittäisen korvauksen:
puts "hinta \$5, väylä u_alu/data\[3\]"
# @loppu korvaukset

# @alku ryhmittely
# Komento jäsennetään sanoiksi kerran. Korvauksen tulos on aina yksi
# sana, vaikka siinä olisi välilyöntejä: sitä ei jäsennetä uudelleen.
set tiedostot "alu.sv regs.sv"
puts [llength $tiedostot]            ;# merkkijono listana: 2
set komento [list puts "a b"]
puts [llength $komento]              ;# 2 sanaa: puts ja "a b"
# {*} levittää listan alkiot erillisiksi sanoiksi:
set liput [list -nonewline]
puts {*}$liput "ilman rivinvaihtoa: "
puts ok
# @loppu ryhmittely

# @alku lista
# Listat rakennetaan list-komennolla, ei merkkijonoja liimaamalla.
set nimi {data[3] valid}
set huono "set_pins $nimi"           ;# kolme sanaa, hakasulkeet auki
set hyva [list set_pins $nimi]       ;# kaksi sanaa, lainaus oikein
puts "huono: $huono ([llength $huono] sanaa)"
puts "hyvä:  $hyva ([llength $hyva] sanaa)"
# @loppu lista
