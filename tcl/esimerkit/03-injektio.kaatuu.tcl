# Aaltosulkeeton expr korvaa muuttujat kahdesti. Jos arvo tulee
# käyttäjältä tai tiedostosta, siinä oleva komento suoritetaan.

proc kerro_kahdella {arvo} {
    return [expr $arvo * 2]          ;# VÄÄRIN: pitää olla {$arvo * 2}
}

puts [kerro_kahdella 21]
# Syötetiedostosta luettu "luku":
puts [kerro_kahdella {[error "syötteen komento suoritettiin"]}]
