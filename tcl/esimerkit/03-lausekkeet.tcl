# Laskenta expr-komennolla: kokonaisluvut, liukuluvut ja muotoilu.

# @alku luvut
puts [expr {2 ** 70}]                ;# kokonaisluvut ovat rajattomia
puts [expr {7 / 2}]                  ;# kokonaislukujako: 3
puts [expr {-7 / 2}]                 ;# pyöristää alaspäin: -4
puts [expr {-7 % 2}]                 ;# jakojäännös jakajan merkkinen: 1
puts [expr {7 / 2.0}]                ;# liukuluku: 3.5
puts [expr {int(3.99)}]              ;# katkaisu: 3
puts [expr {round(2.5)}]             ;# pyöristys nollasta poispäin: 3
puts [expr {0x1F | (1 << 8)}]        ;# bittioperaatiot: 287
# @loppu luvut

# @alku vertailu
# == vertaa lukuina, jos molemmat näyttävät luvuilta; eq aina
# merkkijonoina. Merkkijonoille käytetään aina eq/ne.
puts [expr {"1.0" == "1"}]           ;# 1
puts [expr {"1.0" eq "1"}]           ;# 0
puts [expr {"abc" in {abc def}}]     ;# listan jäsenyys: 1
# @loppu vertailu

# @alku muotoilu
set taajuus [expr {1e3 / 3.3}]
puts [format "%.2f MHz" $taajuus]
puts [format "%08b %04X %o" 0xA5 48879 8]
puts [format "%-8s|%5d|" alu 42]
# @loppu muotoilu
