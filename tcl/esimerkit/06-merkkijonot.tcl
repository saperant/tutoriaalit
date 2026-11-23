# Merkkijonot: string-komennot, string map, säännölliset lausekkeet.

# @alku string
set polku "top/u_core/u_alu/add_0/S\[7\]"
puts [string length $polku]
puts [string range $polku 0 [string first / $polku]-1]
puts [string toupper [file tail u_core/alu.sv]]
puts [string match {*/u_alu/*} $polku]
puts [string is integer -strict 0x1F]
puts [string is integer -strict ""]  ;# ilman -strict tyhjä kelpaa
# @loppu string

# @alku hierarkia
set osat [split $polku /]
puts "taso [llength $osat], lohko [lindex $osat end-1]"
puts [join [lrange $osat 0 end-1] .]
# @loppu hierarkia

# @alku map
# string map korvaa kaikki parit yhdellä kierroksella vasemmalta
# oikealle: pidempi avain ensin, jos avaimet alkavat samoin.
set malli {module @NIMI@ #(parameter W = @W@) (...);}
puts [string map [list @NIMI@ fifo @W@ 32] $malli]
# Hakasulkeet pois väylänimistä, esim. tiedostonimiä varten:
puts [string map {[ _ ] {}} {data[3]}]
# @loppu map

# @alku regexp
set rivi {Slack (VIOLATED) : -0.214ns (required 2.000 - arrival 2.214)}
if {[regexp {Slack \((\w+)\)\s*:\s*(-?[\d.]+)ns} $rivi - tila slack]} {
    puts "$tila $slack"
}
puts [regexp -all -inline {\d+\.\d+} $rivi]
puts [regsub -all {(\w+)\[(\d+)\]} {a[1] b[22]} {\1_\2}]
# @loppu regexp
