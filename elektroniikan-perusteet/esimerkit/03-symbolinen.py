"""Jännitteenjakaja symbolisesti SymPyllä: kaava kuormitetulle jakajalle."""

import sympy as sp

# @alku symbolinen
U, R1, R2, RL, Ua = sp.symbols("U R1 R2 R_L U_a", positive=True)
# Solmun a virtalaki: R1:n kautta tuleva virta = R2:n ja kuorman virrat.
yhtalo = sp.Eq((U - Ua) / R1, Ua / R2 + Ua / RL)
ratkaisu = sp.solve(yhtalo, Ua)[0]
print("U_a =", sp.simplify(ratkaisu))
# Ilman kuormaa (R_L -> ääretön) saadaan tuttu jakajan kaava.
print("R_L -> oo:", sp.limit(ratkaisu, RL, sp.oo))
# Theveninin vastine: tyhjäkäyntijännite ja oikosulkuvirta (U_a = 0).
U_th = sp.limit(ratkaisu, RL, sp.oo)
I_n = U / R1
print("R_th =", sp.simplify(U_th / I_n))
# @loppu symbolinen
# @alku numero
arvot = {U: 12, R1: 10_000, R2: 4_700, RL: 10_000}
print("U_a (R_L = 10 k) =", sp.N(ratkaisu.subs(arvot), 4), "V")
# @loppu numero
