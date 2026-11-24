"""MFB-alipäästö: siirtofunktio solmuyhtälöistä SymPyllä ja vertailu
ngspiceen."""

import math

import sympy as sp

from spice import lopeta, simuloi, vertaa

# @alku symbolinen
s, Ui, Ua, Uo = sp.symbols("s U_i U_a U_o")
R1, R2, R3, C1, C2 = sp.symbols("R1 R2 R3 C1 C2", positive=True)
# Ihanteellinen operaatiovahvistin: invertoiva tulo on virtuaalimaassa.
kcl_a = (Ui - Ua) / R1 + (Uo - Ua) / R2 - Ua / R3 - Ua * s * C1
kcl_m = Ua / R3 + Uo * s * C2          # tulon virta on nolla
ratkaisu = sp.solve([kcl_a, kcl_m], [Ua, Uo], dict=True)[0]
H = sp.simplify(ratkaisu[Uo] / Ui)
osoittaja, nimittaja = sp.fraction(sp.factor(H))
print("osoittaja:", osoittaja)
print("nimittäjä:", sp.collect(sp.expand(nimittaja), s))
# @loppu symbolinen

# @alku arvot
arvot = {R1: 7503, R2: 7503, R3: 7503, C1: 45e-9, C2: 10e-9}
a2, a1, a0 = (float(k.subs(arvot))
              for k in sp.Poly(nimittaja, s).all_coeffs())
w0 = math.sqrt(a0 / a2)
Q = math.sqrt(a0 * a2) / a1
print(f"f0 = {w0 / (2 * math.pi):.1f} Hz, Q = {Q:.3f}")
H_num = sp.lambdify(s, H.subs(arvot))
# @loppu arvot

tulos = simuloi("04-mfb.cir").arvot
vertaa("f_c", tulos["f3"], w0 / (2 * math.pi), "Hz", 0.01)
vertaa("|H| 10 kHz", tulos["g10k"], abs(H_num(2j * math.pi * 10e3)), "",
       0.01)
lopeta()
