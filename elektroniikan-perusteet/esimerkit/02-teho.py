"""Vastuksen virta ja tehohäviö sekä tehonkeston valinta."""

from spice import lopeta, muotoile, simuloi, vertaa

# @alku kasin
U_vastus = 5.0 - 2.0     # vastuksen yli jäävä jännite (V)
R = 47.0
virta = U_vastus / R     # Ohmin laki
teho = U_vastus * virta  # P = U I = I^2 R = U^2 / R
# @loppu kasin

tulos = simuloi("02-teho.cir")
print("Etuvastus 47 ohm:")
vertaa("I", tulos.arvot["@r1[i]"], virta, "A")
vertaa("P", tulos.arvot["@r1[p]"], teho, "W")

# @alku kesto
# Vastus valitaan niin, että tehonkesto on vähintään kaksinkertainen
# häviöön nähden: kuuma vastus vanhenee ja muuttaa arvoaan.
KESTOT = [0.125, 0.25, 0.5, 1.0, 2.0]
kesto = next(k for k in KESTOT if k >= 2 * teho)
print(f"valitaan {muotoile(kesto, 'W')}:n vastus")
# @loppu kesto
lopeta()
