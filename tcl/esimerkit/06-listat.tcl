# Listojen käsittely: haku, lajittelu, muunnos ja suodatus.

set pinnit {data[10] data[2] valid data[0] clk data[1] ready}

# @alku lajittelu
puts [lsort $pinnit]                 ;# merkki kerrallaan
puts [lsort -dictionary $pinnit]     ;# numerot lukuina
# @loppu lajittelu

# @alku haku
puts [lsearch -all -inline -glob $pinnit {data\[*\]}]
puts [lsearch -exact $pinnit valid]  ;# indeksi tai -1
puts [expr {"clk" in $pinnit}]
# @loppu haku

# @alku sisakkaiset
# Lista listoista: polku, slack (ns) ja logiikkatasot.
set polut {
    {u_alu/add/S[7] -0.12 14}
    {u_regs/q[3] 0.45 3}
    {u_fifo/wptr[2] -0.03 9}
}
foreach p [lsort -real -index 1 $polut] {
    lassign $p nimi slack tasot
    puts [format "%-16s %6.2f %3d" $nimi $slack $tasot]
}
puts "huonoin: [lindex [lsort -real -index 1 $polut] 0 0]"
# @loppu sisakkaiset

# @alku lmap
# lmap kerää rungon tulokset; continue jättää alkion pois.
set rikkojat [lmap p $polut {
    if {[lindex $p 1] >= 0} continue
    lindex $p 0
}]
puts "rikkojat: [join $rikkojat {, }]"
puts [lrange [lreverse [lsort -integer [lmap p $polut {
    lindex $p 2
}]]] 0 1]
# @loppu lmap
