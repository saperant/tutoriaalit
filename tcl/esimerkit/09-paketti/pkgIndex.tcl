# Paketin hakemisto: package require lataa tiedoston vasta tarvittaessa.
# $dir on hakemisto, josta tämä tiedosto löytyi.
package ifneeded ajoitus 1.0 [list source [file join $dir ajoitus.tcl]]
