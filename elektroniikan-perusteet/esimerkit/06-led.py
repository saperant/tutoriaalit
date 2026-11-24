"""LEDin etuvastuksen mitoitus ja tarkistus simuloimalla."""

import math

from spice import lopeta, simuloi, vertaa

# @alku mitoitus
U_lahto, I_tavoite = 3.3, 10e-3
# LEDin kynnysjännite tavoitevirralla mallin parametreista:
I_S, n, R_S, U_T = 1e-20, 1.8, 5.0, 0.025865
U_F = n * U_T * math.log(I_tavoite / I_S) + I_tavoite * R_S
R = (U_lahto - U_F) / I_tavoite          # ylimääräinen jännite vastukseen
print(f"U_F = {U_F:.2f} V, laskettu R = {R:.0f} ohm -> E12: 150 ohm")
# @loppu mitoitus

# @alku tarkistus
tulos = simuloi("06-led.cir")             # piirissä Rs = 150 ohm
# Seuraava suurempi E12-arvo: virta jää hieman tavoitteen alle, ja
# U_F laskee vähän, koska virta pienenee.
I_150 = (U_lahto - U_F) / 150
vertaa("I_LED", tulos.arvot["@r1[i]"], I_150, "A", 0.02)
vertaa("U_F", tulos.arvot["v(a)"], U_F, "V", 0.02)
lopeta()
# @loppu tarkistus
