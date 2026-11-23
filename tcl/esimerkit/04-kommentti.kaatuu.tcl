# Kommentti on komento, joka alkaa #-merkillä. Aaltosulkeet lasketaan
# ennen kommenttien tunnistamista, joten pariton sulje kommentissa
# rikkoo rungon.

proc tarkista_leveys {leveys} {
    # vanha versio: if {$leveys > 64} {
    if {$leveys > 128} {
        error "liian leveä väylä: $leveys"
    }
    return ok
}

puts [tarkista_leveys 32]
