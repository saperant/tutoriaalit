# Assosiatiivinen taulukko (array): muuttujien kokoelma, jonka alkioihin
# viitataan muodossa nimi(avain). Vanhat skriptit ja työkalujen omat
# esimerkit käyttävät sitä sanakirjan tilalla.

# @alku perus
array set jakso {clk_core 2.5 clk_io 10.0}
set jakso(clk_dbg) 20.0
puts "$jakso(clk_core) ns, [array size jakso] kelloa"
puts [lsort [array names jakso clk_*o*]]
puts [info exists jakso(clk_usb)]

# Avain on merkkijono, ja muuttujakorvaus toimii sulkeiden sisällä.
# Välilyönnin sisältävä avain vaatii lainauksen tai muuttujan.
set avain "pll 1"
set jakso($avain) 1.25
puts $jakso($avain)
parray jakso clk_*
# @loppu perus

# @alku valitys
# Taulukko ei ole arvo: sitä ei voi välittää eikä palauttaa. Proseduuri
# saa taulukon nimen ja sitoo sen upvar-komennolla.
proc nopein {taulukkonimi} {
    upvar 1 $taulukkonimi t
    set paras {}
    foreach nimi [lsort [array names t]] {
        if {$paras eq {} || $t($nimi) < $t($paras)} { set paras $nimi }
    }
    return $paras
}
puts [nopein jakso]
# @loppu valitys

# @alku muunnos
# array get tuottaa avain–arvo-listan, joka kelpaa sanakirjaksi, ja
# array set purkaa sanakirjan taulukkoon. Järjestys ei säily, joten
# tulostusta varten avaimet lajitellaan.
set d [array get jakso clk_*]
puts [lmap k [lsort [dict keys $d]] { list $k [dict get $d $k] }]

array unset jakso
array set jakso [dict create clk_a 4.0 clk_b 8.0]
puts [lsort [array names jakso]]
# @loppu muunnos
