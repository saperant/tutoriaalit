# Kolme tyypillistä hintaa: lista merkkijonona kasvatettuna,
# esitysten edestakainen muunnos silmukassa ja aaltosulkeeton expr.
# Tulos tulostetaan vain suuruusluokkana, koska ajat vaihtelevat.
# Mitatut erot ovat tyypillisesti 20-kertaisia tai suurempia.

# Paras kolmesta ajosta mikrosekunteina.
proc mittaa {runko} {
    set ajat {}
    for {set i 0} {$i < 3} {incr i} {
        lappend ajat [lindex [time {uplevel 1 $runko} 1] 0]
    }
    return [expr {max([tcl::mathfunc::min {*}$ajat], 1)}]
}

proc vertaa {nimi hidas nopea} {
    set suhde [expr {$hidas / $nopea}]
    puts [format "%-28s %s" $nimi \
              [expr {$suhde >= 3 ? "selvästi hitaampi" : "ero pieni"}]]
}

# @alku kasvatus
proc merkkijonona {n} {
    set l ""
    for {set i 0} {$i < $n} {incr i} { set l "$l $i" }
    return $l
}
proc listana {n} {
    set l {}
    for {set i 0} {$i < $n} {incr i} { lappend l $i }
    return $l
}
# @loppu kasvatus

# @alku muunnos
proc muuntaen {l} {
    set s 0
    for {set i 0} {$i < [llength $l]} {incr i} {
        incr s [lindex $l $i]
        string length $l             ;# pakottaa listan merkkijonoksi
    }
    return $s
}
proc muuntamatta {l} {
    set s 0
    foreach x $l { incr s $x }
    return $s
}
# @loppu muunnos

# @alku expr
proc ilman_sulkeita {n} {
    set s 0
    for {set i 0} {$i < $n} {incr i} { set s [expr $s + $i] }
    return $s
}
proc sulkein {n} {
    set s 0
    for {set i 0} {$i < $n} {incr i} { set s [expr {$s + $i}] }
    return $s
}
# @loppu expr

set n 20000
vertaa "lista merkkijonona" \
    [mittaa {merkkijonona $n}] [mittaa {listana $n}]
set l [listana 2000]
vertaa "esitysten muunnos" \
    [mittaa {muuntaen $l}] [mittaa {muuntamatta $l}]
vertaa "expr ilman aaltosulkeita" \
    [mittaa {ilman_sulkeita $n}] [mittaa {sulkein $n}]
