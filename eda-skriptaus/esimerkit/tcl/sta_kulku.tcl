# Käyttäjän skripti opetus-sta-työkalulle. Argumentit:
#   netlista.blif kellojakso raporttitiedosto
lassign $::skriptin_argv netlista jakso raportti

set soluja [read_blif $netlista]
puts "Luettiin $soluja solua, kiikkuja [llength [get_cells]]"
create_clock -period $jakso clk
set tila [report_timing -file $raportti]
puts "Ajoitus jaksolla $jakso ns: $tila"
