# Käsittelemätön virhe päättää tclsh:n paluuarvolla 1 ja tulostaa
# pinon (errorInfo) virhevirtaan: mistä komennosta ja proseduurista
# virhe lähti ja mitä kautta se kulki.

proc lue_jakso {kellot nimi} {
    return [dict get $kellot $nimi]
}

proc taajuus_mhz {kellot nimi} {
    return [expr {1000.0 / [lue_jakso $kellot $nimi]}]
}

set kellot {clk_core 2.5 clk_axi 4.0}
puts [taajuus_mhz $kellot clk_core]
puts [taajuus_mhz $kellot clk_ddr]
