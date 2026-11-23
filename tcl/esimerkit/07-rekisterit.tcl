# TclOO: rekisterikartan malli. Luokka, konstruktori, metodit,
# periytyminen ja next, sekä mixin lokituksen lisäämiseen.

# @alku luokka
oo::class create Rekisterikartta {
    variable kanta rekisterit arvot

    constructor {kantaosoite} {
        set kanta $kantaosoite
        set rekisterit [dict create]
        set arvot [dict create]
    }

    method lisaa {nimi siirtyma {nollaus 0}} {
        if {[dict exists $rekisterit $nimi]} {
            return -code error -errorcode {REKISTERI KAKSOIS} \
                "rekisteri $nimi on jo määritelty"
        }
        dict set rekisterit $nimi $siirtyma
        dict set arvot $nimi $nollaus
        return [my osoite $nimi]
    }

    method osoite {nimi} {
        return [expr {$kanta + [dict get $rekisterit $nimi]}]
    }

    method kirjoita {nimi arvo} {
        my Tarkista $nimi
        dict set arvot $nimi [expr {$arvo & 0xFFFFFFFF}]
    }

    method lue {nimi} {
        my Tarkista $nimi
        return [dict get $arvot $nimi]
    }

    # Isolla alkukirjaimella alkava metodi ei näy ulos.
    method Tarkista {nimi} {
        if {![dict exists $rekisterit $nimi]} {
            return -code error -errorcode [list REKISTERI TUNTEMATON $nimi] \
                "tuntematon rekisteri: $nimi"
        }
    }
}
# @loppu luokka

# @alku periytyminen
oo::class create Ajastin {
    superclass Rekisterikartta
    constructor {kantaosoite} {
        next $kantaosoite
        my lisaa CTRL 0x0
        my lisaa LOAD 0x4 0xFFFF
        my lisaa COUNT 0x8
    }
    method kaynnista {jakso} {
        my kirjoita LOAD $jakso
        my kirjoita CTRL 1
    }
}
# @loppu periytyminen

# @alku mixin
# Mixin lisää käyttäytymistä mihin tahansa olioon muuttamatta luokkaa.
oo::class create Lokittava {
    method kirjoita {nimi arvo} {
        puts [format "  kirjoitus %-5s 0x%08X <- 0x%X" \
                  $nimi [my osoite $nimi] $arvo]
        next $nimi $arvo
    }
}
# @loppu mixin

# @alku kaytto
set ajastin [Ajastin new 0x40001000]
oo::objdefine $ajastin mixin Lokittava
$ajastin kaynnista 1000
puts "LOAD = [$ajastin lue LOAD], COUNT = [$ajastin lue COUNT]"
try {
    $ajastin lue STATUS
} trap {REKISTERI TUNTEMATON} {viesti} {
    puts "virhe: $viesti"
}
puts [info object class $ajastin]
puts [lsort [info object methods $ajastin -all]]
$ajastin destroy
# @loppu kaytto
