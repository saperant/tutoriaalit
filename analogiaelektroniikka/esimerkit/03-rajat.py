"""Operaatiovahvistimen rajat: lähdön jännitealue, nousunopeus ja offset."""

from spice import lopeta, simuloi, vertaa

tulos = simuloi("03-rajat.cir").arvot
# @alku kasin
U_syotto, marg_perinteinen, marg_rrio = 5.0, 1.5, 0.05
SR, askel = 0.5e6, 8.0
U_os, G = 2e-3, 1 + 100e3 / 1e3
# Ihanteellinen lähtö olisi -6 V; vahvistin leikkaa syöttöjännitteen
# sisäpuolelle jäävään rajaan.
vertaa("perinteinen", tulos["v(o1)"], -(U_syotto - marg_perinteinen), "V")
vertaa("rail-to-rail", tulos["v(o2)"], -(U_syotto - marg_rrio), "V")
# Nousunopeuden rajoittama askel: 10...90 % vie 0,8 * askel / SR.
vertaa("t 10-90 %", tulos["t_nousu"], 0.8 * askel / SR, "s", 0.03)
# Offset vahvistuu samalla ei-invertoivalla vahvistuksella kuin signaali.
vertaa("offset ulos", tulos["v(o4)"], U_os * G, "V", 0.01)
# @loppu kasin
lopeta()
