# Kirjoitusvirhe komennon nimessä: eräajo pysähtyy virheeseen.
lassign $::skriptin_argv netlista jakso raportti
read_blif $netlista
create_clock -period $jakso clk
report_timnig -file $raportti
