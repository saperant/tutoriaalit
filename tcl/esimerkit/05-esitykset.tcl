# Arvojen sisäiset esitykset, viitelaskenta ja kopiointi kirjoitettaessa
# (copy-on-write). tcl::unsupported::representation näyttää arvon
# tyypin ja viitemäärän. Muuttuja välitetään nimellä, jotta proseduurin
# argumentti ei lisää viitettä; komennon oma argumentti lisää yhden.

proc esitys {muuttuja} {
    upvar 1 $muuttuja arvo
    set r [tcl::unsupported::representation $arvo]
    regexp {value is an? (.+?) with a refcount of (\d+)} $r - tyyppi n
    return "$tyyppi, viitteitä [expr {$n - 1}]"
}

# @alku muunnos
set luvut [list 1 2 3]
puts "list:          [esitys luvut]"
set kopio $luvut
puts "kopion jälkeen: [esitys luvut]"
string length $luvut                 ;# tarvitsee merkkijonoesityksen
puts "string length: [esitys luvut]"
llength $luvut                       ;# jäsennetään taas listaksi
puts "llength:       [esitys luvut]"
# @loppu muunnos

# @alku osoite
proc osoite {muuttuja} {
    upvar 1 $muuttuja arvo
    regexp {object pointer at (0x[0-9a-f]+)} \
        [tcl::unsupported::representation $arvo] - p
    return $p
}
set data [lrepeat 100000 0]
set ennen [osoite data]
# Arvoon viittaavat muuttuja ja lreplacen argumentti: jaettu arvo
# kopioidaan ennen muokkausta.
set data [lreplace $data 0 0 1]
puts "lreplace:      sama olio [expr {[osoite data] eq $ennen}]"
set ennen [osoite data]
# K-yhdistelmä: muuttuja tyhjennetään ennen kutsua, joten lista on
# jakamaton ja sitä muokataan paikallaan.
set data [lreplace $data[set data {}] 0 0 2]
puts "K-yhdistelmä:  sama olio [expr {[osoite data] eq $ennen}]"
set ennen [osoite data]
lset data 1 3                        ;# lset muokkaa muuttujaa suoraan
puts "lset:          sama olio [expr {[osoite data] eq $ennen}]"
# @loppu osoite
