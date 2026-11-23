# Yksikkötestit tcltest-paketilla. Ajo: tclsh main.tcl
package require tcltest 2.5
namespace import ::tcltest::test ::tcltest::cleanupTests

source [file join [file dirname [file normalize [info script]]] vaylat.tcl]

# @alku testit
test jasenna-1 "väylä jaetaan osiin" -body {
    vaylat::jasenna {data[7:0]}
} -result {data 7 0}

test jasenna-2 "etunollat eivät ole oktaalilukuja" -body {
    vaylat::jasenna {addr[09:08]}
} -result {addr 9 8}

test jasenna-3 "virheellinen nimi heittää koodin" -body {
    vaylat::jasenna {7data}
} -returnCodes error -errorCode {VAYLA NIMI 7data} \
  -result "virheellinen väylänimi: 7data"

test laajenna-1 "laskeva ja nouseva väylä" -body {
    list [vaylat::laajenna {d[1:0]}] [vaylat::laajenna {d[0:1]}]
} -result {{{d[1]} {d[0]}} {{d[0]} {d[1]}}}

test laajenna-2 "yksittäinen signaali" -body {
    vaylat::laajenna clk
} -result clk
# @loppu testit

# @alku lopetus
# cleanupTests tulostaa yhteenvedon. Paluuarvo kertoo CI:lle,
# epäonnistuiko jokin testi.
set epaonnistui [expr {$::tcltest::numTests(Failed) > 0}]
cleanupTests
exit $epaonnistui
# @loppu lopetus
