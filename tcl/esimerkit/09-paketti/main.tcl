# Käyttää pakettia ajoitus. Hakupolkuun lisätään skriptin oma
# hakemisto, joten ohjelma toimii mistä tahansa käynnistettynä.

lappend auto_path [file dirname [file normalize [info script]]]
package require ajoitus 1.0

set raportti {
    u_alu/S[7]     -0.120
    u_regs/q[3]     0.450
    u_fifo/wptr[2] -0.030
}
set yv [ajoitus yhteenveto [ajoitus jasenna $raportti]]
dict for {avain arvo} $yv { puts "$avain: $arvo" }

# Nimiavaruuden muuttujaa voi säätää täydellä nimellä.
set ::ajoitus::raja 0.5
puts "rajalla 0.5: [dict get [ajoitus yhteenveto \
    [ajoitus jasenna $raportti]] rikkojia] rikkojaa"
puts [lsort [namespace eval ::ajoitus {namespace export}]]
