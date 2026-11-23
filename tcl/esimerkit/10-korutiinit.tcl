# Ajastimet ja korutiinit. Korutiini keskeyttää itsensä yield-
# komennolla ja jatkaa siitä, kun sitä kutsutaan uudelleen.

# @alku ajastimet
after 100 {puts "ajastin 100 ms"}
after 50 {puts "ajastin 50 ms"}
after idle {puts "idle: kun muuta ei ole tehtävänä"}
puts "ajastimet asetettu"
after 150 {set valmis 1}
vwait valmis
# @loppu ajastimet

# @alku generaattori
# Generaattori: palauttaa netlistan sanat yksi kerrallaan ja lopuksi
# tyhjän merkkijonon. Korutiinikomento poistuu, kun proseduuri palaa.
proc sanat {teksti} {
    yield [info coroutine]
    foreach rivi [split $teksti \n] {
        foreach sana [regexp -all -inline {[\w\[\]/]+} $rivi] {
            yield $sana
        }
    }
    return ""
}

coroutine seuraava sanat "INV_X1 u1 (.A(n1), .ZN(n2));\nDFF_X1 r0"
set n 0
while {[set sana [seuraava]] ne ""} {
    incr n
    if {$n <= 3} { puts "sana $n: $sana" }
}
puts "sanoja yhteensä $n"
# @loppu generaattori

# @alku odotus
# Korutiini voi odottaa tapahtumaa ilman takaisinkutsuketjua:
# after ajastaa korutiinin jatkamisen ja yield luovuttaa vuoron.
proc nuku {ms} {
    after $ms [info coroutine]
    yield
}
proc tyo {nimi viive} {
    foreach vaihe {luku synteesi raportti} {
        nuku $viive
        puts "$nimi: $vaihe"
    }
    incr ::kesken -1
}
set kesken 2
coroutine t1 tyo A 30
coroutine t2 tyo B 75
while {$kesken} { vwait kesken }
# @loppu odotus
