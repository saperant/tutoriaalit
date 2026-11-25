Selitys: miksi vajaita ikkunoita ei lasketa
===========================================

Liukuvan keskiarvon voi laskea sarjan alussa kahdella tavalla. Vajaa
ikkuna käyttää niitä arvoja, joita on, jolloin tulos on yhtä pitkä kuin
syöte. Täysi ikkuna aloittaa vasta, kun arvoja on tarpeeksi.

Kirjasto käyttää täyttä ikkunaa. Vajaan ikkunan keskiarvo perustuu
harvempiin arvoihin, joten se heiluu enemmän, ja kuvaajassa sarjan alku
näyttää levottomalta, vaikka sää ei ole muuttunut. Lyhyempi tulos on
pienempi haitta kuin harhaanjohtava kuvaaja.

Tarkka määritelmä on funktion :func:`saa.tilasto.liukuva_keskiarvo`
kuvauksessa.
