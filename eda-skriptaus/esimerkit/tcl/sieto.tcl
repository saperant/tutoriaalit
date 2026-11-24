# Virheensieto Yosysin Tcl-tilassa: epäonnistunut komento on Tcl-virhe,
# jonka voi ottaa kiinni. Ilman catchia skripti pysähtyy ja yosys
# palauttaa nollasta poikkeavan arvon.
yosys -import

# @alku sieto
set ensisijainen $::env(RTL_UUSI)
set vara $::env(RTL)
if {[catch {read_verilog -sv $ensisijainen}]} {
    puts "ei saatu luettua [file tail $ensisijainen], käytetään varaa"
    read_verilog -sv $vara
}
hierarchy -check -top laskuri
puts "hierarkia tarkistettu, jatketaan synteesiin"
# @loppu sieto
