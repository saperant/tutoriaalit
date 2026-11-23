# Tcl 8.6 tulkitsee nollalla alkavan luvun oktaaliluvuksi. Väylän
# indeksi tai kellonaika "08" kaataa laskennan.

proc seuraava_indeksi {nimi} {
    # nimi on esim. "data_07"
    set indeksi [lindex [split $nimi _] end]
    # Oikein: scan $indeksi %d indeksi  (tulkitsee aina kymmenjärj.)
    return [expr {$indeksi + 1}]
}

puts [seuraava_indeksi data_07]
puts [seuraava_indeksi data_08]
